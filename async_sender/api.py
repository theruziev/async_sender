import asyncio
import ssl
import time
from typing import Union, Iterable, Sequence, Optional
from email import charset as ch
from email.encoders import encode_base64
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import make_msgid, formatdate
from email.header import Header

try:
    import aiosmtplib
except ImportError:  # pragma: no cover
    aiosmtplib = None

ch.add_charset("utf-8", ch.SHORTEST, None, "utf-8")


class SenderError(Exception):
    pass


class Mail:
    """AsyncSender Mail main class.  This class is used for manage SMTP server
    connections and send messages.

    :param hostname:  Server name (or IP) to connect to
    :param port: Server port. Defaults to ``25`` if ``use_tls`` is
        ``False``, ``465`` if ``use_tls`` is ``True``.
    :param source_address: The hostname of the client. Defaults to the
        result of :func:`socket.getfqdn`. Note that this call blocks.
    :param timeout: Default timeout value for the connection, in seconds.
        Defaults to 60.
    :param use_tls: If True, make the initial connection to the server
        over TLS/SSL. Note that if the server supports STARTTLS only, this
        should be False.
    :param use_starttls: If True, make the initial connection without encrypt to the server
    over TCP and upgrade plain connection to an encrypted (TLS or SSL) connection.
    :param validate_certs: Determines if server certificates are
        validated. Defaults to True.
    :param client_cert: Path to client side certificate, for TLS
        verification.
    :param client_key: Path to client side key, for TLS verification.
    :param tls_context: An existing :class:`ssl.SSLContext`, for TLS
        verification. Mutually exclusive with ``client_cert``/
        ``client_key``.
    :param cert_bundle: Path to certificate bundle, for TLS verification.
    """

    def __init__(
        self,
        hostname: str = "",
        port: int = None,
        use_tls: bool = False,
        use_starttls: bool = False,
        username: str = None,
        password: str = None,
        from_address: str = None,
        timeout: Union[int, float] = None,
        source_address: str = None,
        loop: asyncio.AbstractEventLoop = None,
        validate_certs: bool = True,
        client_cert: str = None,
        client_key: str = None,
        tls_context: ssl.SSLContext = None,
        cert_bundle: str = None,
    ):

        self.host = hostname
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.use_starttls = use_starttls
        self.from_address = from_address
        self.timeout = timeout
        self.loop = loop
        self.source_address = source_address
        self.validate_certs = validate_certs
        self.client_cert = client_cert
        self.client_key = client_key
        self.tls_context = tls_context
        self.cert_bundle = cert_bundle

    @property
    def connection(self) -> "Connection":
        """
        Open one connection to the SMTP server.
        """
        return Connection(self)

    async def send(self, *messages: "Message"):
        """
        Sends a single or multiple messages.

        :param messages: Message instance.
        """

        async with self.connection as connection:

            for message in messages:
                if self.from_address and not message.from_address:
                    message.from_address = self.from_address
                message.validate()
                await connection.send(message)

    async def send_message(self, *args, **kwargs):
        """Shortcut for send.
        """
        await self.send(Message(*args, **kwargs))


class Message:
    """One email message.

    :param subject: message subject
    :param to: message recipient, should be one or a list of addresses
    :param body: plain text content body
    :param html: HTML content body
    :param from_address: message sender, can be one address or a two-element tuple
    :param cc: CC list, should be one or a list of addresses
    :param bcc: BCC list, should be one or a list of addresses
    :param attachments: a list of attachment instances
    :param reply_to: reply-to address
    :param date: message send date, seconds since the Epoch,
                 default to be time.time()
    :param charset: message charset, default to be 'utf-8'
    :param extra_headers: a dictionary of extra headers
    :param mail_options: a list of ESMTP options used in MAIL FROM commands
    :param rcpt_options: a list of ESMTP options used in RCPT commands
    """

    def __init__(
        self,
        subject: str = None,
        to: Union[str, Iterable] = None,
        body: str = None,
        html: str = None,
        from_address: Union[str, Iterable] = None,
        cc: Union[str, Iterable] = None,
        bcc: Union[str, Iterable] = None,
        attachments: Union["Attachment", Sequence["Attachment"]] = None,
        reply_to: Union[str, Iterable] = None,
        date: Optional[int] = None,
        charset: str = "utf-8",
        extra_headers: dict = None,
        mail_options: list = None,
        rcpt_options: list = None,
    ):
        self.message_id = make_msgid()
        self.subject = subject
        self.body = body
        self.html = html
        self.attachments = attachments or []
        self.date = date
        self.charset = charset
        self.extra_headers = extra_headers
        self.mail_options = mail_options or []
        self.rcpt_options = rcpt_options or []

        self.to = set([to] if isinstance(to, str) else to or [])
        self.from_address = from_address
        self.cc = set([cc] if isinstance(cc, str) else cc or [])
        self.bcc = set([bcc] if isinstance(bcc, str) else bcc or [])
        self.reply_to = reply_to

    @property
    def to_address(self):
        return self.to | self.cc | self.bcc

    def validate(self):
        """Do email message validation.
        """
        if not (self.to or self.cc or self.bcc):
            raise SenderError("Does not specify any recipients(to,cc,bcc)")
        if not self.from_address:
            raise SenderError("Does not specify from_address(sender)")

        if any(self.subject and (c in self.subject) for c in "\n\r"):
            raise SenderError("newline is not allowed in subject")

    def as_string(self) -> str:
        """The message string.
        """
        if self.date is None:
            self.date = time.time()

        msg = MIMEText(self.body, "plain", self.charset)
        if not self.html:
            if len(self.attachments) > 0:
                # plain text with attachments
                msg = MIMEMultipart()
                msg.attach(MIMEText(self.body, "plain", self.charset))
        else:
            msg = MIMEMultipart()
            alternative = MIMEMultipart("alternative")
            alternative.attach(MIMEText(self.body, "plain", self.charset))
            alternative.attach(MIMEText(self.html, "html", self.charset))
            msg.attach(alternative)

        msg["Subject"] = Header(self.subject, self.charset)
        msg["From"] = self.from_address
        msg["To"] = ", ".join(self.to)
        msg["Date"] = formatdate(self.date, localtime=True)
        msg["Message-ID"] = self.message_id
        if self.cc:
            msg["Cc"] = ", ".join(self.cc)
        if self.reply_to:
            msg["Reply-To"] = self.reply_to
        if self.extra_headers:
            for key, value in self.extra_headers.items():
                msg[key] = value

        for attachment in self.attachments:
            f = MIMEBase(*attachment.content_type.split("/"))
            f.set_payload(attachment.data)
            encode_base64(f)
            if attachment.filename is None:
                filename = str(None)
            else:
                filename = attachment.filename
            try:
                filename.encode("ascii")
            except UnicodeEncodeError:
                filename = ("UTF8", "", filename)
            f.add_header("Content-Disposition", attachment.disposition, filename=filename)
            for key, value in attachment.headers.items():
                f.add_header(key, value)
            msg.attach(f)

        return msg.as_string()

    def as_bytes(self) -> bytes:
        return self.as_string().encode(self.charset or "utf-8")

    def __str__(self):
        return self.as_string()  # pragma: no cover

    def attach(self, *attachment: "Attachment"):
        """Adds one or a list of attachments to the message.

        :param attachment: Attachment instance.
        """
        self.attachments.extend(attachment)

    def attach_attachment(self, *args, **kwargs):
        """Shortcut for attach.
        """
        self.attach(Attachment(*args, **kwargs))


class Attachment:
    """File attachment information.

    :param filename: filename
    :param content_type: file mimetype
    :param data: raw data
    :param disposition: content-disposition, default to be 'attachment'
    :param headers: a dictionary of headers, default to be {}
    """

    def __init__(
        self,
        filename: str = None,
        content_type: str = None,
        data=None,
        disposition: str = "attachment",
        headers: dict = None,
    ):
        self.filename = filename
        self.content_type = content_type
        self.data = data
        self.disposition = disposition
        self.headers = headers if headers else {}


class Connection:
    """This class handles connection to the SMTP server.  Instance of this
    class would be one context manager so that you do not have to manage
    connection close manually.

    :param mail: one mail instance
    """

    def __init__(self, mail):
        self.mail = mail
        if aiosmtplib is None:
            raise RuntimeError("Please install 'aiosmtplib'")  # pragma: no cover

    async def __aenter__(self):
        server = aiosmtplib.SMTP(
            hostname=self.mail.host,
            port=self.mail.port,
            use_tls=self.mail.use_tls,
            timeout=self.mail.timeout,
            source_address=self.mail.source_address,
            loop=self.mail.loop,
            validate_certs=self.mail.validate_certs,
            client_cert=self.mail.client_cert,
            client_key=self.mail.client_key,
            tls_context=self.mail.tls_context,
            cert_bundle=self.mail.cert_bundle,
        )

        if self.mail.use_starttls:
            await server.starttls()

        await server.connect()

        if self.mail.username and self.mail.password:
            await server.login(self.mail.username, self.mail.password)

        self.server = server

        return self

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        await self.server.quit()

    async def send(self, message: "Message"):
        """Send one message instance.

        :param message: one message instance.
        """
        await self.server.sendmail(
            message.from_address,
            message.to_address,
            message.as_bytes(),
            message.mail_options,
            message.rcpt_options,
        )

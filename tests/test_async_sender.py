import os

import aiohttp
import pytest
from async_sender import Message, SenderError, Attachment, Mail

SMTP_HOST = os.environ.get("SMTP_HOST", "localhost")
SMTP_PORT = os.environ.get("SMTP_PORT", 1025)
SMTP_USERNAME = os.environ.get("SMTP_USERNAME")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")


@pytest.fixture()
async def clear_inbox():
    async def factory():
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.delete(f"http://localhost:1080/messages") as resp:
                assert resp.status == 204

    return factory


@pytest.fixture()
async def get_emails():
    async def factory():
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.get(f"http://localhost:1080/messages/1.json") as resp:
                assert resp.status == 200
                return await resp.json()

    return factory


def test_subject():
    msg = Message("test")
    assert msg.subject in "test"
    msg = Message("test", from_address="from@example.com", to="to@example.com")
    assert msg.subject in str(msg)


def test_to():
    msg = Message(from_address="from@example.com", to="to@example.com")
    assert msg.to == {"to@example.com"}
    assert "to@example.com" in str(msg)
    msg = Message(to=["to01@example.com", "to02@example.com"])
    assert msg.to == {"to01@example.com", "to02@example.com"}


def test_from_address():
    msg = Message(from_address="from@example.com", to="to@example.com")
    assert msg.from_address == "from@example.com"
    assert "from@example.com" in str(msg)


def test_cc():
    msg = Message(from_address="from@example.com", to="to@example.com", cc="cc@example.com")
    assert "cc@example.com" in str(msg)


def test_bcc():
    msg = Message(from_address="from@example.com", to="to@example.com", bcc="bcc@example.com")
    assert "bcc@example.com" not in str(msg)


def test_to_address():
    msg = Message(to="to@example.com")
    assert msg.to_address == {"to@example.com"}
    msg = Message(
        to="to@example.com", cc="cc@example.com", bcc=["bcc01@example.com", "bcc02@example.com"]
    )
    expected_to_address = {
        "to@example.com",
        "cc@example.com",
        "bcc01@example.com",
        "bcc02@example.com",
    }
    assert msg.to_address == expected_to_address
    msg = Message(to="to@example.com", cc="to@example.com")
    assert msg.to_address == {"to@example.com"}


def test_reply_to():
    msg = Message(
        from_address="from@example.com", to="to@example.com", reply_to="reply-to@example.com"
    )
    assert msg.reply_to == "reply-to@example.com"
    assert "reply-to@example.com" in str(msg)


def test_charset():
    msg = Message()
    assert msg.charset == "utf-8"
    msg = Message(charset="ascii")
    assert msg.charset == "ascii"


def test_extra_headers():
    msg = Message(
        from_address="from@example.com",
        to="to@example.com",
        extra_headers={"Extra-Header-Test": "Test"},
    )
    assert "Extra-Header-Test: Test" in str(msg)


def test_mail_and_rcpt_options():
    msg = Message()
    assert msg.mail_options == []
    assert msg.rcpt_options == []
    msg = Message(mail_options=["BODY=8BITMIME"])
    assert msg.mail_options == ["BODY=8BITMIME"]
    msg = Message(rcpt_options=["NOTIFY=OK"])
    assert msg.rcpt_options == ["NOTIFY=OK"]


def test_validate():
    msg = Message(from_address="from@example.com")
    with pytest.raises(SenderError):
        msg.validate()

    msg = Message(to="to@example.com")
    with pytest.raises(SenderError):
        msg.validate()

    msg = Message(subject="subject\r", from_address="from@example.com", to="to@example.com")
    with pytest.raises(SenderError):
        msg.validate()
    msg = Message(subject="subject\n", from_address="from@example.com", to="to@example.com")
    with pytest.raises(SenderError):
        msg.validate()


def test_attach():
    msg = Message()
    att = Attachment()
    atts = [Attachment() for i in range(3)]
    msg.attach(att)
    assert msg.attachments == [att]
    msg.attach(atts)
    assert msg.attachments == [att] + atts


def test_attach_attachment():
    msg = Message()
    msg.attach_attachment("test.txt", "text/plain", "this is test")
    assert msg.attachments[0].filename == "test.txt"
    assert msg.attachments[0].content_type == "text/plain"
    assert msg.attachments[0].data == "this is test"


def test_plain_text():
    plain_text = "Hello!\nIt works."
    msg = Message(from_address="from@example.com", to="to@example.com", body=plain_text)
    assert msg.body == plain_text
    assert "Content-Type: text/plain" in str(msg)


def test_plain_text_with_attachments():
    msg = Message(
        from_address="from@example.com", to="to@example.com", subject="hello", body="hello world"
    )
    msg.attach_attachment(content_type="text/plain", data=b"this is test")
    assert "Content-Type: multipart/mixed" in str(msg)


def test_html():
    html_text = "<b>Hello</b><br/>It works."
    msg = Message(from_address="from@example.com", to="to@example.com", html=html_text)
    assert msg.html == html_text
    assert "Content-Type: multipart/alternative" in str(msg)


def test_message_id():
    msg = Message(from_address="from@example.com", to="to@example.com")
    assert f"Message-ID: {msg.message_id}" in str(msg)


def test_attachment_ascii_filename():
    msg = Message(from_address="from@example.com", to="to@example.com")
    msg.attach_attachment("my test doc.txt", "text/plain", b"this is test")
    assert "Content-Disposition: attachment; filename=" '"my test doc.txt"' in str(msg)


def test_attachment_unicode_filename():
    msg = Message(from_address="from@example.com", to="to@example.com")
    # Chinese filename :)
    msg.attach_attachment("我的测试文档.txt", "text/plain", "this is test")
    assert "UTF8''%E6%88%91%E7%9A%84%E6%B5%8B%E8%AF" "%95%E6%96%87%E6%A1%A3.txt" in str(msg)


@pytest.mark.asyncio
async def test_send_email(clear_inbox, get_emails):
    await clear_inbox()

    mail = Mail(hostname=SMTP_HOST, port=SMTP_PORT, username=SMTP_USERNAME, password=SMTP_PASSWORD)
    msg = Message(
        from_address="from@example.com",
        subject="Hello Subject",
        to="to@example.com",
        body="Hello World",
    )

    await mail.send(msg)
    email = await get_emails()
    assert msg.from_address in email["sender"]
    assert msg.subject == email["subject"]
    assert msg.body in email["source"]
    assert msg.message_id in email["source"]

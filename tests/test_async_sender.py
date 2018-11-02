import pytest

from async_sender import Mail
from async_sender import Message


@pytest.mark.asyncio
async def test_sending_email():
    msg = Message(
        from_address="bruziev@fix.ru", subject="Hello World!!!!",
        to=["bruziev@fix.ru", "b@mail.ru", "bb@bb.com"],
        bcc=["bruziev@fix.ru", "b@mail.ru", "bb@bb.com"],
        body="Test email"
    )

    mail = Mail(hostname="localhost", port=1025)
    await mail.send(msg)


@pytest.mark.asyncio
async def test_chinese():
    msg = Message("Hello03", to="to@example.com")
    msg.from_address = 'noreply@example.com'
    msg.body = u"你好世界"  # Chinese :)
    msg.html = u"<b>你好世界</b>"

    mail = Mail(hostname="localhost", port=1025)
    await mail.send(msg)

AsyncSender
===========


AsyncSender provides a simple interface to set up SMTP and send asynchronously email messages.


Installation
------------

Install with the following command::

    $ pip install async_sender


Quickstart
----------

Sender is really easy to use.  Emails are managed through a `Mail`
instance::

    from sender import Mail
    import asyncio

    loop = asyncio.get_event_loop()

    mail = Mail()

    loop.run_until_complete(mail.send_message("Hello", from_address="from@example.com",
                      to="to@example.com", body="Hello world!"))


Message
-------

To send one message, we need to create a `Message` instance::

    from sender import Message

    msg = Message("demo subject", from_address="from@example.com",
                  to="to@example.com")




.. AsyncSender documentation master file, created by
   sphinx-quickstart on Fri Nov  2 12:53:23 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to AsyncSender's documentation!
=======================================

.. toctree::
   :maxdepth: 2
   :hidden:

   async_sender
   changelog


AsyncSender provides a simple interface to set up a SMTP connection and send email messages asynchronously.


Installation
------------

Install with the following command::

    $ pip install async_sender


Quickstart
----------

AsyncSender is really easy to use.  Emails are managed through a :class:`Mail`
instance::

    from async_sender import Mail
    import asyncio


    async def run():
        mail = Mail()

        await mail.send_message("Hello", from_address="from@example.com",
                                to="to@example.com", body="Hello world!")


    asyncio.run(run())

Message
-------

To send one message, we need to create a :class:`Message` instance::

    from async_sender import Message

    msg = Message("demo subject", from_address="from@example.com",
                  to="to@example.com")




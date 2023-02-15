.. image:: https://img.shields.io/travis/com/theruziev/async_sender.svg?style=flat-square
        :target: https://travis-ci.com/theruziev/async_sender
.. image:: https://img.shields.io/codecov/c/github/theruziev/async_sender.svg?style=flat-square
        :target: https://codecov.io/gh/theruziev/async_sender
.. image:: https://img.shields.io/pypi/v/async_sender.svg?style=flat-square   
        :alt: PyPI   
        :target: https://pypi.org/project/async_sender/


AsyncSender provides a simple interface to set up a SMTP connection and send email messages asynchronously.


Installation
------------

Install with the following command

.. code-block:: bash

    pip install async_sender


Quickstart
----------

AsyncSender is really easy to use.  Emails are managed through a `Mail`
instance

.. code-block:: python

    from async_sender import Mail
    import asyncio


    async def run():
        mail = Mail()

        await mail.send_message("Hello", from_address="from@example.com",
                                to="to@example.com", body="Hello world!")


    asyncio.run(run())


Message
-------

To send one message, we need to create a `Message` instance

.. code-block:: python

    from async_sender import Message

    msg = Message("demo subject", from_address="from@example.com",
                  to="to@example.com")




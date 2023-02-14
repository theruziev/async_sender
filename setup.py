from setuptools import setup, find_packages
import os

from async_sender import __version__


here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
except IOError:
    README = ''


REQUIRED = [
    'aiosmtplib==2.0.1'
]

setup(
    name='async_sender',
    version=__version__,
    description="AsyncSender is a tiny module for SMTP mail sending, Inspired by Sender.",
    long_description=README,
    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation :: CPython",
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
    ],
    keywords='email, sender, smtp, asyncio',
    author='Bakhtiyor Ruziev',
    author_email='rbakhtiyor+github@gmail.com',
    url='https://github.com/theruziev/async_sender',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIRED,
)

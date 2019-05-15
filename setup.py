
import setuptools
from setuptools import setup, find_packages

setup(
    python_requires='>=3.0',
    name='DelegatorBot',
    version='1.1.2',
    packages=['delegatorbot'],
    include_package_data=True,
    license='MIT',
    keywords='steemit steem upvote bot',
    url='http://github.com/artolabs/delegatorbot',
    author='ArtoLabs',
    author_email='artopium@gmail.com',
    install_requires=[
        'python-dateutil',
        'simplesteem==1.1.17',
        'screenlogger==1.3.1',
        'mysimpledb==1.0',
    ],
    py_modules=['delegatorbot'],
    entry_points = {
        'console_scripts': [
            'runbot=delegatorbot.runbot:run',
        ],
    },
    zip_safe=False
)

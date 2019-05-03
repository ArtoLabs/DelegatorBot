
import setuptools
from setuptools import setup, find_packages

setup(
    python_requires='>=3.0',
    name='DelegatorBot',
    version='1.0',
    packages=find_packages(),
    include_package_data=True,
    package_data={'delegatorbot': ['post_template.txt']},
    license='MIT',
    keywords='steemit steem upvote bot',
    url='http://github.com/artolabs/delegatorbot',
    author='ArtoLabs',
    author_email='artopium@gmail.com',
    install_requires=[
        'python-dateutil',
        'simplesteem',
        'screenlogger',
    ],
    #py_modules=['delegatorbot'],   
    zip_safe=False
)

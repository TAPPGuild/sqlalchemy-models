from setuptools import setup

classifiers = [
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 2",
    "Topic :: Software Development :: Libraries",
]

setup(
    name='bitjws-login',
    version='0.0.3',
    description='User related data models for a server using an SQLAlchemy supported database.',
    author='deginner',
    author_email='support@deginner.com',
    url='https://github.com/deginner/bitjws-login',
    license='MIT',
    classifiers=classifiers,
    include_package_data=True,
    packages=['bitjws_login']
)

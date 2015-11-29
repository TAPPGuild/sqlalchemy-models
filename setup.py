from setuptools import setup

classifiers = [
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 2",
    "Topic :: Software Development :: Libraries",
]

setup(
    name='sqlalchemy-login-models',
    version='0.0.5',
    description=' Generic user and login capabilities for an application using SQLAlchemy.',
    author='deginner',
    author_email='support@deginner.com',
    url='https://github.com/deginner/sqlalchemy-login-models',
    license='MIT',
    classifiers=classifiers,
    include_package_data=True,
    packages=['sqlalchemy_login_models'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-cov']
)

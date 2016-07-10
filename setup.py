from setuptools import setup

classifiers = [
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 2",
    "Topic :: Software Development :: Libraries",
]

setup(
    name='sqlalchemy-models',
    version='0.0.5.9',
    description=' Generic data models for an application using SQLAlchemy.',
    author='Git Guild',
    author_email='support@gitguild.com',
    url='https://github.com/gitguild/sqlalchemy-models',
    license='MIT',
    classifiers=classifiers,
    include_package_data=True,
    packages=['sqlalchemy_models'],
    setup_requires=['pytest-runner'],
    install_requires=['sqlalchemy>=1.0.9'],
    tests_require=['pytest', 'pytest-cov']
)

from setuptools import setup

classifiers = [
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 2",
    "Topic :: Software Development :: Libraries",
]

setup(
    name='sqlalchemy-models',
    version='0.0.6',
    description=' Generic data models for an application using SQLAlchemy.',
    author='Git Guild',
    author_email='support@gitguild.com',
    url='https://github.com/TAPPGuild/sqlalchemy-models',
    license='MIT',
    classifiers=classifiers,
    packages=['sqlalchemy_models'],
    package_dir={'sqlalchemy_models': 'sqlalchemy_models'},
    package_data={'sqlalchemy_models': ['definitions.json']},
    setup_requires=['pytest-runner'],
    install_requires=['sqlalchemy>=1.0.9',
                      'psycopg2',
                      'jsonschema',
                      'alchemyjsonschema'],
    tests_require=['pytest', 'pytest-cov']
)

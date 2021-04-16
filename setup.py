"""Config for setup package behave agent."""

import os

from setuptools import setup


__version__ = '1.0.0'


def read_file(fname):
    """Read the given file.

    :param fname: Filename to be read
    :return: File content
    """
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


setup(
    name='behave-reportportal',
    version=__version__,
    description='Agent for reporting Behave results to the Report Portal',
    long_description=read_file('README.rst'),
    long_description_content_type='text/markdown',
    author_email='SupportEPMC-TSTReportPortal@epam.com',
    url='https://github.com/reportportal/agent-python-behave',
    packages=['behave_reportportal'],
    install_requires=read_file('requirements.txt').splitlines(),
    license='Apache 2.0',
    keywords=['testing', 'reporting', 'reportportal', 'behave'],
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
        ],
)

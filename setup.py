import io
import os

from setuptools import setup

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(PROJECT_ROOT, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='omnilib',
    version='0.0.0.dev',
    description='My All-Purpose Python Library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/nitral/omnilib',
    author='Nilay Binjola',
    author_email='nilaybinjola@gmail.com',
    license="MIT",
    packages=['omnilib', 'omnilib.compute', 'omnilib.http', 'omnilib.util'],
    package_data={'omnilib.http': ['data/probes/*']},
    install_requires=['dill']
)

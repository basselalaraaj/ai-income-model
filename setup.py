from setuptools import find_packages
from setuptools import setup

REQUIRED_PACKAGES = [
    'numpy',
    'pandas',
    'tensorflow',
    'argparse',
]

setup(name='trainer',
      version='1.0',
      url='https://github.com/basselalaraaj/ai-income-model',
      author='Bassel Al Araaj',
      author_email='info@bassel.dev',
      packages=find_packages(),
      include_package_data=True,
      install_requires=REQUIRED_PACKAGES
      )

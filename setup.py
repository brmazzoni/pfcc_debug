from setuptools import setup

setup(
  name='pfcc_debug',
  version='0.1.0',
  py_modules=['main'],
  entry_points={
    'console_scripts': [
      'debug = main:cli',
    ],
  },
)

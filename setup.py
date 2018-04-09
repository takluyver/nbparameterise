from setuptools import setup

setup(name='nbparameterise',
      version='1.0',
      description='Package for setting up parameters for Jupyter Notebooks',
      url='https://github.com/mt-krainski/nbparameterise.git',
      author='takluyver with modifications by mt-krainski',
      author_email='mateusz@krainski.eu',
      license='MIT',
      packages=['nbparameterise', 'nbparameterise.code_drivers'],
      install_requires=[
          'jupyter',
          'astcheck',
          'astsearch',
      ],
      zip_safe=False)
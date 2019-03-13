from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='s3a_decorrelator',
      version='0.2',
      description='Decorrelation algorithm for diffuse sound objects and general upmix',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/s3a-spatialaudio/decorrelation-python-toolbox.git',
      author='Michael Cousins',
      author_email='michaelcousins56@gmail.com',
      license='ISC',
      packages=find_packages()
      packages=['s3a_python_decorrelation_toolbox'],
      install_requires=[
                        'numpy',
                        'soundfile',
                        'scipy',
                        'librosa',
                        'pyloudnorm',
                        'matplotlib'
                        ]
      )


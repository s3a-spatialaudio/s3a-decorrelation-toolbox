from setuptools import setup, find_namespace_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='s3a_decorrelation_toolbox',
      version='0.2.9',
      description='Decorrelation algorithm and toolbox for diffuse sound objects and general upmix',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/s3a-spatialaudio/decorrelation-python-toolbox',
      author='Michael Cousins',
      author_email='michaelcousins56@gmail.com',
      license='ISC',
      packages=['s3a_decorrelation_toolbox'],
      install_requires=[
                        'numpy >= 1.16.2',
                        'scipy >= 1.2.1',
                        'soundfile >= 0.10.0',
                        'librosa >= 0.6.3',
                        'acoustics >=  0.1.2',
                        'pyloudnorm >= 0.0.1',
                        'matplotlib >= 3.0.2'
                        ],
      include_package_data=True,
      classifiers=[
                   "Programming Language :: Python :: 3",
                   "Development Status :: 3 - Alpha",
                   "License :: OSI Approved :: ISC License (ISCL)",
                   "Operating System :: OS Independent",
                   "Topic :: Multimedia :: Sound/Audio"
                   ],
      )

from setuptools import setup, find_packages

setup(name='pyiofile',
      version='1.0a.dev3',
      description='Abstract representation of file and directory pathnames',
      long_description=open("README.rst").read(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
      ],
      keywords='funniest joke comedy flying circus',
      url='http://github.com/storborg/funniest',
      author='frankdog-dev',
      packages=find_packages(),
      install_requires=[
          'markdown',
      ],
      include_package_data=True,
      zip_safe=False)
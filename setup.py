from setuptools import setup, find_packages

setup(name='pyiofile',
      version='1.0a.dev3',
      description='Abstract representation of file and directory pathnames',
      long_description=open("README.rst").read(),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python :: 3',
      ],
      keywords='filewrapper file iofile path pathobject',
      url='http://github.com/frankdog-dev/pyiofile',
      author='frankdog-dev',
      packages=find_packages(),
      py_modules=['pyiofile'],
      include_package_data=True,
      zip_safe=False)

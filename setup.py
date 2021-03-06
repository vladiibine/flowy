#!/usr/bin/env python

from setuptools import find_packages
from setuptools import setup

install_requires = ['boto==2.33.0',
                    'venusian>=1.0a8',
                    'lazy_object_proxy==1.0.1']  # yapf: disable
try:
    import concurrent.futures
except ImportError:
    install_requires.append('futures')

setup(name='flowy',
      version='0.4.dev0',
      description="Python library for Amazon Simple Workflow Service",
      long_description=open('README.rst').read(),
      keywords='AWS SWF workflow',
      author='Sever Banesiu',
      author_email='banesiu.sever@gmail.com',
      url='https://github.com/pbs/flowy',
      license='MIT License',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      setup_requires=['nose', 'setuptools_git', 'wheel'],
      install_requires=install_requires,
      tests_require=['coverage', 'vcrpy'],
      test_suite="nose.collector",
      extras_require={
          'docs': ['sphinx', 'sphinx_rtd_theme'],
          'trace': ['pygraphviz'],
      },
      entry_points={
          "console_scripts": ["flowy = flowy.__main__:main",
                              "flowyexamples = flowy.examples:main", ]
      },
      classifiers=["Development Status :: 5 - Production/Stable",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: MIT License",
                   "Operating System :: OS Independent",
                   "Topic :: Internet",
                   "Programming Language :: Python :: 2.7",
                   "Programming Language :: Python :: 3.4"], )  # yapf: disable

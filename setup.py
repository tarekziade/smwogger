import sys
from setuptools import setup, find_packages


with open('requirements.txt') as f:
    deps = [dep for dep in f.read().split('\n') if dep.strip() != '']
    install_requires = deps

with open('README.rst') as f:
    _DESC = f.read() + '\n\n'


with open('CONTRIBUTORS.rst') as f:
    _DESC += f.read()


setup(name='smwogger',
      version="0.1",
      packages=find_packages(),
      description="Smoke Test tool",
      long_description=_DESC,
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      entry_points="""
      [console_scripts]
      smwogger = smwogger.main:main
      """)

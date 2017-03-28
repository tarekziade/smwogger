import sys
from setuptools import setup, find_packages


with open('requirements.txt') as f:
    deps = [dep for dep in f.read().split('\n') if dep.strip() != '']
    install_requires = deps

with open('README.rst') as f:
    _DESC = f.read() + '\n\n'

with open('CONTRIBUTORS.rst') as f:
    _DESC += f.read() + '\n\n'

with open('CHANGELOG.rst') as f:
    _DESC += f.read()


setup(name='smwogger',
      version="1.1",
      url="https://github.com/tarekziade/smwogger",
      packages=find_packages(),
      author="Tarek Ziade",
      author_email="tarek@ziade.org",
      description="Smoke Test tool",
      long_description=_DESC,
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      entry_points="""
      [console_scripts]
      smwogger = smwogger.main:main
      """)

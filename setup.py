from setuptools import setup, find_packages

version = '1.2'

long_description = (
    open('README.txt').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

setup(name='gummanager.cli',
      version=version,
      description="",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Programming Language :: Python",
      ],
      keywords='',
      author='Carles Bruguera',
      author_email='carles.bruguera@upcnet.es',
      url='',
      license='gpl',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['gummanager'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'docopt',
          'blessings',
          'prettytable',
          'gummanager.libs'
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      gum = gummanager.cli:main
      """,

      )

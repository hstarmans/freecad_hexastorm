from setuptools import setup
import os
# from freecad.hexastorm.version import __version__
# name: this is the name of the distribution.
# Packages using the same name here cannot be installed together

version_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                            "freecad", "hexastorm", "version.py")
with open(version_path) as fp:
    exec(fp.read())

setup(name='freecad.hexastorm',
      version=str(__version__),
      packages=['freecad',
                'freecad.hexastorm'],
      maintainer="Rik Starmans",
      maintainer_email="hstarmans@hexastorm.com",
      url="https://github.com/hstarmans/freecad_hexastorm",
      description="Workbench to simulate rays for the prism scanner design",
      install_requires=['numpy'],
      include_package_data=True)

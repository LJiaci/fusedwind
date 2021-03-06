#
# This file is autogenerated during plugin quickstart and overwritten during
# plugin makedist. DO NOT CHANGE IT if you plan to use plugin makedist to update 
# the distribution.
#

from setuptools import setup, find_packages

kwargs = {'author': 'DTU WInd Energy and NREL NWTC',
 'author_email': 'TBD',
 'classifiers': ['Intended Audience :: Science/Research',
                 'Topic :: Scientific/Engineering'],
 'description': 'Framework for Unified Systems Engineering and Design of Wind Plants',
 'download_url': 'http://github.com/FUSED-Wind/fusedwind',
 'include_package_data': True,
 'install_requires': ['openmdao.main'],
 'keywords': ['openmdao'],
 'license': 'Apache v. 2.0',
 #'maintainer': '',
 #'maintainer_email': '',
 'name': 'fusedwind',
 'package_data': {'fusedwind': []},
 'package_dir': {'': 'src'},
 'packages': ['fusedwind', 'fusedwind.plant_cost', 'fusedwind.plant_flow', 'fusedwind.turbine', 'fusedwind.lib', 'fusedwind.runSuite'],
 #'url': '',
 'version': '0.1.0',
 'zip_safe': False}


setup(**kwargs)


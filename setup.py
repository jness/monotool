from setuptools import setup, find_packages
import sys, os

version = '0.0.34'

setup(
    name='monotool',
    version=version,
    description="Mono tool to help with the build process.",
    long_description="Mono tool to help with the build process.",
    classifiers=[],
    keywords='',
    author='Jeffrey Ness',
    author_email='jeffrey.ness@bigrentz.com',
    url='',
    license='GPLv2',
    packages=find_packages(
        exclude=['ez_setup', 'tests']
    ),
    include_package_data=True,
    data_files=[
        ('monotool/templates/',
            ['monotool/templates/startup_template.stache',
            'monotool/templates/upstart_template.stache']
        )
    ],
    zip_safe=False,
    install_requires=[
        'argparse',
        'pystache'
    ],
    entry_points= {
        'console_scripts': ['monotool = monotool.monotool:main']
        },
    )

"""
setup.py — py2app yapılandırması
"""
from setuptools import setup

APP = ['taslak.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': ['folium', 'pywebview']
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
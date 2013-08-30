#!/usr/bin/env python

from distutils.core import setup
import os

pluginFiles = map(lambda x:'plugins/'+x, os.listdir('plugins'))

setup(name='phong',
  version='0.0.1',
  description='Phong helps you run a hackerspace',
  author='Torrie Fischer',
  author_email='tdfischer@phrobo.net',
  url='http://spacekit.phrobo.net/phong',
  packages=['phong'],
  scripts=['phong.py'],
  data_files=[
    ('/usr/share/phong/plugins', pluginFiles)
  ]
)

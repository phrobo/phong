#!/usr/bin/env python

from distutils.core import setup
from distutils.command.build import build as DistutilsBuild
import os

class BuildCommand(DistutilsBuild):
  def _build(self):
    from distutils.ccompiler import new_compiler
    compiler = new_compiler(compiler=self.compiler,
                                 verbose=self.verbose,
                                 dry_run=self.dry_run,
                                 force=self.force)
    objects = compiler.compile(["phong-su.c",],
                               output_dir=self.build_temp,
                               debug=self.debug)
    compiler.link_executable(objects,
                  'phong-su',
                  output_dir=self.build_temp,
                  debug=self.debug,
                  )
    if not os.path.exists(self.build_scripts):
      os.mkdir(self.build_scripts)
    self.copy_file(os.path.sep.join((self.build_temp, 'phong-su')),
                   os.path.sep.join((self.build_scripts, 'phong-su')))
  def run(self):
    self._build()
    DistutilsBuild.run(self)

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
    ('/usr/lib/phong/plugins', pluginFiles)
  ],
  cmdclass={'build': BuildCommand}
)

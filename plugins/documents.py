# Copyright (C) 2013 Torrie Fischer <tdfischer@hackerbots.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import phong
import datetime
from wikitools import page
import subprocess
import tempfile
import os
import shutil

class DocumentsPlugin(phong.Plugin):
  def availableCommands(self):
    return [BuildDocumentsCommand,]

class BuildDocumentsCommand(phong.Command):
  def name(self):
    return "build-documents"

  def helpText(self):
    return "Build documents from a repository and upload to s3"

  def buildArgs(self, args):
    args.add_argument('-c', '--command', help='Command to build PDF documents',
        default='make')
    args.add_argument('-r', '--repo', help='A repository to use', default=[],
        action='append')
    args.add_argument('-s', '--s3cfg', help='Path to s3cmd configuration',
        default='/etc/phong-s3cmd.cfg')
    args.add_argument('-b', '--bucket', help='Name of s3 bucket and path to upload to',
        default=None)
    args.add_argument('-o', '--output', help="Path to put the files",
        default=None)
    args.add_argument('-f', '--file-suffix', help='File suffixes to upload',
        default=['.pdf', '.png', '.svg'], action='append')

  def execute(self, args):
    if args.output is None:
      outputDir = tempfile.mkdtemp()
    else:
      outputDir = args.output
    foundFiles = []
    for repo in args.repo:
      repoDir = tempfile.mkdtemp()
      name = repo.split('/')[-1]
      subprocess.check_call(["git", "clone", repo, repoDir])
      subprocess.check_call(args.command.split(' '), cwd=repoDir)

      for root, dirs, files in os.walk(repoDir):
        for f in files:
          for s in args.file_suffix:
            if f.endswith(s):
              outnamedir = root.replace(repoDir, outputDir)
              outname = os.path.sep.join((
                outnamedir,
                f
              ))
              if not os.path.exists(outnamedir):
                os.makedirs(outnamedir)
              shutil.copy(
                os.path.sep.join((root, f)),
                outname
              )
              foundFiles.append('/'.join((root.replace(repoDir, ''), f))[1:])
    params = {'files': foundFiles}
    indexContents = self.phong.renderTemplate("Documents/Index", params)
    indexFile = open(os.path.sep.join((outputDir, 'index.html')), 'w')
    indexFile.write(indexContents)
    indexFile.close()
    self._log.info("Output available in %s", outputDir)
    if args.bucket and not args.dry_run:
      subprocess.check_call([
        's3cmd',
        '-c',
        args.s3cfg,
        'sync',
        outputDir+os.path.sep,
        's3://'+args.bucket])

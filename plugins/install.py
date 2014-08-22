# Copyright (C) 2012 Torrie Fischer <tdfischer@hackerbots.net>
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

from phong import Plugin, Command
import pypandoc
import os

class InstallPlugin(Plugin):
  def availableCommands(self):
    return [WikiUserPageCommand,]

class WikiUserPageCommand(Command):
  def name(self):
    return "install-wiki"

  def helpText(self):
    return "Output some information to User:Phong or whatever is configured"

  def execute(self, args):
    wiki = self.phong.wiki.getPage(self.phong.config.get('phong', 'mediawiki-page'))
    output = pypandoc.convert("README.md", "mediawiki")
    params = {
      'readme': output
    }
    aboutPage = self.phong.renderTemplate('About', params)
    wiki.edit(summary="Updating from README.md", bot=True, text=aboutPage)
    self._log.info("Updated [[%s]] from README.md", self.phong.config.get('phong', 'mediawiki-page'))

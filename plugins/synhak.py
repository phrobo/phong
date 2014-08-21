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
import random

class SynhakPlugin(phong.Plugin):
  def __init__(self, *args, **kwargs):
    super(SynhakPlugin, self).__init__(*args, **kwargs)
    self._greetings = None

  def availableCommands(self):
    return []

  def buildContext(self, phong):
    try:
      greeting = self.randomGreeting(phong)
    except:
      return {}
    return {'greeting': greeting}

  def randomGreeting(self, phong):
    if self._greetings is None:
      greetingPage = phong.getTemplate("Synhak/Greetings", buildContext=False).toRaw()
      self._greetings = []
      for line in greetingPage.split("\n"):
        if line.startswith("*"):
          self._greetings.append(line[1:].strip())
    return random.choice(self._greetings)

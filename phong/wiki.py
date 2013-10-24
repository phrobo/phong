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

import wikitools
import datetime
from Cheetah.Template import Template

class Wiki(object):
  def __init__(self, uri, apiURI, username=None, password=None):
    self._uri = uri
    self._site = wikitools.wiki.Wiki(apiURI)
    if username or password:
      self._site.login(username, password)

  def getPage(self, pageName, *args, **kwargs):
    return wikitools.page.Page(self._site, pageName, *args, **kwargs)

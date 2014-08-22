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

from Cheetah.Template import Template
from wikitools import page
import logging
import os
import datetime

class PhongTemplateAPI(object):
  """A sandboxing wrapper around Phong that doesn't expose everything to templates, but most things"""

  def __init__(self, phong):
    self.__phong = phong

  @property
  def now(self):
    return datetime.datetime.utcnow()

  @property
  def argv(self):
    return self.__phong.argv

class TemplateEngine(object):
  def __init__(self, phong):
    self._phong = phong

  def hasTemplate(self, pageName, prefix):
    raise NotImplemented

  def getTemplate(self, pageName, prefix, defaultCxt):
    raise NotImplemented

class PhongTemplate(object):
  def __init__(self, pageName, defaultContext={}):
    self._name = pageName
    self._defaultCxt = defaultContext

  def toRaw(self):
    raise NotImplemented()

  def render(self, context={}):
    cxt = {}
    cxt.update(self._defaultCxt)
    cxt.update(context)
    contents = self.toRaw()
    template = Template(contents, cxt)
    return unicode(template)

  def __unicode__(self):
    return self.render()

  def __str__(self):
    return self.__unicode__()

  def __unicode__(self):
    return self.render()

class FileEngine(TemplateEngine):
  def __init__(self, phong):
    super(FileEngine, self).__init__(phong)

  def hasTemplate(self, pageName, prefix):
    return os.path.exists(self.templatePath(pageName, prefix))

  def getTemplate(self, pageName, prefix, defaultCxt):
    return FileTemplate(self.templatePath(pageName, prefix), defaultCxt)

  def templatePath(self, pageName, prefix):
    if prefix is None:
      prefix = ''
    return os.path.sep.join(('templates', prefix+pageName))

class FileTemplate(PhongTemplate):
  def __init__(self, pageName, defaultCxt):
    super(FileTemplate, self).__init__(pageName, defaultCxt)
    self._file = pageName

  def toRaw(self):
    fh = open(self._file, 'r')
    return fh.read()

class WikiEngine(TemplateEngine):
  def __init__(self, phong):
    super(WikiEngine, self).__init__(phong)

  def hasTemplate(self, pageName, prefix):
    return True
  
  def getTemplate(self, pageName, prefix, defaultCxt):
    if prefix is None:
      prefix = self._phong._config.get('phong', 'mediawiki-template-prefix')
    return MediawikiTemplatePage(self._phong.wiki, prefix+pageName, defaultCxt)

class MediawikiTemplatePage(PhongTemplate):
  def __init__(self, wiki, pageName, defaultCxt):
    super(MediawikiTemplatePage, self).__init__(pageName, defaultCxt)
    self._page = page.Page(wiki._site, pageName)

  @staticmethod
  def extractTemplateContents(text):
    contents = ""
    inTemplate = False
    for line in text.split("\n"):
      if "<phongTemplate>" in line:
        inTemplate = True
        continue
      if "</phongTemplate>" in line:
        inTemplate = False
      if inTemplate:
        contents += line+"\n"
    if len(contents) == 0 and len(text) > 0:
      return text
    return contents

  def toRaw(self):
    return self.extractTemplateContents(self._page.getWikiText())


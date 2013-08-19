from Cheetah.Template import Template
from wikitools import page
import logging

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

class MediawikiTemplatePage(PhongTemplate):
  def __init__(self, wiki, pageName, defaultCxt):
    super(MediawikiTemplatePage, self).__init__(pageName, defaultCxt)
    self._page = page.Page(wiki._site, pageName)
    print self._page

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


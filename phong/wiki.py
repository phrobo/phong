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

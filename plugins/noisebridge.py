# -*- coding: utf-8 -*-
# Copyright (C) 2014 Torrie Fischer <tdfischer@hackerbots.net>
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
import mwparserfromhell as mw
import dateutil.parser
import pytz
import datetime
import hashlib
import calendar
from icalendar import Calendar, Event
import wikitools.page

class NoisebridgePlugin(Plugin):
  def availableCommands(self):
    return [NBEvents, NBManual]

class NBManual(Command):
  def name(self):
    return "nb-wiki-manual"

  def helpText(self):
    return "Updates the Manual page on the wiki, and tags pages on the manual"

  def execute(self, args):
    wiki = self.phong.wiki.getPage("Manual").getWikiText()
    structure = mw.parse(wiki)
    manualSections = {}
    for c in structure.get_sections(flat=True):
      titles = c.filter_headings()
      if len(titles):
        sectionPages = []
        for line in c.ifilter_wikilinks():
          sectionPages.append(unicode(line.title))

        manualSections[titles[0].title.strip()] = sectionPages

    sectionWiki = self.phong.wiki.getPage("Template:ManualSections")
    sectionText = ' - '.join(map(lambda x:"[[Manual#%s|%s]]"%(x,x), manualSections.iterkeys()))
    try:
      if sectionWiki.getWikiText() != sectionText:
        sectionWiki.edit(text=sectionText, bot=True)
    except wikitools.page.NoPage:
        sectionWiki.edit(text=sectionText, bot=True)

    for sectionName, pages in manualSections.iteritems():
      for page in pages:
        print "%s: %s"%(sectionName, page)
        try:
          pageWiki = self.phong.wiki.getPage(unicode(line.title)).getWikiText()
        except wikitools.page.NoPage:
          print "\t✗ Not even a page!!!!"
          continue
        manPage = mw.parse(pageWiki)
        inManual = False
        for tpl in manPage.ifilter_templates():
          if tpl.name == "ManualPage":
            inManual = True
            break
        if inManual:
          print "\t✓ In manual"
        else:
          print "\t✗ Not in manual!"

class NBEvents(Command):
  def name(self):
    return "nb-wiki-events"

  def helpText(self):
    return "Produces an ical schedule of events at Noisebridge"

  def findCalendar(self, wiki):
    return wiki.get_sections(matches="Event Calendar", levels=xrange(0, 100))[0]

  def getEvents(self):
    wiki = self.phong.wiki.getPage("Category:Events").getWikiText()
    structure = mw.parse(wiki)
    calendar = self.findCalendar(structure)
    events = []
    for event in calendar.filter_templates(matches=lambda x:unicode(x.name).strip() == "event"):
      calEvent = Event()
      events.append(calEvent)
      title = None
      startTime = None
      for param in event.params:
        param = param.split('=')
        if len(param) == 2:
          name, value = map(unicode.strip, param)
          if name == "time":
            startTime = dateutil.parser.parse(value).replace(tzinfo=pytz.timezone("America/Los_Angeles"))
            calEvent.add('dtstart', startTime)
          if name == "title":
            title = value
            calEvent.add('summary', title)
          if name == "description":
            calEvent.add('description', value)
        else:
          self._log.warn("Can't figure out how to decode %s", param)
      calEvent.add('uid', self.generateUID(title, startTime))
    return events

  def generateUID(self, title, timestamp):
    stamp = calendar.timegm(timestamp.timetuple())
    hash = hashlib.md5()
    hash.update(title)
    return "%s-%s@noisebridge.net"%(stamp, hash.hexdigest())

  def execute(self, args):
    events = self.getEvents()
    calendar = Calendar()
    for event in events:
      calendar.add_component(event)
    calendar.add('X-WR-CALNAME', "Noisebridge Event Calendar")
    calendar.add('X-WR-TIMEZONE', pytz.timezone("America/Los_Angeles"))
    calendar.add('X-WR-CALDESC', "Events and happenings from the Noisebridge Hacker Space")
    calendar.add('version', '2.0')
    calendar.add('prodid', '-//Phong Robotics//Phong Phongy Phoo//EN')
    calendar.add('X-PUBLISHED-TTL', 'PT1H')
    print calendar.to_ical()

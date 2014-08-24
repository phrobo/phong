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

class NoisebridgePlugin(Plugin):
  def availableCommands(self):
    return [NBEvents]

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
        if len(param):
          name, value = map(unicode.strip, param)
          if name == "time":
            startTime = dateutil.parser.parse(value).replace(tzinfo=pytz.timezone("America/Los_Angeles"))
            calEvent.add('dtstart', startTime)
          if name == "title":
            title = value
            calEvent.add('summary', title)
          if name == "description":
            calEvent.add('description', value)
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

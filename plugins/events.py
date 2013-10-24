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
import dateutil.parser
from dateutil import tz

class SpiffPlugin(phong.Plugin):
  def availableCommands(self):
    return [NewEventMails,EventWiki]

class NewEventCommand(phong.Command):
  def getEvents(self, period, spiff):
    """Returns a tuple of lists of spiff.Event objects ihe form of (upcoming, today)"""
    upcoming = []
    today = []

    dateFormat = "%A, %d. %B %Y %I:%M%p"

    for e in spiff.events():
      now = datetime.datetime.utcnow().replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal())
      start = dateutil.parser.parse(e['start']).astimezone(tz.tzlocal())
      end = dateutil.parser.parse(e['end']).astimezone(tz.tzlocal())
      if now < end and now+datetime.timedelta(days=1) > start:
        today.append(e)
      elif period > 0 and now < end and now+datetime.timedelta(days=period) > start:
        upcoming.append(e)
      e['start'] = start.strftime(dateFormat)
      e['end'] = end.strftime(dateFormat)

    return (upcoming, today)

  def execute(self, args):
    events = self.getEvents(args.period, self.phong.spiff)
    self.handleEvents(events[0], events[1], args)

  def handleEvents(self, upcoming, today, args):
    self.handleUpcomingEvents(upcoming, args)
    self.handleTodayEvents(today, args)
  
  def handleUpcomingEvents(self, events, args):
    pass

  def handleTodayEvents(self, events, args):
    pass

  def buildArgs(self, args):
    super(NewEventCommand, self).buildArgs(args)
    args.add_argument('-p', '--period', help="Days to look ahead", default=7)

class NewEventMails(NewEventCommand, phong.MailCommandMixin):
  def name(self):
    return "new-event-mails"

  def helpText(self):
    return "Generate announcement mails about new Spiff events"

  def buildArgs(self, args):
    super(NewEventMails, self).buildArgs(args)
    self.buildMailArgs(args)

  def handleEvents(self, upcoming, today, args):
    filteredUpcoming = []
    for evt in upcoming:
      if bool(self.state['events'][str(evt['id'])]['upcomingMailSent']) == False:
        filteredUpcoming.append(evt)

    params = {}
    params['upcoming'] = filteredUpcoming
    params['today'] = today
    params['period'] = args.period
    print today, filteredUpcoming
    if len(filteredUpcoming)+len(today) > 0:
      template = self.phong.renderTemplate("Events/UpcomingEventMail", params)
      subject = "Upcoming Events for %s"%(datetime.date.today().strftime("%A %d %B %Y"))
      self.sendMail(template, subject, args)
    if not args.dry_run:
      for evt in filteredUpcoming:
        self.state['events'][str(evt['id'])]['upcomingMailSent'] = True

class EventWiki(NewEventCommand):
  def name(self):
    return "update-events-wikipage"

  def helpText(self):
    return "Update the EventList wiki page with upcoming events"

  def handleEvents(self, upcoming, today, args):
    params = {}
    params['upcoming'] = upcoming
    params['period'] = args.period
    template = self.phong.renderTemplate("Events/EventPage", params)
    eventPage = self.phong.wiki.getPage("EventList")
    try:
      oldContents = eventPage.getWikiText()
    except:
      oldContents = None
    if oldContents != template:
      eventPage.edit(summary="Update events", bot=True, text=template)

import phong
import datetime
import dateutil.parser
from dateutil import tz

class SpiffPlugin(phong.Plugin):
  def availableCommands(self):
    return [NewEventMails,]

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

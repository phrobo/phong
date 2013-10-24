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

from phong import Plugin, Command, MailCommandMixin
import datetime
from wikitools import page

class MeetingPlugin(Plugin):
  def availableCommands(self):
    return [MeetingCommand,]

class MeetingCommand(Command, MailCommandMixin):
  def name(self):
    return "meetings"

  def helpText(self):
    return "Handle meeting minutes"

  def nextMeetingDate(self):
    stamp = map(int, self.phong.wiki.getPage("Next Meeting", followRedir=False).getWikiText().split("/")[1].replace("]", "").split("-"))
    nextDate = datetime.date(stamp[0], stamp[1], stamp[2])
    now = datetime.date.today()
    if now > nextDate:
      nextDate = nextDate+datetime.timedelta(days=7)
    return nextDate

  def lastMeetingDate(self):
    return self.nextMeetingDate()+datetime.timedelta(days=-7)

  def alreadySentMinutes(self):
    return bool(self.state['meetings'][str(self.lastMeetingDate())]['minutesSent'])

  def getMeeting(self, date):
    return Meeting(self, date)

  def minutesReadyToBeSent(self):
    return True
    lastMeeting = self.getMeeting(self.lastMeetingDate())
    return "<phongMinutesNotReady/>" not in lastMeeting.getWikiText()

  def makeNextMeeting(self, args):
    lastMeeting = self.lastMeetingDate()
    nextMeeting = self.nextMeetingDate()
    nextPage = self.phong.wiki.getPage("Next Meeting", followRedir=False)
    lastPage = self.phong.wiki.getPage("Last Meeting", followRedir=False)

    nextMeetingPage = self.getMeeting(nextMeeting)
    if nextMeetingPage.alreadyExists():
      self._log.info("Next meeting page already exists!")
    else:
      params = nextMeetingPage.templateParams()
      template = self.phong.getTemplate("Meetings/Template", params,
          prefix="")
      self._log.info("Creating next meeting at %s", params['meetingLink'])
      if not args.dry_run:
        nextMeetingPage.wikiPage.edit(summary="Created new meeting page",
            bot=True, text=unicode(template))
    self._log.info("Updating [[Last Meeting]]")
    if not args.dry_run:
      lastPage.edit(summary="Update previous meeting link", bot=True,
          text="#Redirect [[Meetings/%s]]"%(Meeting.formatMeetingDate(lastMeeting)))
    self._log.info("Updating [[Next Meeting]]")
    if not args.dry_run:
      nextPage.edit(summary="Update next meeting link", bot=True, text="#Redirect [[Meetings/%s]]"%(Meeting.formatMeetingDate(nextMeeting)))

  def mailLastMinutes(self, args):
    if self.state['meetings'][str(self.lastMeetingDate())]['minutesSent'] is  True:
      self._log.info("Already sent latest minutes!")
      return
    lastMeeting = self.getMeeting(self.lastMeetingDate())
    params = lastMeeting.templateParams()
    params['minutes'] = lastMeeting.wikiPage.getWikiText()
    mailTemplate = self.phong.renderTemplate("Meetings/FinishedMail", params)
    subject = "Meeting minutes from %s"%(self.lastMeetingDate())
    self.sendMail(mailTemplate, subject, args)
    if not args.dry_run:
      self.state['meetings'][str(self.lastMeetingDate())]['minutesSent'] = True

  def execute(self, args):
    if args.minutes:
      self._log.info("Checking if meetings were already sent")
      if self.alreadySentMinutes():
        self._log.info("Minutes were already sent")
      elif self.minutesReadyToBeSent():
        self._log.info("Sending latest minutes")
        self.mailLastMinutes(args)
      else:
        self._log.info("Minutes are not yet ready to be sent.")

    if args.wiki:
      self.makeNextMeeting(args)

    if args.remind:
      if self.isThereAMeetingToday():
        if self.alreadyRemindedAboutMeeting():
          self._log.info("Already sent a mail for today.")
        else:
          self.remindAboutNextMeeting(args)
      else:
        self._log.info("No meeting today, not sending reminder mail.")

  def remindAboutNextMeeting(self, args):
    nextMeeting = self.getMeeting(self.nextMeetingDate())
    params = nextMeeting.templateParams()
    mailTemplate = self.phong.renderTemplate("Meetings/ReminderMail", params)
    subject = "REMINDER: Meeting tonight!"
    self._log.info("Sending reminder mail.")
    self.sendMail(mailTemplate, subject, args)
    if not args.dry_run:
      self.state['meetings'][str(self.nextMeetingDate())]['reminderSent'] = True

  def alreadyRemindedAboutMeeting(self):
    return bool(self.state['meetings'][str(self.nextMeetingDate())]['reminderSent'])

  def isThereAMeetingToday(self):
    now = datetime.date.today()
    if now == self.nextMeetingDate():
      return True

  def buildArgs(self, args):
    self.buildMailArgs(args)
    args.add_argument('-r', '--remind', help='Send out the reminder mail, if one is needed.', default=False, action='store_true')
    args.add_argument('-w', '--wiki', help='Update the wiki', default=False,
        action='store_true')
    args.add_argument('-m', '--minutes', help='Send mail about posted minutes',
        default=False, action='store_true')

class Meeting(object):

  @staticmethod
  def formatMeetingDate(date):
    assert isinstance(date, datetime.date)
    return "%d-%d-%d"%(date.year, date.month, date.day)

  @property
  def wikiPage(self):
    return self._wikiPage

  def __init__(self, command, date, *args, **kwargs):
    self._date = date
    self._pageName = "Meetings/%s"%(Meeting.formatMeetingDate(date))
    self._command = command
    self._phong = command.phong
    self._wikiPage = self._phong.wiki.getPage(self._pageName)

  def templateParams(self):
    return {
      'date': self._date,
      'meetingLink': "%s%s"%(self._phong.config.get('phong', 'mediawiki-url'), self._pageName),
      'next': "%s"%(self.nextMeeting()._pageName),
      'previous': "%s"%(self.previousMeeting()._pageName)
    }

  def nextMeeting(self):
    if self.alreadyExists() and 'next' in self.meta().params:
      (year, month, day) = map(int,
          self.meta().params['next'].split('/')[1].split('-'))
      stamp = datetime.date(day=day, month=month, year=year)
      return Meeting(self._command, stamp)
    return Meeting(self._command, self._date + datetime.timedelta(days=7))

  def previousMeeting(self):
    if self.alreadyExists() and 'previous' in self.meta().params:
      (year, month, day) = map(int,
          self.meta().params['previous'].split('/')[1].split('-'))
      stamp = datetime.date(day=day, month=month, year=year)
      return Meeting(self._command, stamp)
    return Meeting(self._command, self._date + datetime.timedelta(days=-7))

  def meta(self):
    templates = self.wikiPage.getWikiText().split('{{')
    for template in templates:
      if template.startswith('Infobox_meeting'):
        (infobox,foo) = template.split('}}', 1)
        return MeetingMeta(self, infobox)

  def setMeta(self, meta):
    if self.meta() == meta:
      return
    text = ''
    templates = self.getWikiText().split('{{')
    for template in templates:
      if template.startswith('Infobox_meeting'):
        (infobox, foo) = template.split('}}', 1)
        text += repr(meta) + foo
      else:
        text += template
    self.wikiPage.edit(summary="Update meeting links", bot=True, text=text)

  def adjustSequenceLinks(self):
    previous = self.previousMeeting()
    next = self.nextMeeting()
    meta = self.meta()
    meta.params['previous'] = previous._pageName
    meta.params['next'] = next._pageName
    self.setMeta(meta)

  def alreadyExists(self):
    try:
      self.wikiPage.getWikiText()
      return True
    except:
      return False

class MeetingMeta(object):
  def __init__(self, meeting, infoboxText):
    self._meeting = meeting
    self._raw = infoboxText
    self.params = {}
    args = self._raw.split('|')
    curArg = []
    realArgs = []
    for arg in args[1:]:
      if "=" in arg and len(curArg) > 0:
        realArgs.append('|'.join(curArg).strip())
        curArg = []
      curArg.append(arg)
    if len(curArg) > 0:
      realArgs.append('|'.join(curArg))
    for arg in realArgs:
      try:
        (param, value) = map(lambda x:x.strip(), arg.split('=', 1))
      except ValueError:
        print "Couldn't pull metadata from", arg
        raise
      self.params[param] = value

  def __repr__(self):
    ret = "{{Infobox_meeting\n"
    params = []
    if len(self.params) > 0:
      ret += "|"
    for k,v in self.params.iteritems():
      params.append("%s = %s"%(k, v))
    ret += '\n|'.join(params)
    ret += "\n}}"
    return ret

  def __eq__(self, other):
    if len(self.params) != len(other.params):
      return False
    for k,v in self.params.iteritems():
      if k in other.params:
        if v != other.params[k]:
          return False
      else:
        return False
    return True

# Phong, your friendly hackerspace robot

Phong is a robot!

He does things that help hackerspaces move like a well oiled machine:

* Maintaining meeting minutes
* Handling proposals
* Reminding people about events

# A preface by the author

I find hackerspace theory to be incredibly interesting. No two spaces are
exactly alike, yet they share a common theme of making, doing, and hacking. As
such, I try to write Phong to encompass almost every space's functionality out
there. Phong was originally written and is still used today by SYNHAK, the Akron
Hackerspace. SYNHAK's founding mission is to "provide an environment for
people to educate, create, and share amongst themselves and others within
the domains of technology, art and science." Our governmental structure is
modeled after a combination of Maker's Alliance from Cleveland, OH, Noisebridge
from San Francisco, CA, and HeatSync Labs of Phoenix, NM, which has led us to
have strong feelings of transparency among members, inclusiveness of the
wider community outside of the space, and a love of the do-ocracy. We also have a hard time filling all the officer positions all of the time, so we needed
some help.

Phong is intended to help facilitate the following at your hackerspace:

* Increased awareness and transparency about news and events at the space to
  members
* Empower members to take part in the do-ocracy
* Community building

It is my belief that these three things are what make a hackerspace Excellent.

# Requirements

Phong depends on two external software packages:

* Mediawiki, for meeting minutes, various configuration parameters, templates,
  and things
* Spiff, for looking up membership details, events, and other things.

These requirements will eventually be eliminated as the plugin system further
develops.

Python dependencies for phong are specified in pip-requirements:

    pip install -r pip-requirements

## Mediawiki Setup

Phong gets all of his templates from three locations:

* Your Wiki, under the namespace User:Phong/Templates/
* The local-templates directory, as configured in your phongrc
* The templates directory

# Configuration

Most of phong is meant to be ran periodically via cron scripts.

There are two ways to do it:

* Run ``phong cron'' once per hour
* Run ``phong <command>'' at whatever frequency

For details about the cron command, see the relevant section below.

Phong uses a simple ini-style configuration file. Internally, Phong uses
python's ConfigParser module. Please see the relevant documentation for extra
features not documented here.

There are a handful of important core configuration options, along with a
special "defaults" section to supply options across all commands.

## Example Configuration

Phong includes a default configuration with empty variables. Here is a more full
example, gleaned from SYNHAK:

    [phong]
    mediawiki-url = https://synhak.org/
    mediawiki-api-url = https://synhak.org/w/api.php
    mediawiki-username = Phong
    mediawiki-password = yeah right.
    spiff-api = https://synhak.org/auth/

    [defaults]
    mail-from = Phong <phong@synhak.org>
    mail-to = discuss@synhak.org

## Core Options

The phong section contains settings that are essential to Phong's operation.

* mediawiki-url - Used to generate URLs to wiki pages
* mediawiki-api-url - A URL to access your MediaWiki's api.php
* mediawiki-username - MediaWiki username for your Phong
* mediawiki-password - MediaWiki password for your Phong
* spiff-api - A URL that points to your Spiff installation

## Command Options

To configure certain options for a command, you create a section with the
command name and stick your options in there. For example, to configure the
email address that the meetings command sends minutes to:

    [meetings]
    mail-to = discuss@synhak.org

## Common Options

If a command cannot find an option in its section, it will try to look at the
"defaults" section. Failing that, it'll throw an exception unless it has a
builtin default, which is documented below. For example, to change the from
address that Phong uses for all commands, but to have a different one for
meeting minutes:

    [defaults]
    mail-from = Phong <phong@synhak.org>
    [meetings]
    mail-from = MeetBot <meetbot@synhak.org>

This is useful for keeping backwards compatability, if you are switching to
Phong from another system or collection of systems.

Some commands use the same option names for the same tasks:

* mail-from - Used as the From address for any emails sent
* mail-to - Used as the To address for any emails sent

# Templates

Phong uses Cheetah to process templates for various output situations, such as:

* Producing an email of meeting minutes
* Replying to email commands
* Updating a wiki page

These templates are stored on your MediaWiki installation, under a configurable
prefix that defaults to "User:Phong/Templates/". For example, a template that
Phong calls "Events/NewEventMail" would be located at
"User:Phong/Templates/Events/NewEventMail". Mind that final slash, as it is a
simple string concatenation.

In addition, it is possible to add some documentation to a template that does
not get parsed by phong. This is done by wrapping the template with
<phongTemplate> and </phongTemplate>. If those tags are not present, the entire
page is considered to be the template.

# Commands

## meetings

Every hackerspace should have meetings. They are an essential component of
keeping the space together.

### Options

* -r, --remind - If there is a meeting today, send a reminder mail if it hasn't
  been sent already.
* -w, --wiki - Do wiki administrivia
* -m, --minutes - If there was a meeting since the last run, mail out a copy of
  the minutes

### Wiki setup

Phong uses a very specific wiki setup. The good news, is that it is trivial to
configure. There are three special pages, two of which Phong will kindly
maintain for you:

* [[Meetings/Template]]
* [[Next Meeting]]
* [[Last meeting]]

The [[Next Meeting]] page should be exactly:

    #Redirect [[Meetings/YYYY-MM-DD]]

While [[Last Meeting]] should be exactly:

    #Redirect [[Meetings/YYYY-MM-DD]]

Replace YYYY, MM, DD with the numeric values of the year, month, and day of the
respective meetings. This should only need to be done once. Unfortunately, there
is no bootstrapping for this builtin to Phong. The rationale being that you are
unlikely to have a full working setup of Phong and MediaWiki before you have at
least a couple of meetings to discuss starting your hackerspace. Sorry.

Meetings happen once a week on the same day. That is exactly 7 days apart.
None of that every other wednesday/first saturday of the month/days that have
prime numbers rubbish. Please see
http://hackerspaces.org/wiki/The_Plenum_Pattern for details why this will
never change.

You will have to create [[Meetings/Template]] on your own. This page forms the
basis for your meeting minutes, and it is copied to create the next week's
meeting page. While the template contents are entirely up to you, you should
have at least something similar to the following:

    <phongTemplate>
    {{Infobox_meeting
    |time=7PM
    |date=$date
    |venue=21 West North
    |next=$next
    |previous=$previous
    }}
    </phongTemplate>

Your wiki should have a template called Infobox\_meeting. Its content is up to
you, but check out SYNHAK's for an example:

    https://synhak.org/wiki/Template:Infobox_meeting

*Please note:* The template for this page is *not* User:Phong/Templates/ (or
whatever you have configured). The rationale for this is that the meeting agenda
should be a core component of your hackerspace's governance. If your space is
ran by the membership and not a president or benevolent dictator, the membership
should feel welcome to change the agenda as they see fit.

This meeting template should be a special template, as compared to more mundane
ones such as the one for mailing out meeting minutes, or for announcing upcoming
events.

### Template variables
When producing the next week's page and all emails, a number of variables are
available:

* $date - The date the meeting will be occuring on
* $next and $previous - The page names (i.e. Meetings/YYYY-MM-DD) of the next meetings. Your template should include the square brackets.
* $meetingLink - A full URI that points to the wiki page for the next meeting

## new-event-mails

Phong can inform the community about upcoming events that were previously
created in spiff.

### Options

* -p PERIOD, --period PERIOD - An integer number of days to look ahead for
  upcoming events. Defaults to 7. If an event is more than this many days away,
  it won't be mentioned in the mails.

### Wiki templates

This command uses one template: Events/UpcomingEventMail. It has the following
variables available for use:

* $upcoming - Any upcoming events that haven't been in a previous email
* $today - Events that are starting in the next 24 hours. Please note: This does
  not mean "events that start after 12:00 or before 24:00". It means 24 hours
  from when the command is ran.
* $period - How many days in advance Phong looked for upcoming events


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

from yapsy.PluginManager import PluginManager
from yapsy.PluginFileLocator import PluginFileAnalyzerWithInfoFile
from yapsy.IPlugin import IPlugin
import argparse
import ConfigParser
import os
import logging
import phong.state
import phong.wiki
import phong.templates

try:
  import spiff
except:
  spiff = None

from email.mime.text import MIMEText
import smtplib

class Plugin(IPlugin):
  def availableCommands(self):
    return []

  def buildContext(self, phong):
    return {}

class MailCommandMixin(object):
  def buildMailArgs(self, args):
    args.add_argument('-e', '--mail', help='Address to send mail to. May be specified multiple times.', default=[], action='append', type=str, dest='mail_addresses')
    args.add_argument('-f', '--from-address', help='Address to send mail from.', default=None, type=str, dest='mail_from_address')

  def sendMail(self, body, subject, args):
    fromAddr = args.mail_from_address
    if fromAddr is None:
      fromAddr = self.getConfig('mail-from')
    msg = MIMEText(body.encode('UTF-8'), 'plain', 'UTF-8')
    msg['Subject'] = subject
    msg['From'] = fromAddr
    addresses = args.mail_addresses
    if len(addresses) == 0:
      addresses = map(str.strip, self.getConfig('mail-to').split(','))
    msg['To'] = ','.join(addresses)
    self._log.debug("Sending mail to %s: %s %s", addresses, msg.items(), body.encode('UTF-8'))
    if not args.dry_run:
      host = self.getConfig('smtp-host')
      starttls = self.getConfigBool('smtp-starttls')
      username = self.getConfig('smtp-username')
      password = self.getConfig('smtp-password')
      s = smtplib.SMTP(host)
      if starttls:
        s.starttls()
      if username and password:
        s.login(username, password)
      s.sendmail(msg['From'], addresses, msg.as_string())
      s.quit()
    else:
      self._log.debug('Not sending: Dry run')

class Command(object):
  def __init__(self, phong, plugin):
    super(Command, self).__init__()
    self.__phong = phong
    self.__plugin = plugin
    self.__log = logging.getLogger("%s.%s"%(self.__plugin.name,
      self.__class__.__name__))
    self.__state = self.__phong.getState("%s.%s"%(self.__plugin.name,
      self.__class__.__name__))

  @property
  def _log(self):
    return self.__log

  @property
  def phong(self):
    return self.__phong

  def getConfig(self, name):
    if self.phong.config.has_option(self.plugin.name, name):
      return self.phong.config.get(self.plugin.name, name)
    return self.phong.config.get('defaults', name)

  def getConfigBool(self, name):
    if self.phong.config.has_option(self.plugin.name, name):
      return self.phong.config.getboolean(self.plugin.name, name)
    return self.phong.config.getboolean('defaults', name)

  @property
  def plugin(self):
    return self.__plugin

  @property
  def state(self):
    return self.__state

  def helpText(self):
    raise NotImplemented()

  def execute(self, args):
    raise NotImplemented()

  def buildArgs(self, args):
    pass

class Phong(object):
  def __init__(self):
    self._log = logging.getLogger("%s.%s"%(self.__module__,
      self.__class__.__name__))

    analyzer = PluginFileAnalyzerWithInfoFile('phong', 'phong-plugin')
    self._plugins = PluginManager()
    self._plugins.getPluginLocator().setAnalyzers([analyzer])
    self._plugins.setPluginPlaces([
      './plugins/',
      '/usr/lib/phong/plugins',
    ])
    self._config = ConfigParser.ConfigParser()
    self.loadConfig(os.path.sep.join((os.path.dirname(__file__),
      'defaults.cfg')))
    self._wiki = None
    self._commands = []
    self._spiff = None

  @property
  def pluginManager(self):
    return self._plugins()

  @property
  def config(self):
    return self._config

  @property
  def spiff(self):
    if spiff is not None and self._spiff is None:
      self._spiff = spiff.API(self.config.get('phong', 'spiff-api'))
    return self._spiff

  @property
  def wiki(self):
    if self._wiki is None:
      url = self._config.get('phong', 'mediawiki-url')
      api = self._config.get('phong', 'mediawiki-api-url')
      username = self._config.get('phong', 'mediawiki-username')
      password = self._config.get('phong', 'mediawiki-password')
      self._wiki = phong.wiki.Wiki(url, api, username, password)
    return self._wiki

  def buildContext(self):
    context = {}
    for plugin in self._plugins.getAllPlugins():
      cxt = plugin.plugin_object.buildContext(self)
      if isinstance(cxt, dict):
        context.update(cxt)
    return context

  def getTemplate(self, name, defaultContext={}, buildContext=True, prefix=None):
    if buildContext:
      cxt = self.buildContext()
      cxt.update(defaultContext)
    else:
      cxt = defaultContext
    engines = [
      phong.templates.FileEngine(self),
      phong.templates.WikiEngine(self),
    ]
    for e in engines:
      if e.hasTemplate(name, prefix):
        return e.getTemplate(name, prefix, cxt)

  def renderTemplate(self, name, context={}):
    cxt = self.buildContext()
    cxt.update(context)
    return self.getTemplate(name).render(context)

  def loadPlugins(self):
    self._plugins.collectPlugins()

    for plugin in self._plugins.getAllPlugins():
      self._plugins.activatePluginByName(plugin.name)
      for cmd in plugin.plugin_object.availableCommands():
        self._commands.append(cmd(self, plugin))

  def loadConfig(self, path):
    self._log.debug("Loading configuration from %s", path)
    self._config.read(os.path.expanduser(path))

  def getState(self, name):
    dir = os.path.expanduser(self._config.get('phong', 'state-dir'))
    return phong.state.State(os.path.sep.join((dir, "%s.state.json"%(name))))

  def main(self, argv):
    parser = argparse.ArgumentParser(prog='phong', add_help=False)
    parser.add_argument('-c', '--config', help='Configuration file to use',
        default="/etc/phong.cfg")
    parser.add_argument('-d', '--dry-run', help='Dont actually do anything',
        default=False, action='store_true')
    parser.add_argument('-D', '--debug', help='Print debug messages',
        default=False, action='store_true')
    args = parser.parse_known_args(argv)
    parser.add_argument('-h', '--help', help='show this help message and exit', action='help')

    if args[0].debug:
      logging.basicConfig(level=logging.DEBUG)

    self.loadConfig(args[0].config)
    self.loadPlugins()
    subparser = parser.add_subparsers(help='action')
    for command in self._commands:
      pluginArgs = subparser.add_parser(command.name(),
          help=command.helpText())
      pluginArgs.set_defaults(command_obj=command)
      command.buildArgs(pluginArgs)
    args = parser.parse_args(argv)

    return args.command_obj.execute(args)

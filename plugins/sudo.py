import phong
import os
import pwd
import grp

class SudoPlugin(phong.Plugin):
  def availableCommands(self):
    return [SudoCommand,]

class SudoCommand(phong.Command):
  def name(self):
    return "sudo"

  def helpText(self):
    return "Run phong commands in a fashion similar to sudo"

  def buildArgs(self, args):
    subparser = args.add_subparsers(help='command')
    if self.phong._config.has_section('sudo'):
      for alias,cmd in self.phong._config.items('sudo'):
        aliasArgs = subparser.add_parser(alias, help=cmd)
        aliasArgs.set_defaults(sudo_alias=alias)
        aliasArgs.add_argument('extra', nargs='*')

  def execute(self, args):
    alias = args.sudo_alias
    command = self.phong._config.get('sudo', alias).split(' ')
    if self.phong._config.has_option('sudo:'+alias, 'allowed-groups'):
      allowedGroups = map(str.strip, self.phong._config.get('sudo:'+alias,
          'allowed-groups').split(','))
    else:
      allowedGroups = []

    if self.phong._config.has_option('sudo:'+alias, 'allowed-users'):
      allowedUsers = map(str.strip, self.phong._config.get('sudo:'+alias,
          'allowed-users').split(','))
    else:
      allowedUsers = []

    permitted = False

    if '*' in allowedUsers or '*' in allowedGroups:
      permitted = True
    else:
      uid = os.getuid()
      if str(uid) in allowedUsers:
        permitted = True
      elif pwd.getpwuid(uid).pw_name in allowedUsers:
        permitted = True
      else:
        for gid in os.getgroups():
          if str(gid) in allowedGroups:
            permitted = True
            break
          elif grp.getgrgid(gid).gr_name in allowedGroups:
            permitted = True
            break

    if permitted:
      if self.phong._config.has_option('sudo:'+alias, 'run-as-user'):
        runUser = self.phong._config.get('sudo:'+alias, 'run-as-user')
        runUID = pwd.getpwnam(runUser).pw_uid
      else:
        raise RuntimeError, "You must specify a user to run as, even if it is 'root'"
      if self.phong._config.has_option('sudo:'+alias, 'run-as-group'):
        runGroup = self.phong._config.get('sudo:'+alias, 'run-as-group')
        runGID = grp.getgrnam(runGroup).gr_gid
      else:
        runGID = pwd.getpwuid(runUID).pw_gid
      self._log.debug("Setting GID to %s", runGID)
      os.setgid(runGID)
      self._log.debug("Setting UID to %s", runUID)
      os.setuid(runUID)
      subPhong = phong.Phong()
      return subPhong.main(command+args.extra)
    else:
      raise RuntimeError, "Not permitted."
      return False

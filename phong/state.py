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

import json
import os

class StateVar(object):
  def __init__(self, value=None, parent=None):
    self._value = value
    self._parent = parent
    self._data = {}

  def __getitem__(self, key):
    assert isinstance(key, str)
    if key not in self._data:
      self._data[key] = StateVar()
    return self._data[key]

  def __setitem__(self, key, value):
    assert isinstance(key, str)
    self._data[key] = StateVar(value)

  def __delitem__(self, key):
    assert isinstance(key, str)
    del self._data[key]
    self.save()

  def __cmp__(self, other):
    if not isinstance(other, type(self._value)):
      return False
    return self._value.__cmp__(self._value)

  def __unicode__(self):
    return self._value.__unicode__()

  def __str__(self):
    return self._value.__str__()

  def __repr__(self):
    return repr(self.toDict())

  def __nonzero__(self):
    if self._value is None:
      return False
    return self._value.__nonzero__()
  
  def save(self):
    if self._parent is not None:
      self._parent.save()

  def toDict(self):
    keys = {}
    for key in self._data.iterkeys():
      keys[key] = self._data[key].toDict()
    d = {}
    if self._value is not None:
      d['value'] = self._value
    if len(keys) > 0:
      d['keys'] = keys
    return d

  def loadFromDict(self, data):
    if 'value' in data:
      self._value = data['value']
    if 'keys' in data:
      for key in data['keys']:
        self._data[key] = StateVar()
        self._data[key].loadFromDict(data['keys'][key])

class State(StateVar):
  def __init__(self, filename):
    super(State, self).__init__()
    self._filename = filename
    if os.path.exists(self._filename):
      self.load()

  def load(self, filename=None):
    if filename == None:
      filename = self._filename
    data = json.load(open(filename))
    self.loadFromDict(data)

  def save(self, filename=None):
    if filename == None:
      filename = self._filename
    if not os.path.exists(os.path.dirname(filename)):
      os.makedirs(os.path.dirname(filename))
    json.dump(self.toDict(), open(filename, "w"), indent=4)

  def __del__(self):
    self.save()


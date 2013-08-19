import phong
import random

class SynhakPlugin(phong.Plugin):
  def __init__(self, *args, **kwargs):
    super(SynhakPlugin, self).__init__(*args, **kwargs)
    self._greetings = None

  def availableCommands(self):
    return []

  def buildContext(self, phong):
    return {'greeting': self.randomGreeting(phong)}

  def randomGreeting(self, phong):
    if self._greetings is None:
      greetingPage = phong.getTemplate("Synhak/Greetings", buildContext=False).toRaw()
      self._greetings = []
      for line in greetingPage.split("\n"):
        if line.startswith("*"):
          self._greetings.append(line[1:].strip())
    return random.choice(self._greetings)

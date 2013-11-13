import phong
import twitter

class TwitterPlugin(phong.Plugin):
  def availableCommands(self):
    return [TweetCommand,]

class TweetCommand(phong.Command):
  def name(self):
    return "tweet"

  def helpText(self):
    return "Twat a tweet"

  def buildArgs(self, args):
    args.add_argument('status', nargs='*')

  def execute(self, args):
    key = self.phong._config.get('twitter', 'consumer_key')
    secret = self.phong._config.get('twitter', 'consumer_secret')
    access_key = self.phong._config.get('twitter', 'access_key')
    access_secret = self.phong._config.get('twitter', 'access_secret')
    api = twitter.Api(
      consumer_key=key,
      consumer_secret=secret,
      access_token_key=access_key,
      access_token_secret=access_secret
    )
    api.PostUpdate(' '.join(args.status))

class InitParams:
	def __init__(self, *, bot = None, **kwargs):
		self.bot = bot
		if kwargs: self.set_params(**kwargs)

	@classmethod
	def set_params(cls, database_url, add_task):
		from vkbottle.api import get_api
		cls.api = get_api()
		from utils.lvls import LVL
		cls.lvl_class = LVL(database_url, add_task)
		from utils.api import ShikiApi, ThisWaifuDoesNotExist, AMessage, Foaf
		cls.amessage = AMessage()
		cls.twdne = ThisWaifuDoesNotExist()
		cls.shiki = ShikiApi()
		cls.foaf = Foaf()

		from datetime import datetime, tzinfo, timedelta

		class timezone(tzinfo):
			utcoffset = lambda self, dt: timedelta(hours=5)
			dst = lambda self, dt: timedelta()
			tzname = lambda self, dt: '+05:00'

		cls.now = property(lambda self: datetime.now(timezone()))

	@classmethod
	def set_peer_id(cls, peer_id):
		cls.lvl_class(peer_id)
		cls.amessage(peer_id)
		cls.twdne(peer_id)
		cls.shiki(peer_id)


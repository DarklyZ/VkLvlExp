class InitParams:
	def __init__(self, *, bot = None):
		self.bot = bot

	@property
	def now(self):
		now = getattr(self, '_now', False)
		if not now:
			from datetime import datetime, tzinfo, timedelta

			class timezone(tzinfo):
				utcoffset = lambda self, dt: timedelta(hours=5)
				dst = lambda self, dt: timedelta()
				tzname = lambda self, dt: '+05:00'

			now = self._now = lambda: datetime.now(timezone())
		return now()

	@property
	def api(self):
		api = getattr(self, '_api', False)
		if not api:
			from vkbottle.api import get_api
			api = self._api = get_api()
		return api

	@property
	def lvl_class(self):
		lvl_class = getattr(self, '_lvl_class', False)
		if not lvl_class:
			from utils.lvls import get_lvl
			lvl_class = self._lvl_class = get_lvl()
		return lvl_class

	@property
	def amessage(self):
		amessage = getattr(self, '_amessage', False)
		if not amessage:
			from utils.audio_message import get_amessage
			amessage = self._amessage = get_amessage()
		return amessage

	@property
	def twdne(self):
		twdne = getattr(self, '_twdne', False)
		if not twdne:
			from utils.thiswaifudoesnotexist import get_twdne
			twdne = self._twdne= get_twdne()
		return twdne
class InitParams:
	def __init__(self, bot):
		self.bot = bot

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

class InitParams:
	class Params:
		__setattr__ = lambda self, key, value: setattr(self.__class__, key, value)

		def set_peer_id(self, peer_id):
			self.lvl_class(peer_id)
			self.amessage(peer_id)
			self.twdne(peer_id)
			self.shiki(peer_id)

	params = Params()

	def __init__(self, bot, database_url):
		self.params.bot = bot
		from utils.lvls import LVL
		self.params.lvl_class = LVL(database_url)
		from utils.api import ShikiApi, ThisWaifuDoesNotExist, AMessage, Foaf
		self.params.amessage = AMessage()
		self.params.twdne = ThisWaifuDoesNotExist()
		self.params.shiki = ShikiApi()
		self.params.foaf = Foaf()

		from datetime import datetime, tzinfo, timedelta

		class timezone(tzinfo):
			utcoffset = lambda self, dt: timedelta(hours = 5)
			dst = lambda self, dt: timedelta()
			tzname = lambda self, dt: '+05:00'

		self.params.now = property(lambda self: datetime.now(timezone()))

	async def run_db(self):
		await self.params.lvl_class.__aenter__()

	async def run_top(self):
		from asyncio import sleep
		from datetime import timedelta

		temp_new = lambda: self.params.now.replace(hour = 0, minute = 0, second = 0) + timedelta(days = 1)

		temp = temp_new()
		while not await sleep(5 * 60):
			if self.params.lvl_class.now < temp: continue
			await self.params.lvl_class.temp_reset()
			temp = temp_new()

	@staticmethod
	def upload_commands():
		import commands, utils.rules

		commands.HelpCommand()
		commands.LVLCommands()
		commands.NickCommands()
		commands.ExtraCommands()
		commands.ShikimoriCommands()
		commands.ChatActionCommands()
		commands.RegexCommands()

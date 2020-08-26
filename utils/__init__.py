class InitData:
	class Data:
		pass

	def __enter__(self):
		return self.Data

	def __exit__(self, exc_type, exc_val, exc_tb):
		pass

	def __init__(self, token, database_url, debug = False):
		from utils.lvls import LVL
		from vkbottle import Bot
		from utils.api import ShikiApi, ThisWaifuDoesNotExist, AMessage, FoafPHP, YaSpeller

		with self as data:
			data.bot = Bot(token, debug = debug)
			data.lvl_class = LVL(database_url)
			data.amessage = AMessage()
			data.twdne = ThisWaifuDoesNotExist()
			data.shiki = ShikiApi()
			data.speller = YaSpeller()
			data.foaf = FoafPHP()
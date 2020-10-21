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
			data.bot = Bot(token, debug = debug); data.bot.loop_update()
			data.bot.on.chat_message.prefix = [r'\.', '/', '!', ':']

			data.lvl_class, data.amessage = LVL(database_url), AMessage()
			data.twdne, data.shiki = ThisWaifuDoesNotExist(), ShikiApi()
			data.speller, data.foaf = YaSpeller(), FoafPHP()
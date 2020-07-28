class InitData:
	class Data:
		pass

	def __init__(self, token, database_url):
		from utils.lvls import LVL
		from vkbottle import Bot
		from utils.api import ShikiApi, ThisWaifuDoesNotExist, AMessage, Foaf

		self.bot = Bot(token, debug = False)
		self.lvl_class = LVL(database_url)
		self.amessage = AMessage()
		self.twdne = ThisWaifuDoesNotExist()
		self.shiki = ShikiApi()
		self.foaf = Foaf()

	__getattr__ = lambda self, key: getattr(self.Data, key)
	__setattr__ = lambda self, key, value: setattr(self.Data, key, value)

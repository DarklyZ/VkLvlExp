class InitData:
	class Data:
		pass

	def __init__(self, token, database_url, debug = False):
		from utils.lvls import LVL
		from vkbottle import Bot
		from utils.api import ShikiApi, ThisWaifuDoesNotExist, AMessage, Foaf

		self.bot = Bot(token, debug = debug)
		self.lvl_class = LVL(database_url)
		self.amessage = AMessage()
		self.twdne = ThisWaifuDoesNotExist()
		self.shiki = ShikiApi()
		self.foaf = Foaf()

	__getattr__ = lambda self, item: getattr(self.Data, item)
	__setattr__ = lambda self, key, value: setattr(self.Data, key, value)
	__delattr__ = lambda self, item: delattr(self.Data, item)
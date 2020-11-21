class InitData:
	With = None

	class Data:
		pass

	def __enter__(self):
		return self.Data

	def __exit__(self, exc_type, exc_val, exc_tb):
		pass

	def __init__(self, database_url):
		from .lvls import LVL
		from .api import ShikiApi, ThisWaifuDoesNotExist, AMessage, FoafPHP, YaSpeller

		with self as data:
			data.lvl_class, data.amessage = LVL(database_url), AMessage()
			data.twdne, data.shiki = ThisWaifuDoesNotExist(), ShikiApi()
			data.speller, data.foaf = YaSpeller(), FoafPHP()

		InitData.With = self
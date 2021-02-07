from utils import Data
from utils.lvlweb import LVL
from vkbottle import Bot
from webutils import run_app
from os import getenv

class InitData(Data, init = True):
	bot = Bot(getenv('TOKEN'))
	lvlweb = LVL(getenv('DATABASE_URL'))

	def __init__(self):
		self.bot.loop_wrapper.add_task(self.lvlweb.run_connect)
		self.bot.loop_wrapper.add_task(run_app(port = getenv('PORT')))

		self.bot.loop_wrapper.run_forever()

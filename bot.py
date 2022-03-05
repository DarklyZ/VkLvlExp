from vkbottle import BaseMiddleware, Bot
from vkbottle.modules import logger

from utils import Data
from utils.lvl import LVL
from utils.api import (
	ShikiApi, ThisWaifuDoesNotExist,
	AMessage, FoafPHP, YaSpeller
)

from aiohttp.web import (
	Application as App, _run_app as run
)
from webutils.routes import routes
from commands import labelers

from loguru._defaults import LOGURU_ERROR_NO
from os import getenv

logger._core.min_level = LOGURU_ERROR_NO

class InitData(Data, init = True):
	app, bot = App(), Bot(getenv('TOKEN'))
	lvl = LVL(getenv('DATABASE_URL'))
	shiki, amessage = ShikiApi(), AMessage()
	speller, foaf = YaSpeller(), FoafPHP()
	twdne = ThisWaifuDoesNotExist()

	def __init__(self):
		self.app.add_routes(routes)
		for labeler in labelers:
			self.bot.labeler.load(labeler)

		@self.bot.labeler.message_view.register_middleware
		class Register(BaseMiddleware, Data):
			async def pre(self):
				if self.event.peer_id == self.event.from_id or self.event.from_id < 0: return False
				self.set_peer_id(self.event.peer_id)
				await self.lvl.check_add_user(self.event.from_id)
				if not self.event.payload and (exp := await self.lvl.atta(self.event.text, self.event.attachments)):
					await self.lvl.update_lvl(self.event.from_id, exp = exp, boost = True, temp = True, slave = True)

			def set_peer_id(self, peer_id):
				self.lvl(peer_id)
				self.amessage(peer_id)
				self.twdne(peer_id)
				self.shiki(peer_id)

		@self.bot.error_handler.register_error_handler(AssertionError)
		async def assert_handler(e):
			await self.bot.api.messages.send(peer_id = self.lvl.peer_id, message = str(e), random_id = 0)

		self.bot.loop_wrapper.add_task(self.lvl.run_connect(run_top = True))
		self.bot.loop_wrapper.add_task(run(self.app, port = getenv('PORT')))

		self.bot.loop_wrapper.run_forever()
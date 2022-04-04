from vkbottle import BaseMiddleware, Bot
from vkbottle.callback import BotCallback
from vkbottle.modules import logger

from utils import Data
from utils.lvl import LVL
from utils.rules import CommandVBMLRule
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

class InitData(Data, write = True, run = True):
	bot = Bot(getenv('TOKEN'),
		callback = BotCallback(secret_key = getenv('SECRET_KEY')))
	app, lvl = App(), LVL(getenv('DATABASE_URL'))
	shiki, amessage = ShikiApi(), AMessage()
	speller, foaf = YaSpeller(), FoafPHP()
	twdne = ThisWaifuDoesNotExist()

	@bot.labeler.message_view.register_middleware
	class _Register(BaseMiddleware, Data):
		is_conversation = property(lambda self: self.event.peer_id != self.event.from_id or self.event.from_id > 0)

		async def pre(self):
			if not self.is_conversation: return False
			self.set_peer_id(self.event.peer_id)
			await self.lvl.check_add_user(self.event.from_id)
			if not self.event.payload and (exp := await self.lvl.atta(self.event.text, self.event.attachments)):
				await self.lvl.update_lvl(self.event.from_id, exp = exp, boost = True, temp = True, slave = True)

		async def post(self):
			if not self.is_conversation: return False
			self.set_peer_id(None)
			if len([rule for handler in self.handlers for rule in handler.rules if isinstance(rule, CommandVBMLRule)]):
				await self.bot.api.messages.delete(
					delete_for_all = True, peer_id = self.event.peer_id, cmids = self.event.conversation_message_id
				)

		def set_peer_id(self, peer_id):
			self.lvl(peer_id)
			self.amessage(peer_id)
			self.twdne(peer_id)
			self.shiki(peer_id)

	def __init__(self):
		self.app.add_routes(routes)
		for labeler in labelers:
			self.bot.labeler.load(labeler)

		self._register_handlers()

		self.bot.loop_wrapper.add_task(self.lvl.run_connect(run_top = True))
		self.bot.loop_wrapper.add_task(run(self.app, port = getenv('PORT')))

	def __run__(self):
		self.bot.loop_wrapper.run_forever()
		# self.bot.run_forever()

	def _register_handlers(self):
		@self.bot.error_handler.register_error_handler(AssertionError)
		async def assert_handler(e):
			await self.bot.api.messages.send(peer_id = self.lvl.peer_id, message = str(e), random_id = 0)

		@self.bot.error_handler.register_undefined_error_handler
		async def error_handler(e):
			pass
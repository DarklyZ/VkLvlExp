import override_types

from vkbottle import BaseMiddleware, Bot
from vkbottle.modules import logger

from utils import Data
from utils.lvl import LVL
from utils.api import (
	ShikiApi, ThisWaifuDoesNotExist,
	AMessage, FoafPHP, YaSpeller
)

from aiohttp.web import Application, _run_app as run
from webutils.routes import routes

from loguru._defaults import LOGURU_ERROR_NO
from vbml import Patcher
from os import getenv

logger._core.min_level = LOGURU_ERROR_NO
patcher = Patcher()

@patcher.validator(key = 'int')
def int_validator(value):
	return int(value) if value.isdigit() or value[:1] in '+-' and value[1:].isdigit() else None

@patcher.validator(key = 'pos')
def pos_validator(value):
	return int(value) if value.isdigit() or value[:1] == '+' and value[1:].isdigit() else None

@patcher.validator(key = 'max')
def max_validator(value, extra):
	return value if len(value) <= int(extra) else None

@patcher.validator(key = 'inc')
def inc_validator(value, *extra):
	return value.lower() if value.lower() in extra else None

class Register(BaseMiddleware, Data):
	async def pre(self, message):
		if message.peer_id == message.from_id or message.from_id < 0: return False
		self.set_peer_id(message.peer_id)
		await self.lvl.check_add_user(message.from_id)
		if not message.payload and (exp := await self.lvl.atta(message.text, message.attachments)):
			await self.lvl.update_lvl(message.from_id, exp = exp, boost = True, temp = True, slave = True)

	def set_peer_id(self, peer_id):
		self.lvl(peer_id)
		self.amessage(peer_id)
		self.twdne(peer_id)
		self.shiki(peer_id)

class InitData(Data, init = True):
	app = Application()
	bot = Bot(getenv('TOKEN'))
	lvl = LVL(getenv('DATABASE_URL'))
	shiki, amessage = ShikiApi(), AMessage()
	speller, foaf = YaSpeller(), FoafPHP()
	twdne = ThisWaifuDoesNotExist()

	def __init__(self):
		self.app.add_routes(routes)
		self.bot.labeler.message_view.register_middleware(Register())

		import utils.rules
		from commands import labelers

		for custom_labeler in labelers:
			self.bot.labeler.load(custom_labeler)

		self.bot.loop_wrapper.add_task(run(self.app, port = getenv('PORT')))
		self.bot.loop_wrapper.add_task(self.lvl.run_connect)

		# self.bot.run_forever()
		self.bot.loop_wrapper.run_forever()
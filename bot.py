import override_types

from aiohttp.client_exceptions import ServerDisconnectedError, ClientOSError

from vkbottle import BaseMiddleware, Bot, BotPolling
from vkbottle.modules import logger

from utils import Data
from utils.lvls import LVL
from utils.api import ShikiApi, ThisWaifuDoesNotExist, AMessage, FoafPHP, YaSpeller

from loguru._defaults import LOGURU_ERROR_NO
from vbml import Patcher
from os import getenv

from web import run_app

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
		await self.lvl_class.check_add_user(message.from_id)
		if not message.payload and (exp := await self.lvl_class.atta(message.text, message.attachments)):
			await self.lvl_class.update_lvl(message.from_id, exp = exp, boost = True, temp = True)

	def set_peer_id(self, peer_id):
		self.lvl_class(peer_id)
		self.amessage(peer_id)
		self.twdne(peer_id)
		self.shiki(peer_id)

class BotPolling(BotPolling):
	async def listen(self):
		while not self.stop:
			async for event in super().listen():
				if isinstance(event, dict): yield event
				else: break

class InitData(Data, init = True):
	bot = Bot(getenv('TOKEN'), polling = BotPolling())
	lvl_class, amessage = LVL(getenv('DATABASE_URL')), AMessage()
	twdne, shiki = ThisWaifuDoesNotExist(), ShikiApi()
	speller, foaf = YaSpeller(), FoafPHP()

	def __init__(self):
		self.bot.labeler.message_view.register_middleware(Register())

		for error in (ServerDisconnectedError, ClientOSError):
			@self.bot.error_handler.register_error_handler(error)
			async def skip_error(e):
				logger.error(f"{e.__class__.__name__}: restarting...")

		import utils.rules
		from commands import labelers

		for custom_labeler in labelers:
			self.bot.labeler.load(custom_labeler)

		self.bot.loop_wrapper.add_task(self.lvl_class.run_connect)
		self.bot.loop_wrapper.add_task(self.lvl_class.run_top)
		self.bot.loop_wrapper.add_task(run_app(port = getenv('PORT', None)))

		self.bot.run_forever()
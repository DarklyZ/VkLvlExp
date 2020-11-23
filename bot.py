import override_vkbottle_types

from aiohttp.client_exceptions import ServerDisconnectedError
from vkbottle import BaseMiddleware, Bot, LoopWrapper
from vkbottle.modules import logger
from loguru._defaults import LOGURU_ERROR_NO
from utils import InitData
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

class Register(BaseMiddleware, InitData.Data):
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

class RunBot:
	def __init__(self, bot):
		self.bot, self._stop = bot, False
		self.bot.error_handler.register_error_handler(
			ServerDisconnectedError, self.SDE
		)

	async def run_bot(self):
		while not self.stop: await self.bot.run_polling()

	async def SDE(self, e):
		self.bot.polling.stop = True
		return {"updates": []}

	@property
	def stop(self):
		if self.bot.polling.stop and not self._stop:
			self.bot.polling.stop = self._stop
		return self._stop

	@stop.setter
	def stop(self, value):
		self._stop = self.bot.polling.stop = value

with InitData(getenv('DATABASE_URL')) as data:
	data.bot = Bot(getenv('TOKEN'))
	data.bot.labeler.message_view.register_middleware(Register())

	import utils.rules
	from commands import labelers

	for custom_labeler in labelers:
		data.bot.labeler.load(custom_labeler)

	lw = LoopWrapper()
	lw.add_task(RunBot(data.bot).run_bot)
	lw.add_task(data.lvl_class.run_connect)
	lw.add_task(data.lvl_class.run_top)

	lw.run_forever()

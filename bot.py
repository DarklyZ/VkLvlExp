import override_vkbottle_types

from aiohttp.client_exceptions import ServerDisconnectedError, ClientOSError
from vkbottle import BaseMiddleware, Bot
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

class Bot(Bot):
	stop = False

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for e in (ServerDisconnectedError, ClientOSError):
			self.error_handler.register_error_handler(e, self.skip_error)

	async def run_polling(self):
		while not self.stop:
			await super().run_polling()
			self.polling.stop = False

	async def skip_error(self, e):
		logger.error(f"{e.__class__.__name__}: restarting...")
		self.polling.stop = True
		return {'update': []}

with InitData(getenv('DATABASE_URL')) as data:
	data.bot = Bot(getenv('TOKEN'))
	data.bot.labeler.message_view.register_middleware(Register())

	import utils.rules
	from commands import labelers

	for custom_labeler in labelers:
		data.bot.labeler.load(custom_labeler)

	data.bot.loop_wrapper.add_task(data.lvl_class.run_connect)
	data.bot.loop_wrapper.add_task(data.lvl_class.run_top)

	data.bot.run_forever()

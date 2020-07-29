from vbml import Patcher, PatchedValidators
from vkbottle.ext import Middleware
from vkbottle.utils import TaskManager
from utils import InitData
from utils.lvls import atta
from re import I, S
from os import getenv

class Validators(PatchedValidators):
	int = lambda self, value: int(value) if value.isdigit() or value[:1] in '+-' and value[1:].isdigit() else None
	pos = lambda self, value: int(value) if value.isdigit() or value[:1] == '+' and value[1:].isdigit() else None
	max = lambda self, value, extra: value if len(value) <= int(extra) else None
	inc = lambda self, value, *extra: value.lower() if value.lower() in extra else None

Patcher(validators = Validators, flags = I + S)

data = InitData(token = getenv('TOKEN'), database_url = getenv('DATABASE_URL'))

task = TaskManager(data.bot.loop)
task.add_task(data.bot.run(True))

data.bot.on.chat_message.prefix = [r'\.', '/', '!', ':']

task.add_task(data.lvl_class.run_connect)
task.add_task(data.lvl_class.run_top)

import commands, utils.rules

commands.HelpCommand()
commands.LVLCommands()
commands.NickCommands()
commands.ExtraCommands()
commands.ChatActionCommands()
commands.RegexCommands()

@data.bot.middleware.middleware_handler()
class Register(Middleware, InitData.Data):
	async def pre(self, message):
		if message.peer_id == message.from_id or message.from_id < 0: return False
		self.set_peer_id(message.peer_id)
		await self.lvl_class.check_add_user(message.from_id)
		if not message.payload and (exp := atta(message.text, message.attachments)):
			await self.lvl_class.update_lvl(message.from_id, exp = exp, boost = True, temp = True)

	def set_peer_id(self, peer_id):
		self.lvl_class(peer_id)
		self.amessage(peer_id)
		self.twdne(peer_id)
		self.shiki(peer_id)

task.run()

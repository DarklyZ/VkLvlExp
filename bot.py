from vbml import Patcher, PatchedValidators
from vkbottle import Bot
from vkbottle.ext import Middleware
from vkbottle.utils import TaskManager
from lvls import LVL, atta
from re import I, S
from os import getenv

class Validators(PatchedValidators):
	int = lambda self, value: int(value) if value.isdigit() or value[:1] in '+-' and value[1:].isdigit() else None
	pos = lambda self, value: int(value) if value.isdigit() or value[:1] in '+' and value[1:].isdigit() else None
	max = lambda self, value, extra: value if len(value) <= int(extra) else None
	inc = lambda self, value, *extra: value.lower() if value.lower() in extra else None

Patcher(validators = Validators, flags = I + S)
bot = Bot(getenv('TOKEN'), debug = False)

task = TaskManager(bot.loop)
task.add_task(bot.run(True))

bot.on.change_prefix_for_all([r'\.', '/', '!', ':'])
lvl_class = LVL(getenv('DATABASE_URL'), task.add_task)

import rules, commands
commands.bot.load(bot)
commands.chat_action.load(bot)
commands.regex.load(bot)
commands.top.load(bot, task.add_task)

@bot.middleware.middleware_handler()
class Register(Middleware):
	async def middleware(self, message):
		if message.peer_id == message.from_id or message.from_id < 0: return False
		lvl_class(message.peer_id)
		await lvl_class.check_add_user(message.from_id)
		if not message.payload and (exp := atta(message.text, message.attachments)):
			await lvl_class.update_lvl(message.from_id, exp = exp, boost = True, temp = True)

task.run()

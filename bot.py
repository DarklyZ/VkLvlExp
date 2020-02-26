from vbml import Patcher, PatchedValidators
from vkbottle import Bot
from lvls import LVL, atta
from re import I, S
from os import getenv

class Validators(PatchedValidators):
	int = lambda self, value: int(value) if value.isdigit() or value[:1] in '+-' and value[1:].isdigit() else None
	pos = lambda self, value: int(value) if value.isdigit() or value[:1] in '+' and value[1:].isdigit() else None
	max = lambda self, value, extra: value if len(value) <= int(extra) else None
	inc = lambda self, value, *extra: value if value.lower() in extra else None

Patcher(validators = Validators, flags = I + S)
bot = Bot(token = getenv('TOKEN'), debug = False)
bot.on.change_prefix_for_all([r'\.', '/', '!', ':'])
lvl_class = LVL(getenv('DATABASE_URL'), loop = bot.loop)

import rules, commands
commands.bot.load(bot)
commands.chat_action.load(bot)
commands.regex.load(bot)

@bot.on.pre_process()
async def pass_lvl(message):
	lvl_class(message.peer_id)
	if message.peer_id == message.from_id or message.from_id < 0: return
	await lvl_class.check_add_user(message.from_id)
	if not message.payload and (exp := atta(message.text, message.attachments, message.from_id)): await lvl_class.insert_lvl(message.from_id, exp = exp)

bot.run_polling()
from vbml import Patcher, PatchedValidators
from vkbottle import Bot
from lvls import LVL
from re import I, S
from os import getenv

class Validators(PatchedValidators):
	int = lambda self, value: int(value) if value.isdigit() or value[:1] in '+-' and value[1:].isdigit() else None
	pos = lambda self, value: int(value) if value.isdigit() or value[:1] in '+' and value[1:].isdigit() else None
	max = lambda self, value, extra: value if len(value) <= int(extra) else None
	inc = lambda self, value, *extra: value if value.lower() in extra else None

Patcher(validators = Validators, flags = I + S)
bot = Bot(token = getenv('TOKEN'), debug = "ERROR")
bot.on.change_prefix_for_all([r'\.', '/', '!', ':'])
lvl_class = LVL(getenv('DATABASE_URL'), loop = bot.loop)

import rules, bot_commands, chat_action_commands, regex_commands
bot_commands.load(bot)
chat_action_commands.load(bot)
regex_commands.load(bot)

@bot.on.pre_process()
async def pass_lvl(message):
	lvl_class(message.peer_id)
	if message.peer_id == message.from_id or message.from_id < 0: return
	await lvl_class.check_add_user(message.from_id)
	if not message.payload: await lvl_class.atta(message.text, message.attachments, message.from_id)

bot.run_polling()
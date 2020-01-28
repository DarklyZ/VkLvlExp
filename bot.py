from vkbottle.framework.bot import Vals
from vkbottle import Bot
from vbml import Patcher
from lvls import LVL
from re import I, S
from extra import atta, is_admin
from os import getenv

class Validators(Vals):
	int = lambda self, value: int(value) if value.isdigit() or value[:1] in '+-' and value[1:].isdigit() else None
	pos = lambda self, value: int(value) if value.isdigit() or value[:1] in '+' and value[1:].isdigit() else None
	max = lambda self, value, extra: value if len(value) <= int(extra) else None
	symbol = lambda self, value, extra: value if value in extra else None

bot = Bot(token = getenv('TOKEN'), group_id = getenv('GROUP_ID'), debug = True, vbml_patcher = Patcher(validators = Validators, flags = I + S))
bot.on.change_prefix_for_all([r'\.', '/', '!', ':'])
lvl_class = LVL(bot, getenv('DATABASE_URL'), bot.loop)
is_admin.set_api(bot.api)

import bot_commands, chat_action_commands, regex_commands
bot_commands.load(bot, lvl_class)
chat_action_commands.load(bot, lvl_class)
regex_commands.load(bot, lvl_class)

@bot.on.pre_process()
async def pass_lvl(message):
	lvl_class(message.peer_id)
	if message.peer_id == message.from_id or message.from_id < 0: return
	await lvl_class.check_add_user(message.from_id)
	exp = atta(message.text, message.attachments) or None
	if not message.payload and exp: await lvl_class.insert_lvl(message.from_id, exp = exp)

bot.run_polling()
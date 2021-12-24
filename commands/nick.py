from utils import Data as data
from utils.rules import custom_rules
from vkbottle.bot import BotLabeler

def replace_smile(str):
	for smile in ('🥇', '🥈', '🥉', '❸', '❷', '\n'):
		str = str.replace(smile, '❌')
	return str

help = [
	"/Set Nick <Ник> - заменить имя на ник",
	"/Del Nick - вернуть имя"
]

bl = BotLabeler(custom_rules = custom_rules)

@bl.chat_message(command = 'set nick <nick:max[12]>', with_reply_message = False)
async def set_nick(message, nick):
	nick = replace_smile(nick)
	await data.lvl.update_nick(message.from_id, nick = nick)
	await message.answer(f"Ник: \"{nick}\" установлен")

@bl.chat_message(command = 'set nick <nick:max[12]>', is_admin = True, with_reply_message = True)
async def set_nick(message, nick):
	nick = replace_smile(nick)
	await data.lvl.update_nick(message.reply_message.from_id, nick = nick)
	await message.answer(f"Ник: \"{nick}\" установлен")

@bl.chat_message(command = 'del nick', with_reply_message = False)
async def del_nick(message):
	await data.lvl.update_nick(message.from_id)
	await message.answer("Ник удалён")

@bl.chat_message(command = 'del nick', is_admin = True, with_reply_message = True)
async def del_nick(message):
	await data.lvl.update_nick(message.reply_message.from_id)
	await message.answer("Ник удалён")

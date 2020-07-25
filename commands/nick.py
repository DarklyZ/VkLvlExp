from utils import InitParams

def replace_smile(str):
	for smile in ('🥇', '🥈', '🥉', '❸', '❷', '\n'):
		str = str.replace(smile, '❌')
	return str

class NickCommands(InitParams.Params):
	help = [
		'/Set Nick <Ник> - заменить имя на ник',
		'/Del Nick - вернуть имя'
	]

	def __init__(self):
		@self.bot.on.chat_message(text = 'set nick <nick:max[12]>', command = True, with_reply_message = False)
		async def set_nick(message, nick):
			nick = replace_smile(nick)
			await self.lvl_class.update_nick(message.from_id, nick = nick)
			await message(f'Ник: "{nick}" установлен')

		@self.bot.on.chat_message(text = 'set nick <nick:max[12]>', command = True, is_admin = True, with_reply_message = True)
		async def set_nick(message, nick):
			nick = replace_smile(nick)
			await self.lvl_class.update_nick(message.reply_message.from_id, nick = nick)
			await message(f'Ник: "{nick}" установлен')

		@self.bot.on.chat_message(text = 'del nick', command = True, with_reply_message = False)
		async def del_nick(message):
			await self.lvl_class.update_nick(message.from_id)
			await message('Ник удалён')

		@self.bot.on.chat_message(text = 'del nick', command = True, is_admin = True, with_reply_message = True)
		async def del_nick(message):
			await self.lvl_class.update_nick(message.reply_message.from_id)
			await message('Ник удалён')

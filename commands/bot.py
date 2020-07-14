from utils import InitParams
from vkbottle import keyboard_gen
from utils.lvls import atta
from random import randint, choice
from re import search

dict_help = {
	None : [
		'/Help Top - топ',
		'/Help LVL - уровни',
		'/Help Nick - ники',
		'/Help Extra - доп. команды'
	],
	'top' : [
		'/TopLVL[ <от> <до>] - топ 10 участников',
		'/TopTemp[ <от> <до>] - временный топ 10 участников'
	],
	'lvl' : [
		'/MyLVL - мой уровень',
		'/LVL & <rep_mes> - посмотреть уровень участника',
		'/Tele <count> & <rep_mes> - передать свою exp другому',
	],
	'nick' : [
		'/Set Nick <Ник> - заменить имя на ник',
		'/Del Nick - вернуть имя'
	],
	'extra' : [
		'/BAN[ <причина>] & <rep_mes> - типо бан',
		'/Ord <chr>+ - код в юникоде символов',
		'/TWDNE - покажет рандомную вайфу с сайта ThisWaifuDoesNotExist'
	]
}

def replace_smile(str):
	for smile in ('🥇', '🥈', '🥉', '❸', '❷', '\n'):
		str = str.replace(smile, '❌')
	return str

class BotCommands(InitParams):
	def load(self):
		@self.bot.on.chat_message(text = ['help', 'help <extra:inc[top,lvl,nick,extra]>'], command = True)
		async def help(message, extra = None):
			await message('Команды:\n' + '\n'.join(f'{n + 1}) {comm}' for n, comm in enumerate(dict_help[extra])))

		@self.bot.on.chat_message(text = 'mylvl', command = True)
		async def mylvl(message):
			await self.lvl_class.send(id := message.from_id)
			await message(self.lvl_class[id])

		@self.bot.on.chat_message(text = 'lvl', command = True, with_reply_message = True)
		async def lvl(message):
			await self.lvl_class.send(id := message.reply_message.from_id)
			await message(self.lvl_class[id])

		@self.bot.on.chat_message(text = ['ban <text>', 'ban'], command = True, with_reply_message = True)
		async def ban(message, text = 'не указана'):
			await self.lvl_class.user(id := message.reply_message.from_id)
			await message(f"Бан пользователя:\n{self.lvl_class[id]}\nПричина: {text}", keyboard = keyboard_gen([
				[{'text': 'Ясно-понятно', 'color': 'positive', 'payload': {'command': 'ban'}}]
			], inline = True))

		@self.bot.on.chat_message(text = ['echo <text>', 'echo'], command = True, is_admin = True)
		async def echo(message, text = 'Сообщение не указано'):
			await message(f'{text}\n' + ''.join(f"[id{item['member_id']}|💬]"
					for item in (await self.bot.api.messages.get_conversation_members(peer_id = message.peer_id)).items
					if item['member_id'] > 0 and item['member_id'] != message.from_id))

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

		@self.bot.on.chat_message(text = ['exp <exp:int>', 'exp <exp:inc[up,down]>', 'exp <lvl:int> <exp:int>'], command = True, is_admin = True, with_reply_message = True)
		async def exp(message, exp, lvl = 0):
			if exp in ('up', 'down'): exp = atta(message.reply_message.text, message.reply_message.attachments, exp == 'down')
			await self.lvl_class.update_lvl(id := message.reply_message.from_id, exp = exp, lvl = lvl)
			await self.lvl_class.send(id)
			await message((f"{lvl:+}Ⓛ|" if lvl else '') + f"{exp:+}Ⓔ:\n" + self.lvl_class[id])

		@self.bot.on.chat_message(text = ['tele <exp:pos>', 'tele <exp:inc[up]>'], command = True, with_reply_message = True, from_id_pos = True)
		async def tele(message, exp):
			if exp == 'up': exp = atta(message.reply_message.text, message.reply_message.attachments)
			if await self.lvl_class.remove_exp(id1 := message.from_id, exp = exp):
				await self.lvl_class.update_lvl(id2 := message.reply_message.from_id, exp = exp)
				await self.lvl_class.send(id1, id2)
				blank = f"{exp:+}Ⓔ:\n{self.lvl_class[id2]}\n{-exp:+}Ⓔ:\n{self.lvl_class[id1]}"
			else:
				await self.lvl_class.send(id1)
				blank = f"Не хватает Ⓔ!\n{self.lvl_class[id1]}"
			await message(blank)

		@self.bot.on.chat_message(text = 'ord', command = True, with_reply_message = True)
		async def ordo(message):
			await message(f'Не знаю зачем тебе, но получай: {[ord(text) for text in message.reply_message.text]}')

		@self.bot.on.chat_message(text = 'info', command = True, with_reply_message = True)
		async def info(message):
			exp, errors = atta(message.reply_message.text, message.reply_message.attachments, return_errors = True)
			extra = '\nВозможные ошибки:\n' + ' / '.join(f"{err} -> {', '.join(errors[err])}" if errors[err] else err for err in errors) if errors else ''
			await message(f"Стоимость сообщения {exp:+}Ⓔ" + extra)

		@self.bot.on.chat_message(text = 'twdne', command = True)
		async def twdne(message):
			compliment = choice(('симпатичная', 'привлекательная', 'виртуозная', 'превосходная', 'милая', 'бесценная'))
			await message(message = f'Эта вайфу такая {compliment}', attachment = await self.twdne.get_doc(randint(1, 99999)))

		@self.bot.on.chat_message(text = 'date', command = True, with_reply_message = True)
		async def date_created(message):
			date = search(r'<ya:created dc:date="(?P<Y>\d{4})-(?P<M>\d{2})-(?P<D>\d{2}).+?"/>', await self.foaf(id := message.reply_message.from_id))
			await self.lvl_class.user(id)
			await message(message = f"Я проследила за пользователем: {self.lvl_class[id]},\nон создал страницу: {date['D']}-{date['M']}-{date['Y']}")
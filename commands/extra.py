from utils import InitData
from vkbottle import keyboard_gen
from random import randint, choice
from re import search

class ExtraCommands(InitData.Data):
	help = [
		'/BAN[ <причина>] & <rep_mes> - типо бан',
		'/Ord <chr>+ - код в юникоде символов',
		'/TWDNE - покажет рандомную вайфу с сайта ThisWaifuDoesNotExist',
		'/SS Animes|Mangas|Ranobe|Characters|People[ <стр>] <Название/Имя>'
	]

	def __init__(self):
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

		@self.bot.on.chat_message(text = 'ord', command = True, with_reply_message = True)
		async def ordo(message):
			await message(f'Не знаю зачем тебе, но получай: {[ord(text) for text in message.reply_message.text]}')

		@self.bot.on.chat_message(text = 'twdne', command = True)
		async def twdne(message):
			compliment = choice(('симпатичная', 'привлекательная', 'виртуозная', 'превосходная', 'милая', 'бесценная'))
			await message(message = f'Эта вайфу такая {compliment}', attachment = await self.twdne.get_doc(randint(1, 99999)))

		@self.bot.on.chat_message(text = 'date', command = True, with_reply_message = True)
		async def date_created(message):
			date = search(r'<ya:created dc:date="(?P<Y>\d{4})-(?P<M>\d{2})-(?P<D>\d{2}).+?"/>', await self.foaf(id := message.reply_message.from_id))
			await self.lvl_class.user(id)
			await message(message = f"Я проследила за пользователем: {self.lvl_class[id]},\nон создал страницу: {date['D']}-{date['M']}-{date['Y']}")

		@self.bot.on.chat_message(text = 'tts <text>', command = True)
		async def tts(message, text):
			await message(attachment = await self.amessage.get_doc(text))

		@self.bot.on.chat_message(text = ['ss <type:inc[animes,mangas,ranobe,characters,people]> <page:pos> <text>',
				'ss <type:inc[animes,mangas,ranobe,characters,people]> <text>'], command = True)
		async def shiki_search(message, type, text, page = 1):
			response = await self.shiki.search(type, text, page)
			if response:
				objs = [
					[
						f"{num + 1}) {item['russian'] or item['name']}",
						'Шики: ' + await self.shiki.get_shiki_short_link(item['url']),
						'Неко: ' + await self.shiki.get_neko_short_link(item['id']) if type == 'animes' else None
					]
					for num, item in enumerate(response)
				]
				text = '\n'.join('\n'.join(i for i in item if i) for item in objs)
				docs = await self.shiki.get_doc(item['image']['original'] for item in response)
				await message(text, attachment = ','.join(docs))
			else: await message('Не найдено')
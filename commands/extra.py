from utils import Data as data
from vkbottle.tools import Keyboard, Text, KeyboardButtonColor
from vkbottle.bot import BotLabeler
from random import randint, choice
from re import search

help = [
	'/BAN[ <причина>] & <rep_mes> - типо бан',
	'/Ord <chr>+ - код в юникоде символов',
	'/TWDNE - покажет рандомную вайфу с сайта ThisWaifuDoesNotExist',
	'/SS Animes|Mangas|Ranobe|Characters|People[ <стр>] <Название/Имя>',
	'/TTS <text> - озвучит <text>'
]

bl = BotLabeler()

@bl.chat_message(command = ['ban <text>', 'ban'], with_reply_message = True)
async def ban(message, text = 'не указана'):
	await data.lvl.user(id := message.reply_message.from_id)
	await message.answer(f"Бан пользователя:\n{data.lvl[id]}\nПричина: {text}", keyboard = Keyboard(inline = True)
		.add(Text(label = 'Ясно-понятно', payload = {'command': 'ban'}), color = KeyboardButtonColor.POSITIVE)
		.get_json())

@bl.chat_message(command = ['echo <text>', 'echo'], is_admin = True)
async def echo(message, text = 'Сообщение не указано'):
	await message.answer(f'{text}\n' + ''.join(f"[id{item.member_id}|💬]"
		for item in (await data.bot.api.messages.get_conversation_members(peer_id = message.peer_id)).items
		if item.member_id > 0 and item.member_id != message.from_id))

@bl.chat_message(command = 'ord', with_reply_message = True)
async def ordo(message):
	await message.answer(f'Не знаю зачем тебе, но получай: {[ord(text) for text in message.reply_message.text]}')

@bl.chat_message(command = 'twdne')
async def twdne(message):
	compliment = choice(('симпатичная', 'привлекательная', 'виртуозная', 'превосходная', 'милая', 'бесценная'))
	await message.answer(message = f'Эта вайфу такая {compliment}', attachment = await data.twdne.get_doc(randint(1, 99999)))

@bl.chat_message(command = 'date', with_reply_message = True)
async def date_created(message):
	date = search(r'<ya:created dc:date="(?P<Y>\d{4})-(?P<M>\d{2})-(?P<D>\d{2}).+?"/>', await data.foaf(id := message.reply_message.from_id))
	await data.lvl.user(id)
	await message.answer(message = f"Я проследила за пользователем: {data.lvl[id]},\nон создал страницу: {date['D']}-{date['M']}-{date['Y']}")

@bl.chat_message(command = 'tts <text>')
async def tts(message, text):
	await message.answer(attachment = await data.amessage.get_doc(text))

@bl.chat_message(command = ['ss <type:inc[animes,mangas,ranobe,characters,people]> <page:pos> <text>',
		'ss <type:inc[animes,mangas,ranobe,characters,people]> <text>'])
async def shiki_search(message, type, text, page = 1):
	response = await data.shiki.search(type, text, page)
	if response:
		objs = [[f"{num + 1}) {item['russian'] or item['name']}",
				'Шики: ' + await data.shiki.get_shiki_short_link(item['url']),
				'Неко: ' + await data.shiki.get_neko_short_link(item['id']) if type == 'animes' else None]
			for num, item in enumerate(response)]
		text = '\n'.join('\n'.join(i for i in item if i) for item in objs)
		docs = await data.shiki.get_doc(item['image']['original'] for item in response)
		await message.answer(text, attachment = ','.join(docs))
	else: await message.answer('Не найдено')
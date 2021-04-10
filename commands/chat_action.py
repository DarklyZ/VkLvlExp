from utils import Data as data
from vkbottle.bot import BotLabeler

bl = BotLabeler()

@bl.chat_message(command = 'hello', is_admin = True)
async def hello_help(message):
	await message.answer("Ключевые слова:\n{title} - заголовок\n{user} - пользователь\n{name} - имя бота")

@bl.chat_message(command = ['set hello <text>', 'set hello'], is_admin = True)
async def hello_plus(message, text = "* Стандартное приветствие *"):
	try: hello = text.format(title = 'title', user = 'user', name = 'name')
	except: return await message.answer("Неправильный формат")
	await data.lvl.update_text(text)
	await message.answer("Приветствие полученно\n" + hello)

@bl.chat_message(command = 'del hello', is_admin = True)
async def hello_del(message):
	await data.lvl.update_text()
	await message.answer("Приветствие удалено")

@bl.chat_message(action = 'chat_invite_user', with_text = True)
async def add_user(message, text):
	await data.lvl.user(id1 := message.from_id, id2 := message.action.member_id)
	if id1 != id2:
		title = f"* Welcome to the club, buddy. *\nВас призвал(а): {data.lvl[id1]}"
		bot_name = (await data.bot.api.groups.get_by_id())[0].name
		blank = text.format(title = title, user = data.lvl[id2], name = bot_name)
		photo = 457241337
	else:
		blank = f"Вернулся(ась) {data.lvl[id1]}."
		photo = 457241328
	await message.answer(blank, attachment = f'photo-{data.bot.polling.group_id}_{photo}')

@bl.chat_message(action = 'chat_kick_user', with_text = True, is_admin = True)
async def remove_user(message, text):
	await data.lvl.user(id2 := message.action.member_id)
	await message.answer(f"{data.lvl[id2]} заебал(а) админа.", attachment = f'photo-{data.bot.polling.group_id}_457241336')

@bl.chat_message(action = 'chat_kick_user', with_text = True, is_admin = False)
async def remove_user(message, text):
	await data.lvl.user(id2 := message.action.member_id)
	await message.answer(f"{data.lvl[id2]} стал(а) натуралом(.", attachment = f'photo-{data.bot.polling.group_id}_457241328')

@bl.chat_message(action = 'chat_invite_user_by_link', with_text = True)
async def add_user_link(message, text):
	await data.lvl.user(id1 := message.from_id)
	title = f"* Welcome to the club, buddy. *\n* Вы попали в ловушку *"
	bot_name = (await data.bot.api.groups.get_by_id())[0].name
	await message.answer(text.format(title = title, user = data.lvl[id1], name = bot_name), attachment = f'photo-{data.bot.polling.group_id}_457241337')
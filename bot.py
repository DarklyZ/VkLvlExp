from logging import basicConfig
from vk import VK
from vk.bot_framework import Dispatcher, NamedRule, BaseMiddleware
from vk.bot_framework.dispatcher.handler import SkipHandler
from vk.utils import TaskManager
from vk.keyboards import Keyboard, ButtonColor
from vk.types.message import Action
from vk.types.events.community.events_list import Event
from lvls import LVL
from random import choice
from string import punctuation as punc
from json import loads
from os import getenv
from extra import *

basicConfig(level="INFO")

vk, group_id, database_url = VK(getenv('TOKEN')), getenv('GROUP_ID'), getenv('DATABASE_URL')
task_manager = TaskManager(vk.loop)
dp = Dispatcher(vk)
lvl_class = LVL(vk)

@dp.middleware()
class Regist(BaseMiddleware):
	meta = {"deprecated": False}
	
	async def pre_process_event(self, event, data):
		if event.type == Event.MESSAGE_NEW and event.object.message.from_id != event.object.message.peer_id:
			message = event.object.message
			if (message.from_id < 0 or 
				message.reply_message is not None and
				message.reply_message.from_id < 0 or
				message.action is not None and
				message.action.member_id < 0): raise SkipHandler()
			data['lvl'] = lvl_class(message.peer_id)
			if not await data['lvl'].check_user(message.from_id): await data['lvl'].add_user(message.from_id)
			if message.payload is None: await data['lvl'].insert_lvl(message.from_id, exp = atta(message.text, message.attachments))
		return data

@dp.setup_rule
class Commands(NamedRule):
	key = 'commands'
	meta = {"deprecated": False}
    
	def __init__(self, commands):
		self.commands = commands

	async def check(self, message, data):
		msg = message.text.lower().split(maxsplit = 1)
		return msg and msg[0][0] in punc and msg[0][1:] in self.commands

@dp.setup_rule
class WithPayload(NamedRule):
	key = 'with_payload'
	meta = {"deprecated": False}

	def __init__(self, payload):
		self.payload = payload

	async def check(self, message, data):
		if self.payload and message.payload : return True
		elif not self.payload and not message.payload : return True
		else: return False

@dp.setup_rule
class PayloadCommands(NamedRule):
	key = 'payload_commands'
	meta = {"deprecated": False}

	def __init__(self, commands):
		self.commands = commands

	async def check(self, message, data):
		return message.payload and loads(message.payload).get('command') in self.commands

@dp.setup_rule
class IsAdmin(NamedRule):
	key = 'is_admin'
	meta = {"deprecated": False}

	def __init__(self, admin):
		self.admin = admin
	
	async def check(self, message, data):
		try: chat = (await vk.api_request('messages.getConversationsById', {'peer_ids': message.peer_id}))['items'][0]['chat_settings']
		except: is_admin = False
		else: is_admin = message.from_id == chat['owner_id'] or message.from_id in chat['admin_ids']
		if self.admin and is_admin: return True
		elif not self.admin and not is_admin: return True
		else: return False

@dp.message_handler(commands = ['help'], count_args = 0, in_chat = True)
async def help(message, data):
	await message.answer('''Команды:
1) /MyLVL - мой уровень
2) /TopLVL[ <от> <до>] - топ 10 участников
3) /LVL & <rep_mes> - посмотреть уровень участника
4) /Tele <count> & <rep_mes> - передать свою exp другому
5) /BAN[ <причина>] & <rep_mes> - типо бан
6) /Ord <chr>+ - код в юникоде символов''')

@dp.message_handler(commands = ['toplvl'], count_args = 0, in_chat = True)
@dp.message_handler(commands = ['toplvl'], have_args = [ispos, ispos], in_chat = True)
async def toplvl_send(message, data):
	reg_default = ('1', '10')
	reg = (int(data.get('args', reg_default)[0]), int(data.get('args', reg_default)[1]))
	await vk.api_request('messages.send', {'random_id' : 0, 'peer_id' : message.peer_id, 'message' : await data['lvl'].toplvl_size(*reg), 'disable_mentions' : True})

@dp.message_handler(commands = ['mylvl'], count_args = 0, in_chat = True)
async def mylvl(message, data):
	id = message.from_id
	await data['lvl'].send(id)
	await message.answer(data['lvl'][id])

@dp.message_handler(commands = ['lvl'], count_args = 0, with_reply_message = True, in_chat = True)
async def lvl(message, data):
	if message.reply_message.from_id > 0:
		id = message.reply_message.from_id
		await data['lvl'].send(id)
		await message.answer(data['lvl'][id])

ban_key = Keyboard(one_time = None, inline = True)
ban_key.add_text_button('Ясно-понятно', ButtonColor.POSITIVE, {'command' : 'ban'})
ban_key = ban_key.get_keyboard()
@dp.message_handler(commands = ['ban'], with_reply_message = True, in_chat = True)
async def ban(message, data):
	texts = message.text.split(maxsplit = 1)
	id = message.reply_message.from_id
	await data['lvl'].user(id)
	await message.answer(f"Бан пользователя:\n{data['lvl'][id]}\nПричина: {texts[1] if len(texts) == 2 else 'не указана'}", keyboard = ban_key)

@dp.message_handler(commands = ['echo'], count_args = 0, is_admin = True, in_chat = True)
async def echo(message, data):
	try: member_ids = (item['member_id'] for item in (await vk.api_request('messages.getConversationMembers', {'peer_id' : message.peer_id}))['items'] if item['member_id'] > 0 and item['member_id'] != message.from_id)
	except: pass
	else:
		id = message.from_id
		await data['lvl'].user(id)
		await message.answer(f"*{data['lvl'][id]} заорал на всю беседу*\nУслышали это:\n" + ''.join(f'[id{id}|💬]' for id in member_ids))

@dp.message_handler(commands = ['setsmile'], have_args = [lambda arg: len(arg) <= 4], is_admin = True, with_reply_message = True, in_chat = True)
async def set_smile(message, data):
	await data['lvl'].setsmile(message.reply_message.from_id, smile = data['args'][0])
	await message.answer(f"{data['args'][0]} : установлен")

@dp.message_handler(commands = ['delsmile'], count_args = 0, is_admin = True, with_reply_message = True, in_chat = True)
async def del_smile(message, data):
	await data['lvl'].setsmile(message.reply_message.from_id)
	await message.answer('Смайл удалён')

@dp.message_handler(commands = ['exp'], have_args = [lambda arg: arg in '+-'], is_admin = True, with_reply_message = True, in_chat = True)
@dp.message_handler(commands = ['exp'], have_args = [isint], is_admin = True, with_reply_message = True, in_chat = True)
@dp.message_handler(commands = ['exp'], have_args = [isint, isint], is_admin = True, with_reply_message = True, in_chat = True)
async def exp(message, data):
	id = message.reply_message.from_id
	if len(data['args']) == 2:
		lvl, exp = int(data['args'][0]), int(data['args'][1])
		blank = f"{lvl:+}Ⓛ|{exp:+}Ⓔ:\n"
		await data['lvl'].insert_lvl(id, lvl = lvl, exp = exp)
	else:
		exp = int(data['args'][0] if data['args'][0].isdigit() else f"{data['args'][0]}{atta(message.reply_message.text, message.reply_message.attachments)}")
		blank = f"{exp:+}Ⓔ:\n"
		await data['lvl'].insert_lvl(id, exp = exp)
	await data['lvl'].send(id)
	await message.answer(blank + data['lvl'][id])

@dp.message_handler(commands = ['tele'], have_args = [ispos], with_reply_message = True, in_chat = True)
async def tele(message, data):
	id1, id2 = message.from_id, message.reply_message.from_id
	exp = int(data['args'][0])
	if await data['lvl'].remove_exp(id1, exp = exp):
		await data['lvl'].insert_lvl(id2, exp = exp)
		await data['lvl'].send(id1, id2)
		blank = f"{exp:+}Ⓔ:\n{data['lvl'][id2]}\n{-exp:+}Ⓔ:\n{data['lvl'][id1]}"
	else:
		await data['lvl'].send(id1)
		blank = f"Не хватает Ⓔ!\n{data['lvl'][id1]}"
	await message.answer(blank)

@dp.message_handler(commands = ['tele'], have_args = [lambda arg: arg == '+'], with_reply_message = True, in_chat = True)
async def telep(message, data):
	id1, id2 = message.from_id, message.reply_message.from_id
	exp = atta(message.reply_message.text, message.reply_message.attachments)
	if await data['lvl'].remove_exp(id1, exp = exp):
		await data['lvl'].insert_lvl(id2, exp = exp)
		await data['lvl'].send(id1, id2)
		blank = f"{exp:+}Ⓔ:\n{data['lvl'][id2]}\n{-exp:+}Ⓔ:\n{data['lvl'][id1]}"
	else:
		await data['lvl'].send(id1)
		blank = f"Не хватает Ⓔ!\n{data['lvl'][id1]}"
	await message.answer(blank)

@dp.message_handler(commands = ['ord'], count_args = 0, with_reply_message = True, in_chat = True)
async def ordo(message, data):
	ord_list = [ord(text) for text in message.reply_message.text]
	await message.answer(f'Не знаю зачем тебе, но получай: {ord_list}')

@dp.message_handler(commands = ['info'], count_args = 0, with_reply_message = True, in_chat = True)
async def info(message, data):
	exp = atta(message.reply_message.text, message.reply_message.attachments)
	await message.answer(f"Стоимость сообщения {exp:+}Ⓔ")

@dp.message_handler(commands = ['hello'], count_args = 0, is_admin = True, in_chat = True)
async def hello_help(message, data):
	await message.answer('''Ключевые слова:
{title} - заголовок
{user} - пользователь
{name} - имя бота
''')

@dp.message_handler(commands = ['sethello'], in_chat = True, is_admin = True)
async def hello_plus(message, data):
	text = message.text.split(maxsplit = 1)[1]
	try: hello = text.format(title = 'title', user = 'user', name = 'name')
	except Exception as e: await message.answer(f'Ошибка "{e}"')
	else:
		await data['lvl'].add_text(text)
		await message.answer('Приветствие полученно\n' + hello)

@dp.message_handler(commands = ['delhello'], count_args = 0, is_admin = True, in_chat = True)
async def hello_del(message, data):
	await data['lvl'].del_text()
	await message.answer('Приветствие удалено')

@dp.message_handler(chat_action = Action.chat_invite_user)
async def add_user(message, data):
	id1, id2 = message.from_id, message.action.member_id
	text = await data['lvl'].hello_text()
	if text is not None:
		await data['lvl'].user(id1,id2)
		if id1 != id2:
			title = f"* Welcome to the club, buddy. *\nВас призвал(а): {data['lvl'][id1]}"
			bot_name = (await vk.api_request('groups.getById', {'group_id' : group_id}))[0]['name']
			blank = text.format(title = title, user = data['lvl'][id2], name = bot_name)
			photo = 457241337
		else:
			blank = f"Вернулся(ась) {data['lvl'][id1]}."
			photo = 457241328
		await message.answer(blank, attachment = f'photo-{group_id}_{photo}')

@dp.message_handler(chat_action = Action.chat_kick_user, is_admin = False)
async def remove_user(message, data):
	id2 = message.action.member_id
	if await data['lvl'].hello_text() is not None:
		await data['lvl'].user(id2)
		await message.answer(f"{data['lvl'][id2]} стал(а) натуралом(.", attachment = f'photo-{group_id}_457241328')

@dp.message_handler(chat_action = Action.chat_kick_user, is_admin = True)
async def remove_user_admin(message, data):
	id2 = message.action.member_id
	if await data['lvl'].hello_text() is not None:
		await data['lvl'].user(id2)
		await message.answer(f"{data['lvl'][id2]} заебал(а) админа.", attachment = f'photo-{group_id}_457241336')

@dp.message_handler(chat_action = Action.chat_invite_user_by_link)
async def add_user_link(message, data):
	id1 = message.from_id
	text = await data['lvl'].hello_text()
	if text is not None:
		await data['lvl'].user(id1)
		title = f"* Welcome to the club, buddy. *\n* Вы попали в ловушку *"
		bot_name = (await vk.api_request('groups.getById', {'group_id': group_id}))[0]['name']
		blank = text.format(title = title, user = data['lvl'][id1], name = bot_name)
		await message.answer(blank, attachment = f'photo-{group_id}_457241337')

@dp.message_handler(regex = r'^f+$', in_chat = True)
async def f_f(message, data):
	rand = choice((457241326,457241327,457241328,457241331,457241332,457241333,457241334,457241338,457241339))
	await message.answer('Пал боец\nСмертью храбрых', attachment = f'photo-{group_id}_{rand}')

@dp.message_handler(regex = r'^[^\?]*\?{3}$', in_chat = True)
async def hm_(message, data):
	await message.answer('', attachment = f'photo-{group_id}_457241329')

@dp.message_handler(regex = r'^[^\?]*\?{2}$', in_chat = True)
async def h_(message, data):
	await message.answer('', attachment = f'photo-{group_id}_457241330')

@dp.message_handler(regex = r'\bня\b', in_chat = True)
async def nya(message, data):
	await message.answer('Ня!')

@dp.message_handler(regex = r'смерт|суицид|умереть|гибну|окно', in_chat = True)
async def olga(message, data):
	await message.answer(f"Вы написали:\n\"{message.text}\".\nЯ расценила это за попытку суицида.\n[id{await data['lvl'].getconst('olga_id')}|#бля_Оля_живи!!!!!]")

@dp.message_handler(regex = r'\b(?:мирарукурин|мира|рару|руку|кури|рин)\b', in_chat = True)
async def archi(message, data):
	await vk.api_request('messages.send', {'random_id' : 0, 'peer_id' : message.peer_id, 'sticker_id' : 9805})
	await message.answer(f"[id{await data['lvl'].getconst('archi_id')}|💬][id{message.from_id}|🃏]Ожидайте бана…")
		
@task_manager.add_task
async def run():
	await lvl_class.connect_db(database_url)
	dp.run_polling(group_id)

async def on_shutdown():
	await vk.close()
	await lvl_class.close_db()

if __name__ == "__main__":
	task_manager.run(auto_reload = True, on_shutdown = on_shutdown)

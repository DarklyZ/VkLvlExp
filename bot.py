from logging import basicConfig
from vk import VK, types
from vk.bot_framework import Dispatcher, NamedRule, BaseMiddleware
from vk.utils import TaskManager
from vk.keyboards import Keyboard, ButtonColor
from lvls import LVL
from random import choice
from json import loads
from os import getenv
from extra import *

basicConfig(level="INFO")

dp = Dispatcher(VK(getenv('TOKEN')), getenv('GROUP_ID'))
task_manager = TaskManager(dp.vk.loop)
lvl_class = LVL(dp.vk)

@dp.middleware()
class Regist(BaseMiddleware):
	async def pre_process_event(self, event, data):
		from_id, peer_id = event['object']['message']['from_id'], event['object']['message']['peer_id']
		if event['type'] == 'message_new' and from_id != peer_id:
			data['lvl'] = lvl_class(peer_id)
			if not data['lvl'].check_user(from_id) and from_id > 0:
				data['lvl'].add_user(from_id)
		data['message'] = event['object']['message']
		return data

	async def post_process_event(self):
		pass

@dp.setup_rule
class Commands(NamedRule):
	key = 'commands'

	def __init__(self, commands):
		self.commands = commands

	async def check(self, message, data):
		msg = message.text.lower().split()
		return msg and msg[0][1:] in self.commands

@dp.setup_rule
class WithPayload(NamedRule):
	key = 'with_payload'

	def __init__(self, payload):
		self.payload = payload

	async def check(self, message, data):
		if self.payload and message.payload : return True
		elif not self.payload and not message.payload : return True
		else: return False

@dp.setup_rule
class PayloadCommands(NamedRule):
	key = 'payload_commands'

	def __init__(self, commands):
		self.commands = commands

	async def check(self, message, data):
		return message.payload and loads(message.payload)['command'] in self.commands

@dp.setup_rule
class IsAdmin(NamedRule):
	key = 'is_admin'

	def __init__(self, admin):
		self.admin = admin
	
	async def check(self, message, data):
		try: chat = (await dp.vk.api_request('messages.getConversationsById', {'peer_ids': message.peer_id}))['items'][0]['chat_settings']
		except: is_admin = False
		else: is_admin = message.from_id == chat['owner_id'] or message.from_id in chat['admin_ids']
		if self.admin and is_admin: return True
		elif not self.admin and not is_admin: return True
		else: return False

@dp.message_handler(commands = ['help'], count_args = 0, in_chat = True)
async def help(message, data):
	await message.answer('''Команды:
1) /MyLVL - мой уровень
2) /TopLVL[ <от>:<до>] - топ 10 участников
3) /LVL & <id>+ - посмотреть уровни
4) /Tele <count> & <id> - передать свою exp другому
5) /BAN[ <причина>] & <id>+ - типо бан
6) /Ord <chr>+ - код в юникоде символов''')

@dp.message_handler(regex = r'^f+$', in_chat = True)
async def f_f(message, data):
	rand = choice((457241326,457241327,457241328,457241331,457241332,457241333,457241334,457241338,457241339))
	await message.answer('Пал боец\nСмертью храбрых', attachment = f'photo-{dp.group_id}_{rand}')

@dp.message_handler(regex = r'^[^\?]*\?{3}$', in_chat = True)
async def hm_(message, data):
	await message.answer('', attachment = f'photo-{dp.group_id}_457241329')

@dp.message_handler(regex = r'^[^\?]*\?{2}$', in_chat = True)
async def h_(message, data):
	await message.answer('', attachment = f'photo-{dp.group_id}_457241330')

@dp.message_handler(commands = ['toplvl'], count_args = 0, in_chat = True)
@dp.message_handler(commands = ['toplvl'], have_args = [lambda arg: arg.isdigit(), lambda arg: arg.isdigit()], in_chat = True)
async def toplvl_send(message, data):
	reg_default = ('1', '10')
	reg = (int(data.get('args', reg_default)[0]), int(data.get('args', reg_default)[1]))
	await dp.vk.api_request('messages.send', {'random_id' : 0, 'peer_id' : message.peer_id, 'message' : await data['lvl'].toplvl_size(*reg), 'disable_mentions' : True})

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
	if message.reply_message.from_id > 0:
		texts = message.text.split(maxsplit = 1)
		id = message.reply_message.from_id
		await data['lvl'].user(id)
		await message.answer(f"Бан пользователя:\n{data['lvl'][id]}\nПричина: {texts[1] if len(texts) == 2 else 'не указана'}", keyboard = ban_key)

@dp.message_handler(commands = ['echo'], count_args = 0, is_admin = True, in_chat = True)
async def echo(message, data):
	try: member_ids = [item['member_id'] for item in (await dp.vk.api_request('messages.getConversationMembers', {'peer_id' : message.peer_id}))['items'] if item['member_id'] > 0 and item['member_id'] != message.from_id]	
	except: pass
	else:
		id = message.from_id
		await data['lvl'].user(id)
		await message.answer(f"*{data['lvl'][id]} заорал на всю беседу*\nУслышали это:\n" + ''.join(f'[id{id}|💬]' for id in member_ids))

@dp.message_handler(commands = ['setsmile'], have_args = [lambda arg: len(arg) <= 4], is_admin = True, with_reply_message = True, in_chat = True)
async def set_smile(message, data):
	if message.reply_message.from_id > 0:
		data['lvl'].setsmile(message.reply_message.from_id, smile = data['args'][0])
		await message.answer(f"{data['args'][0]} : установлен")

@dp.message_handler(commands = ['delsmile'], count_args = 0, is_admin = True, with_reply_message = True, in_chat = True)
async def del_smile(message, data):
	if message.reply_message.from_id > 0:
		data['lvl'].setsmile(message.reply_message.from_id)
		await message.answer('Смайл удалён')

@dp.message_handler(commands = ['exp'], have_args = [isint], is_admin = True, with_reply_message = True, in_chat = True)
@dp.message_handler(commands = ['exp'], have_args = [isint, isint], is_admin = True, with_reply_message = True, in_chat = True)
async def exp(message, data):
	if message.reply_message.from_id > 0:
		id = message.reply_message.from_id
		if len(data['args']) == 2:
			lvl, exp = int(data['args'][0]), int(data['args'][1])
			blank = f"{lvl:+}Ⓛ|{exp:+}Ⓔ:\n"
			data['lvl'].insert_lvl(id, lvl = lvl, exp = exp)
		else:
			exp = int(data['args'][0])
			blank = f"{exp:+}Ⓔ:\n"
			data['lvl'].insert_lvl(id, exp = exp)
		await data['lvl'].send(id)
		await message.answer(blank + data['lvl'][id])

@dp.message_handler(commands = ['exp'], have_args = [lambda arg: arg in '+-'], is_admin = True, with_reply_message = True, in_chat = True)
async def expp(message, data):
	if message.reply_message.from_id > 0:
		id = message.reply_message.from_id
		exp =  int(f"{data['args'][0]}{atta(message.reply_message.text, message.reply_message.attachments)}")
		data['lvl'].insert_lvl(id, exp = exp)
		await data['lvl'].send(id)
		await message.answer(f"{exp:+}Ⓔ:\n{data['lvl'][id]}")

@dp.message_handler(commands = ['tele'], have_args = [ispos], with_reply_message = True, in_chat = True)
async def tele(message, data):
	if message.reply_message.from_id > 0:
		exp = int(data['args'][0])
		id1, id2 = message.from_id, message.reply_message.from_id
		if data['lvl'].remove_exp(id1, exp = exp):
			data['lvl'].insert_lvl(id2, exp = exp)
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
	exp = atta(message.reply_message.text, message.reply_message.attachments, data['message']['reply_message']['attachments'])
	await message.answer(f'Стоимость сообщения {exp:+}Ⓔ')

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
		data['lvl'].add_text(text)
		await message.answer('Приветствие полученно\n' + hello)

@dp.message_handler(commands = ['delhello'], count_args = 0, is_admin = True, in_chat = True)
async def hello_del(message, data):
	data['lvl'].del_text()
	await message.answer('Приветствие удалено')

@dp.message_handler(chat_action = types.message.Action.chat_invite_user)
async def add_user(message, data):
	id1, id2 = message.from_id, message.action.member_id
	text = data['lvl'].hello_text()
	if id1 > 0 and id2 > 0 and text:
		await data['lvl'].user(id1,id2)
		if id1 != id2:
			title = f"* Welcome to the club, buddy. *\nВас призвал(а): {data['lvl'][id1]}"
			bot_name = (await dp.vk.api_request('groups.getById', {'group_id' : dp.group_id}))[0]['name']
			blank = text.format(title = title, user = data['lvl'][id2], name = bot_name)
			photo = 457241337
		else:
			blank = f"Вернулся(ась) {data['lvl'][id1]}."
			photo = 457241328
		await message.answer(blank, attachment = f'photo-{dp.group_id}_{photo}')

@dp.message_handler(chat_action = types.message.Action.chat_kick_user, is_admin = False)
async def remove_user(message, data):
	id2 = message.action.member_id
	if id2 > 0 and data['lvl'].hello_text():
		await data['lvl'].user(id2)
		await message.answer(f"{data['lvl'][id2]} стал(а) натуралом(.", attachment = f'photo-{dp.group_id}_457241328')

@dp.message_handler(chat_action = types.message.Action.chat_kick_user, is_admin = True)
async def remove_user_admin(message, data):
	id2 = message.action.member_id
	if id2 > 0 and data['lvl'].hello_text():
		await data['lvl'].user(id2)
		await message.answer(f"{data['lvl'][id2]} заебал(а) админа.", attachment = f'photo-{dp.group_id}_457241336')

@dp.message_handler(chat_action = types.message.Action.chat_invite_user_by_link)
async def add_user_link(message, data):
	id1 = message.from_id
	text = data['lvl'].hello_text()
	if id1 > 0 and text:
		await data['lvl'].user(id1)
		title = f"* Welcome to the club, buddy. *\n* Вы попали в ловушку *"
		bot_name = (await dp.vk.api_request('groups.getById', {'group_id': dp.group_id}))[0]['name']
		blank = text.format(title = title, user = data['lvl'][id1], name = bot_name)
		await message.answer(blank, attachment = f'photo-{dp.group_id}_457241337')

@dp.message_handler(with_payload = False, in_chat = True)
async def pass_lvl(message, data):
	if message.from_id > 0:
		exp = atta(message.text, message.attachments, data['message']['attachments'])
		data['lvl'].insert_lvl(message.from_id, exp = exp)
	if search(r'смерт|суицид|умереть|гибну|окно',message.text, I): await message.answer(f'Вы написали:\n"{message.text}".\nЯ расценила это за попытку суицида.\n[id532695720|#бля_Оля_живи!!!!!]')
	if search(r'\b(?:мирарукурин|мира|рару|руку|кури|рин)\b', message.text, I):
		await dp.vk.api_request('messages.send', {'random_id' : 0, 'peer_id' : message.peer_id, 'sticker_id' : 9805})
		await message.answer(f'[id121852428|💬][id{message.from_id}|🃏]Ожидайте бана…')

@task_manager.add_task
async def run():
	dp.run_polling()

if __name__ == "__main__":
	task_manager.run(auto_reload = True)
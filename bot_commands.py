from vk.keyboards import Keyboard, ButtonColor
from extra import atta, isint, ispos

def load(dp, vk):
	
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
		top_range = map(int, data['args']) if 'args' in data else (1, 10)
		await message.answer(await data['lvl'].toplvl_size(*top_range), disable_mentions = True)
	
	@dp.message_handler(commands = ['mylvl'], count_args = 0, in_chat = True)
	async def mylvl(message, data):
		id = message.from_id
		await data['lvl'].send(id)
		await message.answer(data['lvl'][id])
	
	@dp.message_handler(commands = ['lvl'], count_args = 0, with_reply_message = True, in_chat = True)
	async def lvl(message, data):
		id = message.reply_message.from_id
		await data['lvl'].send(id)
		await message.answer(data['lvl'][id])
	
	ban_key = Keyboard(one_time = None, inline = True)
	ban_key.add_text_button('Ясно-понятно', ButtonColor.POSITIVE, {'command' : 'ban'})
	ban_key = ban_key.get_keyboard()
	@dp.message_handler(commands = ['ban'], with_reply_message = True, in_chat = True)
	async def ban(message, data):
		id = message.reply_message.from_id
		await data['lvl'].user(id)
		await message.answer(f"Бан пользователя:\n{data['lvl'][id]}\nПричина: {message.text[5:] or 'не указана'}", keyboard = ban_key)
	
	@dp.message_handler(commands = ['echo'], is_admin = True, in_chat = True)
	async def echo(message, data):
		member_ids = (item['member_id'] for item in (await vk.api_request('messages.getConversationMembers', {'peer_id' : message.peer_id}))['items'] if item['member_id'] > 0 and item['member_id'] != id)
		await message.answer(f"{message.text[6:] or 'Сообщение не указано'}\n{''.join(f'[id{member_id}|💬]' for member_id in member_ids)}")
	
	@dp.message_handler(commands = ['setsmile'], have_args = [lambda arg: len(arg) <= 4], is_admin = True, with_reply_message = True, in_chat = True)
	async def set_smile(message, data):
		await data['lvl'].setsmile(message.reply_message.from_id, smile = data['args'][0])
		await message.answer(f"{data['args'][0]} установлен")
	
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
			exp = int(f"{data['args'][0]}{atta(message.reply_message.text, message.reply_message.attachments)}" if data['args'][0] in '+-' else data['args'][0])
			blank = f"{exp:+}Ⓔ:\n"
			await data['lvl'].insert_lvl(id, exp = exp)
		await data['lvl'].send(id)
		await message.answer(blank + data['lvl'][id])
	
	@dp.message_handler(commands = ['tele'], have_args = [lambda arg: arg == '+'], with_reply_message = True, in_chat = True)
	@dp.message_handler(commands = ['tele'], have_args = [ispos], with_reply_message = True, in_chat = True)
	async def tele(message, data):
		id1, id2 = message.from_id, message.reply_message.from_id
		exp = int(f"{data['args'][0]}{atta(message.reply_message.text, message.reply_message.attachments)}" if data['args'][0] == '+' else data['args'][0])
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
	
	return dp
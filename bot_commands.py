from extra import atta, IsAdmin, WithReplyMessage, FromIdPos
from lvls import LVL
from vbml import Pattern

def load(bot):
	lvl_class = LVL.get_current()
	
	@bot.on.chat_message(text = 'help', command = True)
	async def help(message):
		await message('''Команды:
1) /MyLVL - мой уровень
2) /TopLVL[ <от> <до>] - топ 10 участников
3) /LVL & <rep_mes> - посмотреть уровень участника
4) /Tele <count> & <rep_mes> - передать свою exp другому
5) /BAN[ <причина>] & <rep_mes> - типо бан
6) /Ord <chr>+ - код в юникоде символов''')
	
	@bot.on.chat_message(text = ['toplvl <one:pos> <two:pos>', 'toplvl'], command = True)
	async def toplvl_send(message, one = 1, two = 10):
		await message(await lvl_class.toplvl_size(one, two), disable_mentions = True)
	
	@bot.on.chat_message(text = 'mylvl', command = True)
	async def mylvl(message):
		id = message.from_id
		await lvl_class.send(id)
		await message(lvl_class[id])
	
	@bot.on.chat_message(WithReplyMessage(True), text = 'lvl', command = True)
	async def lvl(message):
		id = message.reply_message.from_id
		await lvl_class.send(id)
		await message(lvl_class[id])
	
	@bot.on.chat_message(WithReplyMessage(True), text = ['ban <text>', 'ban'], command = True)
	async def ban(message, text = 'не указана'):
		id = message.reply_message.from_id
		await lvl_class.user(id)
		await message(f"Бан пользователя:\n{lvl_class[id]}\nПричина: {text}")
	
	@bot.on.chat_message(IsAdmin(True), text = ['echo <text>', 'echo'], command = True)
	async def echo(message, text = 'Сообщение не указано'):
		member_ids = (item['member_id'] for item in (await vk.api_request('messages.getConversationMembers', {'peer_id' : message.peer_id}))['items'] if item['member_id'] > 0 and item['member_id'] != id)
		await message(f"{text}\n{''.join(f'[id{member_id}|💬]' for member_id in member_ids)}")
	
	@bot.on.chat_message(IsAdmin(True), WithReplyMessage(True), text = 'set smile <smile:max[4]>', command = True)
	async def set_smile(message, smile):
		await lvl_class.setsmile(message.reply_message.from_id, smile = smile)
		await message(f"{smile} установлен")
	
	@bot.on.chat_message(IsAdmin(True), WithReplyMessage(True), text = 'del smile', command = True)
	async def del_smile(message):
		await lvl_class.setsmile(message.reply_message.from_id)
		await message('Смайл удалён')
	
	@bot.on.chat_message(IsAdmin(True), WithReplyMessage(True), text = 'exp <lvl:int> <exp:int>', command = True)
	async def exp(message, lvl, exp):
		id = message.reply_message.from_id
		await lvl_class.insert_lvl(id, lvl = lvl, exp = exp)
		await lvl_class.send(id)
		await message(f"{lvl:+}Ⓛ|{exp:+}Ⓔ:\n" + lvl_class[id])
	
	@bot.on.chat_message(IsAdmin(True), WithReplyMessage(True), text = ['exp <exp:int>','exp <exp:inc[up,down]>'], command = True)
	async def exp(message, exp):
		id = message.reply_message.from_id
		if exp in ('up', 'down'): exp = atta(message.reply_message.text, message.reply_message.attachments) * {'up': 1, 'down': -1}[exp]
		await lvl_class.insert_lvl(id, exp = exp)
		await lvl_class.send(id)
		await message(f"{exp:+}Ⓔ:\n" + lvl_class[id])
	
	@bot.on.chat_message(WithReplyMessage(True), FromIdPos(True), text = ['tele <exp:pos>', 'tele <exp:inc[up]>'], command = True)
	async def tele(message, exp):
		id1, id2 = message.from_id, message.reply_message.from_id
		if exp == 'up': exp = atta(message.reply_message.text, message.reply_message.attachments)
		if await lvl_class.remove_exp(id1, exp = exp):
			await lvl_class.insert_lvl(id2, exp = exp)
			await lvl_class.send(id1, id2)
			blank = f"{exp:+}Ⓔ:\n{lvl_class[id2]}\n{-exp:+}Ⓔ:\n{lvl_class[id1]}"
		else:
			await lvl_class.send(id1)
			blank = f"Не хватает Ⓔ!\n{lvl_class[id1]}"
		await message(blank)
	
	@bot.on.chat_message(WithReplyMessage(True), text = 'ord', command = True)
	async def ordo(message):
		ord_list = [ord(text) for text in message.reply_message.text]
		await message(f'Не знаю зачем тебе, но получай: {ord_list}')
	
	@bot.on.chat_message(WithReplyMessage(True), text = 'info', command = True)
	async def info(message):
		exp = atta(message.reply_message.text, message.reply_message.attachments)
		await message(f"Стоимость сообщения {exp:+}Ⓔ")
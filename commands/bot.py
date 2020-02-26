def load(bot):
	from vkbottle import keyboard_gen
	from lvls import LVL, atta
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
		await lvl_class.send(id := message.from_id)
		await message(lvl_class[id])
	
	@bot.on.chat_message(text = 'lvl', command = True, with_reply_message = True)
	async def lvl(message):
		await lvl_class.send(id := message.reply_message.from_id)
		await message(lvl_class[id])

	@bot.on.chat_message(text = ['ban <text>', 'ban'], command = True, with_reply_message = True)
	async def ban(message, text = 'не указана'):
		await lvl_class.user(id := message.reply_message.from_id)
		await message(f"Бан пользователя:\n{lvl_class[id]}\nПричина: {text}", keyboard = keyboard_gen([
			[{'text': 'Ясно-понятно', 'color': 'positive', 'payload': {'command': 'ban'}}]
		], inline = True))
	
	@bot.on.chat_message(text = ['echo <text>', 'echo'], command = True, is_admin = True)
	async def echo(message, text = 'Сообщение не указано'):
		await message(f'{text}\n' + ''.join(f"[id{item['member_id']}|💬]"
											for item in (await bot.api.messages.getConversationMembers(peer_id = message.peer_id))['items']
											if item['member_id'] > 0 and item['member_id'] != message.from_id))
	
	@bot.on.chat_message(text = 'set smile <smile:max[4]>', command = True, is_admin = True, with_reply_message = True)
	async def set_smile(message, smile):
		await lvl_class.setsmile(message.reply_message.from_id, smile = smile)
		await message(f"{smile} установлен")
	
	@bot.on.chat_message(text = 'del smile', command = True, is_admin = True, with_reply_message = True)
	async def del_smile(message):
		await lvl_class.setsmile(message.reply_message.from_id)
		await message('Смайл удалён')
	
	@bot.on.chat_message(text = 'exp <lvl:int> <exp:int>', command = True, is_admin = True, with_reply_message = True)
	async def exp(message, lvl, exp):
		await lvl_class.insert_lvl(id := message.reply_message.from_id, lvl = lvl, exp = exp)
		await lvl_class.send(id)
		await message(f"{lvl:+}Ⓛ|{exp:+}Ⓔ:\n" + lvl_class[id])
	
	@bot.on.chat_message(text = ['exp <exp:int>','exp <exp:inc[up,down]>'], command = True, is_admin = True, with_reply_message = True)
	async def exp(message, exp):
		if exp in ('up', 'down'): exp = atta(message.reply_message.text, message.reply_message.attachments, exp == 'down')
		await lvl_class.insert_lvl(id := message.reply_message.from_id, exp = exp)
		await lvl_class.send(id)
		await message(f"{exp:+}Ⓔ:\n" + lvl_class[id])
	
	@bot.on.chat_message(text = ['tele <exp:pos>', 'tele <exp:inc[up]>'], command = True, with_reply_message = True, from_id_pos = True)
	async def tele(message, exp):
		if exp == 'up': exp = atta(message.reply_message.text, message.reply_message.attachments)
		if await lvl_class.remove_exp(id1 := message.from_id, exp = exp):
			await lvl_class.insert_lvl(id2 := message.reply_message.from_id, exp = exp)
			await lvl_class.send(id1, id2)
			blank = f"{exp:+}Ⓔ:\n{lvl_class[id2]}\n{-exp:+}Ⓔ:\n{lvl_class[id1]}"
		else:
			await lvl_class.send(id1)
			blank = f"Не хватает Ⓔ!\n{lvl_class[id1]}"
		await message(blank)
	
	@bot.on.chat_message(text = 'ord', command = True, with_reply_message = True)
	async def ordo(message):
		await message(f'Не знаю зачем тебе, но получай: {[ord(text) for text in message.reply_message.text]}')
	
	@bot.on.chat_message(text = 'info', command = True, with_reply_message = True)
	async def info(message):
		await message(f"Стоимость сообщения {atta(message.reply_message.text, message.reply_message.attachments):+}Ⓔ")

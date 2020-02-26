def load(bot):
	from lvls import LVL as lvl_class
	lvl_class = lvl_class.get_current()
	
	@bot.on.chat_message(text = 'hello', command = True, is_admin = True)
	async def hello_help(message):
		await message('''Ключевые слова:
{title} - заголовок
{user} - пользователь
{name} - имя бота''')

	@bot.on.chat_message(text = ['set hello <text>', 'set hello'], command = True, is_admin = True)
	async def hello_plus(message, text = '* Стандартное приветствие *'):
		try: hello = text.format(title = 'title', user = 'user', name = 'name')
		except: await message('Неправильный формат')
		else:
			await lvl_class.add_text(text)
			await message('Приветствие полученно\n' + hello)
	
	@bot.on.chat_message(text = 'del hello', command = True, is_admin = True)
	async def hello_del(message):
		await lvl_class.add_text()
		await message('Приветствие удалено')
	
	@bot.on.chat_message(chat_action_rule = 'chat_invite_user', with_text = True)
	async def add_user(message, text):
		await lvl_class.user(id1 := message.from_id, id2 := message.action.member_id)
		if id1 != id2:
			title = f"* Welcome to the club, buddy. *\nВас призвал(а): {lvl_class[id1]}"
			bot_name = (await bot.api.groups.getById(group_id = bot.group_id))[0]['name']
			blank = text.format(title = title, user = lvl_class[id2], name = bot_name)
			photo = 457241337
		else:
			blank = f"Вернулся(ась) {lvl_class[id1]}."
			photo = 457241328
		await message(blank, attachment = f'photo-{bot.group_id}_{photo}')
	
	@bot.on.chat_message(chat_action_rule = 'chat_kick_user', with_text = True, is_admin = True)
	async def remove_user(message, text):
		await lvl_class.user(id2 := message.action.member_id)
		await message(f"{lvl_class[id2]} заебал(а) админа.", attachment = f'photo-{bot.group_id}_457241336')

	@bot.on.chat_message(chat_action_rule = 'chat_kick_user', with_text = True, is_admin = False)
	async def remove_user(message, text):
		await lvl_class.user(id2 := message.action.member_id)
		await message(f"{lvl_class[id2]} стал(а) натуралом(.", attachment = f'photo-{bot.group_id}_457241328')
	
	@bot.on.chat_message(chat_action_rule = 'chat_invite_user_by_link', with_text = True)
	async def add_user_link(message, text):
		await lvl_class.user(id1 := message.from_id)
		title = f"* Welcome to the club, buddy. *\n* Вы попали в ловушку *"
		bot_name = (await bot.api.groups.getById(group_id = bot.group_id))[0]['name']
		await message(text.format(title = title, user = lvl_class[id1], name = bot_name), attachment = f'photo-{bot.group_id}_457241337')
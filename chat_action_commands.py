from extra import is_admin

def load(bot, lvl_class):
	@bot.on.chat_message(text = 'hello', command = True)
	async def hello_help(message):
		if not await is_admin(message): return await message('Вы (или я) не являетесь администратором!', attachment = f'photo-{bot.group_id}_457241328')
		await message('''Ключевые слова:
{title} - заголовок
{user} - пользователь
{name} - имя бота''')

	@bot.on.chat_message(text = 'set hello', command = True)
	@bot.on.chat_message(text = 'set hello <text>', command = True)
	async def hello_plus(message, text = '* Стандартное приветствие *'):
		if not await is_admin(message): return await message('Вы (или я) не являетесь администратором!', attachment = f'photo-{bot.group_id}_457241328')
		try: hello = text.format(title = 'title', user = 'user', name = 'name')
		except: await message('Неправильный формат')
		else:
			await lvl_class.add_text(text)
			await message('Приветствие полученно\n' + hello)
	
	@bot.on.chat_message(text = 'del hello', command = True)
	async def hello_del(message):
		if not await is_admin(message): return await message('Вы (или я) не являетесь администратором!', attachment = f'photo-{bot.group_id}_457241328')
		await lvl_class.del_text()
		await message('Приветствие удалено')
	
	@bot.on.chat_action('chat_invite_user')
	async def add_user(message):
		id1, id2 = message.from_id, message.action.member_id
		text = await lvl_class.hello_text()
		if not text: return
		await lvl_class.user(id1,id2)
		if id1 != id2:
			title = f"* Welcome to the club, buddy. *\nВас призвал(а): {lvl_class[id1]}"
			bot_name = (await bot.api.groups.getById(group_id = group_id))[0]['name']
			blank = text.format(title = title, user = lvl_class[id2], name = bot_name)
			photo = 457241337
		else:
			blank = f"Вернулся(ась) {lvl_class[id1]}."
			photo = 457241328
		await message(blank, attachment = f'photo-{bot.group_id}_{photo}')
	
	@bot.on.chat_action('chat_kick_user')
	async def remove_user(message):
		id2 = message.action.member_id
		if not await lvl_class.hello_text(): return
		await lvl_class.user(id2)
		if await is_admin(message): await message(f"{lvl_class[id2]} заебал(а) админа.", attachment = f'photo-{bot.group_id}_457241336')
		else: await message(f"{lvl_class[id2]} стал(а) натуралом(.", attachment = f'photo-{bot.group_id}_457241328')
	
	@bot.on.chat_action('chat_invite_user_by_link')
	async def add_user_link(message):
		id1 = message.from_id
		text = await lvl_class.hello_text()
		if not text: return
		await lvl_class.user(id1)
		title = f"* Welcome to the club, buddy. *\n* Вы попали в ловушку *"
		bot_name = (await vk.api_request('groups.getById', {'group_id': group_id}))[0]['name']
		await message(text.format(title = title, user = lvl_class[id1], name = bot_name), attachment = f'photo-{bot.group_id}_457241337')
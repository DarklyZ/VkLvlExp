from vk.types.message import Action

def load(dp, vk, group_id):
	
	@dp.message_handler(commands = ['hello'], count_args = 0, is_admin = True, in_chat = True)
	async def hello_help(message, data):
		await message.answer('''Ключевые слова:
{title} - заголовок
{user} - пользователь
{name} - имя бота''')
	
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
	
	return dp
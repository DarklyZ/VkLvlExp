from utils import InitParams

class ChatActionCommands(InitParams.Params):
	def __init__(self):
		@self.bot.on.chat_message(text = 'hello', command = True, is_admin = True)
		async def hello_help(message):
			await message('Ключевые слова:\n{title} - заголовок\n{user} - пользователь\n{name} - имя бота')

		@self.bot.on.chat_message(text = ['set hello <text>', 'set hello'], command = True, is_admin = True)
		async def hello_plus(message, text = '* Стандартное приветствие *'):
			try: hello = text.format(title = 'title', user = 'user', name = 'name')
			except: return await message('Неправильный формат')
			await self.lvl_class.update_text(text)
			await message('Приветствие полученно\n' + hello)
		
		@self.bot.on.chat_message(text = 'del hello', command = True, is_admin = True)
		async def hello_del(message):
			await self.lvl_class.update_text()
			await message('Приветствие удалено')
		
		@self.bot.on.chat_message(chat_action_rule = 'chat_invite_user', with_text = True)
		async def add_user(message, text):
			await self.lvl_class.user(id1 := message.from_id, id2 := message.action.member_id)
			if id1 != id2:
				title = f"* Welcome to the club, buddy. *\nВас призвал(а): {self.lvl_class[id1]}"
				bot_name = (await self.bot.api.groups.get_by_id(group_id = self.bot.group_id))[0].name
				blank = text.format(title = title, user = self.lvl_class[id2], name = bot_name)
				photo = 457241337
			else:
				blank = f"Вернулся(ась) {self.lvl_class[id1]}."
				photo = 457241328
			await message(blank, attachment = f'photo-{self.bot.group_id}_{photo}')
		
		@self.bot.on.chat_message(chat_action_rule = 'chat_kick_user', with_text = True, is_admin = True)
		async def remove_user(message, text):
			await self.lvl_class.user(id2 := message.action.member_id)
			await message(f"{self.lvl_class[id2]} заебал(а) админа.", attachment = f'photo-{self.bot.group_id}_457241336')
	
		@self.bot.on.chat_message(chat_action_rule = 'chat_kick_user', with_text = True, is_admin = False)
		async def remove_user(message, text):
			await self.lvl_class.user(id2 := message.action.member_id)
			await message(f"{self.lvl_class[id2]} стал(а) натуралом(.", attachment = f'photo-{self.bot.group_id}_457241328')
		
		@self.bot.on.chat_message(chat_action_rule = 'chat_invite_user_by_link', with_text = True)
		async def add_user_link(message, text):
			await self.lvl_class.user(id1 := message.from_id)
			title = f"* Welcome to the club, buddy. *\n* Вы попали в ловушку *"
			bot_name = (await self.bot.api.groups.get_by_id(group_id = self.bot.group_id))[0]['name']
			await message(text.format(title = title, user = self.lvl_class[id1], name = bot_name), attachment = f'photo-{self.bot.group_id}_457241337')
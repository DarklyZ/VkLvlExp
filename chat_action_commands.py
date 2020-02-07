from extra import IsAdmin, WithText
from vkbottle.rule import ChatActionRule
from lvls import LVL

def load(bot):
	lvl_class = LVL.get_current()
	
	@bot.on.chat_message(IsAdmin(True), text = 'hello', command = True)
	async def hello_help(message):
		await message('''Ключевые слова:
{title} - заголовок
{user} - пользователь
{name} - имя бота''')

	@bot.on.chat_message(IsAdmin(True), text = ['set hello <text>', 'set hello'], command = True)
	async def hello_plus(message, text = '* Стандартное приветствие *'):
		try: hello = text.format(title = 'title', user = 'user', name = 'name')
		except: await message('Неправильный формат')
		else:
			await lvl_class.add_text(text)
			await message('Приветствие полученно\n' + hello)
	
	@bot.on.chat_message(IsAdmin(True), text = 'del hello', command = True)
	async def hello_del(message):
		await lvl_class.del_text()
		await message('Приветствие удалено')
	
	@bot.on.chat_message(ChatActionRule('chat_invite_user'), WithText(True))
	async def add_user(message, text):
		id1, id2 = message.from_id, message.action.member_id
		await lvl_class.user(id1, id2)
		if id1 != id2:
			title = f"* Welcome to the club, buddy. *\nВас призвал(а): {lvl_class[id1]}"
			bot_name = (await bot.api.groups.getById(group_id = bot.group_id))[0]['name']
			blank = text.format(title = title, user = lvl_class[id2], name = bot_name)
			photo = 457241337
		else:
			blank = f"Вернулся(ась) {lvl_class[id1]}."
			photo = 457241328
		await message(blank, attachment = f'photo-{bot.group_id}_{photo}')
	
	@bot.on.chat_message(ChatActionRule('chat_kick_user'), WithText(True))
	async def remove_user(message, text):
		id2 = message.action.member_id
		await lvl_class.user(id2)
		if await IsAdmin(True).check(message): await message(f"{lvl_class[id2]} заебал(а) админа.", attachment = f'photo-{bot.group_id}_457241336')
		else: await message(f"{lvl_class[id2]} стал(а) натуралом(.", attachment = f'photo-{bot.group_id}_457241328')
	
	@bot.on.chat_message(ChatActionRule('chat_invite_user_by_link'), WithText(True))
	async def add_user_link(message, text):
		id1 = message.from_id
		await lvl_class.user(id1)
		title = f"* Welcome to the club, buddy. *\n* Вы попали в ловушку *"
		bot_name = (await bot.api.groups.getById(group_id = bot.group_id))[0]['name']
		await message(text.format(title = title, user = lvl_class[id1], name = bot_name), attachment = f'photo-{bot.group_id}_457241337')
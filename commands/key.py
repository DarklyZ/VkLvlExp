from utils import Data as data, custom_rules
from vkbottle.bot import BotLabeler

bl = BotLabeler(custom_rules = custom_rules)

@bl.chat_message(command = 'get key')
async def get_key(message):
	await data.lvl.get_key(message.from_id)
	try: await message.answer(user_id = message.from_id, message = 'Ключ: ' + data.lvl['KEY'])
	except: await message.answer("Разрешите отправку сообщений от сообщества Вам в лс")
	else: await message.answer("Ключ я отправила Вам в лс")

@bl.chat_message(command = 'reset key')
async def reset_key(message):
	await data.lvl.set_key(message.from_id)
	try: await message.answer(user_id = message.from_id, message = 'Ключ: ' + data.lvl['KEY'])
	except: await message.answer("Разрешите отправку сообщений от сообщества Вам в лс")
	else: await message.answer("Ключ я отправила Вам в лс")

@bl.chat_message(command = 'del key')
async def del_key(message):
	await data.lvl.set_key(message.from_id, set_null = True)
	await message.answer("Ваш ключ удалён")
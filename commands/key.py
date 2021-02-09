from utils import Data as data
from vkbottle.bot import BotLabeler

bl = BotLabeler()

@bl.chat_message(command = 'get key')
async def get_key(message):
	try: await message.answer(user_id = message.from_id, message = 'Ключ: ' + await data.lvl.get_key(message.from_id))
	except: await message.answer("Разрешите отправку сообщений от сообщества Вам в лс")
	else: await message.answer("Ключ я отправила Вам в лс")

@bl.chat_message(command = 'reset key')
async def reset_key(message):
	try: await message.answer(user_id = message.from_id, message = 'Ключ: ' + await data.lvl.set_key(message.from_id))
	except: await message.answer("Разрешите отправку сообщений от сообщества Вам в лс")
	else: await message.answer("Ключ я отправила Вам в лс")

@bl.chat_message(command = 'del key')
async def del_key(message):
	await data.lvl.set_key(message.from_id, set_null = True)
	await message.answer("Ваш ключ удалён")
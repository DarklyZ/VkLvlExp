from utils import Data as data
from utils.rules import custom_rules
from vkbottle.bot import BotLabeler
from random import choice
from os import getenv

bl = BotLabeler(custom_rules = custom_rules)

@bl.chat_message(regex = r'^f+$')
async def f_f(message):
	rand = choice((457241326,457241327,457241328,457241331,457241332,457241333,457241334,457241338,457241339))
	await message.answer("Пал боец\nСмертью храбрых", attachment = f'photo-{data.bot.callback.group_id}_{rand}')

@bl.chat_message(regex = r'^[^\?]*\?{3}$')
async def hm_(message):
	await message.answer(attachment = f'photo-{data.bot.callback.group_id}_457241329')

@bl.chat_message(regex = r'^[^\?]*\?{2}$')
async def h_(message):
	await message.answer(attachment = f'photo-{data.bot.callback.group_id}_457241330')

@bl.chat_message(regex = r'\bня\b')
async def nya(message):
	await message.answer(sticker_id = 9808)

@bl.chat_message(regex = r'смерт|суицид|умереть|гибну|окно')
async def olga(message):
	await message.answer(f"Вы написали:\n\"{message.text}\".\nЯ расценила это за попытку суицида.\n[id{await data.lvl.var('olga_id')}|#бля_Оля_живи!!!!!]")

@bl.chat_message(regex = r'\b(?:мирарукурин|мира|рару|руку|кури|рин|черемша)\b')
async def archi(message):
	await message.answer(sticker_id = 9805)
	await message.answer(f"[id{await data.lvl.var('archi_id')}|💬][id{message.from_id}|🃏]Ожидайте бана…")

@bl.chat_message(regex = r'\b(?:украин.{0,3})|(?:хохо?л.{0,2})\b')
async def uk(message):
	await message.ctx_api.messages.delete(
		delete_for_all = True, peer_id = message.peer_id, cmids = message.conversation_message_id
	)
def load(bot):
	from random import choice
	from lvls import LVL
	lvl_class = LVL.get_current()
	
	@bot.on.chat_message(regex = r'^f+$')
	async def f_f(message):
		rand = choice((457241326,457241327,457241328,457241331,457241332,457241333,457241334,457241338,457241339))
		await message('Пал боец\nСмертью храбрых', attachment = f'photo-{bot.group_id}_{rand}')
	
	@bot.on.chat_message(regex = r'^[^\?]*\?\?\?$')
	async def hm_(message):
		await message(attachment = f'photo-{bot.group_id}_457241329')
	
	@bot.on.chat_message(regex = r'^[^\?]*\?\?$')
	async def h_(message):
		await message(attachment = f'photo-{bot.group_id}_457241330')
	
	@bot.on.chat_message(regex = r'\bня\b')
	async def nya(message):
		await message(sticker_id = 9808)
	
	@bot.on.chat_message(regex = r'смерт|суицид|умереть|гибну|окно')
	async def olga(message):
		await message(f"Вы написали:\n\"{message.text}\".\nЯ расценила это за попытку суицида.\n[id{await lvl_class.getconst('olga_id')}|#бля_Оля_живи!!!!!]")
	
	@bot.on.chat_message(regex = r'\b(?:мирарукурин|мира|рару|руку|кури|рин)\b')
	async def archi(message):
		await message(sticker_id = 9805)
		await message(f"[id{await lvl_class.getconst('archi_id')}|💬][id{message.from_id}|🃏]Ожидайте бана…")

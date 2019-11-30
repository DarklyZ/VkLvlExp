from random import choice

def load(dp, group_id):
	
	@dp.message_handler(regex = r'^f+$', in_chat = True)
	async def f_f(message, data):
		rand = choice((457241326,457241327,457241328,457241331,457241332,457241333,457241334,457241338,457241339))
		await message.answer('Пал боец\nСмертью храбрых', attachment = f'photo-{group_id}_{rand}')
	
	@dp.message_handler(regex = r'^[^\?]*\?{3}$', in_chat = True)
	async def hm_(message, data):
		await message.answer('', attachment = f'photo-{group_id}_457241329')
	
	@dp.message_handler(regex = r'^[^\?]*\?{2}$', in_chat = True)
	async def h_(message, data):
		await message.answer('', attachment = f'photo-{group_id}_457241330')
	
	@dp.message_handler(regex = r'\bня\b', in_chat = True)
	async def nya(message, data):
		await message.answer('', sticker_id = 9808)
	
	@dp.message_handler(regex = r'смерт|суицид|умереть|гибну|окно', in_chat = True)
	async def olga(message, data):
		await message.answer(f"Вы написали:\n\"{message.text}\".\nЯ расценила это за попытку суицида.\n[id{await data['lvl'].getconst('olga_id')}|#бля_Оля_живи!!!!!]")
	
	@dp.message_handler(regex = r'\b(?:мирарукурин|мира|рару|руку|кури|рин)\b', in_chat = True)
	async def archi(message, data):
		await message.answer('', sticker_id = 9805)
		await message.answer(f"[id{await data['lvl'].getconst('archi_id')}|💬][id{message.from_id}|🃏]Ожидайте бана…")
	
	return dp
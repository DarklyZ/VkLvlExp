from utils import InitParams

class ShikimoriCommands(InitParams):
	def __init__(self):
		@self.bot.on.chat_message(text = ['ss <type:inc[animes,mangas,ranobe,characters,people]> <page:pos> <text>',
				'ss <type:inc[animes,mangas,ranobe,characters,people]> <text>'], command = True)
		async def shiki_search(message, type, text, page = 1):
			response = await self.shiki.search(type, text, page)
			if response:
				objs = [
					[
						f"{num + 1}) {item['russian'] or item['name']}",
						'Шики: ' + await self.shiki.get_shiki_short_link(item['url']),
						'Неко: ' + await self.shiki.get_neko_short_link(item['id']) if type == 'animes' else None
					]
					for num, item in enumerate(response)
				]
				text = '\n'.join('\n'.join(i for i in item if i) for item in objs)
				docs = await self.shiki.get_doc(item['image']['original'] for item in response)
				await message(text, attachment = ','.join(docs))
			else: await message('Не найдено')
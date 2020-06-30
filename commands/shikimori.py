from utils import InitParams

class ShikimoriCommands(InitParams):
	def load(self):
		@self.bot.on.chat_message(text = ['ss <type:inc[animes,mangas,ranobe,characters]> <page:pos> <text>',
				'ss <type:inc[animes,mangas,ranobe,characters]> <text>'], command = True)
		async def shiki_search(message, type, text, page = 1):
			response = (await self.shiki.search(type, text))[(page - 1) * 10 : (page - 1) * 10 + 10]
			if response:
				docs = await self.shiki.get_doc(item['image']['original'] for item in response)
				russian = '\n'.join(f"{num + 1}) {item['russian'] or item['name']}" for num, item in enumerate(response))
				await message(russian, attachment = ','.join(docs))
			else: await message('Не найдено')
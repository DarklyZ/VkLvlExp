from utils import InitParams

class ShikimoriCommands(InitParams):
	def load(self):
		@self.bot.on.chat_message(text = ['ss <type:inc[animes,mangas,ranobe,characters]> <page:pos> <text>',
				'ss <type:inc[animes,mangas,ranobe,characters]> <text>'], command = True)
		async def shiki_search(message, type, text, page = 1):
			response = await self.shiki.search(type, text)
			docs = await self.shiki.get_doc([item['image']['original'] for item in response], page)
			russian = '\n'.join(item['russian'] for item in response[(page - 1) * 10 : (page - 1) * 10 + 10])
			await message(russian or 'Не найдено', attachment = ','.join(docs))
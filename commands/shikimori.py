from utils import InitParams

class ShikimoriCommands(InitParams):
	def load(self):
		@self.bot.on.chat_message(text = ['ss <type:inc[animes,mangas,ranobe,characters]> <page:pos> <text>',
				'ss <type:inc[animes,mangas,ranobe,characters]> <text>'], command = True)
		async def _(message, type, text, page = 1):
			response = await self.shiki.search(text)
			docs = await self.shiki.get_doc([item['image']['original'] for item in response], page)
			await message('Не найдено' if not docs else None, attachment = ','.join(docs))
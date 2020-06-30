from utils import InitParams

class ShikimoriCommands(InitParams):
	def load(self):
		@self.bot.on.chat_message(text = ['ss <page:pos> <text>', 'ss <text>'], command = True)
		async def _(message, text, page = 1):
			response = await self.shiki.search(text)
			docs = await self.shiki.get_doc([item['image']['original'] for item in response], page)
			await message('Не найдено' if not docs else None, attachment = ','.join(docs))
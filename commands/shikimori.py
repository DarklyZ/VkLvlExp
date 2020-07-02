from utils import InitParams

class ShikimoriCommands(InitParams):
	def load(self):
		@self.bot.on.chat_message(text = ['ss <type:inc[animes,mangas,ranobe,characters,people]> <page:pos> <text>',
				'ss <type:inc[animes,mangas,ranobe,characters,people]> <text>'], command = True)
		async def shiki_search(message, type, text, page = 1):
			response = await self.shiki.search(type, text, page)
			if response:
				docs = await self.shiki.get_doc(item['image']['original'] for item in response)
				russian = '\n'.join([f"""{num + 1}) {item['russian'] or item['name']} {
						(await self.bot.api.utils.get_short_link('http://shikimori.one' + item['url'])).short_url
				}""" for num, item in enumerate(response)])
				await message(russian, attachment = ','.join(docs))
			else: await message('Не найдено')
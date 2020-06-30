from utils import InitParams

class ShikimoriCommands(InitParams):
	def load(self):

		@self.bot.on.chat_message(text = 'Акаме <text>')
		async def _(message, text):
			await self.shiki.search(text)
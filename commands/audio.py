from utils.init import InitParams

class AudioCommands(InitParams):
	def load(self):
		#-------------Зона тестирования-------------
		@self.bot.on.chat_message(text = 'test <text>', command = True)
		async def test(message, text):
			await message(attachment = await self.amessage.get_doc(text))
		#-------------Зона тестирования-------------

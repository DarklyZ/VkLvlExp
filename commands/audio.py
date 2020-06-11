def load(bot):
	from audio_message import get_audio_message
	amessage = get_audio_message()

	#-------------Зона тестирования-------------
	@bot.on.chat_message(text = 'test <text>', command = True)
	async def test(message, text):
		await message(attachment = await amessage.get_doc(text))
	#-------------Зона тестирования-------------

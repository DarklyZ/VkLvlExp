def load(bot, run):
	from asyncio import sleep
	from lvls import LVL
	lvl_class = LVL.get_current()

	def temp_new():
		temp = lvl_class.now
		#return temp.replace(day=temp.day + 8 - temp.weekday(), hour=0, minute=0, second=0)
		return temp.replace(minute = temp.minute + 20)

	@run
	async def async_top_loop():
		temp = temp_new()
		while not await sleep(5 * 60):
			if lvl_class.now < temp: continue
			print('Очистка')
			await lvl_class.temp_reset()
			temp = temp_new()

	@bot.on.chat_message(text = ['toplvl <one:pos> <two:pos>', 'toplvl'], command = True)
	async def toplvl_send(message, one = 1, two = 10):
		await message(await lvl_class.toplvl_size(one, two), disable_mentions = True)

	@bot.on.chat_message(text = ['toptemp <one:pos> <two:pos>', 'toptemp'], command = True)
	async def toplvl_send(message, one = 1, two = 10):
		await message(await lvl_class.toptemp_size(one, two), disable_mentions = True)

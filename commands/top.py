def load(bot, run):
	from asyncio import sleep
	from lvls import LVL
	from datetime import timedelta
	lvl_class = LVL.get_current()

	temp_new = lambda: lvl_class.now.replace(hour = 0, minute = 0, second = 0) + timedelta(days = 1)

	@run
	async def async_top_loop():
		temp = temp_new()
		while not await sleep(5 * 60):
			if lvl_class.now < temp: continue
			await lvl_class.temp_reset()
			temp = temp_new()

	@bot.on.chat_message(text = ['toplvl <one:pos> <two:pos>', 'toplvl'], command = True)
	async def toplvl_send(message, one = 1, two = 10):
		await message(await lvl_class.toplvl_size(one, two), disable_mentions = True)

	@bot.on.chat_message(text = ['toptemp <one:pos> <two:pos>', 'toptemp'], command = True)
	async def toptemp_send(message, one = 1, two = 10):
		await message(await lvl_class.toptemp_size(one, two), disable_mentions = True)

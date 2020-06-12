from init import InitCommands
from asyncio import sleep
from datetime import timedelta

class TopCommands(InitCommands):
	def load(self, run):
		temp_new = lambda: self.lvl_class.now.replace(hour = 0, minute = 0, second = 0) + timedelta(days = 1)

		@run
		async def async_top_loop():
			temp = temp_new()
			while not await sleep(5 * 60):
				if self.lvl_class.now < temp: continue
				await self.lvl_class.temp_reset()
				temp = temp_new()

		@self.bot.on.chat_message(text = ['toplvl <one:pos> <two:pos>', 'toplvl'], command = True)
		async def toplvl_send(message, one = 1, two = 10):
			await message(await self.lvl_class.toplvl_size(one, two), disable_mentions = True)

		@self.bot.on.chat_message(text = ['toptemp <one:pos> <two:pos>', 'toptemp'], command = True)
		async def toptemp_send(message, one = 1, two = 10):
			await message(await self.lvl_class.toptemp_size(one, two), disable_mentions = True)

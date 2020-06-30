from vkbottle.utils import ContextInstanceMixin
from utils import InitParams
from aiohttp import request

class ShikiApi(ContextInstanceMixin, InitParams):
	def __init__(self):
		self.set_current(self)

	async def search(self, text):
		async with request('GET', 'http://shikimori.one/api/animes/search', params = {'q' : text}) as response:
			print(await response.json())

def get_shiki():
	return ShikiApi.get_current()
from vkbottle.utils import ContextInstanceMixin
from utils import InitParams
from io import BytesIO
from aiohttp import request
from vkbottle import vkscript

class ShikiApi(ContextInstanceMixin, InitParams):
	def __init__(self):
		self.set_current(self)

	def __call__(self, peer_id):
		self.peer_id = peer_id

	async def search(self, text):
		async with request('GET', 'http://shikimori.one/api/animes/search', params = {'q' : text}) as response:
			return await response.json()

	async def get_doc(self, urls, page):
		server = await self.api.photos.get_messages_upload_server(peer_id = self.peer_id)
		saves = []
		for url in urls[(page - 1) * 10 : (page - 1) * 10 + 10]:
			async with request('GET', 'http://shikimori.one' + url) as response:
				with BytesIO(await response.read()) as bfile:
					bfile.name = '.jpg'
					async with request('POST', server.upload_url, data = {'photo': bfile}) as response:
						res = await response.json(content_type = 'text/html')
						saves.append(await self.api.photos.save_messages_photo(server = res['server'], photo = res['photo'], hash = res['hash']))
		return [f'photo{save[0].owner_id}_{save[0].id}' for save in saves]

def get_shiki():
	return ShikiApi.get_current()

from vkbottle.utils import ContextInstanceMixin
from utils import InitParams
from aiohttp import request
from io import BytesIO

class ThisWaifuDoesNotExist(ContextInstanceMixin, InitParams):
	url = 'https://www.thiswaifudoesnotexist.net/example-{id}.jpg'

	def __init__(self):
		self.set_current(self)

	def __call__(self, peer_id):
		self.peer_id = peer_id

	async def get_doc(self, id):
		server = await self.api.photos.get_messages_upload_server(peer_id = self.peer_id)
		async with request('GET', self.url.format(id = id)) as response:
			with BytesIO(await response.read()) as bfile:
				bfile.name = '.jpg'
				async with request('POST', server.upload_url, data = {'photo': bfile}) as response:
					res = await response.json(content_type = 'text/html')
					save = await self.api.photos.save_messages_photo(server = res['server'], photo = res['photo'], hash = res['hash'])
		return f'photo{save[0].owner_id}_{save[0].id}'

def get_twdne():
	return ThisWaifuDoesNotExist.get_current()
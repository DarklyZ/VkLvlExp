from . import Data
from asyncpg import connect

class LVLABC(dict, Data):
	def __init__(self, database_url):
		super().__init__()
		self.database_url = database_url

	def __call__(self, peer_id):
		self.clear()
		self.peer_id = peer_id
		return self

	async def run_connect(self):
		self.con = await connect(self.database_url, ssl = 'require')

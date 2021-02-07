from . import Data
from asyncpg import connect
from itertools import groupby

dict_boost = {1: 2, 3: 2, 5: 1, 7: 1}

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

	async def update_lvl(self, *ids, lvl = 0, exp = 0, boost = False, temp = False):
		await self.con.execute("update lvl set lvl = lvl + $1, exp = exp + $2, temp_exp = temp_exp + $3 where user_id = any($4) and peer_id = $5", lvl, exp, exp if temp else 0, ids, self.peer_id)

		if boost:
			boost_ids = {row['user_id']: dict_boost[row['row_number']]
					for row in await self.con.fetch("select row_number() over (order by temp_exp desc), user_id from lvl where temp_exp > 0 and peer_id = $1 limit 7", self.peer_id)
					if row['user_id'] in ids and row['row_number'] % 2 != 0}
			for key, group in groupby(boost_ids, lambda id: boost_ids[id]):
				await self.con.execute("update lvl set exp = exp + $1, temp_exp = temp_exp - $2 where user_id = any($3) and peer_id = $4", exp * key, round(exp * key / (key + 1)) if temp else 0, tuple(group), self.peer_id)

		for row in await self.con.fetch("select user_id, lvl, exp from lvl where (exp < 0 or lvl < 1 or exp >= lvl * 2000) and peer_id = $1", self.peer_id):
			row_lvl, row_exp = row['lvl'], row['exp']
			while row_exp >= row_lvl * 2000:
				row_exp -= row_lvl * 2000
				row_lvl += 1
			while row_exp < 0 and row_lvl > 0:
				row_lvl -= 1
				row_exp += row_lvl * 2000
			if row_lvl > 0: await self.con.execute("update lvl set lvl = $1, exp = $2 where user_id = $3 and peer_id = $4", row_lvl, row_exp, row['user_id'], self.peer_id)
			else: await self.con.execute("delete from lvl where user_id = $1 and peer_id = $2", row['user_id'], self.peer_id)

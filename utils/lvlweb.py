from .lvlabc import LVLabc

class LVL(LVLabc):
	async def get_lvl(self, *ids):
		self.update(
			response = [{'user_id': row['user_id'], 'lvl': row['lvl'], 'exp': row['exp']}
				for row in await self.con.fetch("select user_id, lvl, exp from lvl where user_id = any($1) and peer_id = $2 order by lvl desc, exp desc", ids, self.peer_id)]
		)

	async def get_top(self, x, y):
		try:
			ids = [row['user_id']
			       for row in await self.con.fetch("select user_id from lvl where peer_id = $1 order by lvl desc, exp desc limit $2 offset $3", self.peer_id, y - x + 1, x - 1)]
			await self.get_lvl(*ids)
		except Exception as e: self.update(response = [])
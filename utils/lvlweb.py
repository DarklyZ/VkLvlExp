from .lvlabc import LVLABC

class LVL(LVLABC):
	async def get_lvl(self, *ids):
		self.update(
			response = [{'user_id': row['user_id'], 'lvl': row['lvl'], 'exp': row['exp']}
				for row in await self.con.fetch("select user_id, lvl, exp from lvl where user_id = any($1) and peer_id = $2 order by lvl desc, exp desc", ids, self.peer_id)]
		)

	async def get_top(self, x, y):
		pass
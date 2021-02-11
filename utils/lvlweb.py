from .lvlabc import LVLabc

class LVL(LVLabc):
	async def join_key(self, key):
		if row := await self.con.fetchrow("select user_id, peer_id from lvl where key = $1", key):
			self(row['peer_id'])
			return row['user_id']

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
		except: self.update(response = [])

	async def get_status(self, chat_settings, id):
		is_admin = id == chat_settings.owner_id or id in chat_settings.admin_ids
		self.update(response = {'title': chat_settings.title, 'photo': chat_settings.photo.photo_50, 'status': 'admin' if is_admin else 'user'})
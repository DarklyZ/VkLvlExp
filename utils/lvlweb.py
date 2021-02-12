from .lvlabc import LVLabc

class LVL(LVLabc):
	async def join_key(self, key):
		if row := await self.con.fetchrow("select user_id, peer_id from lvl where key = $1", key):
			self(row['peer_id'])
			return row['user_id']

	async def get_user(self, *ids):
		nick = {row['user_id']: row['nick']
			for row in await self.con.fetch("select user_id, nick from lvl where user_id = any($1) and nick is not null and peer_id = $2", ids, self.peer_id)}
		usr = {user.id: [user.first_name + ' ' + user.last_name, user.photo_50]
		    for user in await self.bot.api.users.get(user_ids = str(ids)[1:-1], fields = 'photo_50')}
		self.update(
			response = [{'user_id': row['user_id'], 'name': usr[row['user_id']][0], 'nick': nick.get(row['user_id']),
			        'photo': usr[row['user_id']][1], 'lvl': row['lvl'], 'exp': row['exp']}
				for row in await self.con.fetch("select user_id, lvl, exp from lvl where user_id = any($1) and peer_id = $2 order by lvl desc, exp desc", ids, self.peer_id)]
		)

	async def get_top(self, x, y):
		try:
			ids = [row['user_id']
				for row in await self.con.fetch("select user_id from lvl where peer_id = $1 order by lvl desc, exp desc limit $2 offset $3", self.peer_id, y - x + 1, x - 1)]
			await self.get_user(*ids)
		except: self.update(response = [])

	async def get_status(self, chat_settings, id):
		is_admin = id == chat_settings.owner_id or id in chat_settings.admin_ids
		self.update(response = {'title': chat_settings.title, 'photo': chat_settings.photo.photo_50, 'status': 'admin' if is_admin else 'user'})
from asyncpg import connect
from datetime import datetime, tzinfo, timedelta
from vkbottle.utils import ContextInstanceMixin
from re import findall, I

bdate = lambda user, date : '🎂' if 'bdate' in user and user['bdate'].startswith(f"{date.day}.{date.month}") else ''

class timezone(tzinfo):
	utcoffset = lambda self, dt : timedelta(hours = 5)
	dst = lambda self, dt : timedelta()
	tzname = lambda self, dt : '+05:00'

class LVL(dict, ContextInstanceMixin):
	def __init__(self, database_url, api = None, loop = None, tz = None):
		super().__init__()

		self.tz = tz or timezone()

		if not api:
			from vkbottle.api import Api
			api = Api.get_current()

		self.api = api

		if not loop:
			from asyncio import get_event_loop
			loop = get_event_loop()

		loop.run_until_complete(self.connect_db(database_url))

		self.set_current(self)

	def __call__(self, peer_id):
		self.clear()
		self.peer_id = peer_id
	
	async def connect_db(self, database_url):
		self.con = await connect(database_url, ssl = 'require')

	async def close_db(self):
		await self.con.close()

	async def getconst(self, const):
		row = await self.con.fetchrow("select * from myconstants")
		return row[const]
		
	async def insert_lvl(self, *ids, lvl = 0, exp = 0):
		await self.con.execute("update lvl set lvl = lvl + $1, exp = exp + $2 where user_id = any($3) and peer_id = $4", lvl, exp, ids, self.peer_id)
		rows = await self.con.fetch("select user_id,lvl,exp from lvl where (exp < 0 or lvl < 1 or exp >= lvl * 2000) and peer_id = $1", self.peer_id)
		for row in rows:
			row_lvl, row_exp = row['lvl'], row['exp']
			while row_exp >= row_lvl * 2000:
				row_exp -= row_lvl * 2000
				row_lvl += 1
			while row_exp < 0 and row_lvl > 0:
				row_lvl -= 1
				row_exp += row_lvl * 2000
			if row_lvl > 0: await self.con.execute("update lvl set lvl = $1, exp = $2 where user_id = $3 and peer_id = $4", row_lvl, row_exp, row['user_id'], self.peer_id)
			else: await self.con.execute("delete from lvl where user_id = $1 and peer_id = $2", row['user_id'], self.peer_id)

	async def remove_exp(self, id, exp = 0):
		row = await self.con.fetchrow("select count(*) > 0 as bool from lvl where user_id = $1 and exp >= $2 and peer_id = $3", id, exp, self.peer_id)
		if not row['bool']: return
		await self.con.execute("update lvl set exp = exp - $1 where user_id = $2 and peer_id = $3", exp, id, self.peer_id)
		return True
	
	async def user(self, *ids):
		now = datetime.now(self.tz)
		rows = await self.con.fetch("select user_id, smile from lvl where user_id = any($1) and smile is not null and peer_id = $2", ids, self.peer_id)
		smile = {row['user_id'] : row['smile'] for row in rows}
		rows = await self.con.fetch("select user_id from lvl where peer_id = $1 order by lvl desc, exp desc limit 3", self.peer_id)
		top = {row['user_id'] : smile for row, smile in zip(rows, '🥇🥈🥉')}
		self.update({user['id'] : f"{top.get(user['id'], '')}{bdate(user, now)}{user['first_name']} {user['last_name'][:3]}{smile.get(user['id'], '')}" for user in await self.api.users.get(user_ids = ids, fields = 'bdate')})

	async def send(self, *ids):
		rows = await self.con.fetch("select user_id,lvl,exp from lvl where user_id = any($1) and peer_id = $2", ids, self.peer_id)
		lvl = {row['user_id'] : f"{row['lvl']}Ⓛ|{row['exp']}/{row['lvl'] * 2000}Ⓔ" for row in rows}
		await self.user(*ids)
		self.update({id : f"{self[id]}:{lvl.get(id, 'lvl:error')}" for id in ids})

	async def toplvl_size(self, x, y):
		try: rows = await self.con.fetch("select row_number() over (order by lvl desc,exp desc), user_id, lvl, exp from lvl where peer_id = $1 limit $2 offset $3", self.peer_id, y - x + 1, x - 1)
		except: return f'Я не могу отобразить {x} - {y}'
		else:
			await self.user(*(row['user_id'] for row in rows))
			return f"TOP {rows[0]['row_number']} - {rows[-1]['row_number']}\n" + '\n'.join(f"[id{row['user_id']}|{row['row_number']}]:{self[row['user_id']]}:{row['lvl']}Ⓛ|{row['exp']}Ⓔ" for row in rows)

	async def check_add_user(self, id):
		row = await self.con.fetchrow("select count(*) > 0 as bool from lvl where user_id = $1 and peer_id = $2", id, self.peer_id)
		if not row['bool']: await self.con.execute("insert into lvl (user_id, peer_id) values ($1, $2)", id, self.peer_id)

	async def setsmile(self, *ids, smile = None):
		await self.con.execute("update lvl set smile = $1 where user_id = any($2) and peer_id = $3", smile, ids, self.peer_id)

	async def add_text(self, text):
		if await self.hello_text(): await self.con.execute("update hello set text = $1 where peer_id = $2", text, self.peer_id)
		else: await self.con.execute("insert into hello (peer_id, text) values ($1, $2)", self.peer_id, text)

	async def del_text(self):
		await self.con.execute("delete from hello where peer_id = $1", self.peer_id,)

	async def hello_text(self):
		row = await self.con.fetchrow("select text from hello where peer_id = $1", self.peer_id)
		return row and row['text']

	async def atta(self, text='', attachments=[], id = None, negative = False):
		s = sum(3 if len(chars) >= 6 else 1 for chars in findall(r'\b[a-zа-яё]{3,}\b', text, I))
		count = s if s < 50 else 50
		for attachment in attachments:
			if attachment.type == 'photo':
				pixel = max(size.width * size.height for size in attachment.photo.sizes)
				count += round(pixel / (1280 * 720 / 70)) if pixel < 1280 * 720 else 70
			elif attachment.type == 'wall':
				count += 40
			elif attachment.type == 'doc' and attachment.doc.ext == 'gif':
				count += 20
			elif attachment.type == 'audio_message':
				count += round(attachment.audio_message.duration) if attachment.audio_message.duration < 25 else 25
			elif attachment.type == 'video':
				count += round(attachment.video.duration / 1.5) if attachment.video.duration < 60 * 2 else 80
			elif attachment.type == 'sticker':
				count += 10
			elif attachment.type == 'audio':
				count += round(attachment.audio.duration / 3) if attachment.audio.duration < 60 * 3 else 60
		if id and count: await self.insert_lvl(id, exp = count if not negative else -count)
		return count
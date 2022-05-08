from . import Data
from asyncpg import connect
from itertools import groupby
from datetime import datetime, tzinfo, timedelta
from string import ascii_letters
from random import choice
from asyncio import sleep
from re import split, I

class timezone(tzinfo):
	utcoffset = lambda self, dt: timedelta(hours = 5)
	dst = lambda self, dt: timedelta()
	tzname = lambda self, dt: '+05:00'

tz = timezone()

def getcake(bdate):
	if isinstance(bdate, str):
		bdate, date = datetime.strptime(bdate, '%d.%m' if bdate.count('.') == 1 else '%d.%m.%Y'), datetime.now(tz)
		return '🎂' if bdate.day == date.day and bdate.month == date.month else ''
	else: return ''

def getprice(slcount, lvl):
	if slcount == 0: return 120
	elif (price := round((1.1 ** slcount - 1) * 1e4)) < (maxexp := lvl * 2000 - 50):
		return price
	else: return maxexp

get = lambda dict, key: dict.get(key, '')
getpercent = lambda slcounts: percent if (percent := 5 * slcounts + 5) < 50 else 50
dict_boost = {1: 2, 3: 2, 5: 1, 7: 1}
dict_top = {1: '🥇', 2: '🥈', 3: '🥉'}
dict_topboost = {1: '❸', 3: '❸', 5: '❷', 7: '❷'}

class LVL(dict, Data):
	def __init__(self, database_url):
		super().__init__()
		self.database_url = database_url

	def __call__(self, peer_id):
		self.clear()
		self.peer_id = peer_id

	async def var(self, n, v = None):
		if not v: return (await self.con.fetchrow(f"select {n} from variables"))[n]
		else: await self.con.execute(f"update variables set {n} = $1", v)

	# RUN

	async def get_temp(self, method):
		if method == 'read':
			if temp := await self.var('update_date'):
				return datetime.fromtimestamp(temp).replace(tzinfo = tz)
			else: return await self.get_temp('write')
		elif method == 'write':
			temp = datetime.now(tz).replace(hour = 0, minute = 0, second = 0) + timedelta(days = 1)
			await self.var('update_date', temp.timestamp())
			return temp

	async def run_connect(self, run_top = False):
		self.con = await connect(self.database_url, ssl = 'require')

		if run_top:
			temp = await self.get_temp('read')
			while not await sleep(60):
				if datetime.now(tz) < temp: continue
				await self.con.execute("update lvl set temp_exp = 0")
				temp = await self.get_temp('write')

	# ALL

	async def update_lvl(self, *ids, lvl = 0, exp = 0, boost = False, temp = False, slave = False):
		await self.con.execute("update lvl set lvl = lvl + $1, exp = exp + $2, temp_exp = temp_exp + $3 where user_id = any($4) and peer_id = $5", lvl, exp, exp if temp else 0, ids, self.peer_id)

		if boost:
			boost_ids = {row['user_id']: dict_boost[row['row_number']]
				for row in await self.con.fetch("select row_number() over (order by temp_exp desc), user_id from lvl where temp_exp > 0 and peer_id = $1 limit 7", self.peer_id)
				if row['user_id'] in ids and row['row_number'] % 2 != 0}
			for key, group in groupby(boost_ids, lambda id: boost_ids[id]):
				await self.con.execute("update lvl set exp = exp + $1, temp_exp = temp_exp - $2 where user_id = any($3) and peer_id = $4", exp * key, round(exp * key / (key + 1)) if temp else 0, tuple(group), self.peer_id)

		if slave:
			for row in await self.con.fetch("select master, slcount from lvl where user_id = any($1) and work is not null and peer_id = $2", ids, self.peer_id):
				await self.con.execute("update lvl set exp = exp + $1 where user_id = $2 and peer_id = $3", round(exp * getpercent(row['slcount']) / 100), row['master'], self.peer_id)

		for row in await self.con.fetch("select user_id, lvl, exp from lvl where (exp < 0 or lvl < 1 or exp >= lvl * 2000) and peer_id = $1", self.peer_id):
			row_lvl, row_exp = row['lvl'], row['exp']
			while row_exp >= row_lvl * 2000:
				row_exp -= row_lvl * 2000
				row_lvl += 1
			while row_exp < 0 and row_lvl > 0:
				row_lvl -= 1
				row_exp += row_lvl * 2000
			if row_lvl > 0: await self.con.execute("update lvl set lvl = $1, exp = $2, master = null, work = null where user_id = $3 and peer_id = $4", row_lvl, row_exp, row['user_id'], self.peer_id)
			else: await self.con.execute("delete from lvl where user_id = $1 and peer_id = $2", row['user_id'], self.peer_id)

	async def remove_exp(self, id, exp = 0):
		max_exp, = await self.con.fetchrow("select exp from lvl where user_id = $1 and peer_id = $2", id, self.peer_id)
		assert max_exp >= exp, f"Не хватает {exp - max_exp} exp"
		await self.update_lvl(id, exp = -exp)

	async def update_nick(self, *ids, nick = None):
		await self.con.execute("update lvl set nick = $1 where user_id = any($2) and peer_id = $3", nick, ids, self.peer_id)

	async def update_text(self, text = None):
		if text and await self.con.execute("update hello set text = $1 where peer_id = $2", text, self.peer_id) == 'UPDATE 0':
			await self.con.execute("insert into hello (peer_id, text) values ($1, $2)", self.peer_id, text)
		else: await self.con.execute("delete from hello where peer_id = $1", self.peer_id)

	async def sync_users(self, *users):
		await self.con.execute("delete from lvl where user_id != all($1) and peer_id = $2", users, self.peer_id)

	async def slave_buy(self, id, slave):
		lvl, master, slcount = await self.con.fetchrow("select lvl, master, slcount from lvl where user_id = $1 and peer_id = $2", slave, self.peer_id)
		master_id, = await self.con.fetchrow("select master from lvl where user_id = $1 and peer_id = $2", id, self.peer_id)
		assert id != slave and id != master and slave != master_id, "Нельзя купить себя, своего раба или своего хозяина"

		await self.remove_exp(id, exp := getprice(slcount, lvl))
		if master: await self.update_lvl(master, exp = exp)
		await self.con.execute("update lvl set master = $1, slcount = slcount + 1, work = null where user_id = $2 and peer_id = $3", id, slave, self.peer_id)
		return master, exp

	async def slave_work(self, id, slave, work, slave_name = None):
		execute = await self.con.execute("update lvl set work = $1 where user_id = $2 and master = $3 and peer_id = $4", work, slave, id, self.peer_id)
		assert execute != 'UPDATE 0', f"Вы не можете сменить работу у {slave_name}"

	# BOT

	async def check_add_user(self, id):
		if (await self.con.fetchrow("select count(user_id) = 0 as bool from lvl where user_id = $1 and peer_id = $2", id, self.peer_id))['bool']:
			await self.con.execute("insert into lvl (user_id, peer_id) values ($1, $2)", id, self.peer_id)

	async def user(self, *ids):
		nick = {row['user_id']: row['nick']
			for row in await self.con.fetch("select user_id, nick from lvl where user_id = any($1) and nick is not null and peer_id = $2", ids, self.peer_id)}
		top = {row['user_id']: dict_top[row['row_number']]
			for row in await self.con.fetch("select row_number() over (order by lvl desc, exp desc), user_id from lvl where peer_id = $1 limit 3", self.peer_id)}
		topboost = {row['user_id']: dict_topboost[row['row_number']]
			for row in await self.con.fetch("select row_number() over (order by temp_exp desc), user_id from lvl where temp_exp > 0 and peer_id = $1 limit 7", self.peer_id)
			if row['row_number'] % 2 != 0}
		for user in await self.bot.api.users.get(user_ids = ','.join(map(str, ids)), fields = 'bdate'):
			self[user.id] = f"{get(top, user.id)}{get(topboost, user.id)}{getcake(user.bdate)}{nick.get(user.id) or user.first_name + ' ' + user.last_name[:3]}"

	async def send(self, *ids):
		await self.user(*ids)
		for row in await self.con.fetch("select user_id, lvl, exp, slcount, work from lvl where user_id = any($1) and peer_id = $2", ids, self.peer_id):
			self[row['user_id']] += f":{row['lvl']}Ⓛ|{row['exp']}/{row['lvl'] * 2000}Ⓔ:Ⓟ{getprice(row['slcount'], row['lvl'])}Ⓔ" + \
				(f"->{getpercent(row['slcount'])}%" if row['work'] else '')

	async def send_work(self, *ids):
		await self.user(*{row['master']
			for row in await self.con.fetch("select master from lvl where user_id = any($1) and master is not null and peer_id = $2", ids, self.peer_id)})
		masters = self.copy()
		await self.send(*ids)
		for row in await self.con.fetch("select user_id, master, work from lvl where user_id = any($1) and peer_id = $2", ids, self.peer_id):
			if row['master'] in masters: self[row['user_id']] += f"\nⓂ:{masters[row['master']]}:Ⓦ:{row['work'] or '-'}"

	async def slaves_by(self, id):
		fetch = await self.con.fetch("select user_id, work from lvl where master = $1 and peer_id = $2", id, self.peer_id)
		await self.send(*{row['user_id'] for row in fetch})
		self['SLAVES'] = '\n'.join((f"На работе {key}:\n" if key else "Без работы:\n") + '\n'.join(self[row['user_id']] for row in group) for key, group in groupby(fetch, lambda row: row['work']))

	async def set_key(self, id, set_null = False):
		async def get_key(count):
			key = ''.join(choice(ascii_letters) for _ in range(count))
			if (await self.con.fetchrow("select count(key) = 0 as bool from lvl where key = $1", key))['bool']:
				return key
			else: return await get_key(count)

		if not set_null:
			self['KEY'] = await get_key(10)
			await self.con.execute("update lvl set key = $1 where user_id = $2 and peer_id = $3", self['KEY'], id, self.peer_id)
		else: await self.con.execute("update lvl set key = null where user_id = $1 and peer_id = $2", id, self.peer_id)

	async def get_key(self, id):
		self['KEY'] = (await self.con.fetchrow("select key from lvl where user_id = $1 and peer_id = $2", id, self.peer_id))['key']
		if not self['KEY']: await self.set_key(id)

	async def hello_text(self):
		if row := await self.con.fetchrow("select text from hello where peer_id = $1", self.peer_id):
			self['HELLO'] = row['text']

	async def toplvl_size(self, x, y):
		assert x <= y, f"Я не могу отобразить {x} - {y}"

		rows = await self.con.fetch("select row_number() over (order by lvl desc, exp desc), user_id, lvl, exp from lvl where peer_id = $1 limit $2 offset $3", self.peer_id, y - x + 1, x - 1)
		assert rows, "TOPLVL пустой"

		await self.user(*{row['user_id'] for row in rows})
		self['TOPLVL'] = f"TOP {rows[0]['row_number']} - {rows[-1]['row_number']}\n" + '\n'.join(f"[id{row['user_id']}|{row['row_number']}]:{self[row['user_id']]}:{row['lvl']}Ⓛ|{row['exp']}Ⓔ" for row in rows)

	async def toptemp_size(self, x, y):
		assert x <= y, f"Я не могу отобразить {x} - {y}"

		rows = await self.con.fetch("select row_number() over (order by temp_exp desc), user_id, temp_exp from lvl where temp_exp > 0 and peer_id = $1 limit $2 offset $3", self.peer_id, y - x + 1, x - 1)
		assert rows, "TOPTEMP пустой"

		await self.user(*{row['user_id'] for row in rows})
		self['TOPTEMP'] = f"TOPTEMP {rows[0]['row_number']} - {rows[-1]['row_number']}\n" + '\n'.join(f"[id{row['user_id']}|{row['row_number']}]:{self[row['user_id']]}:{row['temp_exp']}ⓉⒺ" for row in rows)

	@classmethod
	async def atta(cls, text = '', attachments = [], negative = False, return_errors = False):
		if text:
			dict_errors = {change['word']: change['s'] for change in await cls.speller.spell(text)}
			s = sum(3 if len(chars) >= 6 else 1 for chars in split(r'[^a-zа-яё]+', text, flags = I) if len(chars) >= 3 and chars not in dict_errors)
			count = s if s < 50 else 50
		else:
			count, dict_errors = 0, {}

		for attachment in attachments:
			match attachment.type.value:
				case 'photo':
					pixel = max(size.width * size.height for size in attachment.photo.sizes)
					count += round(pixel * 50 / (1280 * 720)) if pixel < 1280 * 720 else 50
				case 'wall':
					count += await cls.atta(attachment.wall.text, attachment.wall.attachments or [])
				case 'wall_reply':
					count += await cls.atta(attachment.wall_reply.text, attachment.wall_reply.attachments or [])
				case 'audio_message':
					count += attachment.audio_message.duration if attachment.audio_message.duration < 25 else 25
				case 'video':
					count += round(attachment.video.duration * 80 / 30) if attachment.video.duration < 30 else 80
				case 'audio':
					count += round(attachment.audio.duration * 60 / 180) if attachment.audio.duration < 180 else 60
				case 'doc' if attachment.doc.ext == 'gif': count += 20
				case 'sticker': count += 10

		count *= -1 if negative else 1
		return (count, dict_errors) if return_errors else count

	# WEB

	async def join_key(self, key):
		if row := await self.con.fetchrow("select user_id, peer_id from lvl where key = $1", key):
			self(row['peer_id'])
			return row['user_id']

	async def get_user(self, *ids):
		nick = {row['user_id']: row['nick']
			for row in await self.con.fetch("select user_id, nick from lvl where user_id = any($1) and nick is not null and peer_id = $2", ids, self.peer_id)}
		usr = {user.id: [user.first_name + ' ' + user.last_name, user.photo_50]
		    for user in await self.bot.api.users.get(user_ids = ','.join(str(id) for id in ids), fields = 'photo_50')}
		self['response'] = [{'user_id': row['user_id'], 'name': usr[row['user_id']][0], 'nick': nick.get(row['user_id']),
				'photo': usr[row['user_id']][1], 'lvl': row['lvl'], 'exp': row['exp']}
			for row in await self.con.fetch("select user_id, lvl, exp from lvl where user_id = any($1) and peer_id = $2 order by lvl desc, exp desc", ids, self.peer_id)]

	async def get_top(self, x, y):
		try:
			ids = [row['user_id']
				for row in await self.con.fetch("select user_id from lvl where peer_id = $1 order by lvl desc, exp desc limit $2 offset $3", self.peer_id, y - x + 1, x - 1)]
			await self.get_user(*ids)
		except: self['response'] = []

	async def get_status(self, chat_settings, id):
		is_admin = id == chat_settings.owner_id or id in chat_settings.admin_ids
		self['response'] = {'title': chat_settings.title, 'photo': chat_settings.photo.photo_50, 'status': 'admin' if is_admin else 'user'}

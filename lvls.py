from psycopg2 import connect
from psycopg2.extras import DictCursor
from os import getenv

con = connect(getenv('DATABASE_URL'), sslmode='require')
cur = con.cursor(cursor_factory = DictCursor)
con.autocommit = True

class LVL(dict):
	def __init__(self, vk):
		super().__init__()
		self.vk = vk

	def __call__(self, peer_id):
		self.clear()
		self.peer_id = peer_id
		return self
		
	def insert_lvl(self,  *ids, lvl = 0, exp = 0):
		cur.execute("update lvl set lvl = lvl + %s, exp = exp + %s where user_id in %s and peer_id = %s",(lvl, exp, ids, self.peer_id))
		cur.execute("select user_id,lvl,exp from lvl where (exp < 0 or lvl < 1 or exp >= lvl * 2000) and peer_id = %s", (self.peer_id,))
		for row in cur.fetchall():
			while row['exp'] >= row['lvl'] * 2000:
				row['exp'] -= row['lvl'] * 2000
				row['lvl'] += 1
			while row['exp'] < 0 and row['lvl'] > 0:
				row['lvl'] -= 1
				row['exp'] += row['lvl'] * 2000
			if row['lvl'] > 0: cur.execute("update lvl set lvl = %s, exp = %s where user_id = %s and peer_id = %s", (row['lvl'], row['exp'], row['user_id'], self.peer_id))
			else: cur.execute("delete from lvl where user_id = %s and peer_id = %s",(row['user_id'], self.peer_id))

	def remove_exp(self, id, exp = 0):
		cur.execute("select count(*) > 0 as bool from lvl where user_id = %s and exp >= %s and peer_id = %s",(id, exp, self.peer_id))
		if cur.fetchone()['bool']:
			cur.execute("update lvl set exp = exp - %s where user_id = %s and peer_id = %s",(exp, id, self.peer_id))
			return True
		else: return False

	async def user(self, *ids):
		cur.execute("select user_id, smile from lvl where user_id in %s and smile is not null and peer_id = %s", (ids, self.peer_id))
		smile = {row['user_id'] : row['smile'] for row in cur.fetchall()}
		cur.execute("select user_id from lvl where peer_id = %s order by lvl desc, exp desc limit 3", (self.peer_id,))
		top = {row['user_id'] : smile for row, smile in zip(cur.fetchall(), ('🥇', '🥈', '🥉'))}
		self.update({user['id'] : f"{top.get(user['id'], '')}{user['first_name']} {user['last_name'][:3]}{smile.get(user['id'], '')}" for user in await self.vk.api_request('users.get', {'user_ids' : str(ids)[1:-1]})})

	async def send(self, *ids):
		cur.execute("select user_id,lvl,exp from lvl where user_id in %s and peer_id = %s", (ids, self.peer_id))
		lvl = {row['user_id'] : f"{row['lvl']}Ⓛ|{row['exp']}/{row['lvl'] * 2000}Ⓔ" for row in cur.fetchall()}
		await self.user(*ids)
		self.update({id : f"{self[id]}:{lvl.get(id, 'lvl:error')}" for id in ids})

	async def toplvl_size(self, x, y):
		try: cur.execute("select row_number() over (order by lvl desc,exp desc),user_id,lvl,exp from lvl where peer_id = %s limit %s offset %s", (self.peer_id, y - x + 1, x - 1))
		except: return f'Я не могу отобразить {x} - {y}'
		else:
			rows = cur.fetchall()
			await self.user(*(row['user_id'] for row in rows))
			return f"TOP {rows[0]['row_number']} - {rows[-1]['row_number']}\n" + '\n'.join(f"[id{row['user_id']}|{row['row_number']}]:{self[row['user_id']]}:{row['lvl']}Ⓛ|{row['exp']}Ⓔ" for row in rows)

	def check_user(self, id):
		cur.execute("select count(*) > 0 as bool from lvl where user_id = %s and peer_id = %s", (id, self.peer_id))
		return cur.fetchone()['bool']

	def add_user(self, id):
		cur.execute("insert into lvl (user_id, peer_id) values (%s, %s)", (id, self.peer_id))

	def setsmile(self, *ids, smile = None):
		cur.execute("update lvl set smile = %s where user_id in %s and peer_id = %s", (smile, ids, self.peer_id))

	def add_text(self, text):
		if self.hello_text(): cur.execute("update hello set text = %s where peer_id = %s", (text, self.peer_id))
		else: cur.execute("insert into hello (peer_id, text) values (%s, %s)", (self.peer_id, text))

	def del_text(self):
		cur.execute("delete from hello where peer_id = %s", (self.peer_id,))

	def hello_text(self):
		cur.execute("select text from hello where peer_id = %s", (self.peer_id,))
		return cur.fetchone().get('text')
		
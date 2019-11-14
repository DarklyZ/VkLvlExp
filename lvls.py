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
		cur.execute("UPDATE LVL SET LVL = LVL + %s, EXP = EXP + %s WHERE USER_ID in %s and PEER_ID = %s",(lvl, exp, ids, self.peer_id))
		cur.execute("SELECT USER_ID,LVL,EXP FROM LVL WHERE (EXP < 0 or LVL < 1 or EXP >= LVL * 2000) and PEER_ID = %s", (self.peer_id,))
		for row in cur.fetchall():
			while row['exp'] >= row['lvl'] * 2000:
				row['exp'] -= row['lvl'] * 2000
				row['lvl'] += 1
			while row['exp'] < 0 and row['lvl'] > 0:
				row['lvl'] -= 1
				row['exp'] += row['lvl'] * 2000
			if row['lvl'] > 0: cur.execute("UPDATE LVL SET LVL = %s, EXP = %s WHERE USER_ID = %s and PEER_ID = %s", (row['lvl'], row['exp'], row['user_id'], self.peer_id))
			else: cur.execute("DELETE FROM LVL WHERE USER_ID = %s and PEER_ID = %s",(row['user_id'], self.peer_id))

	def remove_exp(self, id, exp = 0):
		cur.execute("SELECT TRUE FROM LVL WHERE USER_ID = %s and EXP >= %s and PEER_ID = %s",(id, exp, self.peer_id))
		if cur.fetchone().get('bool'):
			cur.execute("UPDATE LVL SET EXP = EXP - %s WHERE USER_ID = %s and PEER_ID = %s",(exp, id, self.peer_id))
			return True
		else: return False

	async def user(self, *ids):
		cur.execute("SELECT USER_ID, SMILE FROM LVL WHERE USER_ID in %s and SMILE IS NOT NULL and PEER_ID = %s", (ids, self.peer_id))
		smile = {row['user_id'] : row['smile'] for row in cur.fetchall()}
		cur.execute("SELECT USER_ID FROM LVL WHERE PEER_ID = %s ORDER BY LVL DESC, EXP DESC LIMIT 3", (self.peer_id,))
		top = {row['user_id'] : smile for row, smile in zip(cur.fetchall(), ('🥇', '🥈', '🥉'))}
		self.update({user['id'] : f"{top.get(user['id'], '')}{user['first_name']} {user['last_name'][:3]}{smile.get(user['id'], '')}" for user in await self.vk.api_request('users.get', {'user_ids' : str(ids)[1:-1]})})

	async def send(self, *ids):
		cur.execute("SELECT USER_ID,LVL,EXP FROM LVL WHERE USER_ID in %s and PEER_ID = %s", (ids, self.peer_id))
		lvl = {row['user_id'] : f"{row['lvl']}Ⓛ|{row['exp']}/{row['lvl'] * 2000}Ⓔ" for row in cur.fetchall()}
		await self.user(*ids)
		self.update({id : f"{self[id]}:{lvl.get(id, 'lvl:error')}" for id in ids})

	async def toplvl_size(self, x, y):
		try: cur.execute("SELECT row_number() OVER (ORDER BY LVL DESC,EXP DESC),USER_ID,LVL,EXP FROM LVL WHERE PEER_ID = %s LIMIT %s OFFSET %s", (self.peer_id, y - x + 1, x - 1))
		except: return f'Я не могу отобразить {x} - {y}'
		else:
			rows = cur.fetchall()
			await self.user(*(row['user_id'] for row in rows))
			return f"TOP {rows[0]['row_number']} - {rows[-1]['row_number']}\n" + '\n'.join(f"[id{row['user_id']}|{row['row_number']}]:{self[row['user_id']]}:{row['lvl']}Ⓛ|{row['exp']}Ⓔ" for row in rows)

	def check(self, id):
		cur.execute("SELECT TRUE FROM LVL WHERE USER_ID = %s and PEER_ID = %s", (id, self.peer_id))
		return cur.fetchone().get('bool')

	def add_user(self, id):
		cur.execute("INSERT INTO LVL (USER_ID, PEER_ID) VALUES (%s, %s)", (id, self.peer_id))

	def setsmile(self, *ids, smile = None):
		cur.execute("UPDATE LVL SET SMILE = %s WHERE USER_ID in %s and PEER_ID = %s", (smile, ids, self.peer_id))

	def add_text(self, text):
		if self.hello_text(): cur.execute("UPDATE HELLO SET TEXT = %s WHERE PEER_ID = %s", (text, self.peer_id))
		else: cur.execute("INSERT INTO HELLO (PEER_ID, TEXT) VALUES (%s, %s)", (self.peer_id, text))

	def del_text(self):
		cur.execute("DELETE FROM HELLO WHERE PEER_ID = %s", (self.peer_id,))

	def hello_text(self):
		cur.execute("SELECT TEXT FROM HELLO WHERE PEER_ID = %s", (self.peer_id,))
		return cur.fetchone().get('text')
		
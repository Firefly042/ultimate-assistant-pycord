import os
import asyncio
import asyncpg as pg
import asyncpg.exceptions as pgexceptions
from sshtunnel import SSHTunnelForwarder

from utils import utils


class ShowcaseDBConnection:
	def __new__(cls):
		if not hasattr(cls, 'instance'):
			cls.instance = super(ShowcaseDBConnection, cls).__new__(cls)
		return cls.instance

	def __init__(self):
		self.ssh, self.pool = asyncio.get_event_loop().run_until_complete(self.connect())

		# Cache banned users
		self.banned_users = asyncio.get_event_loop().run_until_complete(self.get_banned_users())
		self.banned_users = [str(user["authorid"]) for user in self.banned_users]

		self.banned_list = ", ".join(self.banned_users)


	async def connect(self):
		SSH_HOST = os.getenv("SSH_HOST")
		SSH_USER = os.getenv("SSH_USER")
		SSH_KEY = os.getenv("SSH_KEY")
		DB_HOST = os.getenv("DB_HOST")
		DB_USER = os.getenv("DB_USER")
		DB_PASSWORD = os.getenv("DB_PASSWORD")
		DB_NAME = "showcase"

		ssh = SSHTunnelForwarder(
			(SSH_HOST, 22),
			ssh_username=SSH_USER,
			ssh_private_key=SSH_KEY,
			remote_bind_address=(DB_HOST, 5432))
		ssh.start()

		pool = await pg.create_pool(
			host="localhost",
			port=ssh.local_bind_port,
			user=DB_USER,
			password=DB_PASSWORD,
			database=DB_NAME,
			command_timeout=15,
			max_inactive_connection_lifetime=1800)

		print("Connected to showcase database")
		return ssh, pool


	async def disconnect(self):
		await self.pool.close()
		self.ssh.close()
		print("Closed showcase db and ssh connections")


# ------------------------------------------------------------------------
# Functions
# ------------------------------------------------------------------------
	async def add_character(self, author_id, char_id, name, surname, hex_color, description, image_url, image_credit):
		async with self.pool.acquire() as conn:
			await conn.execute("INSERT INTO characters (authorid, charid, name, surname, hexcolor, description, imageurl, imagecredit) VALUES($1, $2, $3, $4, $5, $6, $7, $8);", author_id, char_id, name, surname, hex_color, description, image_url, image_credit)


	async def edit_character(self, author_id, char_id, field_to_change, new_value):
		async with self.pool.acquire() as conn:
			try:
				rowcount = await conn.execute(f"UPDATE characters set {field_to_change} = $1 WHERE authorid = $2 AND charid = $3;", new_value, author_id, char_id)
			except pgexceptions.DataError:
				return False

			return (int(rowcount[7:]) > 0)


	async def remove_character(self, author_id, char_id):
		async with self.pool.acquire() as conn:
			try:
				rowcount = await conn.execute("DELETE from characters WHERE authorid = $1 AND charid = $2;", author_id, char_id)
			except pgexceptions.DataError:
				return False

			return (int(rowcount[7:]) > 0)


	async def dev_remove_character(self, char_id):
		async with self.pool.acquire() as conn:
			 await conn.execute("DELETE from characters WHERE charid = $1;", char_id)


	async def get_random_chars(self, amount):
		async with self.pool.acquire() as conn:
			 data = await conn.fetch(f"SELECT * FROM characters WHERE authorid NOT IN ({self.banned_list}) AND approved ORDER BY random() LIMIT {amount};")
			 return data


	async def get_char(self, char_id):
		async with self.pool.acquire() as conn:
			try:
				data = await conn.fetchrow("SELECT * FROM characters WHERE charid = $1;", char_id)
				return data
			except pgexceptions.DataError:
				return None


	async def get_user_chars(self, author_id):
		async with self.pool.acquire() as conn:
			try:
				data = await conn.fetch("SELECT * FROM characters WHERE authorid = $1;", author_id)
				return data
			except pgexceptions.DataError:
				return []


	async def get_user_approved_chars(self, author_id):
		async with self.pool.acquire() as conn:
			try:
				data = await conn.fetch("SELECT * FROM characters WHERE authorid = $1 and approved", author_id)
				return data
			except pgexceptions.DataError:
				return []


	async def get_banned_users(self):
		async with self.pool.acquire() as conn:
			data = await conn.fetch("SELECT authorid FROM banned_users;")
			return data


	def get_banned_users_cache(self):
		return self.banned_users


	async def add_banned_user(self, user_id):
		# Add to cache
		self.banned_users.append(str(user_id))
		self.banned_list = ", ".join(self.banned_users)
		async with self.pool.acquire() as conn:
			await conn.execute("INSERT INTO banned_users VALUES($1);", user_id)


	async def remove_banned_user(self, user_id):
		self.banned_users.remove(str(user_id))
		self.banned_list = ", ".join(self.banned_users)
		async with self.pool.acquire() as conn:
			await conn.execute("DELETE FROM banned_users WHERE authorid = $1;", user_id)


	async def flag_character(self, char_id, flag):
		async with self.pool.acquire() as conn:
			await conn.execute("UPDATE characters SET approved = $1 WHERE charid = $2;", flag, char_id)


	async def fuzzy_search(self, name, surname):
		async with self.pool.acquire() as conn:
			if (name and surname):
				data = await conn.fetch(f"SELECT * FROM characters WHERE authorid NOT IN ({self.banned_list}) AND approved AND levenshtein($1, name) <= 2 AND levenshtein($2, surname) <=2;", name, surname)
			else:
				data = await conn.fetch(f"SELECT * FROM characters WHERE authorid NOT IN ({self.banned_list}) AND approved AND (levenshtein($1, name) <= 2 OR levenshtein($2, surname) <=2);", name, surname)

			return data


	async def exact_search(self, name, surname):
		async with self.pool.acquire() as conn:
			if (name and surname):
				data = await conn.fetch(f"SELECT * FROM characters WHERE authorid NOT IN ({self.banned_list}) AND approved AND name = $1 AND surname = $2;", name, surname)
			else:
				data = await conn.fetch(f"SELECT * FROM characters WHERE authorid NOT IN ({self.banned_list}) AND approved AND (name = $1 OR surname = $2);", name, surname)

			return data
# ------------------------------------------------------------------------
# Test work
# ------------------------------------------------------------------------

db = ShowcaseDBConnection()
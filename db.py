import os
import math
from datetime import datetime
from datetime import timedelta
import asyncio
import asyncpg as pg
import asyncpg.exceptions as pgexceptions
from sshtunnel import SSHTunnelForwarder

from utils import utils
# from postgresql_credentials import *


class DBConnection:
	def __new__(cls):
		if not hasattr(cls, 'instance'):
			cls.instance = super(DBConnection, cls).__new__(cls)
		return cls.instance

	def __init__(self):
		self.ssh, self.conn = asyncio.get_event_loop().run_until_complete(self.connect())

	async def connect(self):
		SSH_HOST = os.getenv("SSH_HOST")
		SSH_USER = os.getenv("SSH_USER")
		SSH_KEY = os.getenv("SSH_KEY")
		DB_HOST = os.getenv("DB_HOST")
		DB_USER = os.getenv("DB_USER")
		DB_PASSWORD = os.getenv("DB_PASSWORD")
		DB_NAME = os.getenv("DB_NAME")

		ssh = SSHTunnelForwarder(
			(SSH_HOST, 22),
			ssh_username=SSH_USER,
			ssh_private_key=SSH_KEY,
			remote_bind_address=(DB_HOST, 5432))
		ssh.start()

		conn = await pg.connect(
			host="localhost",
			port=ssh.local_bind_port,
			user=DB_USER,
			password=DB_PASSWORD,
			database=DB_NAME)

		print("Connected to database")
		return ssh, conn


	async def disconnect(self):
		await self.conn.close()
		self.ssh.close()
		print("Closed db and ssh connections")


# ------------------------------------------------------------------------
# Basic GuildInfo functions
# ------------------------------------------------------------------------
	async def get_all_guild_ids(self):
		"""Returns dictionary of all IDs recorded in db"""

		data = await self.conn.fetch("SELECT guildid FROM guildinfo")
		return [record["guildid"] for record in data]


	async def add_guilds(self, guild_ids):
		"""Called when bot joins a guild, or when it is restarted and has been added to guilds"""

		guilds = [(i,) for i in guild_ids]
		try:
			await self.conn.executemany("INSERT INTO guildinfo (guildid) VALUES ($1);", guilds)
		except pgexceptions.UniqueViolationError:
			return


	async def remove_guilds(self, existing_guilds):
		"""Called on dev command with a list of guilds to preserve"""

		guild_list = ", ".join(existing_guilds)

		# GuildInfo
		rowcount = await self.conn.execute(f"DELETE FROM guildinfo WHERE guildid NOT IN ({guild_list}) RETURNING 1;")

		# Rowcount seems to be a string-like in the form of "DELETE <n>"
		# Don't actually need it to be an integer since we just print it
		removed_guilds = rowcount[7:]

		# The other tables
		await self.conn.execute(f"DELETE FROM announcements WHERE guildid NOT IN ({guild_list});")
		await self.conn.execute(f"DELETE FROM characters WHERE guildid NOT IN ({guild_list});")
		await self.conn.execute(f"DELETE FROM gacha WHERE guildid NOT IN ({guild_list});")
		await self.conn.execute(f"DELETE FROM investigations WHERE guildid NOT IN ({guild_list});")

		return removed_guilds


	async def edit_guild(self, guild_id, field, value):
		"""Edit any existing field in the db. Definitely do not allow direct user access to this."""

		await self.conn.execute(f"UPDATE GuildInfo SET {field} = $1 WHERE GuildID = $2;", value, guild_id)


	async def get_guild_info(self, guild_id):
		"""Returns a single row"""

		data = await self.conn.fetchrow("SELECT * FROM GuildInfo WHERE GuildID = $1;", guild_id)
		return data


# ------------------------------------------------------------------------
# Profiles
# ------------------------------------------------------------------------
	async def new_character(self, guild_id, player_id, name, surname=None, channel_id=None):
		"""Register new character to database"""

		try:
			await self.conn.execute("INSERT INTO Characters (GuildID, PlayerID, Name, Surname, ChannelID) VALUES ($1, $2, $3, $4, $5);", guild_id, player_id, name, surname, channel_id)
		except pgexceptions.UniqueViolationError as error:
			raise Exception("IntegrityError") from error


	async def remove_character(self, guild_id, player_id, name):
		"""Removes character. Returns False if nothing changed"""

		rowcount = await self.conn.execute("DELETE FROM Characters WHERE GuildID = $1 AND PlayerID = $2 AND Name = $3 RETURNING 1;", guild_id, player_id, name)

		return (int(rowcount[7:]) > 0)


	async def set_active_character(self, guild_id, player_id, name):
		"""Called on profile switch"""

		rowcount = await self.conn.execute("UPDATE Characters SET Active = true WHERE GuildID = $1 AND PlayerID = $2 AND Name = $3;", guild_id, player_id, name)

		if (int(rowcount[7:]) < 1):
			raise Exception("Cannot swap into nonexistent character")

		await self.conn.execute("UPDATE Characters SET Active = false WHERE GuildID = $1 AND PlayerID = $2 AND Name != $3;", guild_id, player_id, name)


	async def update_character(self, guild_id, player_id, name, field, value):
		"""Edit any existing Character field in the db. Definitely do not allow direct user access to this."""

		try:
			rowcount = await self.conn.execute(f"UPDATE Characters SET {field} = $1 WHERE GuildID = $2 AND PlayerID = $3 AND Name = $4;", value, guild_id, player_id, name)
		except pgexceptions.UniqueViolationError as error:
			raise Exception("IntegrityError") from error

		return (int(rowcount[7:]) > 0)


	async def get_character(self, guild_id, player_id, name):
		"""Returns dictionary character info"""

		data = await self.conn.fetchrow("SELECT * FROM Characters WHERE GuildID = $1 AND PlayerID = $2 AND Name = $3 LIMIT 1", guild_id, player_id, name)
		
		return data


	async def get_active_char(self, guild_id, player_id):
		"""Returns active character"""

		data = await self.conn.fetchrow("SELECT * FROM Characters WHERE GuildID = $1 AND PlayerID = $2 AND Active = true LIMIT 1;", guild_id, player_id)	
		return data

	async def get_all_chars(self, guild_id):
		"""Returns all character info for a single guild"""

		data = await self.conn.fetch("SELECT * FROM Characters WHERE GuildID = $1;", guild_id)
		return data


# ------------------------------------------------------------------------
# Currency
# ------------------------------------------------------------------------
	async def increase_currency_single(self, guild_id, player_id, amount):
		"""Increase for active character"""

		try:
			rowcount = await self.conn.execute("UPDATE Characters SET Currency = Currency + $1 WHERE GuildID = $2 AND PlayerID = $3 AND Active = true RETURNING 1;", amount, guild_id, player_id)
		except pgexceptions.CheckViolationError:
			rowcount = await self.conn.execute("UPDATE Characters SET Currency = 32000 WHERE GuildID = $1 AND PlayerID = $2 AND Active = true RETURNING 1;", guild_id, player_id)

		return (int(rowcount[7:]) > 0)


	async def increase_currency_inactive(self, guild_id, player_id, amount, name):
		"""Same as above but for inactive character"""

		try:
			rowcount = await self.conn.execute("UPDATE Characters SET Currency = Currency + $1 WHERE GuildID = $2 AND PlayerID = $3 AND Name = $4;", amount, guild_id, player_id, name)
		except pgexceptions.CheckViolationError:
			rowcount = await self.conn.execute("UPDATE Characters SET Currency = 32000 WHERE GuildID = $1 AND PlayerID = $2 AND Name = $3;", guild_id, player_id, name)

		return (int(rowcount[7:])  > 0)


	async def decrease_currency_single(self, guild_id, player_id, amount):
		"""Decrease for active character"""

		try:
			rowcount = await self.conn.execute("UPDATE Characters SET Currency = Currency - $1 WHERE GuildID = $2 AND PlayerID = $3 AND Active = true;", amount, guild_id, player_id)
		except pgexceptions.CheckViolationError:
			rowcount = await self.conn.execute("UPDATE Characters SET Currency = 0 WHERE GuildID = $1 AND PlayerID = $2 AND Active = true;", guild_id, player_id)

		return (int(rowcount[7:]) > 0)


	async def decrease_currency_inactive(self, guild_id, player_id, amount, name):
		"""Same as above but for inactive character"""

		try:
			rowcount = await self.conn.execute("UPDATE Characters SET Currency = Currency - $1 WHERE GuildID = $2 AND PlayerID = $3 AND Name = $4;", amount, guild_id, player_id, name)
		except pgexceptions.CheckViolationError:
			rowcount = await self.conn.execute("UPDATE Characters SET Currency = 0 WHERE GuildID = $1 AND PlayerID = $2 AND Name = $3;", guild_id, player_id, name)

		return (int(rowcount[7:])  > 0)


	async def increase_currency_all(self, guild_id, amount):
		"""Increase amount for all active characters"""

		rowcount = await self.conn.execute("UPDATE Characters SET Currency = Currency + $1 WHERE GuildID = $2 AND Active = true;", amount, guild_id)

		return (int(rowcount[7:]) > 0)

# ------------------------------------------------------------------------
# Gacha
# ------------------------------------------------------------------------
	async def get_all_gacha(self, guild_id):
		"""Returns every item for a guild"""

		data = await self.conn.fetch("SELECT * FROM Gacha WHERE GuildID = $1;", guild_id)
		return data


	async def add_gacha(self, guild_id, name, desc, amount=None, thumbnail=None):
		"""Register a new gacha item"""

		try:
			await self.conn.execute("INSERT INTO Gacha (GuildID, Name, Description, Amount, AmountRemaining, ThumbnailURL) VALUES($1, $2, $3, $4, $5, $6);", guild_id, name, desc, amount, amount, thumbnail)
		except pgexceptions.UniqueViolationError as error:
			raise Exception("IntegrityError") from error


	async def get_single_gacha(self, guild_id, name):
		"""Get a single item, uniquely identified"""


		data = await self.conn.fetchrow("SELECT * FROM Gacha WHERE GuildID = $1 AND Name = $2 LIMIT 1;", guild_id, name)
		return data


	async def remove_gacha_item(self, guild_id, name):
		"""Removes single gacha item. Returns true if deletion happened"""

		rowcount = await self.conn.execute("DELETE FROM Gacha WHERE GuildID = $1 AND Name = $2 RETURNING 1;", guild_id, name)

		return (int(rowcount[7:]) > 0)


	async def remove_all_gacha(self, guild_id):
		"""Removes all gacha items for a guild"""

		await self.conn.execute("DELETE FROM Gacha WHERE GuildID = $1;", guild_id)


	async def get_random_item(self, guild_id):
		"""
		Returns a random item from guild gacha.
		Decrements and removes as needed
		"""

		item = await self.conn.fetchrow("SELECT * FROM Gacha WHERE GuildID = $1 ORDER BY RANDOM() LIMIT 1;", guild_id)

		if (item["amount"]):
			new_amount = item["amountremaining"]-1

			# Deletion case
			if (new_amount < 1):
				await self.conn.execute("DELETE FROM Gacha WHERE GuildID = $1 AND Name = $2;", guild_id, item["name"])
				return item

			# Reduction case
			await self.conn.execute("UPDATE Gacha SET AmountRemaining = $1 WHERE GuildID = $2 AND Name = $3;", new_amount, guild_id, item["name"])

		return item


# ------------------------------------------------------------------------
# Inventory
# ------------------------------------------------------------------------
	async def add_item(self, guild_id, player_id, item, name=None, amount=1, desc=None):
		"""Adds item to inventory JSON string"""

		if (name):
			inventory = await self.conn.fetchval("SELECT Inventory FROM Characters WHERE GuildID = $1 AND PlayerID = $2 AND Name = $3;", guild_id, player_id, name)
		else:
			inventory = await self.conn.fetchval("SELECT Inventory FROM Characters WHERE GuildID = $1 AND PlayerID = $2 AND Active = true;", guild_id, player_id)

		# Add or edit amount
		try:
			inventory = utils.str_to_dict(inventory)
		except TypeError:
			return False

		try:
			current_amount = inventory[item]["amount"]
			inventory[item]["amount"] = min(current_amount+amount, 9999)
		except KeyError:
			inventory[item] = {"amount": amount, "desc": None}

		if (not inventory[item]["desc"]):
			inventory[item]["desc"] = desc


		# json to str
		inventory = utils.dict_to_str(inventory)

		# Rewrite entry
		if (name):
			rowcount = await self.conn.execute("UPDATE characters SET inventory = $1 WHERE guildid = $2 AND playerid = $3 AND name = $4", inventory, guild_id, player_id, name)
		else:
			rowcount = await self.conn.execute("UPDATE characters SET inventory = $1 WHERE guildid = $2 AND playerid = $3 AND active = true", inventory, guild_id, player_id)

		return (int(rowcount[7:]) > 0)


	async def remove_item(self, guild_id, player_id, item, name=None, amount=1):
		"""Removes item from JSON string"""

		# Get current inventory dictionary string
		if (name):
			inventory = await self.conn.fetchval("SELECT Inventory FROM Characters WHERE GuildID = $1 AND PlayerID = $2 AND Name = $3;", guild_id, player_id, name)
		else:
			inventory = await self.conn.fetchval("SELECT Inventory FROM Characters WHERE GuildID = $1 AND PlayerID = $2 AND Active = true;", guild_id, player_id)

		try:
			inventory =utils.str_to_dict(inventory)
		except TypeError:
			return False

		try:
			current_amount = inventory[item]["amount"]

			# Test for 0 amount
			if (current_amount-amount <= 0):
				inventory.pop(item)
			else:
				inventory[item]["amount"] = max(0, current_amount-amount)
		except KeyError:
			return False

		# String to dict
		inventory = utils.dict_to_str(inventory)

		# Write to database
		if (name):
			rowcount = await self.conn.execute("UPDATE Characters SET Inventory = $1 WHERE GuildID = $2 AND PlayerID = $3 AND Name = $4;", inventory, guild_id, player_id, name)
		else:
			rowcount = await self.conn.execute("UPDATE Characters SET Inventory = $1 WHERE GuildID = $2 AND PlayerID = $3 AND Active = true;", inventory, guild_id, player_id)


		return (int(rowcount[7:]) > 0)


	async def get_inventory(self, guild_id, player_id, name=None):
		"""Return dictionary"""

		if (name):
			inventory = await self.conn.fetchval("SELECT Inventory FROM Characters WHERE GuildID = $1 AND PlayerID = $2 AND Name = $3;", guild_id, player_id, name)
		else:
			inventory = await self.conn.fetchval("SELECT Inventory FROM Characters WHERE GuildID = $1 AND PlayerID = $2 AND Active = true;", guild_id, player_id)

		# Convert string to dict (error if nonexistent)
		return utils.str_to_dict(inventory)


# ------------------------------------------------------------------------
# Dice
# ------------------------------------------------------------------------
	async def add_roll(self, guild_id, player_id, name, roll):
		"""Edits JSON in database"""

		# Enforce case
		name = name.lower()

		# Check length
		# JSONB update doesn't play nicely with $ arguments
		# So we bruteforce it
		rolls = await self.conn.fetchval("SELECT customrolls FROM characters WHERE guildid = $1 AND playerid = $2 AND active = true;", guild_id, player_id)

		try:
			rolls = utils.str_to_dict(rolls)
		except TypeError as error:
			return False

		if (len(rolls) == 25 and name not in rolls.keys()):
			raise Exception("Limit of 25")

		# Update JSON
		rolls[name] = roll
		rolls = utils.dict_to_str(rolls)

		rowcount = await self.conn.execute("UPDATE characters SET customrolls = $1 WHERE guildid = $2 AND playerid = $3 and active = true;", rolls, guild_id, player_id)

		return (int(rowcount[7:]) > 0)


	async def rm_roll(self, guild_id, player_id, name):
		"""Edits JSON in database"""

		# Enforce case
		name = name.lower()

		rowcount = await self.conn.execute("UPDATE characters SET customrolls = customrolls-$1 WHERE guildid = $2 AND playerid = $3 AND active = true", name, guild_id, player_id)

		return (int(rowcount[7:]) > 0)


# ------------------------------------------------------------------------
# Announcements
# ------------------------------------------------------------------------
	async def add_announcement(self, announcement_id, guild_id, channel_id, message, interval, start_time):
		"""Insert new automatic post into database"""

		await self.conn.execute("INSERT INTO announcements (id, guildid, channelid, message, interval, nextposting) VALUES ($1, $2, $3, $4, $5, $6);", announcement_id, guild_id, channel_id, message, interval, start_time)


	async def get_guild_announcements(self, guild_id):
		"""Return all automatic posts for a single guild"""

		data = await self.conn.fetch("SELECT * FROM announcements WHERE guildid = $1;", guild_id)
		return data


	async def get_current_announcements(self, utc_time):
		"""Increments them as well"""

		utc_int = int(utc_time.strftime("%Y%m%d%H%M"))
		announcements = await self.conn.fetch("SELECT * FROM announcements WHERE nextposting = $1;", utc_int)


		# Increment
		params = []
		for announcement in announcements:
			announcement_id = announcement["id"]

			next_posting_datetime = utc_time + timedelta(hours=announcement["interval"])
			next_posting_int = int(next_posting_datetime.strftime("%Y%m%d%H%M"))

			params.append((next_posting_int, announcement_id))

		# Update
		await self.conn.executemany("UPDATE announcements SET nextposting = $1 WHERE id = $2;", params)

		return announcements


	async def remove_announcement(self, guild_id, announcement_id):
		"""Remove automatic post from database"""

		rowcount = await self.conn.execute("DELETE FROM announcements WHERE guildid = $1 AND id = $2;", guild_id, announcement_id)

		return (int(rowcount[7:]) > 0)


	async def toggle_guild_announcements(self, guild_id, val):
		"""Val false - Paused, Val true - Run"""

		await self.conn.execute("UPDATE guildinfo SET announcementsenabled = $1 WHERE guildid = $2;", val, guild_id)

	async def update_passed_announcements(self):
		"""Update announcements where NextPosting < utc_time"""

		parse_str = "%Y%m%d%H%M"
		
		utc_time = datetime.utcnow()
		utc_int = int(utc_time.strftime(parse_str))
		announcements = await self.conn.fetch("SELECT * FROM announcements WHERE nextposting <= $1;", utc_int)


		params = []
		for announcement in announcements:
			ID = announcement["id"]
			interval = announcement["interval"]
			
			outdated_posting_str = str(announcement["nextposting"])
			outdated_posting_datetime = datetime.strptime(outdated_posting_str, parse_str)

			hours_missed = (utc_time - outdated_posting_datetime).total_seconds() / 3600
			cycles_missed = math.ceil(hours_missed/interval)

			next_posting_datetime = outdated_posting_datetime + timedelta(hours=cycles_missed*interval)
			next_posting_int = int(next_posting_datetime.strftime(parse_str))

			params.append((next_posting_int, ID))

		# Update
		rowcount = await self.conn.executemany("UPDATE announcements SET nextposting = $1 WHERE id = $2 RETURNING 1;", params)

		# print (rowcount)
		return len(params)


# ------------------------------------------------------------------------
# Investigations
# ------------------------------------------------------------------------
	async def add_investigation(self, guild_id, channel_id, names, desc, stealable):
		"""Add investigatable item. Does not check for repeats"""

		await self.conn.execute("INSERT INTO investigations (guildid, channelid, names, description, stealable) VALUES ($1, $2, $3, $4, $5);", guild_id, channel_id, names, desc, stealable)


	async def get_investigation(self, guild_id, channel_id, name):
		"""Get an investigatable item by name"""

		data = await self.conn.fetchrow("SELECT * FROM investigations WHERE guildid = $1 AND channelid = $2 AND names ? $3;", guild_id, channel_id, name)
		
		return data


	async def set_investigation_taken(self, guild_id, channel_id, name, char_name):
		"""Sets TakenBy to player ID"""

		await self.conn.execute("UPDATE investigations SET takenby = $1 WHERE guildid = $2 AND channelid = $3 AND names ? $4;", char_name, guild_id, channel_id, name)


	async def remove_investigation(self, guild_id, channel_id, name):
		"""Remove an item by name"""

		rowcount = await self.conn.execute("DELETE FROM investigations WHERE guildid = $1 AND channelid = $2 AND names ? $3;", guild_id, channel_id, name)

		return (int(rowcount[7:]) > 0)


	async def get_all_investigations(self, guild_id):
		"""Return all investigations for guild"""

		data = await self.conn.fetch("SELECT * FROM investigations WHERE guildid = $1;", guild_id)
		return data

# ------------------------------------------------------------------------
# Test work
# ------------------------------------------------------------------------
# loop = asyncio.get_event_loop()

db = DBConnection()

# loop.run_until_complete(db.add_announcement(12474859, 405186895371567116, 461265486655520788, "This is\nanother message.", 24, 202209111430))


# names = ["item 1", "item"]
# names = utils.dict_to_str(names)

# data = loop.run_until_complete(db.get_all_investigations(437627669648113664))

# print(data)

# loop.run_until_complete(db.disconnect())
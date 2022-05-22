"""
Original template by @Firefly#7113, Nov 2021
"""

import sqlite3
import math
from datetime import datetime
from datetime import timedelta
from utils import utils

# ------------------------------------------------------------------------
# Essential default setup and functions
# ------------------------------------------------------------------------
def dict_factory(cursor, row):
	"""Formats the request output as a dictionary"""
	dct = {}
	for idx, col in enumerate(cursor.description):
		dct[col[0]] = row[idx]
	return dct


DB_NAME = "main.db"
conn = sqlite3.connect(DB_NAME)
conn.row_factory = dict_factory
cs = conn.cursor()
print(f"Connected to {DB_NAME}")


def disconnect():
	"""Called when the shutdown command is used for proper practice"""

	conn.close()
	print("Database connection closed")


def get_all_guild_ids():
	"""Returns dictionary of all IDs recorded in db"""

	cs.execute("SELECT GuildID FROM GuildInfo;")
	return [row["GuildID"] for row in cs.fetchall()]


def add_guilds(guild_ids):
	"""Called when bot joins a guild, or when it is restarted and has been added to guilds"""

	guilds = [(i,) for i in guild_ids]
	cs.executemany("INSERT INTO GuildInfo ('GuildID') VALUES (?);", guilds)
	conn.commit()


def remove_guilds(existing_guilds):
	"""Called on dev command with a list of guilds to preserve"""

	guild_list = ", ".join(existing_guilds)

	# GuildInfo
	cs.execute(f"DELETE FROM GuildInfo WHERE GuildID NOT IN ({guild_list});")
	conn.commit()

	removed_guilds = cs.rowcount

	# The other tables
	cs.execute(f"DELETE FROM Announcements WHERE GuildID NOT IN ({guild_list});")
	cs.execute(f"DELETE FROM Characters WHERE GuildID NOT IN ({guild_list});")
	cs.execute(f"DELETE FROM Gacha WHERE GuildID NOT IN ({guild_list});")
	cs.execute(f"DELETE FROM Investigations WHERE GuildID NOT IN ({guild_list});")
	conn.commit()

	return removed_guilds


def edit_guild(guild_id, field, value):
	"""Edit any existing field in the db. Definitely do not allow direct user access to this."""

	cs.execute(f"UPDATE GuildInfo SET {field} = ? WHERE GuildID = ?;", (value, guild_id))
	conn.commit()


def get_guild_info(guild_id):
	"""Returns dictionary of guild"""

	cs.execute("SELECT * FROM GuildInfo WHERE GuildID = ? LIMIT 1;", (guild_id,))
	return cs.fetchone()

def get_player_roles():
	"""Returns array of all player role IDs"""

	cs.execute("SELECT PlayerRole FROM GuildInfo;")
	roles = [entry["PlayerRole"] for entry in cs.fetchall() if entry["PlayerRole"]]
	print(roles)
	return roles

# ------------------------------------------------------------------------
# Other functions
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# Profiles
# ------------------------------------------------------------------------
def new_character(guild_id, player_id, name, surname=None, channel_id=None):
	"""Register new character to database"""

	try:
		cs.execute("INSERT INTO Characters ('GuildID', 'PlayerID', 'Name', 'Surname', 'ChannelID') VALUES(?, ?, ?, ?, ?);", (guild_id, player_id, name, surname, channel_id))
	except sqlite3.IntegrityError as error:
		raise Exception("IntegrityError") from error
	conn.commit()


def remove_character(guild_id, player_id, name):
	"""Removes character. Returns False if nothing changed"""

	cs.execute("DELETE FROM Characters WHERE GuildID = ? AND PlayerID = ? AND Name = ? LIMIT 1;", (guild_id, player_id, name))
	conn.commit()

	return (cs.rowcount > 0)


def set_active_character(guild_id, player_id, name):
	"""Called on profile switch"""

	cs.execute("UPDATE Characters SET Active = 1 WHERE GuildID = ? AND PlayerID = ? AND Name = ? LIMIT 1;", (guild_id, player_id, name))
	if (cs.rowcount < 1):
		raise Exception("Cannot swap into nonexistent character")

	cs.execute("UPDATE Characters SET Active = 0 WHERE GuildID = ? AND PlayerID = ? AND Name != ?;", (guild_id, player_id, name))
	conn.commit()


# Returns True if anything was changed (character found)
def update_character(guild_id, player_id, name, field, value):
	"""Edit any existing Character field in the db. Definitely do not allow direct user access to this."""

	try:
		cs.execute(f"UPDATE Characters SET {field} = ? WHERE GuildID = ? AND PlayerID = ? AND Name = ? LIMIT 1;", (value, guild_id, player_id, name))
		conn.commit()
	except sqlite3.IntegrityError as error:
		raise Exception("IntegrityError") from error

	return (cs.rowcount > 0)


def get_character(guild_id, player_id, name):
	"""Returns dictionary character info"""

	cs.execute("SELECT * FROM Characters WHERE GuildID = ? AND PlayerID = ? AND Name = ? LIMIT 1;", (guild_id, player_id, name))
	return cs.fetchone()


def get_active_char(guild_id, player_id):
	"""returns active character"""

	cs.execute("SELECT * FROM Characters WHERE GuildID = ? AND PlayerID = ? AND Active = 1 LIMIT 1;", (guild_id, player_id))
	return cs.fetchone()


def get_all_chars(guild_id):
	"""Returns all character info for a single guild"""

	cs.execute("SELECT * FROM Characters WHERE GuildID = ?;", (guild_id,))
	return cs.fetchall()

# ------------------------------------------------------------------------
# Currency
# ------------------------------------------------------------------------
# Returns True if anything changed
def increase_currency_single(guild_id, player_id, amount):
	"""Increase for active character"""

	cs.execute("UPDATE Characters SET Currency = Currency + ? WHERE GuildID = ? AND PlayerID = ? AND Active = 1 LIMIT 1;", (amount, guild_id, player_id))
	conn.commit()

	return (cs.rowcount > 0)


def decrease_currency_single(guild_id, player_id, amount):
	"""Decrease for active character"""

	try:
		cs.execute("UPDATE Characters SET Currency = Currency - ? WHERE GuildID = ? AND PlayerID = ? AND Active = 1 LIMIT 1;", (amount, guild_id, player_id))
	except sqlite3.IntegrityError:
		cs.execute("UPDATE Characters SET Currency = 0 WHERE GuildID = ? AND PlayerID = ? AND Active = 1 LIMIT 1;", (guild_id, player_id))

	conn.commit()

	return (cs.rowcount > 0)


def increase_currency_all(guild_id, amount):
	"""Increase amount for all active characters"""

	cs.execute("UPDATE Characters SET Currency = Currency + ? WHERE GuildID = ? AND Active = 1;", (amount, guild_id))
	conn.commit()

	return (cs.rowcount > 0)

# ------------------------------------------------------------------------
# Gacha
# ------------------------------------------------------------------------
def get_all_gacha(guild_id):
	"""Returns every item for a guild"""

	cs.execute("SELECT * FROM Gacha WHERE GuildID = ?;", (guild_id,))
	return cs.fetchall()


def add_gacha(guild_id, name, desc, amount, thumbnail):
	"""Register a new gacha item"""

	try:
		cs.execute("INSERT INTO Gacha ('GuildID', 'Name', 'Desc', 'Amount', 'AmountRemaining', 'ThumbnailURL') VALUES(?, ?, ?, ?, ?, ?);", (guild_id, name, desc, amount, amount, thumbnail))
	except sqlite3.IntegrityError as error:
		raise Exception("IntegrityError") from error

	conn.commit()


def get_single_gacha(guild_id, name):
	"""Get a single item, uniquely identified"""

	cs.execute("SELECT * FROM Gacha WHERE GuildID = ? AND Name = ? LIMIT 1;", (guild_id, name))
	return cs.fetchone()


def remove_gacha_item(guild_id, name):
	"""Removes single gacha item. Returns true if deletion happened"""

	cs.execute("DELETE FROM Gacha WHERE GuildID = ? AND Name = ? LIMIT 1;", (guild_id, name))
	conn.commit()

	return (cs.rowcount > 0)


def remove_all_gacha(guild_id):
	"""Removes all gacha items for a guild"""

	cs.execute("DELETE FROM Gacha WHERE GuildID = ?;", (guild_id,))
	conn.commit()


def get_random_item(guild_id):
	"""
	Returns a random item from guild gacha.
	Decrements and removes as needed
	"""

	cs.execute("SELECT * FROM Gacha WHERE GuildID = ? ORDER BY RANDOM() LIMIT 1;", (guild_id,))

	item = cs.fetchone()
	if (item["Amount"]):
		new_amount = item["AmountRemaining"]-1

		# Deletion case
		if (new_amount < 1):
			cs.execute("DELETE FROM Gacha WHERE GuildID = ? AND Name = ? LIMIT 1;", (guild_id, item["Name"]))
			conn.commit()
			return item

		# Reduction case
		cs.execute("UPDATE Gacha SET AmountRemaining = ? WHERE GuildID = ? AND Name = ? LIMIT 1;", (new_amount, guild_id, item["Name"]))
		conn.commit()

	return item


# ------------------------------------------------------------------------
# Inventory
# ------------------------------------------------------------------------
def add_item(guild_id, player_id, item, amount=1, desc=None):
	"""Adds item to inventory JSON string"""

	# Get current inventory dictionary string
	cs.execute("SELECT Inventory FROM Characters WHERE GuildID = ? AND PlayerID = ? AND Active = 1 LIMIT 1;", (guild_id, player_id))

	# Convert string to dict (error if nonexistent)
	try:
		inventory = utils.str_to_dict(cs.fetchone()["Inventory"])
	except TypeError:
		return False

	# Add or edit amount
	try:
		current_amount = inventory[item]["amount"]
		inventory[item]["amount"] = min(current_amount+amount, 9999)
	except KeyError:
		inventory[item] = {}
		inventory[item]["amount"] = amount
		inventory[item]["desc"] = desc

	# String to dictionary
	inventory_str = utils.dict_to_str(inventory)

	# Write and commit back to db
	cs.execute("UPDATE Characters SET Inventory = ? WHERE GuildID = ? AND PlayerID = ? AND Active = 1 LIMIT 1;", (inventory_str, guild_id, player_id))

	conn.commit()

	return (cs.rowcount > 0)


def remove_item(guild_id, player_id, item, amount=1):
	"""Removes item from JSON string"""

	# Get current inventory dictionary string
	cs.execute("SELECT Inventory FROM Characters WHERE GuildID = ? AND PlayerID = ? AND Active = 1 LIMIT 1;", (guild_id, player_id))

	# Convert string to dict (error if nonexistent)
	try:
		inventory = utils.str_to_dict(cs.fetchone()["Inventory"])
	except TypeError:
		return False

	# Add or edit amount
	try:
		current_amount = inventory[item]["amount"]

		# Test for 0 amount
		if (current_amount-amount <= 0):
			inventory.pop(item)
		else:
			inventory[item]["amount"] = max(0, current_amount-amount)
	except KeyError:
		return False

	# String to dictionary
	inventory_str = utils.dict_to_str(inventory)

	# Write and commit back to db
	cs.execute("UPDATE Characters SET Inventory = ? WHERE GuildID = ? AND PlayerID = ? AND Active = 1 LIMIT 1;", (inventory_str, guild_id, player_id))

	conn.commit()

	return (cs.rowcount > 0)


def get_inventory(guild_id, player_id):
	"""Return dictionary"""

	cs.execute("SELECT Inventory FROM Characters WHERE GuildID = ? AND PlayerID = ? AND Active = 1 LIMIT 1;", (guild_id, player_id))

	# Convert string to dict (error if nonexistent)
	return utils.str_to_dict(cs.fetchone()["Inventory"])


# ------------------------------------------------------------------------
# Dice
# ------------------------------------------------------------------------
def add_roll(guild_id, player_id, name, roll):
	"""Edits JSON compatible string in database"""

	# Get current roll dictionary string
	cs.execute("SELECT CustomRolls FROM Characters WHERE GuildID = ? AND PlayerID = ? AND Active = 1 LIMIT 1;", (guild_id, player_id))

	# Convert string to dict (error if nonexistent)
	try:
		rolls = utils.str_to_dict(cs.fetchone()["CustomRolls"])
	except TypeError:
		return False

	# Limit to 25
	if (len(rolls) == 25 and name.lower() not in rolls.keys()):
		raise Exception("Limit of 25!")

	# Add or edit amount
	rolls[name.lower()] = roll

	# String to dictionary
	rolls_str = utils.dict_to_str(rolls)

	# Write and commit back to db
	cs.execute("UPDATE Characters SET CustomRolls = ? WHERE GuildID = ? AND PlayerID = ? AND Active = 1 LIMIT 1;", (rolls_str, guild_id, player_id))

	conn.commit()

	return (cs.rowcount > 0)


def rm_roll(guild_id, player_id, name):
	"""Edits JSON compatible string in database"""

	# Get current roll dictionary string
	cs.execute("SELECT CustomRolls FROM Characters WHERE GuildID = ? AND PlayerID = ? AND Active = 1 LIMIT 1;", (guild_id, player_id))

	# Convert string to dict (error if nonexistent)
	try:
		rolls = utils.str_to_dict(cs.fetchone()["CustomRolls"])
	except TypeError as error:
		raise TypeError from error

	# Add or edit amount
	try:
		rolls.pop(name.lower())
	except KeyError as error:
		raise KeyError from error

	# String to dictionary
	rolls_str = utils.dict_to_str(rolls)

	# Write and commit back to db
	cs.execute("UPDATE Characters SET CustomRolls = ? WHERE GuildID = ? AND PlayerID = ? AND Active = 1 LIMIT 1;", (rolls_str, guild_id, player_id))

	conn.commit()

	return (cs.rowcount > 0)


# ------------------------------------------------------------------------
# Announcements
# ------------------------------------------------------------------------
def add_announcement(announcement_id, guild_id, channel_id, message, interval, start_time):
	"""Insert new automatic post into database"""

	cs.execute("INSERT INTO Announcements ('ID', 'GuildID', 'ChannelID', 'Message', 'Interval', 'NextPosting') VALUES (?, ?, ?, ?, ?, ?);", (announcement_id, guild_id, channel_id, message, interval, start_time))
	conn.commit()


def get_guild_announcements(guild_id):
	"""Return all automatic posts for a single guild"""

	cs.execute("SELECT * FROM Announcements WHERE GuildID = ?;", (guild_id,))
	return cs.fetchall()


def get_current_announcements(utc_time):
	"""Increments them as well"""

	utc_int = int(utc_time.strftime("%Y%m%d%H%M"))
	cs.execute("SELECT * FROM Announcements WHERE NextPosting = ?;", (utc_int,))

	announcements = cs.fetchall()

	# Increment
	params = []
	for announcement in announcements:
		announcement_id = announcement["ID"]

		next_posting_datetime = utc_time + timedelta(announcement["Interval"])
		next_posting_int = int(next_posting_datetime.strftime("%Y%m%d%H%M"))

		params.append((next_posting_int, announcement_id))

	# Update
	cs.executemany("UPDATE Announcements SET NextPosting = ? WHERE ID = ?;", params)
	conn.commit()

	return announcements


def remove_announcement(guild_id, announcement_id):
	"""Remove automatic post from database"""

	cs.execute("DELETE FROM Announcements WHERE GuildID = ? AND ID = ? LIMIT 1;", (guild_id, announcement_id))
	conn.commit()

	return (cs.rowcount > 0)


def toggle_guild_announcements(guild_id, val):
	"""Val 0 - Paused, Val 1 - Run"""

	cs.execute("UPDATE GuildInfo SET AnnouncementsEnabled = ? WHERE GuildID = ? LIMIT 1;", (val, guild_id))
	conn.commit()


def update_passed_announcements():
	"""Update announcements where NextPosting < utc_time"""

	parse_str = "%Y%m%d%H%M"
	
	utc_time = datetime.utcnow()
	utc_int = int(utc_time.strftime(parse_str))
	cs.execute("SELECT * FROM Announcements WHERE NextPosting <= ?;", (utc_int,))

	announcements = cs.fetchall()

	params = []
	for announcement in announcements:
		ID = announcement["ID"]
		interval = announcement["Interval"]
		
		outdated_posting_str = str(announcement["NextPosting"])
		outdated_posting_datetime = datetime.strptime(outdated_posting_str, parse_str)

		hours_missed = (utc_time - outdated_posting_datetime).total_seconds() / 3600
		cycles_missed = math.ceil(hours_missed/interval)

		next_posting_datetime = outdated_posting_datetime + timedelta(hours=cycles_missed*interval)
		next_posting_int = int(next_posting_datetime.strftime(parse_str))

		params.append((next_posting_int, ID))

	# Update
	cs.executemany("UPDATE Announcements SET NextPosting = ? WHERE ID = ?;", params)
	conn.commit()

	return cs.rowcount


# ------------------------------------------------------------------------
# Investigations
# ------------------------------------------------------------------------
def add_investigation(guild_id, channel_id, names, desc, stealable):
	"""Add investigatable item. Does not check for repeats"""

	stealable = int(stealable)

	cs.execute("INSERT INTO Investigations ('GuildID', 'ChannelID', 'Names', 'Desc', 'Stealable') VALUES (?, ?, json(?), ?, ?);", (guild_id, channel_id, names, desc, stealable))
	conn.commit()


def get_investigation(guild_id, channel_id, name):
	"""Get an investigatable item by name"""

	cs.execute("SELECT * FROM Investigations WHERE GuildID = ? AND ChannelID = ? AND Names LIKE ? LIMIT 1;", (guild_id, channel_id, f"%\"{name}\"%"))
	return cs.fetchone()


def set_investigation_taken(guild_id, channel_id, name, player_id):
	"""Sets TakenBy to player ID"""

	cs.execute("UPDATE Investigations SET TakenBy = ? WHERE GuildID = ? AND ChannelID = ? AND Names LIKE ? LIMIT 1;", (player_id, guild_id, channel_id, f"%\"{name}\"%"))
	conn.commit()


def remove_investigation(guild_id, channel_id, name):
	"""Remove an item by name"""

	cs.execute("DELETE FROM Investigations WHERE GuildID = ? AND ChannelID = ? AND Names LIKE ? LIMIT 1;", (guild_id, channel_id, f"%\"{name}\"%"))
	conn.commit()

	return (cs.rowcount > 0)


def get_all_investigations(guild_id):
	"""Return all investigations for guild"""

	cs.execute("SELECT * FROM Investigations WHERE GuildID = ?;", (guild_id,))
	return cs.fetchall()
#!/usr/bin/env python
"""
Original template by @Firefly#7113, April 2022
"""

import os
import shutil
import atexit

import discord

from config import TESTING_SERVERS
import db


# ------------------------------------------------------------------------
# Adjust bot intents
# ------------------------------------------------------------------------
bot_intents = discord.Intents.default()


# ------------------------------------------------------------------------
# Instantiate bot
# ------------------------------------------------------------------------
bot = discord.Bot(debug_guilds=TESTING_SERVERS, intents=bot_intents, activity=discord.Game(name="CHECK PROFILE DESCRIPTION"))


# ------------------------------------------------------------------------
# Bot shutdown/sigint
# ------------------------------------------------------------------------
@atexit.register
def app_died():
	"""Called on exit"""

	db.disconnect()

	# Remove __pycache__
	try:
		shutil.rmtree("__pycache__")
	except FileNotFoundError:
		pass

	try:
		shutil.rmtree("./cogs/__pycache__")
	except FileNotFoundError:
		pass

	try:
		shutil.rmtree("./utils/__pycache__")
	except FileNotFoundError:
		pass

	print("Removed __pycache__")


# ------------------------------------------------------------------------
# Essential event listeners
# ------------------------------------------------------------------------
@bot.event
async def on_ready():
	"""Indicates that bot is logged in"""
	print(f"Logged in as {bot.user}")


# ------------------------------------------------------------------------
# Cog handling
# ------------------------------------------------------------------------
for fname in os.listdir('./cogs'):
	if (fname.endswith('.py') and fname != '__init__.py'):
		bot.load_extension(f"cogs.{fname[:-3]}")


# ------------------------------------------------------------------------
# Update announcements
# ------------------------------------------------------------------------
passed_announcements = db.update_passed_announcements()
print(f"{passed_announcements} announcements updated")


# ------------------------------------------------------------------------
# Run bot
# ------------------------------------------------------------------------
tokenfile = open("TOKEN.txt", 'r', encoding='utf-8')
with tokenfile:
	token = tokenfile.readline()
	tokenfile.close()

bot.run(token)

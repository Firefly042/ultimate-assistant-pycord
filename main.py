#!/usr/bin/env python
"""
Original template by @Firefly#7113, April 2022
"""

import os
import shutil
import atexit

import discord
from discord.commands import permissions

from config import TESTING_SERVERS
import db


# ------------------------------------------------------------------------
# Adjust bot intents
# ------------------------------------------------------------------------
bot_intents = discord.Intents.default()


# ------------------------------------------------------------------------
# Instantiate bot
# ------------------------------------------------------------------------
bot = discord.Bot(debug_guilds=TESTING_SERVERS, intents=bot_intents)


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


@bot.command(name="shutdown")
@permissions.is_owner()
async def shutdown(ctx):
	"""Owner kill switch."""

	await ctx.respond("Logging out...", ephemeral=True)
	await bot.close()


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
	if (fname.endswith('.py') and fname != 'template_cog.py' and fname != '__init__.py'):
		bot.load_extension(f"cogs.{fname[:-3]}")


# ------------------------------------------------------------------------
# Run bot
# ------------------------------------------------------------------------
tokenfile = open("TOKEN.txt", 'r', encoding='utf-8')
with tokenfile:
	token = tokenfile.readline()
	tokenfile.close()

bot.run(token)

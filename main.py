#!/usr/bin/env python
"""
Original template by @Firefly#7113, April 2022
"""

import os
import shutil
import atexit

import discord

import db


# ------------------------------------------------------------------------
# Adjust bot intents
# ------------------------------------------------------------------------
bot_intents = discord.Intents.default()


# ------------------------------------------------------------------------
# Instantiate bot
# ------------------------------------------------------------------------
# bot = discord.Bot(debug_guilds=[os.getenv("DEVELOPER_SERVER")], intents=bot_intents, activity=discord.Game(name="CHECK PROFILE DESCRIPTION"))

bot = discord.Bot(intents=bot_intents, activity=discord.Game(name="CHECK PROFILE DESCRIPTION"))


# ------------------------------------------------------------------------
# Bot shutdown/sigint
# ------------------------------------------------------------------------
@atexit.register
def app_died():
	"""Called on exit"""

	db.disconnect()

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
token = os.getenv("TOKEN")

bot.run(token)

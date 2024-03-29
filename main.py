#!/usr/bin/env python
"""
Original template by @Firefly#7113, April 2022
"""

import os
import shutil
import asyncio
import atexit

import discord

from db import db


# ------------------------------------------------------------------------
# Adjust bot intents
# ------------------------------------------------------------------------
bot_intents = discord.Intents.default()


# ------------------------------------------------------------------------
# Instantiate bot
# ------------------------------------------------------------------------
# bot = discord.Bot(debug_guilds=[os.getenv("DEVELOPER_SERVER")], intents=bot_intents, activity=discord.Game(name="/help"))

bot = discord.Bot(intents=bot_intents, activity=discord.Game(name="/help"))


# ------------------------------------------------------------------------
# Bot shutdown/sigint
# ------------------------------------------------------------------------
# @asyncio_atexit.register
# async def app_died():
# 	"""Called on exit"""

# 	await db.disconnect()
# 	loop.close()
# 	# asyncio.get_event_loop().run_until_complete(db.disconnect())


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
passed_announcements = asyncio.get_event_loop().run_until_complete(db.update_passed_announcements())
print(f"{passed_announcements} announcements updated")


# ------------------------------------------------------------------------
# Run bot
# ------------------------------------------------------------------------
token = os.getenv("TOKEN")

bot.run(token)

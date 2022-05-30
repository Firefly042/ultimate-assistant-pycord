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

HELP_MESSAGE = "If you are seeing this, Ultimate Assistant has officially migrated to slash commands! Try typing `/` into discord and checking them out.\n\nIf you do not see them, you may need to re-invite the bot by clicking its name and using the in-profile invite. After that, the slash commands may take an hour or so to register to your server.\n<https://discord.com/api/oauth2/authorize?client_id=668970741525381141&permissions=274877975552&scope=bot%20applications.commands>\n\nTo get started, type `/help`!\n\n(This command will be phased out by 31st August, 2022)"

# ------------------------------------------------------------------------
# Adjust bot intents
# ------------------------------------------------------------------------
bot_intents = discord.Intents.default()
bot_intents.message_content = True


# ------------------------------------------------------------------------
# Instantiate bot
# ------------------------------------------------------------------------
bot = discord.Bot(debug_guilds=TESTING_SERVERS, intents=bot_intents, activity=discord.Game(name="!help (IMPORTANT CHANGES)"))


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


@bot.event
async def on_message(message):
	"""A temporary help command for transition period"""
	if (message.content.lower() == "!help"):
		try:
			await message.channel.send(HELP_MESSAGE)
		except discord.Forbidden:
			return
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

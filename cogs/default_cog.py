"""
Author @Firefly#7113
Necessary bot functions
"""

import os
import shutil
import datetime

import discord
from discord import slash_command
from discord.commands import permissions
from discord.ext import commands

import aiocron

import db


# ------------------------------------------------------------------------
# COMPONENT CLASSES AND CONSTANTS
# ------------------------------------------------------------------------


# ------------------------------------------------------------------------
# COG
# ------------------------------------------------------------------------
def setup(bot):
	bot.add_cog(DefaultCog(bot))

# pylint: disable=no-self-use
class DefaultCog(commands.Cog):
	"""Default functionality. This should not be changed."""

	def __init__(self, bot):
		self.bot = bot
		print(f"Added {self.__class__.__name__}")


# ------------------------------------------------------------------------
# Crontabs
# https://crontab.cronhub.io/
# Crontabs appear to execute in a LIFO stack order
# Do not need to be explicitly started
# ------------------------------------------------------------------------
	@staticmethod
	@aiocron.crontab('0 1 * * *')
	async def backup_db():
		"""
		Backs up the database once every 24 hours at 1AM, server time
		Files older than 30 days will be removed
		"""

		today = datetime.date.today()
		fname = f"./db_backups/{today}.db"
		shutil.copy("main.db", fname)

		for file in os.listdir("./db_backups"):
			fpath = os.path.join("./db_backups", file)
			mod_date = datetime.datetime.fromtimestamp(os.path.getmtime(fpath))

			if (file.endswith(".db") and datetime.datetime.now() - mod_date > datetime.timedelta(days=30)):
				os.remove(fpath)


# ------------------------------------------------------------------------
# Listeners
# ------------------------------------------------------------------------
	@commands.Cog.listener()
	async def on_ready(self):
		"""
		Adds guilds to db if bot was added to them while offline
		Flushes out guilds that removed bot since it was last online
		"""

		bot_guilds = [guild.id for guild in self.bot.guilds]

		db_guilds = db.get_all_guild_ids()

		bot_guilds_not_in_db = [i for i in bot_guilds if i not in db_guilds]
		db_guilds_not_in_bot = [i for i in db_guilds if i not in bot_guilds]
		db.add_guilds(bot_guilds_not_in_db)
		db.remove_guilds(db_guilds_not_in_bot)

		print(f"Added {len(bot_guilds_not_in_db)} guilds to database and" \
			f" removed {len(db_guilds_not_in_bot)}")


	@commands.Cog.listener()
	async def on_guild_join(self, guild):
		"""Add to db when bot is added to guild"""
		db.add_guilds([guild.id])


# ------------------------------------------------------------------------
# Commands
# ------------------------------------------------------------------------
	@slash_command(name="info")
	async def info(self, ctx):
		"""Displays basic info and statistics about the bot"""

		guild_list = ""
		for guild in self.bot.guilds:
			guild_list += guild.name+"\n"

		embed = discord.Embed()
		embed.title = f"{self.bot.user.name}"
		embed.description = """Original code by @Firefly#7113
		[Github](https://github.com/Firefly042), [Server](https://discord.gg/VZYKBptWFJ)"""
		embed.add_field(name=f"Servers ({len(self.bot.guilds)})", value=guild_list)

		await ctx.respond(embed=embed)


	@slash_command(name="devtest")
	@permissions.is_owner()
	async def devtest(self, ctx):
		"""Dev scratchwork. Comment out probably."""

		db.remove_item(ctx.guild.id, ctx.interaction.user.id, "item 1", amount=1)
		await ctx.respond("Dev Test", ephemeral=True)

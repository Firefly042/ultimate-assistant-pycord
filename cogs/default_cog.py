"""
Author @Firefly#7113
Necessary bot functions
"""

import os
import shutil
import datetime

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
		"""

		bot_guilds = [guild.id for guild in self.bot.guilds]
		db_guilds = db.get_all_guild_ids()
		bot_guilds_not_in_db = [i for i in bot_guilds if i not in db_guilds]

		db.add_guilds(bot_guilds_not_in_db)

		print(f"Added {len(bot_guilds_not_in_db)} guilds to database")


	@commands.Cog.listener()
	async def on_guild_join(self, guild):
		"""Add to db when bot is added to guild"""
		db.add_guilds([guild.id])


# ------------------------------------------------------------------------
# Commands
# ------------------------------------------------------------------------

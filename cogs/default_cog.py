"""
Author @Firefly#7113
Necessary bot functions
"""

import os
import shutil
import datetime

from discord.ext import commands

import aiocron

from db import db


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
# Listeners
# ------------------------------------------------------------------------
	@commands.Cog.listener()
	async def on_ready(self):
		"""
		Adds guilds to db if bot was added to them while offline
		"""

		bot_guilds = [guild.id for guild in self.bot.guilds]
		db_guilds = await db.get_all_guild_ids()
		bot_guilds_not_in_db = [i for i in bot_guilds if i not in db_guilds]

		await db.add_guilds(bot_guilds_not_in_db)

		print(f"Added {len(bot_guilds_not_in_db)} guilds to database")


	@commands.Cog.listener()
	async def on_guild_join(self, guild):
		"""Add to db when bot is added to guild"""
		await db.add_guilds([guild.id])


# ------------------------------------------------------------------------
# Commands
# ------------------------------------------------------------------------

"""
Author @Firefly#7113
Developer-only commands
"""

import os

import discord
from discord import option
from discord.commands import SlashCommandGroup, CommandPermission
from discord.ext import commands

from config import DEVELOPER_SERVER
import db

from utils import utils
from utils.embed_list import EmbedList


# ------------------------------------------------------------------------
# COMPONENT CLASSES AND CONSTANTS
# ------------------------------------------------------------------------


# ------------------------------------------------------------------------
# COG
# ------------------------------------------------------------------------
def setup(bot):
	bot.add_cog(DeveloperCog(bot))

# pylint: disable=no-self-use, too-many-arguments
class DeveloperCog(commands.Cog):
	"""Inventory management for admins"""

	def __init__(self, bot):
		self.bot = bot
		print(f"Added {self.__class__.__name__}")


# ------------------------------------------------------------------------
# Command groups
# Change the decorator to @<name>.command()
# ------------------------------------------------------------------------
	dev = SlashCommandGroup("dev", "Developer only", permissions=[CommandPermission("owner", 2, True)], guild_ids=[DEVELOPER_SERVER])


# ------------------------------------------------------------------------
# Crontabs
# https://crontab.cronhub.io/
# Crontabs appear to execute in a LIFO stack order
# Do not need to be explicitly started
# ------------------------------------------------------------------------


# ------------------------------------------------------------------------
# Listeners
# ------------------------------------------------------------------------


# ------------------------------------------------------------------------
# Commands
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# /dev status
# ------------------------------------------------------------------------
	@dev.command(name="status", guild_only=False)
	@option("message", str, description="Short status")
	async def status(self, ctx, message):
		"""Set bot's playing status"""

		await self.bot.change_presence(activity=discord.Game(name=message))
		await ctx.respond("Changed presence")

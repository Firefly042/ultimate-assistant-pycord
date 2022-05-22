"""
Author @Firefly#7113
Developer-only commands
"""

import discord
from discord import option
from discord.commands import SlashCommandGroup
from discord.ext import commands

import db
from config import DEVELOPER_SERVER


# ------------------------------------------------------------------------
# COG
# ------------------------------------------------------------------------
def setup(bot):
	bot.add_cog(DeveloperCog(bot))

# pylint: disable=no-self-use, too-many-arguments
class DeveloperCog(commands.Cog):
	"""Developer utilities"""

	def __init__(self, bot):
		self.bot = bot
		print(f"Added {self.__class__.__name__}")


# ------------------------------------------------------------------------
# Command groups
# Change the decorator to @<name>.command()
# ------------------------------------------------------------------------
	dev = SlashCommandGroup("dev", "Developer only", guild_ids=[DEVELOPER_SERVER])


# ------------------------------------------------------------------------
# Commands
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# /dev status
# ------------------------------------------------------------------------
	@dev.command(name="status")
	@option("message", str, description="Short status")
	async def status(self, ctx, message):
		"""Set bot's playing status"""

		await self.bot.change_presence(activity=discord.Game(name=message))
		await ctx.respond("Changed presence")


# ------------------------------------------------------------------------
# /dev rm_guilds
# ------------------------------------------------------------------------
	@dev.command(name="rm_guilds")
	async def rm_guilds(self, ctx):
		"""Removes all info associated with guilds that the bot is no longer in"""

		bot_guild_ids = [str(guild.id) for guild in self.bot.guilds]

		n_removed = db.remove_guilds(bot_guild_ids)

		await ctx.respond(f"Removed {n_removed} non-member guilds from database")


# ------------------------------------------------------------------------
# /dev test
# ------------------------------------------------------------------------
	@dev.command(name="test")
	async def test(self, ctx):
		"""Dev test"""

		await ctx.respond("dev test")

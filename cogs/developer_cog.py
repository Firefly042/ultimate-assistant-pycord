"""
Author @Firefly#7113
Developer-only commands
"""

import discord
from discord import option
from discord.commands import SlashCommandGroup
from discord.ext import commands

import db
from config import DEVELOPER_SERVER, DEVELOPER_ID


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
		self.dm_channel = None # Cannot have async init, initialized on first use
		print(f"Added {self.__class__.__name__}")


# ------------------------------------------------------------------------
# Command groups
# Change the decorator to @<name>.command()
# ------------------------------------------------------------------------
	dev = SlashCommandGroup("dev", "Developer only", guild_ids=[DEVELOPER_SERVER])


# ------------------------------------------------------------------------
# Listeners
# ------------------------------------------------------------------------
	@commands.Cog.listener()
	async def on_guild_join(self, guild):
		"""DM developer"""

		if (not self.dm_channel):
			self.dm_channel = await self.bot.fetch_channel(DEVELOPER_ID)

		await self.dm_channel.send(f"Added to **{guild.name}** ({guild.id})")


	@commands.Cog.listener()
	async def on_guild_remove(self, guild):
		"""DM developer"""

		if (not self.dm_channel):
			self.dm_channel = await self.bot.fetch_channel(DEVELOPER_ID)

		await self.dm_channel.send(f"Removed from **{guild.name}** ({guild.id})")


	@commands.Cog.listener()
	async def on_application_command_error(self, ctx, exception):
		"""DM developer"""

		if (not self.dm_channel):
			self.dm_channel = await self.bot.fetch_channel(DEVELOPER_ID)

		msg = f"**GuildID**: {ctx.guild.id}\n"
		msg += f"**ChannelID**: {ctx.channel.id}\n"
		msg += f"**UserID**: {ctx.interaction.user.id}"
		msg += f"**Command**: {ctx.command.qualified_name}"
		msg += f"**Exception**: {type(exception)}\n--------------------------------------------"

		await self.dm_channel.send(msg[:1024])


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

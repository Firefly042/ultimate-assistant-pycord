"""
Author @Firefly#7113
Developer-only commands
"""

import os

import discord
from discord import option
from discord.commands import SlashCommandGroup
from discord.ext import commands

from db import db


# ------------------------------------------------------------------------
# COG
# ------------------------------------------------------------------------
def setup(bot):
	bot.add_cog(DeveloperCog(bot))

# pylint: disable=no-self-use, too-many-arguments
class DeveloperCog(commands.Cog):
	"""Developer utilities"""

	def __init__(self, bot):
		self.bot: discord.Bot = bot
		self.dm_channel = None # Cannot have async init
		self.bot.loop.create_task(self.get_dm_channel()) # ...so instead we get it here
		print(f"Added {self.__class__.__name__}")


	async def get_dm_channel(self):
		# This whole thing will break if this is run before the bot logs in
		await self.bot.wait_until_ready()

		dev_user = await self.bot.fetch_user(os.getenv("DEVELOPER_ID"))
		self.dm_channel = await dev_user.create_dm()


# ------------------------------------------------------------------------
# Command groups
# Change the decorator to @<name>.command()
# ------------------------------------------------------------------------
	dev = SlashCommandGroup("dev", "Developer only", guild_ids=[os.getenv("DEVELOPER_SERVER")])


# ------------------------------------------------------------------------
# Listeners
# ------------------------------------------------------------------------
	@commands.Cog.listener()
	async def on_guild_join(self, guild):
		"""DM developer"""
		await self.dm_channel.send(f"Added to **{guild.name}** ({guild.id})")


	@commands.Cog.listener()
	async def on_guild_remove(self, guild):
		"""DM developer"""

		await self.dm_channel.send(f"Removed from **{guild.name}** ({guild.id})")


	# @commands.Cog.listener()
	# async def on_application_command_error(self, ctx, exception):
	# 	"""DM developer"""

	# 	msg = f"**GuildID**: {ctx.guild.id}\n"
	# 	msg += f"**ChannelID**: {ctx.channel.id}\n"
	# 	msg += f"**UserID**: {ctx.interaction.user.id}\n"
	# 	msg += f"**Command**: /{ctx.command.qualified_name}\n"
	# 	if (ctx.selected_options):
	# 		msg += "**Options**: "
	# 		msg += ", ".join([f"{opt['name']}: {opt['value']}" for opt in ctx.selected_options]) + "\n"
	# 	msg += f"**Exception**: {exception}\n--------------------------------------------"

	# 	await self.dm_channel.send(msg[:1024])


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

		n_removed = await db.remove_guilds(bot_guild_ids)

		await ctx.respond(f"Removed {n_removed} non-member guilds from database")


# ------------------------------------------------------------------------
# /dev test
# ------------------------------------------------------------------------
	@dev.command(name="test")
	async def test(self, ctx):
		"""Dev test"""
		embed = discord.Embed(
			title="Isaac Adams",
			description="This is Isaac.")

		embed.add_field(name="Author", value="<@367692200030502912>")
		embed.add_field(name="Image Credit", value="arisu (anc)")
		embed.set_footer(text="ID: 234612983")
		embed.set_image(url="https://media.discordapp.net/attachments/958828954314223706/963872744641011734/isaac.png")

		await ctx.respond(embed=embed)

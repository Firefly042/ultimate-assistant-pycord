"""
Author @Firefly#7113
Developer-only commands
"""

import os
import json
from datetime import datetime
import aiocron
import atexit

import discord
from discord import option
from discord.commands import SlashCommandGroup
from discord.ext import commands

from db import db
from showcase_db import db as showcase_db
from localization import loc

from utils import utils

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

		# Statistics logging
		try:
			fobject = open("command_log.json", "r", encoding="utf-8")
			self.cmd_log = json.load(fobject)
			fobject.close()
		except:
			self.cmd_log = {}

		@aiocron.crontab('5/15 * * * *')
		async def every_fifteen_minutes():
			await self.commit_log()

		atexit.register(self.commit_log_at_exit)

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
# Crontabs
# https://crontab.cronhub.io/
# Crontabs appear to execute in a LIFO stack order
# Do not need to be explicitly started
# ------------------------------------------------------------------------
	async def commit_log(self):
		"""Writes command log file"""

		fobject = open("command_log.json", "w", encoding="utf-8")
		fobject.write(json.dumps(
			self.cmd_log,
			sort_keys=True,
			indent=4,
			separators=(",", ": ")
			)
		)
		fobject.close()


	def commit_log_at_exit(self):
		"""Called on exit"""

		fobject = open("command_log.json", "w", encoding="utf-8")
		fobject.write(json.dumps(
			self.cmd_log,
			sort_keys=True,
			indent=4,
			separators=(",", ": ")
			)
		)
		fobject.close()

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


	@commands.Cog.listener()
	async def on_application_command(self, ctx):
		name = ctx.command.qualified_name
		time = datetime.utcnow().strftime("%Y-%m-%d, %H:%M:%S")
		if (name not in self.cmd_log.keys()):
			self.cmd_log[name] = []

		self.cmd_log[name].append(time)


	@commands.Cog.listener()
	async def on_application_command_error(self, ctx, exception):
		"""DM developer"""

		# Cooldown errors are actually handled nicely
		if (type(exception) == commands.errors.CommandOnCooldown):
			return

		# Otherwise DM
		msg = f"**GuildID**: {ctx.guild.id}\n"
		msg += f"**ChannelID**: {ctx.channel.id}\n"
		msg += f"**UserID**: {ctx.interaction.user.id}\n"
		msg += f"**Command**: /{ctx.command.qualified_name}\n"
		if (ctx.selected_options):
			msg += "**Options**: "
			msg += ", ".join([f"{opt['name']}: {opt['value']}" for opt in ctx.selected_options]) + "\n"
		msg += f"**Exception**: {exception}\n--------------------------------------------"

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

		n_removed = await db.remove_guilds(bot_guild_ids)

		await ctx.respond(f"Removed {n_removed} non-member guilds from database")

# ------------------------------------------------------------------------
# /dev flag_showcase
# ------------------------------------------------------------------------
	@dev.command(name="flag_showcase")
	@option("char_id", str)
	@option("flag", bool, default=False)
	async def flag_showcase(self, ctx, char_id, flag):
		"""Flag a showcase character (set to True to unflag)"""

		await showcase_db.flag_character(char_id, flag)
		await ctx.respond(f"Flagged showcase {char_id} as {flag}")

# ------------------------------------------------------------------------
# /dev showcase_ban
# ------------------------------------------------------------------------
	@dev.command(name="showcase_ban")
	@option("user_id", str)
	@option("ban", bool, default=True)
	async def showcase_ban(self, ctx, user_id, ban):
		"""Ban or unban a user from the showcase (False to unban)"""

		if (ban):
			await showcase_db.add_banned_user(user_id)
			await ctx.respond(f"Banned <@{user_id}> from showcase")
		else:
			await showcase_db.remove_banned_user(user_id)
			await ctx.respond(f"Unbanned <@{user_id}> from showcase")

# ------------------------------------------------------------------------
# /dev showcase_rm
# ------------------------------------------------------------------------
	@dev.command(name="showcase_rm")
	@option("char_id", str)
	async def showcase_rm(self, ctx, char_id):
		"""Ban or unban a user from the showcase (False to unban)"""

		await showcase_db.dev_remove_character(char_id)
		await ctx.respond(f"Removed {char_id} from showcase")

# ------------------------------------------------------------------------
# /dev test
# ------------------------------------------------------------------------
	@dev.command(name="test")
	async def test(self, ctx):
		await ctx.respond("Test", ephemeral=True)
"""
Original template by @Firefly#7113, April 2022
Commands for character registration and profile management
"""
import re
import math

import discord
from discord import slash_command, option
from discord.commands import permissions, SlashCommandGroup, CommandPermission
from discord.ext import commands

# import aiocron

# from config import ADMIN_ROLE, PLAYER_ROLE
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
	"""Setup. Change TemplateCog to Class name"""
	bot.add_cog(MessageAdminCog(bot))

# pylint: disable=no-self-use
class MessageAdminCog(commands.Cog):
	"""Messaging management for mods"""

	def __init__(self, bot):
		self.bot = bot
		print(f"Added {self.__class__.__name__}")


# ------------------------------------------------------------------------
# Command groups
# Change the decorator to @<name>.command()
# ------------------------------------------------------------------------
	message_admin = SlashCommandGroup("msg_admin", "Admin messaging management")


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
# /msg_admin anon
# ------------------------------------------------------------------------
	@message_admin.command(name="anon")
	@option("toggle", str, choices=["ON", "OFF"], description="Select permission")
	@commands.has_permissions(administrator=True)
	async def toggle(self, ctx, toggle):
		"""Enable or disable anonymous messaging. All players will need a private channel to use these."""

		if (toggle == "OFF"):
			db.edit_guild(ctx.guild.id, "AnonPermitted", 0)
			await ctx.respond("Anonymous messaging is **disabled** for your server.")
			return

		# Toggle on if chosen, but warn if any characters have not been assigned private channels
		db.edit_guild(ctx.guild.id, "AnonPermitted", 1)
		msg = "Anonymous messaging is **enabled** for your server."

		chars = db.get_all_chars(ctx.guild.id)

		chars_without_channels = [char['Name'] for char in chars if not char['ChannelID']]

		if (len(chars_without_channels) > 0):
			name_list = ", ".join(chars_without_channels)
			msg += f"\n\n**These characters are missing associated channels: {name_list}**\nYou will need to assign them one with `/profile_admin edit channel` for them to use messaging commands!"

		await ctx.respond(msg)

# ------------------------------------------------------------------------
# /msg_admin channels
# ------------------------------------------------------------------------
	@message_admin.command(name="channels")
	@option("visible", bool, default=False, description="Set to True for permanent response")
	@commands.has_permissions(administrator=True)
	async def channels(self, ctx, visible):
		"""List characters and their associated messaging channels"""

		chars = db.get_all_chars(ctx.guild.id)

		# Alphabetize
		chars = sorted(chars, key=lambda d: d['Name'])

		# Iterate
		msg = "__Messaging Channels__"
		for char in chars:
			if (char['ChannelID']):
				msg += f"\n{char['Name']}: <#{char['ChannelID']}>"
			else:
				msg += f"\n{char['Name']}: **NONE**"

		await ctx.respond(msg[:1800], ephemeral=not visible)
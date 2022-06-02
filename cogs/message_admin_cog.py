"""
Author @Firefly#7113
Admin messaging commands
"""

import discord
from discord import option
from discord.commands import SlashCommandGroup
from discord.ext import commands

import db
from localization import loc


# ------------------------------------------------------------------------
# COG
# ------------------------------------------------------------------------
def setup(bot):
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
	message_admin = SlashCommandGroup("msg_admin", "Admin messaging management",
		default_member_permissions=discord.Permissions(administrator=True),
		guild_only=True,
		name_localizations=loc.group_names("msg_admin"),
		description_localizations=loc.group_descriptions("msg_admin"))


# ------------------------------------------------------------------------
# Commands
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# /msg_admin anon
# ------------------------------------------------------------------------
	@message_admin.command(name="anon",
		name_localizations=loc.command_names("msg_admin", "anon"),
		description_localizations=loc.command_descriptions("msg_admin", "anon"))
	@option("toggle", str,
		description="Select permission",
		choices=loc.choices("msg_admin", "anon", "toggle"),
		name_localizations=loc.option_names("msg_admin", "anon", "toggle"),
		description_localizations=loc.option_descriptions("msg_admin", "anon", "toggle"))
	async def toggle(self, ctx, toggle):
		"""Enable or disable anonymous messaging. All players will need a private channel to use these."""

		if (toggle == "OFF"):
			db.edit_guild(ctx.guild.id, "AnonPermitted", 0)

			res = loc.response("msg_admin", "anon", "res1", ctx.interaction.locale)
			await ctx.respond(res)
			return

		# Toggle on if chosen, but warn if any characters have not been assigned private channels
		db.edit_guild(ctx.guild.id, "AnonPermitted", 1)
		msg = loc.response("msg_admin", "anon", "res2", ctx.interaction.locale)

		chars = db.get_all_chars(ctx.guild.id)

		if chars_without_channels := [char['Name'] for char in chars if not char['ChannelID']]:
			name_list = ", ".join(chars_without_channels)
			msg += loc.response("msg_admin", "anon", "warning", ctx.interaction.locale).format(name_list)

		await ctx.respond(msg)

# ------------------------------------------------------------------------
# /msg_admin channels
# ------------------------------------------------------------------------
	@message_admin.command(name="channels",
		name_localizations=loc.command_names("msg_admin", "channels"),
		description_localizations=loc.command_descriptions("msg_admin", "channels"))
	@option("visible", bool, default=False,
		description="Set to 'True' for a permanent, visible response.",
		name_localizations=loc.common("visible-name"),
		description_localizations=loc.common("visible-desc"))
	async def channels(self, ctx, visible):
		"""List characters and their associated messaging channels"""

		chars = db.get_all_chars(ctx.guild.id)

		# Alphabetize
		chars = sorted(chars, key=lambda d: d['Name'])

		# Iterate
		msg =  loc.response("msg_admin", "channels", "res1", ctx.interaction.locale)
		for char in chars:
			if (char['ChannelID']):
				msg += f"\n{char['Name']}: <#{char['ChannelID']}>"
			else:
				msg += loc.response("msg_admin", "channels", "res2", ctx.interaction.locale).format(char["Name"])

		await ctx.respond(msg[:1800], ephemeral=not visible)

"""
Author @Firefly#7113
Player messaging commands
"""

import discord
from discord import option
from discord.commands import SlashCommandGroup
from discord.ext import commands

import db
from localization import loc

from utils import utils


# ------------------------------------------------------------------------
# COG
# ------------------------------------------------------------------------
def setup(bot):
	bot.add_cog(MessagePublicCog(bot))

# pylint: disable=no-self-use
class MessagePublicCog(commands.Cog):
	"""Messaging commands"""

	def __init__(self, bot):
		self.bot = bot
		print(f"Added {self.__class__.__name__}")


# ------------------------------------------------------------------------
# Command groups
# Change the decorator to @<name>.command()
# ------------------------------------------------------------------------
	message = SlashCommandGroup("msg", "Private messaging",
		guild_only=True,
		name_localizations=loc.group_names("msg"),
		description_localizations=loc.group_descriptions("msg"))


# ------------------------------------------------------------------------
# Commands
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# /msg whisper
# ------------------------------------------------------------------------
	@message.command(name="whisper",
		name_localizations=loc.command_names("msg", "whisper"),
		description_localizations=loc.command_descriptions("msg", "whisper"))
	@option("player", discord.Member,
		description="Character to privately message",
		name_localizations=loc.option_names("msg", "whisper", "player"),
		description_localizations=loc.option_descriptions("msg", "whisper", "player"))
	@option("message", str,
		description="Message to send, limit 1500 characters",
		name_localizations=loc.option_names("msg", "whisper", "message"),
		description_localizations=loc.option_descriptions("msg", "whisper", "message"))
	@option("recipient_name", str, default=None,
		description="The registered display name of the character, if not active",
		name_localizations=loc.common("inactive-recipient-name"),
		description_localizations=loc.common("inactive-char-desc"))
	async def whisper(self, ctx, player, message, recipient_name):
		"""Non-anonymously message another player's designated channel. Sends receipt to your channel"""

		sender = db.get_active_char(ctx.guild.id, ctx.interaction.user.id)

		# Query for recipient info
		recipient = db.get_character(ctx.guild.id, player.id, recipient_name) if recipient_name else db.get_active_char(ctx.guild.id, player.id)

		# Attempt to fetch channel (recipient)
		try:
			channel_r = await ctx.guild.fetch_channel(recipient['ChannelID'])
			embed_r_color = utils.hex_to_color(recipient['HexColor'])
		except discord.HTTPException:
			error = loc.response("msg", "whisper", "error-channel", ctx.interaction.locale).format(recipient["Name"])
			await ctx.respond(error, ephemeral=True)
			return
		except TypeError:
			error = loc.response("msg", "whisper", "error-char", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		# Attempt to fetch channel (sender)
		try:
			channel_s = await ctx.guild.fetch_channel(sender['ChannelID'])
			embed_s_color = utils.hex_to_color(sender['HexColor'])
		except discord.HTTPException:
			error = loc.response("msg", "whisper", "error-channel", ctx.interaction.locale).format(sender["Name"])
			await ctx.respond(error, ephemeral=True)
			return
		except TypeError:
			error = loc.common_res("no-character", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		# Attempt to send to recipient channel
		title_r = loc.response("msg", "whisper", "receiver-title", ctx.interaction.locale).format(sender["Name"])
		embed_r = discord.Embed(color=embed_s_color, title=title_r, description=message[:1500])
		try:
			await channel_r.send(content=f"<@{player.id}>", embed=embed_r)
		except discord.Forbidden:
			error = loc.response("msg", "whisper", "error-perms", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		# Receipt to sender channel
		title_s = loc.response("msg", "whisper", "sender-receipt", ctx.interaction.locale).format(recipient["Name"])
		embed_s = discord.Embed(color=embed_r_color, title=title_s, description=message[:1500])
		try:
			await channel_s.send(embed=embed_s)
		except discord.Forbidden:
			warning = loc.response("msg", "whisper", "warning-perms", ctx.interaction.locale).format(recipient["Name"])
			await ctx.respond(warning, ephemeral=True)
			return

		res = loc.response("msg", "whisper", "res1", ctx.interaction.locale).format(recipient["Name"])
		await ctx.respond(res, ephemeral=True)

# ------------------------------------------------------------------------
# /msg anon
# ------------------------------------------------------------------------
	@message.command(name="anon",
		name_localizations=loc.command_names("msg", "anon"),
		description_localizations=loc.command_descriptions("msg", "anon"))
	@option("player", discord.Member, description="Character to privately message")
	@option("message", str, description="Message to send. Limit 1500 characters")
	@option("recipient_name", str, default=None,
		description="The registered display name of the character, if not active",
		name_localizations=loc.common("inactive-recipient-name"),
		description_localizations=loc.common("inactive-char-desc"))
	async def anon(self, ctx, player, message, recipient_name):
		"""Anonymously message another player's designated channel. Sends receipt to your channel"""

		# Check if command is enabled
		enabled = db.get_guild_info(ctx.guild.id)["AnonPermitted"]
		if (not enabled):
			error = loc.response("msg", "anon", "error-disabled", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		sender = db.get_active_char(ctx.guild.id, ctx.interaction.user.id)

		# Query for recipient info
		recipient = db.get_character(ctx.guild.id, player.id, recipient_name) if recipient_name else db.get_active_char(ctx.guild.id, player.id)

		# Attempt to fetch channel (recipient)
		try:
			channel_r = await ctx.guild.fetch_channel(recipient['ChannelID'])
			embed_r_color = utils.hex_to_color(recipient['HexColor'])
		except discord.HTTPException:
			error = loc.response("msg", "anon", "error-channel", ctx.interaction.locale).format(recipient["Name"])
			await ctx.respond(error, ephemeral=True)
			return
		except TypeError:
			error = loc.response("msg", "anon", "error-char", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		# Attempt to fetch channel (sender)
		try:
			channel_s = await ctx.guild.fetch_channel(sender['ChannelID'])
		except discord.HTTPException:
			error = loc.response("msg", "anon", "error-channel", ctx.interaction.locale).format(sender["Name"])
			await ctx.respond(error, ephemeral=True)
			return
		except TypeError:
			error = loc.common_res("no-character", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		# Attempt to send to recipient channel
		title_r = loc.response("msg", "anon", "receiver-title", ctx.interaction.locale)
		embed_r = discord.Embed(title=title_r, description=message[:1500])
		try:
			await channel_r.send(content=f"<@{player.id}>", embed=embed_r)
		except discord.Forbidden:
			error = loc.response("msg", "anon", "error-perms", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		# Receipt to sender channel
		title_s = loc.response("msg", "anon", "sender-receipt", ctx.interaction.locale).format(recipient["Name"])
		embed_s = discord.Embed(color=embed_r_color, title=title_s, description=message[:1500])
		try:
			await channel_s.send(embed=embed_s)
		except discord.Forbidden:
			warning = loc.response("msg", "anon", "warning-perms", ctx.interaction.locale).format(recipient["Name"])
			await ctx.respond(warning, ephemeral=True)
			return

		res = loc.response("msg", "anon", "res1", ctx.interaction.locale).format(recipient["Name"])
		await ctx.respond(res, ephemeral=True)

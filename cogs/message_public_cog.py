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
	async def whisper(self, ctx, player, message):
		"""Non-anonymously message another player's designated channel. Sends receipt to your channel"""

		sender = db.get_active_char(ctx.guild.id, ctx.interaction.user.id)

		# Query for recipient info
		recipient = db.get_active_char(ctx.guild.id, player.id)

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
		embed_r = discord.Embed(color=embed_s_color, title=f"Message from {sender['Name']}", description=message[:1500])
		try:
			await channel_r.send(content=f"<@{player.id}>", embed=embed_r)
		except discord.Forbidden:
			error = loc.response("msg", "whisper", "error-perms", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		# Receipt to sender channel
		title = loc.response("msg", "whisper", "receiver-title", ctx.interaction.locale).format(recipient["Name"])
			await ctx.respond(error, ephemeral=True)
		embed_s = discord.Embed(color=embed_r_color, title=title, description=message[:1500])
		try:
			await channel_s.send(embed=embed_s)
		except discord.Forbidden:
			warning = loc.response("msg", "whisper", "warning-perms", ctx.interaction.locale).format(recipient["Name"])
			await ctx.respond(warning, ephemeral=True)
			return

		res()
		await ctx.respond(f"Messaged {recipient['Name']}!", ephemeral=True)

# ------------------------------------------------------------------------
# /msg anon
# ------------------------------------------------------------------------
	@message.command(name="anon")
	@option("player", discord.Member, description="Character to privately message")
	@option("message", str, description="Message to send. Limit 1500 characters")
	async def anon(self, ctx, player, message):
		"""Anonymously message another player's designated channel. Sends receipt to your channel"""

		# Check if command is enabled
		enabled = db.get_guild_info(ctx.guild.id)["AnonPermitted"]
		if (not enabled):
			error = loc.response("msg", "anon", "error-disabled", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		sender = db.get_active_char(ctx.guild.id, ctx.interaction.user.id)

		# God I hope discord implements dynamic command perms soon
		# Query for recipient info
		recipient = db.get_active_char(ctx.guild.id, player.id)

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
		title = loc.response("msg", "anon", "receiver-title", ctx.interaction.locale)
		embed_r = discord.Embed(title=title, description=message[:1500])
		try:
			await channel_r.send(content=f"<@{player.id}>", embed=embed_r)
		except discord.Forbidden:
			error = loc.response("msg", "anon", "error-perms", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		# Receipt to sender channel
		receipt_title = loc.response("msg", "anon", "sender-receipt", ctx.interaction.locale).format(recipient["Name"])
		embed_s = discord.Embed(color=embed_r_color, title=receipt_title, description=message[:1500])
		try:
			await channel_s.send(embed=embed_s)
		except discord.Forbidden:
			warning = loc.response("msg", "anon", "warning-perms", ctx.interaction.locale).format(recipient["Name"])
			await ctx.respond(warning, ephemeral=True)
			return

		res = loc.response("msg", "anon", "res1").format(recipient["Name"])
		await ctx.respond(res, ephemeral=True)

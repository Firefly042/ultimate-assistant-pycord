"""
Author @Firefly#7113
Player messaging commands
"""

import discord
from discord import option
from discord.commands import SlashCommandGroup
from discord.ext import commands

# import aiocron

# from config import ADMIN_ROLE, PLAYER_ROLE
import db

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
	message = SlashCommandGroup("msg", "Private messaging")


# ------------------------------------------------------------------------
# Commands
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# /msg whisper
# ------------------------------------------------------------------------
	@message.command(name="whisper")
	@option("player", discord.Member, description="Character to privately message")
	@option("message", str, description="Message to send. Limit 1500 characters")
	async def whisper(self, ctx, player, message):
		"""Non-anonymously message another player's designated channel. Sends receipt to your channel"""

		sender = db.get_active_char(ctx.guild.id, ctx.interaction.user.id)

		# God I hope discord implements dynamic command perms soon
		# Query for recipient info
		recipient = db.get_active_char(ctx.guild.id, player.id)

		# Attempt to fetch channel (recipient)
		try:
			channel_r = await ctx.guild.fetch_channel(recipient['ChannelID'])
			embed_r_color = utils.hex_to_color(recipient['HexColor'])
		except discord.HTTPException:
			await ctx.respond(f"Missing or invalid channel for {recipient['Name']}!", ephemeral=True)
			return
		except TypeError:
			await ctx.respond("That user does not have an active character!", ephemeral=True)
			return

		# Attempt to fetch channel (sender)
		try:
			channel_s = await ctx.guild.fetch_channel(sender['ChannelID'])
			embed_s_color = utils.hex_to_color(sender['HexColor'])
		except discord.HTTPException:
			await ctx.respond(f"Missing or invalid channel for {sender['Name']}!", ephemeral=True)
			return
		except TypeError:
			await ctx.respond("You do not have an active character!", ephemeral=True)
			return

		# Attempt to send to recipient channel
		embed_r = discord.Embed(color=embed_s_color, title=f"Message from {sender['Name']}", description=message[:1500])
		try:
			await channel_r.send(content=f"<@{player.id}>", embed=embed_r)
		except discord.Forbidden:
			await ctx.respond("Missing permissions in recipient channel!", ephemeral=True)
			return

		# Receipt to sender channel
		embed_s = discord.Embed(color=embed_r_color, title=f"Message to {recipient['Name']}", description=message[:1500])
		try:
			await channel_s.send(embed=embed_s)
		except discord.Forbidden:
			await ctx.respond(f"Messaged {recipient['Name']}, but missing permissions in your channel!", ephemeral=True)
			return

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
			await ctx.respond("Anonymous messaging is disabled in this server!", ephemeral=True)
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
			await ctx.respond(f"Missing or invalid channel for {recipient['Name']}!", ephemeral=True)
			return
		except TypeError:
			await ctx.respond("That user does not have an active character!", ephemeral=True)
			return

		# Attempt to fetch channel (sender)
		try:
			channel_s = await ctx.guild.fetch_channel(sender['ChannelID'])
		except discord.HTTPException:
			await ctx.respond(f"Missing or invalid channel for {sender['Name']}!", ephemeral=True)
			return
		except TypeError:
			await ctx.respond("You do not have an active character!", ephemeral=True)
			return

		# Attempt to send to recipient channel
		embed_r = discord.Embed(title="Anonymous message!", description=message[:1500])
		try:
			await channel_r.send(content=f"<@{player.id}>", embed=embed_r)
		except discord.Forbidden:
			await ctx.respond("Missing permissions in recipient channel!", ephemeral=True)
			return

		# Receipt to sender channel
		embed_s = discord.Embed(color=embed_r_color, title=f"Anonymous message to {recipient['Name']}", description=message[:1500])
		try:
			await channel_s.send(embed=embed_s)
		except discord.Forbidden:
			await ctx.respond(f"Messaged {recipient['Name']}, but missing permissions in your channel!", ephemeral=True)
			return

		await ctx.respond(f"Messaged {recipient['Name']}!", ephemeral=True)

"""
Author @Firefly#7113
Commands for character registration and profile management
"""

import discord
from discord import option
from discord.commands import SlashCommandGroup
from discord.ext import commands

import db


# ------------------------------------------------------------------------
# COMPONENT CLASSES AND CONSTANTS
# ------------------------------------------------------------------------


# ------------------------------------------------------------------------
# COG
# ------------------------------------------------------------------------
def setup(bot):
	bot.add_cog(ProfileAdminCog(bot))

# pylint: disable=no-self-use, too-many-arguments
class ProfileAdminCog(commands.Cog):
	"""Admin profile registration and editing"""

	def __init__(self, bot):
		self.bot = bot
		print(f"Added {self.__class__.__name__}")


# ------------------------------------------------------------------------
# Command groups
# Change the decorator to @<name>.command()
# ------------------------------------------------------------------------
	profile_admin = SlashCommandGroup("profile_admin", "Admin Profile setup")
	profile_admin_edit = profile_admin.create_subgroup("edit", "Admin profile editing")


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
# /profile_admin new
# ------------------------------------------------------------------------
	@profile_admin.command(name="new")
	@option("player", discord.Member, description="Who will play this character")
	@option("name", str, description="The character's given/default name to display. 32 character max")
	@option("surname", str, description="The rest of the character's name, if any. 32 character max", default=None)
	@option("channel", discord.TextChannel, description="Where anonymous messages and whispers will be sent.", default=None)
	@commands.has_permissions(administrator=True)
	async def profile_admin_new(self, ctx, player, name, surname, channel):
		"""Register a player, character, and name to the bot"""

		name = name[:32]
		if (surname):
			surname = surname[:32]

		if (channel):
			channel_id = channel.id
		else:
			channel_id = None

		# Add to db, catches uniqueness error
		try:
			db.new_character(ctx.guild.id, player.id, name, surname, channel_id)
		except:
			await ctx.respond(f"Cannot add {name} without causing a duplicate!", ephemeral=True)
			return

		# Set it as active character for the player
		db.set_active_character(ctx.guild.id, player.id, name)

		# Discord response (success)
		if (not surname):
			surname = ""
		await ctx.respond(f"Added {name} {surname}")

# ------------------------------------------------------------------------
# /profile_admin edit text
# ------------------------------------------------------------------------
	@profile_admin_edit.command(name="text")
	@option("player", discord.Member, description="The player")
	@option("name", str, description="Character's display name.")
	@option("field_to_change", str, choices=["Name", "Surname"], description="Specify Name or Surname.")
	@option("new_value", str, description="New name or surname. 32 character maximum")
	@commands.has_permissions(administrator=True)
	async def profile_admin_edit_text(self, ctx, player, name, field_to_change, new_value):
		"""Edit a character's name or surname"""

		new_value = new_value[:32]

		# Update character, catches uniqueness error. Returns true or false if anything was changed
		try:
			char_updated = db.update_character(ctx.guild.id, player.id, name, field_to_change, new_value)
		except:
			await ctx.respond(f"Cannot edit {name} without causing a duplicate!", ephemeral=True)
			return

		# Notify if nothing was changed (char not found)
		if (not char_updated):
			await ctx.respond("Could not find a character with that name for that player!", ephemeral=True)
			return

		# Discord response (success)
		await ctx.respond(f"Updated character for {player.name}.")

# ------------------------------------------------------------------------
# /profile_admin edit channel
# ------------------------------------------------------------------------
	@profile_admin_edit.command(name="channel",)
	@option("player", discord.Member)
	@option("name", str)
	@option("channel", discord.TextChannel)
	@commands.has_permissions(administrator=True)
	async def profile_admin_edit_channel(self, ctx, player, name, channel):
		"""Add or edit a character's associated channel"""

		# No need to check for uniqueness because no name changes
		char_updated = db.update_character(ctx.guild.id, player.id, name, "ChannelID", channel.id)

		# Notify if nothing was changed (char not found)
		if (not char_updated):
			await ctx.respond("Could not find a character with that name for that player!", ephemeral=True)
			return

		# Discord response
		await ctx.respond(f"Updated character for {player.name}")

# ------------------------------------------------------------------------
# /profile_admin rm
# ------------------------------------------------------------------------
	@profile_admin.command(name="rm")
	@option("player", discord.Member, description="Who played this character")
	@option("name", str, description="The character's display name")
	@commands.has_permissions(administrator=True)
	async def profile_admin_rm(self, ctx, player, name):
		"""Unregister a character"""

		char_removed = db.remove_character(ctx.guild.id, player.id, name)

		if (not char_removed):
			await ctx.respond("Could not find that character under that player!", ephemeral=True)
			return

		await ctx.respond(f"Removed {name}. This player may not have an active character anymore, but can `/profile swap` to another!")

# ------------------------------------------------------------------------
# /profile_admin disable
# ------------------------------------------------------------------------
	@profile_admin.command(name="disable")
	@option("player", discord.Member)
	@option("name", str)
	@commands.has_permissions(administrator=True)
	async def profile_admin_disable(self, ctx, player, name):
		"""Set a character to inactive (disabling the player's ability to use commands)"""

		# No need to check for uniqueness because no name changes
		char_updated = db.update_character(ctx.guild.id, player.id, name, "Active", 0)

		# Notify if nothing was changed (char not found)
		if (not char_updated):
			await ctx.respond("Could not find a character with that name for that player!", ephemeral=True)
			return

		# Discord response
		await ctx.respond(f"Disabled character for {player.name}")

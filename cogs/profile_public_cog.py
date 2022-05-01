"""
Author @Firefly#7113
Player/Public ommands for character profile management
"""

import re

import discord
from discord import option
from discord.commands import SlashCommandGroup
from discord.ext import commands

# import aiocron

# from config import ADMIN_ROLE, PLAYER_ROLE
import db

from utils import utils

# ------------------------------------------------------------------------
# COMPONENT CLASSES AND CONSTANTS
# ------------------------------------------------------------------------


# ------------------------------------------------------------------------
# COG
# ------------------------------------------------------------------------
def setup(bot):
	bot.add_cog(ProfilePublicCog(bot))

# pylint: disable=no-self-use, bare-except
class ProfilePublicCog(commands.Cog):
	"""Profile commands for public or player use"""

	def __init__(self, bot):
		self.bot = bot
		print(f"Added {self.__class__.__name__}")


# ------------------------------------------------------------------------
# Command groups
# Change the decorator to @<name>.command()
# ------------------------------------------------------------------------
	profile = SlashCommandGroup("profile", "Character profiles")
	profile_embed = profile.create_subgroup("embed", "Profile editing")


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
# /profile embed edit
# ------------------------------------------------------------------------
	@profile_embed.command(name="edit")
	@option("name", str, description="Your character's display name")
	@option("field_to_change", str, choices=["HexColor", "ThumbnailURL", "ImageURL"])
	@option("new_value", str, description="Hex code (without #) or image url")
	async def profile_embed_edit(self, ctx, name, field_to_change, new_value):
		"""Edit profile embed fields (color, thumbnail, or image)"""

		# Obligatory hex code regex validation, exits without attempting
		if (field_to_change == "HexColor"):
			match = re.search(r'^(?:[0-9a-fA-F]{3}){1,2}$', new_value)
			if (not match):
				await ctx.respond(f"#{new_value} is not a valid hex!", ephemeral=True)
				return

		# Get previous image content
		if (field_to_change == "ThumbnailURL"):
			previous_content = db.get_character(ctx.guild.id, ctx.interaction.user.id, name)["ThumbnailURL"]
		elif (field_to_change == "ImageURL"):
			previous_content = db.get_character(ctx.guild.id, ctx.interaction.user.id, name)["ImageURL"]

		# Update db values. No name changes so uniqueness is not an issue
		char_updated = db.update_character(ctx.guild.id, ctx.interaction.user.id, name, field_to_change, new_value)

		# Notify if no changes (char not found)
		if (not char_updated):
			await ctx.respond("Could not find a character with that name for you!", ephemeral=True)
			return

		# Preview embed, warn and revert if malformed image URL
		try:
			embed = utils.get_profile_embed(ctx.guild.id, ctx.interaction.user.id, name)
			await ctx.respond("Updated", embed=embed, ephemeral=True)
		except discord.HTTPException:
			await ctx.respond("I cannot display that image URL! Reverting.", ephemeral=True)
			db.update_character(ctx.guild.id, ctx.interaction.user.id, name, field_to_change, previous_content)

# ------------------------------------------------------------------------
# /profile embed field
# ------------------------------------------------------------------------
	@profile_embed.command(name="field")
	@option("name", str, description="Your character's display name")
	@option("field_title", str, description="Up to 256 characters")
	@option("field_content", str, description="Up to 1024 characters")
	async def profile_embed_field(self, ctx, name, field_title, field_content):
		"""Add or edit up to 25 fields to your character's profile embed"""

		# Get existing fields from db and convert to python dict
		fields = db.get_character(ctx.guild.id, ctx.interaction.user.id, name)["ProfileFields"]
		fields = utils.str_to_dict(fields)

		# Enforce embed length limits
		field_title = field_title[:256]
		field_content = field_content[:1024]

		# Enforce limit of 25 fields
		if (field_title not in fields.keys() and len(fields) == 25):
			await ctx.respond("You must remove a field before adding a new one!", ephemeral=True)
			return

		# Make changes to dict
		fields[field_title] = field_content

		# Update db, no uniqueness risks
		char_updated = db.update_character(ctx.guild.id, ctx.interaction.user.id, name, "ProfileFields", utils.dict_to_str(fields))

		# Notify if char not found
		if (not char_updated):
			await ctx.respond("Could not find a character with that name for you!", ephemeral=True)
			return


		# Attempt to send embed and warn if limits have been exceeded
		try:
			embed = utils.get_profile_embed(ctx.guild.id, ctx.interaction.user.id, name)
			await ctx.respond("Updated", embed=embed, ephemeral=True)
		except:
			await ctx.respond("Your embed has exceeded the maximum length of 6000. Reverting.", ephemeral=True)
			fields.pop(field_title)
			db.update_character(ctx.guild.id, ctx.interaction.user.id, name, "ProfileFields", utils.dict_to_str(fields))

# ------------------------------------------------------------------------
# /profile embed desc
# ------------------------------------------------------------------------
	@profile_embed.command(name="desc")
	@option("name", str, description="Your character's display name")
	@option("content", str, description="Up to 4096 characters")
	async def profile_embed_desc(self, ctx, name, content):
		"""Add or edit profile embed description"""

		# Get previous content, if any
		previous_content = db.get_character(ctx.guild.id, ctx.interaction.user.id, name)["ProfileDesc"]

		# Enforce embed length limits
		content = content[:4096]

		# Update db, no uniqueness risks
		char_updated = db.update_character(ctx.guild.id, ctx.interaction.user.id, name, "ProfileDesc", content)

		# Notify if char not found
		if (not char_updated):
			await ctx.respond("Could not find a character with that name for you!", ephemeral=True)
			return


		# Attempt to send embed and warn if limits have been exceeded
		try:
			embed = utils.get_profile_embed(ctx.guild.id, ctx.interaction.user.id, name)
			await ctx.respond("Updated", embed=embed, ephemeral=True)
		except:
			await ctx.respond("Your embed has exceeded the maximum length of 6000. Reverting.", ephemeral=True)
			db.update_character(ctx.guild.id, ctx.interaction.user.id, name, "ProfileDesc", previous_content)

# ------------------------------------------------------------------------
# /profile swap
# ------------------------------------------------------------------------
	@profile.command(name="swap")
	@option("name", str, description="Display name of character to swap to")
	@option("visible", bool, default=False, description="Set to True for a permanent reply")
	async def profile_swap(self, ctx, name, visible):
		"""Set your active character"""

		try:
			db.set_active_character(ctx.guild.id, ctx.interaction.user.id, name)
		except:
			await ctx.respond(f"Cannot find a character named {name} for you!", ephemeral=True)
			return

		await ctx.respond(f"Swapped character to {name}", ephemeral=not visible)

# ------------------------------------------------------------------------
# /profile current
# ------------------------------------------------------------------------
	@profile.command(name="current")
	@option("visible", bool, default=False, description="Set to True for a permanent reply")
	async def profile_current(self, ctx, visible):
		"""Check your active character"""

		char = db.get_active_char(ctx.guild.id, ctx.interaction.user.id)
		try:
			await ctx.respond(f"You are currently playing as **{char['Name']}**", ephemeral=not visible)
		except TypeError:
			await ctx.respond("You do not currently have an active character!", ephemeral=True)

# ------------------------------------------------------------------------
# /profile view
# ------------------------------------------------------------------------
	@profile.command(name="view")
	@option("player", discord.Member, description="The user")
	@option("name", str, description="The character's display (first) name")
	@option("visible", bool, default=False, description="Set to True for a permanent reply")
	async def profile_view(self, ctx, player, name, visible):
		"""View a character's profile. Invisible by default"""

		embed = utils.get_profile_embed(ctx.guild.id, player.id, name)
		await ctx.respond(embed=embed, ephemeral=not visible)

	@profile_view.error
	async def profile_view_error(self, ctx, _):
		"""Won't catch exception in normal method for some reason. So it's here."""
		await ctx.respond("Cannot find that character for that player!", ephemeral=True)

# ------------------------------------------------------------------------
# /profile list
# ------------------------------------------------------------------------
	@profile.command(name="list", )
	@option("visible", bool, default=False, description="Set to True for a permanent reply")
	async def profile_list(self, ctx, visible):
		"""Lists all registered characters for server"""
		all_chars = db.get_all_chars(ctx.guild.id)

		embed = discord.Embed(title=f"Characters in {ctx.guild.name}")

		# Order chars by name, error if no characters
		try:
			all_chars = sorted(all_chars, key=lambda d: d["Name"])
		except TypeError:
			await ctx.respond("This server has no registered characters!")
			return

		msg = ""
		for char in all_chars:
			name = char["Name"]
			if char["Surname"]:
				name += " " + char["Surname"]

			player = f"<@{char['PlayerID']}>"
			msg += f"{name} ({player})\n"

		embed.description = msg[:3900]
		await ctx.respond(embed=embed, ephemeral=not visible)

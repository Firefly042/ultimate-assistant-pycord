"""
Author @Firefly#7113
Player/Public commands for character profile management
"""

import re

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
	profile = SlashCommandGroup("profile", "Character profiles",
		name_localizations=loc.group_names("profile"),
		description_localizations=loc.group_descriptions("profile"))

	profile_embed = profile.create_subgroup("embed", "Profile editing")
	profile_embed.name_localizations = loc.group_names("profile_embed")
	profile_embed.description_localizations = loc.group_descriptions("profile_embed")


# ------------------------------------------------------------------------
# Commands
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# /profile embed edit
# ------------------------------------------------------------------------
	@profile_embed.command(name="edit",
		name_localizations=loc.command_names("profile_embed", "edit"),
		description_localizations=loc.command_descriptions("profile_embed", "edit"))
	@option("name", str,
		description="Your character's display name",
		name_localizations=loc.option_names("profile_embed", "edit", "name"),
		description_localizations=loc.option_descriptions("profile_embed", "edit", "name"))
	@option("field_to_change", str,
		choices=["HexColor", "ThumbnailURL", "ImageURL"])
	@option("new_value", str,
		description="Hex code (without #) or image url",
		name_localizations=loc.option_names("profile_embed", "edit", "new_value"),
		description_localizations=loc.option_descriptions("profile_embed", "edit", "new_value"))
	async def profile_embed_edit(self, ctx, name, field_to_change, new_value):
		"""Edit profile embed fields (color, thumbnail, or image)"""

		# Obligatory hex code regex validation, exits without attempting
		if (field_to_change == "HexColor"):
			match = re.search(r'^(?:[0-9a-fA-F]{3}){1,2}$', new_value)
			if (not match):
				error = loc.response("profile_embed", "edit", "error-hex", ctx.interaction.locale).format(new_value)
				await ctx.respond(error, ephemeral=True)
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
			error = loc.response("profile_embed", "edit", "error-missing", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		# Preview embed, warn and revert if malformed image URL
		try:
			embed = utils.get_profile_embed(ctx.guild.id, ctx.interaction.user.id, name)
			res = loc.response("profile_embed", "edit", "res1", ctx.interaction.locale)
			await ctx.respond(res, embed=embed, ephemeral=True)
		except discord.HTTPException:
			error = loc.response("profile_embed", "edit", "error-url", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			db.update_character(ctx.guild.id, ctx.interaction.user.id, name, field_to_change, previous_content)

# ------------------------------------------------------------------------
# /profile embed field
# ------------------------------------------------------------------------
	@profile_embed.command(name="field",
		name_localizations=loc.command_names("profile_embed", "field"),
		description_localizations=loc.command_descriptions("profile_embed", "field"))
	@option("name", str,
		description="Your character's display name",
		name_localizations=loc.option_names("profile_embed", "field", "name"),
		description_localizations=loc.option_descriptions("profile_embed", "field", "name"))
	@option("field_title", str,
		description="Up to 256 characters",
		name_localizations=loc.option_names("profile_embed", "field", "field_title"),
		description_localizations=loc.option_descriptions("profile_embed", "field", "field_title"))
	@option("field_content", str,
		description="Up to 1024 characters",
		name_localizations=loc.option_names("profile_embed", "field", "field_content"),
		description_localizations=loc.option_descriptions("profile_embed", "field", "field_content"))
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
			error = loc.response("profile_embed", "field", "error-limit", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		# Make changes to dict
		fields[field_title] = field_content

		# Update db, no uniqueness risks
		char_updated = db.update_character(ctx.guild.id, ctx.interaction.user.id, name, "ProfileFields", utils.dict_to_str(fields))

		# Notify if char not found
		if (not char_updated):
			error = loc.response("profile_embed", "field", "error-missing", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return


		# Attempt to send embed and warn if limits have been exceeded
		try:
			embed = utils.get_profile_embed(ctx.guild.id, ctx.interaction.user.id, name)
			res = loc.response("profile_embed", "field", "res1", ctx.interaction.locale)
			await ctx.respond(res, embed=embed, ephemeral=True)
		except:
			error = loc.response("profile_embed", "field", "error-length", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			fields.pop(field_title)
			db.update_character(ctx.guild.id, ctx.interaction.user.id, name, "ProfileFields", utils.dict_to_str(fields))

# ------------------------------------------------------------------------
# /profile embed desc
# ------------------------------------------------------------------------
	@profile_embed.command(name="desc",
		name_localizations=loc.command_names("profile_embed", "desc"),
		description_localizations=loc.command_descriptions("profile_embed", "desc"))
	@option("name", str,
		description="Your character's display name",
		name_localizations=loc.option_names("profile_embed", "desc", "name"),
		description_localizations=loc.option_descriptions("profile_embed", "desc", "name"))
	@option("content", str,
		description="Up to 4096 characters",
		name_localizations=loc.option_names("profile_embed", "desc", "content"),
		description_localizations=loc.option_descriptions("profile_embed", "desc", "content"))
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
			error = loc.response("profile_embed", "desc", "error-missing", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return


		# Attempt to send embed and warn if limits have been exceeded
		try:
			res = loc.response("profile_embed", "desc", "res1", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			await ctx.respond(res, embed=embed, ephemeral=True)
		except:
			error = loc.response("profile_embed", "desc", "error-length", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			db.update_character(ctx.guild.id, ctx.interaction.user.id, name, "ProfileDesc", previous_content)

# ------------------------------------------------------------------------
# /profile swap
# ------------------------------------------------------------------------
	@profile.command(name="swap",
		name_localizations=loc.command_names("profile", "swap"),
		description_localizations=loc.command_descriptions("profile", "swap"))
	@option("name", str,
		description="Display name of character to swap to",
		name_localizations=loc.option_names("profile", "swap", "name"),
		description_localizations=loc.option_descriptions("profile", "swap", "name"))
	@option("visible", bool, default=False,
		description="Set to 'True' for a permanent, visible response.",
		name_localizations=loc.common("visible-name"),
		description_localizations=loc.common("visible-desc"))
	async def profile_swap(self, ctx, name, visible):
		"""Set your active character"""

		try:
			db.set_active_character(ctx.guild.id, ctx.interaction.user.id, name)
		except:
			error = loc.response("profile", "swap", "error-missing", ctx.interaction.locale).format(name)
			await ctx.respond(error, ephemeral=True)
			return

		res = loc.response("profile", "swap", "res1", ctx.interaction.locale).format(name)
		await ctx.respond(res, ephemeral=not visible)

# ------------------------------------------------------------------------
# /profile current
# ------------------------------------------------------------------------
	@profile.command(name="current",
		name_localizations=loc.command_names("profile", "current"),
		description_localizations=loc.command_descriptions("profile", "current"))
	@option("visible", bool, default=False,
		description="Set to 'True' for a permanent, visible response.",
		name_localizations=loc.common("visible-name"),
		description_localizations=loc.common("visible-desc"))
	async def profile_current(self, ctx, visible):
		"""Check your active character"""

		char = db.get_active_char(ctx.guild.id, ctx.interaction.user.id)
		try:
			res = loc.response("profile", "current", "res1", ctx.interaction.locale).format(char["Name"])
			await ctx.respond(res, ephemeral=not visible)
		except TypeError:
			error = loc.common("no-character")
			await ctx.respond(error, ephemeral=True)

# ------------------------------------------------------------------------
# /profile view
# ------------------------------------------------------------------------
	@profile.command(name="view",
		name_localizations=loc.command_names("profile", "view"),
		description_localizations=loc.command_descriptions("profile", "view"))
	@option("player", discord.Member,
		description="The user who plays this character",
		name_localizations=loc.option_names("profile", "view", "player"),
		description_localizations=loc.option_descriptions("profile", "view", "player"))
	@option("name", str,
		description="Character's display name (usually given name)",
		name_localizations=loc.option_names("profile", "view", "name"),
		description_localizations=loc.option_descriptions("profile", "view", "name"))
	@option("visible", bool, default=False,
		description="Set to 'True' for a permanent, visible response.",
		name_localizations=loc.common("visible-name"),
		description_localizations=loc.common("visible-desc"))
	async def profile_view(self, ctx, player, name, visible):
		"""View a character's profile"""

		embed = utils.get_profile_embed(ctx.guild.id, player.id, name)

		try:
			await ctx.respond(embed=embed, ephemeral=not visible)
		except discord.HTTPException:
			error = loc.response("profile", "view", "error-url", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)

	@profile_view.error
	async def profile_view_error(self, ctx, _):
		"""Won't catch exception in normal method for some reason. So it's here."""

		error = loc.response("profile", "view", "error-missing", ctx.interaction.locale)
		await ctx.respond(error, ephemeral=True)

# ------------------------------------------------------------------------
# /profile list
# ------------------------------------------------------------------------
	@profile.command(name="list",
		name_localizations=loc.command_names("profile", "list"),
		description_localizations=loc.command_descriptions("profile", "list"))
	@option("visible", bool, default=False,
		description="Set to 'True' for a permanent, visible response.",
		name_localizations=loc.common("visible-name"),
		description_localizations=loc.common("visible-desc"))
	async def profile_list(self, ctx, visible):
		"""Lists all registered characters for this server"""

		all_chars = db.get_all_chars(ctx.guild.id)

		title = loc.response("profile", "list", "res1", ctx.interaction.locale).format(ctx.guild.name)
		embed = discord.Embed(title=title)

		# Order chars by name, error if no characters
		try:
			all_chars = sorted(all_chars, key=lambda d: d["Name"])
		except TypeError:
			error = loc.response("profile", "list", "error-nochars", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
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

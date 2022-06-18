"""
Author @Firefly#7113
Developer-only commands
"""

import os
import re
import math

import discord
from discord import option
from discord.commands import SlashCommandGroup
from discord.ext import commands

from showcase_db import db
from localization import loc
from utils import utils
from utils.embed_list import EmbedList


# ------------------------------------------------------------------------
# COMPONENT CLASSES AND CONSTANTS
# ------------------------------------------------------------------------
def make_showcase_embed(char, locale):
	embed = discord.Embed(
		title=char["name"] if not char["surname"] else f"{char['name']} {char['surname']}",
		color=utils.hex_to_color(char["hexcolor"]),
		description=char["description"])
		
	embed.set_footer(text=loc.common_res("showcase-embed-footer", locale).format(id=char["charid"]))
	
	if (char["imageurl"]):
		embed.set_image(url=char["imageurl"])

	# Author field
	embed.add_field(
		name=loc.common_res("showcase-author-field", locale),
		value=f"<@{char['authorid']}>")

	# Image credit field
	if (char["imagecredit"]):
		embed.add_field(
			name=loc.common_res("showcase-credit-field", locale),
			value=char["imagecredit"])

	return embed


def make_char_list_embeds(characters, locale, with_user=False):
	"""Takes character list (sorted alphabetically)"""

	# Need to make a copy since a reference is passed and the unedited array is needed later
	characters_for_embed = characters.copy()
	n_embeds = math.ceil(len(characters) / 20)
	embeds = [discord.Embed(title=f"{i+1}/{n_embeds}") for i in range(n_embeds)]

	for i in range(n_embeds):
		for j in range(20):
			try:
				char = characters_for_embed.pop(0)
			except IndexError:
				break

			# Name 
			field_i_title = char["name"] if not char["surname"] else f"{char['name']} {char['surname']}"

			# Should flag any characters where approved = false
			if (not char["approved"]):
				field_i_title += "*"

			field_i_val = f"({char['charid']})"
			if (with_user):
				field_i_val += f" <@{char['authorid']}>"
			
			field_i_val += "\n" + char["description"][:180]
			
			if (len(char["description"]) > 180):
				field_i_val += "..."

			embeds[i].add_field(name=field_i_title, value=field_i_val, inline=False)
			embeds[i].set_footer(text=loc.common_res("showcase-flagged-footer", locale))

	return embeds


class InputModal(discord.ui.Modal):
	def __init__(self, name, surname, hex_color, image_url, image_credit, ctx, embed, dm_channel):
		super().__init__(title=loc.response("showcase", "submit", "modal-title", ctx.interaction.locale))

		self.embed = embed
		self.dm_channel = dm_channel
		self.ctx = ctx
		self.name = name
		self.surname = surname
		self.hex_color = hex_color
		self.image_url = image_url
		self.image_credit = image_credit

		self.add_item(discord.ui.InputText(
			style=discord.InputTextStyle.multiline,
			label=loc.response("showcase", "submit", "modal-label", ctx.interaction.locale),
			min_length=1,
			max_length=2000))


	async def callback(self, interaction):
		"""Submit input and edit character database entry"""
		
		content = self.children[0].value
		self.embed.description = content

		try:
			res = loc.response("showcase", "submit", "res1", self.ctx.interaction.locale)
			await interaction.response.send_message(content=res, embed=self.embed, ephemeral=True)
		except discord.HTTPException:
			error = loc.response("showcase", "submit", "error-url", self.ctx.interaction.locale)
			await interaction.response.send_message(error, ephemeral=True)
			return

		# Add to database
		await db.add_character(self.ctx.interaction.user.id, self.ctx.interaction.id, self.name, self.surname, self.hex_color, content, self.image_url, self.image_credit)

		# DM Embed to developer for screening
		await self.dm_channel.send(content="**SHOWCASE SUBMISSION**", embed=self.embed)
		self.stop()


class InputUpdateModal(discord.ui.Modal):
	def __init__(self, char, ctx, dm_channel):
		super().__init__(title=loc.response("showcase_edit", "desc", "modal-title", ctx.interaction.locale))

		self.char = dict(char)
		self.dm_channel = dm_channel
		self.ctx = ctx

		self.add_item(discord.ui.InputText(
			style=discord.InputTextStyle.multiline,
			label="input-text",
			value=char["description"][:2000],
			min_length=1,
			max_length=2000))


	async def callback(self, interaction):
		"""Submit input and edit character database entry"""
		
		content = self.children[0].value
		self.char["description"] = content
		await db.edit_character(self.ctx.interaction.user.id, self.char["charid"], "description", content)

		# DM Embed to developer for screening
		embed = make_showcase_embed(self.char, interaction.locale)
		await self.dm_channel.send(content="**SHOWCASE UPDATE**", embed=embed)

		await interaction.response.send_message(embed=embed, ephemeral=True)

		self.stop()


class EmbedMenuList(discord.ui.View):

	def __init__(self, embeds, interaction, characters, visible):
		super().__init__(timeout=120)

		self.embeds = embeds
		self.interaction = interaction
		self.characters = characters
		self.visible = visible

		self.prev_button = [c for c in self.children if c.custom_id == "prev"][0]
		self.next_button = [c for c in self.children if c.custom_id == "next"][0]

		if (len(embeds) > 1):
			self.next_button.disabled = False

		self.current_page = 0
		self.max_pages = len(embeds)

		# Initialize select menu
		self.current_options = [discord.SelectOption(
			label=char["name"] if not char["surname"] else f"{char['name']} {char['surname']}",
			value=str(char["charid"])
			) for char in self.characters[0:19]]

		self.select_menu = [c for c in self.children if c.custom_id == "select"][0]
		self.select_menu.placeholder = loc.common_res("showcase-select-placeholder", interaction.locale)
		self.select_menu.options = self.current_options
		self.select_menu.row = 1

	async def on_timeout(self):
		"""Disable and stop listening for interaction"""

		try:
			self.disable_all_items()
			await self.interaction.edit_original_message(view=self)
		except discord.errors.NotFound:
			return


	# Previous page
	@discord.ui.button(custom_id="prev",
		label="<",
		style = discord.ButtonStyle.red,
		disabled = True,
		row=0
	)
	async def button_prev_callback(self, _, interaction):
		"""Previous embed"""

		self.current_page -= 1
		self.next_button.disabled = False
		if (self.current_page == 0):
			self.prev_button.disabled = True

		# Update select menu options
		self.current_options = [discord.SelectOption(
			label=char["name"] if not char["surname"] else f"{char['name']} {char['surname']}",
			value=str(char["charid"])
			) for char in self.characters[20*self.current_page:20*self.current_page+19]]

		self.select_menu.options = self.current_options

		await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)


	# Next page
	@discord.ui.button(custom_id="next",
		label=">",
		style = discord.ButtonStyle.green,
		disabled = True,
		row=0
	)
	async def button_next_callback(self, _, interaction):
		"""Next embed"""

		self.current_page += 1
		self.prev_button.disabled = False
		if (self.current_page == len(self.embeds)-1):
			self.next_button.disabled = True

		# Update select menu options
		self.current_options = [discord.SelectOption(
			label=char["name"] if not char["surname"] else f"{char['name']} {char['surname']}",
			value=str(char["charid"])
			) for char in self.characters[20*self.current_page:20*self.current_page+19]]

		self.select_menu.options = self.current_options

		await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)


	@discord.ui.select(custom_id="select")
	async def select_callback(self, select, interaction):
		char = [c for c in self.characters if str(c["charid"]) == select.values[0]][0]
		embed = make_showcase_embed(char, interaction.locale)
		await interaction.response.send_message(embed=embed, ephemeral=not self.visible)


# ------------------------------------------------------------------------
# COG
# ------------------------------------------------------------------------
def setup(bot):
	bot.add_cog(ShowcasePublicCog(bot))

# pylint: disable=no-self-use, too-many-arguments
class ShowcasePublicCog(commands.Cog):
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
	showcase = SlashCommandGroup("showcase", "Public character showcase",
		name_localizations=loc.group_names("showcase"),
		description_localizations=loc.group_descriptions("showcase"))

	edit = showcase.create_subgroup("edit", "Edit existing showcase")
	edit.name_localizations = loc.group_names("showcase_edit")
	edit.description_localizations = loc.group_descriptions("showcase_edit")


# ------------------------------------------------------------------------
# Commands
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# /showcase submit
# ------------------------------------------------------------------------
	@showcase.command(name="submit",
		name_localizations=loc.command_names("showcase", "submit"),
		description_localizations=loc.command_descriptions("showcase", "submit"))
	@option("firstname", str,
		description="The display name of character (64 character max)",
		name_localizations=loc.option_names("showcase", "submit", "firstname"),
		description_localizations=loc.option_descriptions("showcase", "submit", "firstname"))
	@option("surname", str, default=None,
		description="The surname of character (64 character max)",
		name_localizations=loc.option_names("showcase", "submit", "surname"),
		description_localizations=loc.option_descriptions("showcase", "submit", "surname"))
	@option("hex_color", str, default="000000",
		description="Optional embed hex color (without '#')",
		name_localizations=loc.option_names("showcase", "submit", "hex_color"),
		description_localizations=loc.option_descriptions("showcase", "submit", "hex_color"))
	@option("image_url", str, default=None,
		description="Optional image url. Credit must be provided, even to yourself.",
		name_localizations=loc.option_names("showcase", "submit", "image_url"),
		description_localizations=loc.option_descriptions("showcase", "submit", "image_url"))
	@option("image_credit", str, default=None,
		description="Brief credit for image (128 character max)",
		name_localizations=loc.option_names("showcase", "submit", "image_credit"),
		description_localizations=loc.option_descriptions("showcase", "submit", "image_credit"))
	async def submit(self, ctx, firstname, surname, hex_color, image_url, image_credit):
		"""Submit an original character to UA's public showcase. You will be prompted for a description."""

		# Banned users cannot submit new characters
		if (str(ctx.interaction.user.id) in db.get_banned_users_cache()):
			error = loc.response("showcase", "submit", "error-banned", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return


		# Enforce character limit of 100
		existing_chars = await db.get_user_chars(ctx.interaction.user.id)
		if (len(existing_chars) == 100):
			error = loc.response("showcase", "submit", "error-limit", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		# Enforce limits
		firstname = firstname[:64]
		if (surname):
			surname = surname[:64]

		# Hex validity check
		match = re.search(r'^(?:[0-9a-fA-F]{6})$', hex_color)
		if (not match):
			error = loc.response("showcase", "submit", "error-hex", ctx.interaction.locale).format(hex_color)
			await ctx.respond(error, ephemeral=True)
			return

		# Image credit violation
		if (image_url and not image_credit):
			error = loc.response("showcase", "submit", "error-credit", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		# Initialize embed
		embed_title = firstname if not surname else f"{firstname} {surname}"
		embed = discord.Embed(title=embed_title, color=utils.hex_to_color(hex_color))
		
		embed.set_footer(text=loc.common_res("showcase-embed-footer", ctx.interaction.locale).format(id=ctx.interaction.id))
		
		if (image_url):
			image_url = image_url[:2000]
			embed.set_image(url=image_url)

		embed.add_field(
			name=loc.common_res("showcase-author-field", ctx.interaction.locale),
			value=f"<@{ctx.interaction.user.id}>")

		if (image_credit):
			embed.add_field(
				name=loc.common_res("showcase-credit-field", ctx.interaction.locale),
				value=image_credit)

		# Prompt for description
		modal = InputModal(firstname, surname, hex_color, image_url, image_credit, ctx, embed, self.dm_channel)
		await ctx.send_modal(modal)

# ------------------------------------------------------------------------
# /showcase mine
# ------------------------------------------------------------------------
	@showcase.command(name="mine",
		name_localizations=loc.command_names("showcase", "mine"),
		description_localizations=loc.command_descriptions("showcase", "mine"))
	@option("visible", bool, default=False,
		description="Set to 'True' for a permanent, visible response.",
		name_localizations=loc.common("visible-name"),
		description_localizations=loc.common("visible-desc"))
	async def mine(self, ctx, visible):
		"""An overview of your showcase characters"""

		characters = await db.get_user_chars(ctx.interaction.user.id)

		# No characters
		if (len(characters) == 0):
			error = loc.response("showcase", "mine", "error-none", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		# Sort alphabetically
		characters = sorted(characters, key=lambda c:c["name"])

		embeds = make_char_list_embeds(characters, ctx.interaction.locale)

		await ctx.respond(view=EmbedMenuList(embeds, ctx.interaction, characters, visible), ephemeral=not visible, embed=embeds[0])

# ------------------------------------------------------------------------
# /showcase user
# ------------------------------------------------------------------------
	@showcase.command(name="user",
		name_localizations=loc.command_names("showcase", "user"),
		description_localizations=loc.command_descriptions("showcase", "user"))
	@option("user_tag", discord.Member, default=None,
		description="The discord user <@id> tag to search for",
		name_localizations=loc.option_names("showcase", "user", "user_tag"),
		description_localizations=loc.option_descriptions("showcase", "user", "user_tag"))
	@option("user_id", str, default=None,
		description="The discord user id to search for",
		name_localizations=loc.option_names("showcase", "user", "user_id"),
		description_localizations=loc.option_descriptions("showcase", "user", "user_id"))
	@option("visible", bool, default=False,
		description="Set to 'True' for a permanent, visible response.",
		name_localizations=loc.common("visible-name"),
		description_localizations=loc.common("visible-desc"))
	async def user(self, ctx, user_tag, user_id, visible):
		"""An overview of a specified user's showcase characters"""

		if (user_tag):
			characters = await db.get_user_approved_chars(user_tag.id)
		elif (user_id):
			characters = await db.get_user_approved_chars(user_id)
		else:
			error = loc.response("showcase", "user", "no-arg", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		# No characters
		if (len(characters) == 0):
			error = loc.response("showcase", "user", "error-none", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		# Sort alphabetically
		characters = sorted(characters, key=lambda c:c["name"])

		embeds = make_char_list_embeds(characters, ctx.interaction.locale)

		await ctx.respond(view=EmbedMenuList(embeds, ctx.interaction, characters, visible), ephemeral=not visible, embed=embeds[0])

# ------------------------------------------------------------------------
# /showcase character
# ------------------------------------------------------------------------
	@showcase.command(name="character",
		name_localizations=loc.command_names("showcase", "character"),
		description_localizations=loc.command_descriptions("showcase", "character"))
	@option("char_id", str,
		description="The character's ID (found with /showcase search)",
		name_localizations=loc.option_names("showcase", "character", "char_id"),
		description_localizations=loc.option_descriptions("showcase", "character", "char_id"))
	@option("visible", bool, default=False,
		description="Set to 'True' for a permanent, visible response.",
		name_localizations=loc.common("visible-name"),
		description_localizations=loc.common("visible-desc"))
	async def character(self, ctx, char_id, visible):
		"""Display a showcase character using their ID"""

		char = await db.get_char(char_id)

		try:
			embed = make_showcase_embed(char, ctx.interaction.locale)
		except TypeError:
			error = loc.common_res("showcase-id-error", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		await ctx.respond(embed=embed, ephemeral=not visible)

# ------------------------------------------------------------------------
# /showcase search
# ------------------------------------------------------------------------
	@showcase.command(name="search",
		name_localizations=loc.command_names("showcase", "search"),
		description_localizations=loc.command_descriptions("showcase", "search"))
	@option("name", str, default=None,
		description="The character's first/given/display name",
		name_localizations=loc.option_names("showcase", "search", "name"),
		description_localizations=loc.option_descriptions("showcase", "search", "name"))
	@option("surname", str, default=None,
		description="The character's last/family name",
		name_localizations=loc.option_names("showcase", "search", "surname"),
		description_localizations=loc.option_descriptions("showcase", "search", "surname"))
	@option("exact", bool, default=False,
		description="Set to 'True' to only receive exact matches",
		name_localizations=loc.option_names("showcase", "search", "exact"),
		description_localizations=loc.option_descriptions("showcase", "search", "exact"))
	@option("visible", bool, default=False,
		description="Set to 'True' for a permanent, visible response.",
		name_localizations=loc.common("visible-name"),
		description_localizations=loc.common("visible-desc"))
	async def search(self, ctx, name, surname, exact, visible):
		"""Search by character name and/or surname"""

		# No parameters
		if (not name and not surname):
			error = loc.response("showcase", "search", "no-arg", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return
		
		# Search
		if (not exact):
			characters = await db.fuzzy_search(name, surname)
		else:
			characters = await db.exact_search(name, surname)

		# No results
		if (len(characters) == 0):
			error = loc.response("showcase", "search", "error-none", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return
		# Too many results
		elif (len(characters) > 200):
			error = loc.response("showcase", "search", "error-toomany", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		# Sort alphabetically
		if (name):
			characters = sorted(characters, key=lambda c:c["name"])
		else:
			characters = sorted(characters, key=lambda c:c["surname"])

		embeds = make_char_list_embeds(characters, ctx.interaction.locale, with_user=True)

		await ctx.respond(view=EmbedMenuList(embeds, ctx.interaction, characters, visible), ephemeral=not visible, embed=embeds[0])

# ------------------------------------------------------------------------
# /showcase edit basic
# ------------------------------------------------------------------------
	@edit.command(name="basic",
		name_localizations=loc.command_names("showcase_edit", "basic"),
		description_localizations=loc.command_descriptions("showcase_edit", "basic"))
	@option("char_id", str,
		description="Character's ID",
		name_localizations=loc.option_names("showcase_edit", "basic", "char_id"),
		description_localizations=loc.option_descriptions("showcase_edit", "basic", "char_id"))
	@option("field_to_change", str,
		choices=loc.choices("showcase_edit", "basic", "field_to_change"),
		description="Name, surname, or hex",
		name_localizations=loc.option_names("showcase_edit", "basic", "field_to_change"),
		description_localizations=loc.option_descriptions("showcase_edit", "basic", "field_to_change"))
	@option("new_value", str,
		description="New value",
		name_localizations=loc.option_names("showcase_edit", "basic", "new_value"),
		description_localizations=loc.option_descriptions("showcase_edit", "basic", "new_value"))
	async def edit_basic(self, ctx, char_id, field_to_change, new_value):
		"""Edit character name, surname, or hex"""

		# Banned users cannot edit characters
		if (str(ctx.interaction.user.id) in db.get_banned_users_cache()):
			error = loc.response("showcase", "submit", "error-banned", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		# Obligatory hex code regex validation, exits without attempting
		if (field_to_change == "HexColor"):
			match = re.search(r'^(?:[0-9a-fA-F]{6})$', new_value)
			if (not match):
				error = loc.response("showcase_edit", "basic", "error-hex", ctx.interaction.locale).format(new_value)
				await ctx.respond(error, ephemeral=True)
				return

		# Enforce length limits
		new_value = new_value[:64]
		updated = await db.edit_character(ctx.interaction.user.id, char_id, field_to_change.lower(), new_value)

		if (not updated):
			error = loc.common_res("showcase-not-author", ctx.interaction.locale).format(id=char_id)
			await ctx.respond(error, ephemeral=True)
			return

		# DM update if text
		if (field_to_change != "HexColor"):
			dm_content = f"**SHOWCASE UPDATE**\nID: {char_id}\n{field_to_change} -> {new_value}"
			await self.dm_channel.send(content=dm_content)

		res = loc.common_res("showcase-updated", ctx.interaction.locale)
		await ctx.respond(res, ephemeral=True)

# ------------------------------------------------------------------------
# /showcase edit image
# ------------------------------------------------------------------------
	@edit.command(name="image",
		name_localizations=loc.command_names("showcase_edit", "image"),
		description_localizations=loc.command_descriptions("showcase_edit", "image"))
	@option("char_id", str,
		description="Character's ID",
		name_localizations=loc.option_names("showcase_edit", "image", "char_id"),
		description_localizations=loc.option_descriptions("showcase_edit", "image", "char_id"))
	@option("new_value", str,
		description="New value",
		name_localizations=loc.option_names("showcase_edit", "image", "new_value"),
		description_localizations=loc.option_descriptions("showcase_edit", "image", "new_value"))
	@option("credit", str,
		description="Image credit",
		name_localizations=loc.option_names("showcase_edit", "image", "credit"),
		description_localizations=loc.option_descriptions("showcase_edit", "image", "credit"))
	async def edit_image(self, ctx, char_id, new_value, credit):
		"""Edit showcase image"""

		# Banned users cannot edit characters
		if (str(ctx.interaction.user.id) in db.get_banned_users_cache()):
			error = loc.response("showcase", "submit", "error-banned", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		# Get existing information
		char = await db.get_char(char_id)

		# Not author (or no character)
		if (not char or char["authorid"] != ctx.interaction.user.id):
			error = loc.common_res("showcase-not-author", ctx.interaction.locale).format(id=char_id)
			await ctx.respond(error, ephemeral=True)
			return

		# Edit
		char = dict(char)
		char["imageurl"] = new_value
		char["imagecredit"] = credit[:128]

		embed = make_showcase_embed(char, ctx.interaction.locale)

		# Attempt to display
		try:
			await ctx.respond(embed=embed, ephemeral=True)
		except discord.HTTPException:
			error = loc.response("showcase_edit", "image", "invalid-image", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		# DM update
		dm_content = f"**SHOWCASE UPDATE**\nID: {char_id}\nImageURL -> {new_value}\nCredit -> {credit}"
		await self.dm_channel.send(content=dm_content)

		# Edit
		await db.edit_character(ctx.interaction.user.id, char_id, "imageurl", new_value)
		await db.edit_character(ctx.interaction.user.id, char_id, "imagecredit", credit[:128])

# ------------------------------------------------------------------------
# /showcase edit desc
# ------------------------------------------------------------------------
	@edit.command(name="desc",
		name_localizations=loc.command_names("showcase_edit", "desc"),
		description_localizations=loc.command_descriptions("showcase_edit", "desc"))
	@option("char_id", str,
		description="Character's ID",
		name_localizations=loc.option_names("showcase_edit", "desc", "char_id"),
		description_localizations=loc.option_descriptions("showcase_edit", "desc", "char_id"))
	async def edit_desc(self, ctx, char_id):
		"""Edit showcase description"""

		# Banned users cannot edit characters
		if (str(ctx.interaction.user.id) in db.get_banned_users_cache()):
			error = loc.response("showcase", "submit", "error-banned", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		# Get existing information
		char = await db.get_char(char_id)

		# Not author (or no character)
		if (not char or char["authorid"] != ctx.interaction.user.id):
			error = loc.common_res("showcase-not-author", ctx.interaction.locale).format(id=char_id)
			await ctx.respond(error, ephemeral=True)
			return

		# Modal populated with existing description
		modal = InputUpdateModal(char, ctx, self.dm_channel)
		await ctx.send_modal(modal)

# ------------------------------------------------------------------------
# /showcase rm
# ------------------------------------------------------------------------
	@showcase.command(name="rm",
		name_localizations=loc.command_names("showcase", "rm"),
		description_localizations=loc.command_descriptions("showcase", "rm"))
	@option("char_id", str,
		description="Character's ID",
		name_localizations=loc.option_names("showcase", "rm", "char_id"),
		description_localizations=loc.option_descriptions("showcase", "rm", "char_id"))
	async def remove(self, ctx, char_id):
		"""Remove a showcase by ID"""

		removed = await db.remove_character(ctx.interaction.user.id, char_id)

		if (not removed):
			error = loc.common_res("showcase-not-author", ctx.interaction.locale).format(id=char_id)
			await ctx.respond(error, ephemeral=True)
			return

		res = loc.response("showcase", "rm", "res1", ctx.interaction.locale).format(id=char_id)
		await ctx.respond(res)

# ------------------------------------------------------------------------
# /showcase report
# ------------------------------------------------------------------------
	@showcase.command(name="report",
		name_localizations=loc.command_names("showcase", "report"),
		description_localizations=loc.command_descriptions("showcase", "report"))
	@option("char_id", str,
		description="Character's ID",
		name_localizations=loc.option_names("showcase", "report", "char_id"),
		description_localizations=loc.option_descriptions("showcase", "report", "char_id"))
	@option("reason", str,
		description="Reason for report (NSFW, Hatespeech, Plagiarism, Other)",
		choices=loc.choices("showcase", "report", "reason"),
		name_localizations=loc.option_names("showcase", "report", "reason"),
		description_localizations=loc.option_descriptions("showcase", "report", "reason"))
	@option("details", str, default=None,
		description="Required for Plagiarism or Other",
		name_localizations=loc.option_names("showcase", "report", "details"),
		description_localizations=loc.option_descriptions("showcase", "report", "details"))
	async def report(self, ctx, char_id, reason, details):
		"""Report a showcase by ID"""

		# Detail required for plagiarism or other
		if ((reason == "Plagiarism" or reason == "Other") and not details):
			error = loc.response("showcase", "report", "error-details", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		char = await db.get_char(char_id)

		try:
			embed = make_showcase_embed(char, ctx.interaction.locale)
		except TypeError:
			error = loc.common_res("showcase-id-error", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		# DM
		dm_content =f"**SHOWCASE REPORTED**\nReporter: <@{ctx.interaction.user.id}>\nReason: {reason}"
		if (details):
			dm_content += f"\nDetails: {details[:512]}"

		await self.dm_channel.send(content=dm_content, embed=embed)

		res = loc.response("showcase", "report", "res1", ctx.interaction.locale).format(id=char_id)
		await ctx.respond(res)

# ------------------------------------------------------------------------
# /showcase random
# ------------------------------------------------------------------------
	@showcase.command(name="random",
		name_localizations=loc.command_names("showcase", "random"),
		description_localizations=loc.command_descriptions("showcase", "random"))
	@option("amount", int, default=1,
		min_value=1,
		max_value=5,
		description="The number of showcases to list",
		name_localizations=loc.option_names("showcase", "random", "amount"),
		description_localizations=loc.option_descriptions("showcase", "random", "amount"))
	@option("visible", bool, default=True,
		description="Set to 'False' for a private response",
		name_localizations=loc.option_names("showcase", "random", "visible"),
		description_localizations=loc.option_descriptions("showcase", "random", "visible"))
	@commands.cooldown(1, 15, commands.BucketType.user)
	async def random(self, ctx, amount, visible):
		"""View up to 5 random showcases"""

		characters = await db.get_random_chars(amount)
		# Case of single
		if (amount == 1):
			char = characters[0]
			embed = make_showcase_embed(char, ctx.interaction.locale)
			await ctx.respond(embed=embed, ephemeral=not visible)
			return

		# Otherwise, make a list
		# Sort alphabetically
		characters = sorted(characters, key=lambda c:c["name"])

		embeds = make_char_list_embeds(characters, ctx.interaction.locale, with_user=True)

		await ctx.respond(view=EmbedMenuList(embeds, ctx.interaction, characters, visible), ephemeral=not visible, embed=embeds[0])


	@random.error
	async def random_error(self, ctx, error):
		if (type(error) == commands.errors.CommandOnCooldown):
			await ctx.respond(error, ephemeral=True)
			return
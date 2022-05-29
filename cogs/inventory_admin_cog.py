"""
Author @Firefly#7113
Admin inventory commands
"""

import math

import discord
from discord import option
from discord.commands import SlashCommandGroup
from discord.ext import commands

import db
from localization import loc

from utils import utils
from utils.embed_list import EmbedList


# ------------------------------------------------------------------------
# COG
# ------------------------------------------------------------------------
def setup(bot):
	bot.add_cog(InventoryAdminCog(bot))

# pylint: disable=no-self-use, too-many-arguments
class InventoryAdminCog(commands.Cog):
	"""Inventory management for admins"""

	def __init__(self, bot):
		self.bot = bot
		print(f"Added {self.__class__.__name__}")


# ------------------------------------------------------------------------
# Command groups
# Change the decorator to @<name>.command()
# ------------------------------------------------------------------------
	inventory_admin = SlashCommandGroup("inv_admin", "Admin inventory management",
		name_localizations=loc.group_names("inv_admin"),
		description_localizations=loc.group_descriptions("inv_admin"))


# ------------------------------------------------------------------------
# Commands
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# /inv_admin take
# ------------------------------------------------------------------------
	@inventory_admin.command(name="take",
		name_localizations=loc.command_names("inv_admin", "take"),
		description_localizations=loc.command_descriptions("inv_admin", "take"))
	@option("player", discord.Member,
		description="Active character to take from",
		name_localizations=loc.option_names("inv_admin", "take", "player"),
		description_localizations=loc.option_descriptions("inv_admin", "take", "player"))
	@option("item", str,
		description="Case sensitive item name",
		name_localizations=loc.option_names("inv_admin", "take", "item"),
		description_localizations=loc.option_descriptions("inv_admin", "take", "item"))
	@option("amount", int, default=1, min_value=1, max_value=9999,
		description="Amount to take (default 1)",
		name_localizations=loc.option_names("inv_admin", "take", "amount"),
		description_localizations=loc.option_descriptions("inv_admin", "take", "amount"))
	@option("visible", bool, default=False,
		description="Set to 'True' for a permanent, visible response.",
		name_localizations=loc.common("visible-name"),
		description_localizations=loc.common("visible-desc"))
	async def take(self, ctx, player, item, amount, visible):
		"""Take one or more of an item from a player's inventory"""

		updated = db.remove_item(ctx.guild.id, player.id, item, amount)

		if (not updated):
			error = loc.response("inv_admin", "take", "error-missing", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		res = loc.response("inv_admin", "take", "res1", ctx.interaction.locale).format(amount=amount, item=item, name=player.name)
		await ctx.respond(res, ephemeral=not visible)

# ------------------------------------------------------------------------
# /inv_admin give
# ------------------------------------------------------------------------
	@inventory_admin.command(name="give",
		name_localizations=loc.command_names("inv_admin", "give"),
		description_localizations=loc.command_descriptions("inv_admin", "give"))
	@option("recipient", discord.Member,
		description="Active character to give item to",
		name_localizations=loc.option_names("inv_admin", "give", "recipient"),
		description_localizations=loc.option_descriptions("inv_admin", "give", "recipient"))
	@option("item", str,
		description="Case sensitive item to give",
		name_localizations=loc.option_names("inv_admin", "give", "item"),
		description_localizations=loc.option_descriptions("inv_admin", "give", "item"))
	@option("amount", int, default=1, min_value=1, max_value=999,
		name_localizations=loc.option_names("inv_admin", "give", "amount"),
		description_localizations=loc.option_descriptions("inv_admin", "give", "amount"))
	@option("desc", str, default=None,
		description="A short description of the item (256 character maximum)",
		name_localizations=loc.option_names("inv_admin", "give", "desc"),
		description_localizations=loc.option_descriptions("inv_admin", "give", "desc"))
	@option("visible", bool, default=False,
		description="Set to 'True' for a permanent, visible response.",
		name_localizations=loc.common("visible-name"),
		description_localizations=loc.common("visible-desc"))
	async def give(self, ctx, recipient, item, amount, desc, visible):
		"""Add one or more of an item to a player's inventory. Description optional"""

		# Be sure to enforce embed limits
		if (desc):
			desc = desc[:256]
		updated = db.add_item(ctx.guild.id, recipient.id, item[:64], amount, desc)

		if (not updated):
			error = loc.response("inv_admin", "give", "error-missing", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		res = loc.response("inv_admin", "give", "res1", ctx.interaction.locale).format(amount=amount, item=item[:64], name=recipient.name)
		await ctx.respond(res, ephemeral=not visible)

# ------------------------------------------------------------------------
# /inv_admin view
# ------------------------------------------------------------------------
	@inventory_admin.command(name="view",
		name_localizations=loc.command_names("inv_admin", "view"),
		description_localizations=loc.command_descriptions("inv_admin", "view"))
	@option("player", discord.Member,
		description="Player with an active character",
		name_localizations=loc.option_names("inv_admin", "view", "player"),
		description_localizations=loc.option_descriptions("inv_admin", "view", "player"))
	@option("visible", bool, default=False,
		description="Set to 'True' for a permanent, visible response.",
		name_localizations=loc.common("visible-name"),
		description_localizations=loc.common("visible-desc"))
	async def view(self, ctx, player, visible):
		"""View a specified player's inventory (active character only)"""

		try:
			inventory = db.get_inventory(ctx.guild.id, player.id)
			hex_color = db.get_active_char(ctx.guild.id, player.id)["HexColor"]
		except TypeError:
			error = loc.response("inv_admin", "view", "error-missing", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		# Handle no items case
		if (len(inventory) == 0):
			error = loc.response("inv_admin", "view", "error-nothing", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		# Order by key
		inventory = dict(sorted(inventory.items()))

		# To stay safely within limits, we'll allow up to 10 items per embed
		n_embeds = math.ceil(len(inventory) / 10)
		embeds = [discord.Embed(title=f"{i+1}/{n_embeds}", color=utils.hex_to_color(hex_color)) for i in range(n_embeds)]

		keys = list(inventory.keys())
		for i in range(0, n_embeds):
			for _ in range(10):
				try:
					item_name = keys.pop(0)
					item = inventory.pop(item_name)
				except IndexError:
					break

				title = f"{item_name}"
				if (item["amount"] > 1):
					title += f" (x{item['amount']})"

				if (item["desc"]):
					desc = item["desc"]
				else:
					desc = loc.response("inv_admin", "view", "no-description", ctx.interaction.locale)

				embeds[i].add_field(name=title, value=desc, inline=False)

		await ctx.respond(view=EmbedList(embeds, ctx.interaction), ephemeral=not visible, embed=embeds[0])

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

from utils import utils
from utils.embed_list import EmbedList


# ------------------------------------------------------------------------
# COMPONENT CLASSES AND CONSTANTS
# ------------------------------------------------------------------------


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
	inventory_admin = SlashCommandGroup("inv_admin", "Admin inventory management")


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
# /inv_admin take
# ------------------------------------------------------------------------
	@inventory_admin.command(name="take")
	@option("player", discord.Member, description="Active character to take from")
	@option("item", str, description="Case sensitive item name, 64 character maximum")
	@option("amount", int, default=1, min_value=1, max_value=9999, description="Amount to take, default 1")
	@option("visible", bool, default=False, description="Set to True for public response")
	@commands.has_permissions(administrator=True)
	async def take(self, ctx, player, item, amount, visible):
		"""Take one or more of an item from a player's inventory"""

		updated = db.remove_item(ctx.guild.id, player.id, item, amount)

		if (not updated):
			await ctx.respond("That player is not holding any of that item! (Or you did not specify a player with an active character).", ephemeral=True)
			return

		await ctx.respond(f"Took {amount} {item} from {player.name}", ephemeral=not visible)

# ------------------------------------------------------------------------
# /inv_admin give
# ------------------------------------------------------------------------
	@inventory_admin.command(name="give")
	@option("recipient", discord.Member, description="The recipient")
	@option("item", str, description="Case sensitive item to give")
	@option("amount", int, default=1, description="How much you will give, default 1", min_value=1, max_value=999)
	@option("desc", str, default=None, description="Short description of item")
	@option("visible", bool, default=False, description="Set True for public response")
	@commands.has_permissions(administrator=True)
	async def give(self, ctx, recipient, item, amount, desc, visible):
		"""Add one or more of an item to a player's inventory. Description optional"""

		# Be sure to enforce embed limits
		if (desc):
			desc = desc[:256]
		updated = db.add_item(ctx.guild.id, recipient.id, item[:64], amount, desc)

		if (not updated):
			await ctx.respond("That user does not have an active character!", ephemeral=True)
			return

		await ctx.respond(f"Gave {amount} {item[:64]} to {recipient.name}", ephemeral=not visible)


# ------------------------------------------------------------------------
# /inv_admin view
# ------------------------------------------------------------------------
	@inventory_admin.command(name="view")
	@option("player", discord.Member, description="Player with an active character")
	@option("visible", bool, default=False, description="Set to true for permanent response.")
	@commands.has_permissions(administrator=True)
	async def view(self, ctx, player, visible):
		"""View a specified player's inventory (active character only)"""

		try:
			inventory = db.get_inventory(ctx.guild.id, player.id)
			hex_color = db.get_active_char(ctx.guild.id, player.id)["HexColor"]
		except TypeError:
			await ctx.respond("That user does not have an active character!", ephemeral=True)
			return

		# Handle no items case
		if (len(inventory) == 0):
			await ctx.respond("That player has nothing in their inventory!", ephemeral=True)
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
					desc = "No Description"

				embeds[i].add_field(name=title, value=desc, inline=False)

		await ctx.respond(view=EmbedList(embeds), ephemeral=not visible, embed=embeds[0])

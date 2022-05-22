"""
Author @Firefly#7113
Player inventory management
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
# COG
# ------------------------------------------------------------------------
def setup(bot):
	bot.add_cog(InventoryPublicCog(bot))

# pylint: disable=no-self-use, too-many-arguments
class InventoryPublicCog(commands.Cog):
	"""Inventory management for players"""

	def __init__(self, bot):
		self.bot = bot
		print(f"Added {self.__class__.__name__}")


# ------------------------------------------------------------------------
# Command groups
# Change the decorator to @<name>.command()
# ------------------------------------------------------------------------
	inventory = SlashCommandGroup("inv", "Player inventory management")


# ------------------------------------------------------------------------
# Crontabs
# https://crontab.cronhub.io/
# Crontabs appear to execute in a LIFO stack order
# Do not need to be explicitly started
# ------------------------------------------------------------------------


# ------------------------------------------------------------------------
# Commands
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# /inv take
# ------------------------------------------------------------------------
	@inventory.command(name="take")
	@option("item", str, description="Case sensitive item name, 64 character maximum")
	@option("amount", int, default=1, min_value=1, max_value=9999, description="Amount to take, default 1")
	@option("desc", str, default=None, description="Optional description, 256 character maximum")
	@option("visible", bool, default=False, description="Set to True for public response")
	async def take(self, ctx, item, amount, desc, visible):
		"""Add one or more of an item to your inventory. Description optional"""

		# Be sure to enforce embed limits
		if (desc):
			desc = desc[:256]
		updated = db.add_item(ctx.guild.id, ctx.interaction.user.id, item[:64], amount, desc)

		if (not updated):
			await ctx.respond("You do not have an active character!", ephemeral=True)
			return

		await ctx.respond(f"Took {amount} {item[:64]}", ephemeral=not visible)

# ------------------------------------------------------------------------
# /inv drop
# ------------------------------------------------------------------------
	@inventory.command(name="drop")
	@option("item", str, description="Name of item to drop. Case sensitive")
	@option("amount", int, default=1, min_value=1, max_value=9999, description="Amount to drop, default 1")
	@option("visible", bool, default=False, description="Set to True for public response")
	async def drop(self, ctx, item, amount, visible):
		"""Remove one or more of an item from your inventory (case sensitive)"""

		updated = db.remove_item(ctx.guild.id, ctx.interaction.user.id, item, amount)

		if (not updated):
			await ctx.respond("You either do not have an active character or you are not carrying that item!", ephemeral=True)
			return

		await ctx.respond(f"Dropped {amount} {item}", ephemeral=not visible)

# ------------------------------------------------------------------------
# /inv give
# ------------------------------------------------------------------------
	@inventory.command(name="give")
	@option("recipient", discord.Member, description="The recipient")
	@option("item", str, description="Case sensitive item to give")
	@option("amount", int, default=1, description="How much you will give, default 1", min_value=1, max_value=999)
	@option("visible", bool, default=True, description="Set false for hidden result")
	async def give(self, ctx, recipient, item, amount, visible):
		"""Give another active character one or more of an item in your inventory."""

		# Try to get inventory
		try:
			sender_inv = db.get_inventory(ctx.guild.id, ctx.interaction.user.id)
		except TypeError:
			await ctx.respond("You do not have an active character!", ephemeral=True)
			return

		# Check item availibility
		try:
			_ = sender_inv[item]
		except KeyError:
			await ctx.respond(f"You are not carrying {item}!", ephemeral=True)
			return

		if (sender_inv[item]["amount"] < amount):
			await ctx.respond(f"You do not have enough {item}!", ephemeral=True)
			return


		# Check that sender is valid by attempting to udpate
		recipient_updated = db.add_item(ctx.guild.id, recipient.id, item, amount, sender_inv[item]["desc"])

		if (not recipient_updated):
			await ctx.respond(f"{recipient.name} does not have an active character!", ephemeral=True)
			return

		# Remove from sender inventory
		db.remove_item(ctx.guild.id, ctx.interaction.user.id, item, amount)
		await ctx.respond(f"Gave {amount} {item} to {recipient.name}", ephemeral=not visible)

# ------------------------------------------------------------------------
# /inv view
# ------------------------------------------------------------------------
	@inventory.command(name="view")
	@option("visible", bool, default=False, description="Set to true for permanent response.")
	async def view(self, ctx, visible):
		"""View your inventory"""

		try:
			inventory = db.get_inventory(ctx.guild.id, ctx.interaction.user.id)
			hex_color = db.get_active_char(ctx.guild.id, ctx.interaction.user.id)["HexColor"]
		except TypeError:
			await ctx.respond("You do not have an active character!", ephemeral=True)
			return

		# Handle no items case
		if (len(inventory) == 0):
			await ctx.respond("You have nothing in your inventory!", ephemeral=True)
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

		await ctx.respond(view=EmbedList(embeds, ctx.interaction), ephemeral=not visible, embed=embeds[0])

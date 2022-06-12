"""
Author @Firefly#7113
Player inventory management
"""

import math

import discord
from discord import option
from discord.commands import SlashCommandGroup
from discord.ext import commands

from db import db
from localization import loc

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
	inventory = SlashCommandGroup("inv", "Player inventory management",
		guild_only=True,
		name_localizations=loc.group_names("inv"),
		description_localizations=loc.group_descriptions("inv"))


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
	@inventory.command(name="take",
		name_localizations=loc.command_names("inv", "take"),
		description_localizations=loc.command_descriptions("inv", "take"))
	@option("item", str,
		description="Case sensitive item name, 64 character maximum",
		name_localizations=loc.option_names("inv", "take", "item"),
		description_localizations=loc.option_descriptions("inv", "take", "item"))
	@option("amount", int, default=1, min_value=1, max_value=9999,
		description="Amount to take, (default 1)",
		name_localizations=loc.option_names("inv", "take", "amount"),
		description_localizations=loc.option_descriptions("inv", "take", "amount"))
	@option("desc", str, default=None,
		description="Optional description, 256 character maximum",
		name_localizations=loc.option_names("inv", "take", "desc"),
		description_localizations=loc.option_descriptions("inv", "take", "desc"))
	@option("visible", bool, default=False,
		description="Set to 'True' for a permanent, visible response.",
		name_localizations=loc.common("visible-name"),
		description_localizations=loc.common("visible-desc"))
	async def take(self, ctx, item, amount, desc, visible):
		"""Add one or more of an item to your inventory. Description optional"""

		# Be sure to enforce embed limits
		if (desc):
			desc = desc[:256]
		updated = await db.add_item(ctx.guild.id, ctx.interaction.user.id, item[:64], amount=amount, desc=desc)

		if (not updated):
			error = loc.common_res("no-character", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		res = loc.response("inv", "take", "res1", ctx.interaction.locale).format(amount=amount, item=item[:64])
		await ctx.respond(res, ephemeral=not visible)

# ------------------------------------------------------------------------
# /inv drop
# ------------------------------------------------------------------------
	@inventory.command(name="drop",
		name_localizations=loc.command_names("inv", "drop"),
		description_localizations=loc.command_descriptions("inv", "drop"))
	@option("item", str,
		description="Name of item to drop (case sensitive)",
		name_localizations=loc.option_names("inv", "drop", "item"),
		description_localizations=loc.option_descriptions("inv", "drop", "item"))
	@option("amount", int, default=1, min_value=1, max_value=9999,
		description="Amount to drop, default 1",
		name_localizations=loc.option_names("inv", "drop", "amount"),
		description_localizations=loc.option_descriptions("inv", "drop", "amount"))
	@option("visible", bool, default=False,
		description="Set to 'True' for a permanent, visible response.",
		name_localizations=loc.common("visible-name"),
		description_localizations=loc.common("visible-desc"))
	async def drop(self, ctx, item, amount, visible):
		"""Remove one or more of an item from your inventory (case sensitive)"""

		updated = await db.remove_item(ctx.guild.id, ctx.interaction.user.id, item, amount=amount)

		if (not updated):
			error = loc.response("inv", "drop", "error-missing", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		res = loc.response("inv", "drop", "res1", ctx.interaction.locale).format(amount=amount, item=item)
		await ctx.respond(res, ephemeral=not visible)

# ------------------------------------------------------------------------
# /inv give
# ------------------------------------------------------------------------
	@inventory.command(name="give",
		name_localizations=loc.command_names("inv", "give"),
		description_localizations=loc.command_descriptions("inv", "give"))
	@option("recipient", discord.Member,
		description="The player to receive your item",
		name_localizations=loc.option_names("inv", "give", "recipient"),
		description_localizations=loc.option_descriptions("inv", "give", "recipient"))
	@option("item", str,
		description="Case sensitive item to give",
		name_localizations=loc.option_names("inv", "give", "item"),
		description_localizations=loc.option_descriptions("inv", "give", "item"))
	@option("recipient_name", str, default=None,
		description="The registered display name of the character, if not active",
		name_localizations=loc.common("inactive-recipient-name"),
		description_localizations=loc.common("inactive-char-desc"))
	@option("amount", int, default=1, min_value=1, max_value=999,
		description="Amount to give, detault 1",
		name_localizations=loc.option_names("inv", "give", "amount"),
		description_localizations=loc.option_descriptions("inv", "give", "amount"))
	@option("visible", bool, default=True,
		description="Set 'False' for a hidden response.",
		name_localizations=loc.option_names("inv", "give", "visible"),
		description_localizations=loc.option_descriptions("inv", "give", "visible")
		)
	async def give(self, ctx, recipient, item, recipient_name, amount, visible):
		"""Give another active character one or more of an item in your inventory"""

		# Try to get inventory
		try:
			sender_inv = await db.get_inventory(ctx.guild.id, ctx.interaction.user.id)
		except TypeError:
			error = loc.common_res("no-character", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		# Check item availibility
		try:
			_ = sender_inv[item]
		except KeyError:
			error = loc.response("inv", "give", "error-missing", ctx.interaction.locale).format(item)
			await ctx.respond(error, ephemeral=True)
			return

		if (sender_inv[item]["amount"] < amount):
			error = loc.response("inv", "give", "error-amount", ctx.interaction.locale).format(item)
			await ctx.respond(error, ephemeral=True)
			return


		# Check that sender is valid by attempting to udpate
		recipient_updated = await db.add_item(ctx.guild.id, recipient.id, item, name=recipient_name, amount=amount, desc=sender_inv[item]["desc"])

		if (not recipient_updated):
			error = loc.response("inv", "give", "error-recipient", ctx.interaction.locale).format(recipient.name)
			await ctx.respond(error, ephemeral=True)
			return

		# Remove from sender inventory
		await db.remove_item(ctx.guild.id, ctx.interaction.user.id, item, amount=amount)

		res = loc.response("inv", "give", "res1", ctx.interaction.locale).format(amount=amount, item=item, name=recipient.name)
		await ctx.respond(res, ephemeral=not visible)

# ------------------------------------------------------------------------
# /inv view
# ------------------------------------------------------------------------
	@inventory.command(name="view",
		name_localizations=loc.command_names("inv", "view"),
		description_localizations=loc.command_descriptions("inv", "view"))
	@option("visible", bool, default=False,
		description="Set to 'True' for a permanent, visible response.",
		name_localizations=loc.common("visible-name"),
		description_localizations=loc.common("visible-desc"))
	async def view(self, ctx, visible):
		"""View your inventory"""

		try:
			inventory = await db.get_inventory(ctx.guild.id, ctx.interaction.user.id)
			hex_color = await db.get_active_char(ctx.guild.id, ctx.interaction.user.id)["hexcolor"]
		except TypeError:
			error = loc.common_res("no-character", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		# Handle no items case
		if (len(inventory) == 0):
			error = loc.response("inv", "view", "error-items", ctx.interaction.locale)
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
					desc = loc.response("inv", "view", "no-description", ctx.interaction.locale)

				embeds[i].add_field(name=title, value=desc, inline=False)

		await ctx.respond(view=EmbedList(embeds, ctx.interaction), ephemeral=not visible, embed=embeds[0])

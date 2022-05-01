"""
Author @Firefly#7113
Admin gacha management
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
	bot.add_cog(GachaAdminCog(bot))

# pylint: disable=no-self-use
class GachaAdminCog(commands.Cog):
	"""Gacha setup and maintenence for mods"""

	def __init__(self, bot):
		self.bot = bot
		print(f"Added {self.__class__.__name__}")


# ------------------------------------------------------------------------
# Command groups
# Change the decorator to @<name>.command()
# ------------------------------------------------------------------------
	gacha_admin = SlashCommandGroup("gacha_admin", "Admin Gacha management")
	currency = gacha_admin.create_subgroup("currency", "Currency management")

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
# /gacha_admin currency name
# ------------------------------------------------------------------------
	@currency.command(name="name")
	@option("name", str, description="Plural form recommended")
	@commands.has_permissions(administrator=True)
	async def admin_currency_name(self, ctx, name):
		"""Set the name of your game's currency"""

		db.edit_guild(ctx.guild.id, "CurrencyName", name)
		await ctx.respond(f"Set currency name to {name}")

# ------------------------------------------------------------------------
# /gacha_admin currency cost
# ------------------------------------------------------------------------
	@currency.command(name="cost")
	@option("cost", int, description="1 to 999", min_value=1, max_value=999)
	@commands.has_permissions(administrator=True)
	async def admin_currency_cost(self, ctx, cost):
		""""Set the cost of a single /gacha use"""

		db.edit_guild(ctx.guild.id, "GachaCost", cost)
		await ctx.respond(f"Set cost to {cost}")

# ------------------------------------------------------------------------
# /gacha_admin currency give
# ------------------------------------------------------------------------
	@currency.command(name="give")
	@option("player", discord.Member)
	@option("amount", int, description="Amount to give", min_value=1, max_value=999)
	@commands.has_permissions(administrator=True)
	async def admin_currency_give(self, ctx, player, amount):
		"""Give currency to an active character"""

		char_updated = db.increase_currency_single(ctx.guild.id, player.id, amount)

		if (not char_updated):
			await ctx.respond(f"Could not find an active character for {player.name}", ephemeral=True)
			return

		await ctx.respond(f"Gave {amount} to {player.name}.")

# ------------------------------------------------------------------------
# /gacha_admin currency take
# ------------------------------------------------------------------------
	@currency.command(name="take")
	@option("player", discord.Member, description="User must have an active character")
	@option("amount", int, description="Amount to take", min_value=1, max_value=999)
	@commands.has_permissions(administrator=True)
	async def admin_currency_take(self, ctx, player, amount):
		"""Take currency from an active character"""

		char_updated = db.decrease_currency_single(ctx.guild.id, player.id, amount)

		if (not char_updated):
			await ctx.respond(f"Could not find an active character for {player.name}", ephemeral=True)
			return

		await ctx.respond(f"Took {amount} from {player.name}.")

# ------------------------------------------------------------------------
# /gacha_admin currency give_all
# ------------------------------------------------------------------------
	@currency.command(name="give_all")
	@option("amount", int, description="Amount to give", min_value=1, max_value=999)
	@commands.has_permissions(administrator=True)
	async def admin_currency_give_all(self, ctx, amount):
		"""Give currency to all active characters"""

		chars_updated = db.increase_currency_all(ctx.guild.id, amount)

		if (not chars_updated):
			await ctx.respond("Could not find any active characters for this server!", ephemeral=True)
			return

		await ctx.respond(f"Gave {amount} to all active characters.")

# ------------------------------------------------------------------------
# /gacha_admin currency view
# ------------------------------------------------------------------------
	@currency.command(name="view")
	@option("player", discord.Member)
	@option("visible", bool, default=False, description="Set to True for permanent response")
	@commands.has_permissions(administrator=True)
	async def admin_currency_view(self, ctx, player, visible):
		"""View currency of an active character"""

		char = db.get_active_char(ctx.guild.id, player.id)
		currency_name = db.get_guild_info(ctx.guild.id)["CurrencyName"]
		try:
			await ctx.respond(f"{char['Name']} has {char['Currency']} {currency_name}", ephemeral=not visible)
		finally:
			await ctx.respond(f"{player.name} does not have an active character!", ephemeral=True)

# ------------------------------------------------------------------------
# /gacha_admin currency view_all
# ------------------------------------------------------------------------
	@currency.command(name="view_all")
	@option("visible", bool, default=False, description="Set to True for permanent response")
	@commands.has_permissions(administrator=True)
	async def admin_currency_view_all(self, ctx, visible):
		"""View currency for all characters (active and inactive)"""

		chars = db.get_all_chars(ctx.guild.id)
		currency_name = db.get_guild_info(ctx.guild.id)["CurrencyName"]

		msg = f"__{currency_name}__\n"
		for char in chars:
			msg += f"{char['Name']}: {char['Currency']}\n"

		await ctx.respond(msg[:1800], ephemeral=not visible)

# ------------------------------------------------------------------------
# /gacha_admin add
# ------------------------------------------------------------------------
	@gacha_admin.command(name="add")
	@option("name", str, description="Item's name. Maximum of 64 characters")
	@option("desc", str, description="Item's description. 1024 character maximum")
	@option("amount", int, default=None, min_value=1, max_value=99999, description="Enter a number to make the item limited.")
	@option("thumbnail", str, default=None, description="Optional thumbnail image URL")
	@commands.has_permissions(administrator=True)
	async def gacha_admin_add(self, ctx, name, desc, amount, thumbnail):
		"""Register a new item to gacha, optional item limits and thumbnail"""

		# Enforce limits
		name = name[:64]
		desc = desc[:1024]

		# Add if possible
		try:
			db.add_gacha(ctx.guild.id, name, desc, amount, thumbnail)
		except:
			await ctx.respond("Cannot add a duplicate name!", ephemeral=True)
			return

		# Attempt to send gacha embed
		item = db.get_single_gacha(ctx.guild.id, name)
		try:
			embed = utils.get_gacha_embed(item)
			if (not amount):
				amount = "unlimited"
			await ctx.respond(f"Added item ({amount})", embed=embed, ephemeral=True)
		except discord.HTTPException:
			await ctx.respond("I cannot display that image URL! Removing item", ephemeral=True)
			db.remove_gacha_item(ctx.guild.id, name)

# ------------------------------------------------------------------------
# /gacha_admin rm
# ------------------------------------------------------------------------
	@gacha_admin.command(name="rm")
	@option("name", str, description="The display name of item to remove")
	@commands.has_permissions(administrator=True)
	async def gacha_admin_rm(self, ctx, name):
		"""Remove an item from gacha by name"""

		item_removed = db.remove_gacha_item(ctx.guild.id, name)

		if (not item_removed):
			await ctx.respond("Could not find that item!", ephemeral=True)
			return

		await ctx.respond(f"Removed {name}.")

# ------------------------------------------------------------------------
# /gacha_admin list
# ------------------------------------------------------------------------
	@gacha_admin.command(name="list")
	@option("visible", bool, default=False, description="Set to true for permanent response.")
	@commands.has_permissions(administrator=True)
	async def gacha_admin_list(self, ctx, visible):
		""""List all gacha items"""

		items = db.get_all_gacha(ctx.guild.id)

		# Handle no items case
		if (len(items) == 0):
			await ctx.respond("You have no gacha items in this server!", ephemeral=True)
			return

		# Order chars by name, error if no characters
		items = sorted(items, key=lambda d: d["Name"])

		# To stay safely within limits, we'll allow up to 35 items per embed
		n_embeds = math.ceil(len(items) / 35)
		embeds = [discord.Embed(title=f"{i+1}/{n_embeds}") for i in range(n_embeds)]

		for i in range(0, n_embeds):
			msg_i = ""
			for _ in range(35):
				try:
					item = items.pop(0)
				except IndexError:
					break

				if (item["Amount"]):
					amnt_str = f"({item['AmountRemaining']} / {item['Amount']})"
				else:
					amnt_str = ""

				msg_i += f"**{item['Name']}** {amnt_str} - {item['Desc'][:32]} \n"

			embeds[i].description = msg_i[:3900]

		await ctx.respond(view=EmbedList(embeds), ephemeral=not visible, embed=embeds[0])

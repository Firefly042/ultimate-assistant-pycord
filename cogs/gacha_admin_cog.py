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
from localization import loc

from utils import utils
from utils.embed_list import EmbedList


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
	gacha_admin = SlashCommandGroup("gacha_admin", "Admin Gacha management",
		name_localizations=loc.group_names("gacha_admin"),
		description_localizations=loc.group_descriptions("gacha_admin"))

	currency = gacha_admin.create_subgroup("currency", "Admin currency management")
	currency.name_localizations = loc.group_names("gacha_admin_currency")
	currency.description_localizations = loc.group_descriptions("gacha_admin_currency")

# ------------------------------------------------------------------------
# Commands
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# /gacha_admin currency name
# ------------------------------------------------------------------------
	@currency.command(name="name", guild_only=True,
		name_localizations=loc.command_names("gacha_admin_currency", "name"),
		description_localizations=loc.command_descriptions("gacha_admin_currency", "name"))
	@option("name", str,
		description="Plural form recommended",
		name_localizations=loc.option_names("gacha_admin_currency", "name", "name"),
		description_localizations=loc.option_descriptions("gacha_admin_currency", "name", "name"))
	async def admin_currency_name(self, ctx, name):
		"""Set the name of your game's currency"""

		# Reasonable limit
		name = name[:32]
		
		db.edit_guild(ctx.guild.id, "CurrencyName", name)

		res = loc.response("gacha_admin_currency", "name", "res1", ctx.interaction.locale).format(name)
		await ctx.respond(res)

# ------------------------------------------------------------------------
# /gacha_admin currency cost
# ------------------------------------------------------------------------
	@currency.command(name="cost", guild_only=True,
		name_localizations=loc.command_names("gacha_admin_currency", "cost"),
		description_localizations=loc.command_descriptions("gacha_admin_currency", "cost"))
	@option("amount", int, min_value=1, max_value=999,
		description="1 to 999",
		name_localizations=loc.option_names("gacha_admin_currency", "cost", "amount"),
		description_localizations=loc.option_descriptions("gacha_admin_currency", "cost", "amount"))
	async def admin_currency_cost(self, ctx, amount):
		"""Set the cost of a single gacha use"""

		db.edit_guild(ctx.guild.id, "GachaCost", amount)

		res = loc.response("gacha_admin_currency", "cost", "res1", ctx.interaction.locale).format(amount)
		await ctx.respond(res)

# ------------------------------------------------------------------------
# /gacha_admin currency give
# ------------------------------------------------------------------------
	@currency.command(name="give", guild_only=True,
		name_localizations=loc.command_names("gacha_admin_currency", "give"),
		description_localizations=loc.command_descriptions("gacha_admin_currency", "give"))
	@option("player", discord.Member,
		name_localizations=loc.option_names("gacha_admin_currency", "give", "player"))
	@option("amount", int, min_value=1, max_value=999,
		description="Amount to give",
		name_localizations=loc.option_names("gacha_admin_currency", "give", "amount"),
		description_localizations=loc.option_descriptions("gacha_admin_currency", "give", "amount"))
	async def admin_currency_give(self, ctx, player, amount):
		"""Give currency to an active character"""

		char_updated = db.increase_currency_single(ctx.guild.id, player.id, amount)

		if (not char_updated):
			error = loc.response("gacha_admin_currency", "give", "error-missing", ctx.interaction.locale).format(player.name)
			await ctx.respond(error, ephemeral=True)
			return

		res = loc.response("gacha_admin_currency", "give", "res1", ctx.interaction.locale).format(amount=amount, name=player.name)
		await ctx.respond(res)

# ------------------------------------------------------------------------
# /gacha_admin currency take
# ------------------------------------------------------------------------
	@currency.command(name="take", guild_only=True,
		name_localizations=loc.command_names("gacha_admin_currency", "take"),
		description_localizations=loc.command_descriptions("gacha_admin_currency", "take"))
	@option("player", discord.Member,
		name_localizations=loc.option_names("gacha_admin_currency", "take", "player"))
	@option("amount", int, min_value=1, max_value=999,
		description="Amount to take",
		name_localizations=loc.option_names("gacha_admin_currency", "take", "amount"),
		description_localizations=loc.option_descriptions("gacha_admin_currency", "take", "amount"))
	async def admin_currency_take(self, ctx, player, amount):
		"""Take currency from an active character"""

		char_updated = db.decrease_currency_single(ctx.guild.id, player.id, amount)

		if (not char_updated):
			error = loc.response("gacha_admin_currency", "take", "error-missing", ctx.interaction.locale).format(player.name)
			await ctx.respond(error, ephemeral=True)
			return

		res = loc.response("gacha_admin_currency", "take", "res1", ctx.interaction.locale).format(amount=amount, name=player.name)
		await ctx.respond(res)

# ------------------------------------------------------------------------
# /gacha_admin currency give_all
# ------------------------------------------------------------------------
	@currency.command(name="give_all", guild_only=True,
		name_localizations=loc.command_names("gacha_admin_currency", "give_all"),
		description_localizations=loc.command_descriptions("gacha_admin_currency", "give_all"))
	@option("amount", int, min_value=1, max_value=999,
		description="Amount to give",
		name_localizations=loc.option_names("gacha_admin_currency", "give_all", "amount"),
		description_localizations=loc.option_descriptions("gacha_admin_currency", "give_all", "amount"))
	async def admin_currency_give_all(self, ctx, amount):
		"""Give currency to all active characters"""

		chars_updated = db.increase_currency_all(ctx.guild.id, amount)

		if (not chars_updated):
			error = loc.response("gacha_admin_currency", "give_all", "error-missing", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		res = loc.response("gacha_admin_currency", "give_all", "res1", ctx.interaction.locale).format(amount)
		await ctx.respond(res)

# ------------------------------------------------------------------------
# /gacha_admin currency view
# ------------------------------------------------------------------------
	@currency.command(name="view", guild_only=True,
		name_localizations=loc.command_names("gacha_admin_currency", "view"),
		description_localizations=loc.command_descriptions("gacha_admin_currency", "view"))
	@option("player", discord.Member,
		name_localizations=loc.option_names("gacha_admin_currency", "view", "player"))
	@option("visible", bool, default=False,
		description="Set to 'True' for a permanent, visible response.",
		name_localizations=loc.common("visible-name"),
		description_localizations=loc.common("visible-desc"))
	async def admin_currency_view(self, ctx, player, visible):
		"""View currency of an active character"""

		char = db.get_active_char(ctx.guild.id, player.id)
		currency_name = db.get_guild_info(ctx.guild.id)["CurrencyName"]
		try:
			res = loc.response("gacha_admin_currency", "view", "res1", ctx.interaction.locale).format(name=char["Name"], amount=char["Currency"], units=currency_name)
			await ctx.respond(res, ephemeral=not visible)
		except:
			error = loc.response("gacha_admin_currency", "view", "error-missing", ctx.interaction.locale).format(player.name)
			await ctx.respond(error, ephemeral=True)

# ------------------------------------------------------------------------
# /gacha_admin currency view_all
# ------------------------------------------------------------------------
	@currency.command(name="view_all", guild_only=True,
		name_localizations=loc.command_names("gacha_admin_currency", "view_all"),
		description_localizations=loc.command_descriptions("gacha_admin_currency", "view_all"))
	@option("visible", bool, default=False,
		description="Set to 'True' for a permanent, visible response.",
		name_localizations=loc.common("visible-name"),
		description_localizations=loc.common("visible-desc"))
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
	@gacha_admin.command(name="add", guild_only=True,
		name_localizations=loc.command_names("gacha_admin", "add"),
		description_localizations=loc.command_descriptions("gacha_admin", "add"))
	@option("name", str,
		description="Item name. Maximum of 64 characters",
		name_localizations=loc.option_names("gacha_admin", "add", "name"),
		description_localizations=loc.option_descriptions("gacha_admin", "add", "name"))
	@option("desc", str,
		description="Item description. 1024 character maximum",
		name_localizations=loc.option_names("gacha_admin", "add", "desc"),
		description_localizations=loc.option_descriptions("gacha_admin", "add", "desc"))
	@option("amount", int, default=None, min_value=1, max_value=99999,
		description="Enter a number to make the item limited.",
		name_localizations=loc.option_names("gacha_admin", "add", "amount"),
		description_localizations=loc.option_descriptions("gacha_admin", "add", "amount"))
	@option("thumbnail", str, default=None,
		description="Optional thumbnail image URL",
		name_localizations=loc.option_names("gacha_admin", "add", "thumbnail"),
		description_localizations=loc.option_descriptions("gacha_admin", "add", "thumbnail"))
	async def gacha_admin_add(self, ctx, name, desc, amount, thumbnail):
		"""Register a new item to gacha, optional item limits and thumbnail"""

		# Enforce limits
		name = name[:64]
		desc = desc[:1024]

		# Add if possible
		try:
			db.add_gacha(ctx.guild.id, name, desc, amount, thumbnail)
		except:
			error = loc.response("gacha_admin", "add", "error-duplicate", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		# Attempt to send gacha embed
		item = db.get_single_gacha(ctx.guild.id, name)
		try:
			embed = utils.get_gacha_embed(item)
			if (not amount):
				amount = "unlimited"

			res = loc.response("gacha_admin", "add", "res1", ctx.interaction.locale).format(amount=amount)
			await ctx.respond(res, embed=embed, ephemeral=True)
		except discord.HTTPException:
			error = loc.response("gacha_admin", "add", "error-url", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			db.remove_gacha_item(ctx.guild.id, name)

# ------------------------------------------------------------------------
# /gacha_admin rm
# ------------------------------------------------------------------------
	@gacha_admin.command(name="rm", guild_only=True,
		name_localizations=loc.command_names("gacha_admin", "rm"),
		description_localizations=loc.command_descriptions("gacha_admin", "rm"))
	@option("name", str,
		description="The display name of item to remove",
		name_localizations=loc.option_names("gacha_admin", "rm", "name"),
		description_localizations=loc.option_descriptions("gacha_admin", "rm", "name"))
	async def gacha_admin_rm(self, ctx, name):
		"""Remove an item from gacha by name"""

		item_removed = db.remove_gacha_item(ctx.guild.id, name)

		if (not item_removed):
			error = loc.response("gacha_admin", "rm", "error-missing", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		res = loc.response("gacha_admin", "rm", "res1", ctx.interaction.locale).format(name)
		await ctx.respond(res)

# ------------------------------------------------------------------------
# /gacha_admin list
# ------------------------------------------------------------------------
	@gacha_admin.command(name="list", guild_only=True,
		name_localizations=loc.command_names("gacha_admin", "list"),
		description_localizations=loc.command_descriptions("gacha_admin", "list"))
	@option("visible", bool, default=False,
		description="Set to 'True' for a permanent, visible response.",
		name_localizations=loc.common("visible-name"),
		description_localizations=loc.common("visible-desc"))
	async def gacha_admin_list(self, ctx, visible):
		"""List all gacha items"""

		items = db.get_all_gacha(ctx.guild.id)

		# Handle no items case
		if (len(items) == 0):
			error = loc.response("gacha_admin", "list", "error-none", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
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

		await ctx.respond(view=EmbedList(embeds, ctx.interaction), ephemeral=not visible, embed=embeds[0])

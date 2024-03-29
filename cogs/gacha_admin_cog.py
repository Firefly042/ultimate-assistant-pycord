"""
Author @Firefly#7113
Admin gacha management
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
	gacha_admin = SlashCommandGroup("gacha_admin", "Admin Gacha management",default_member_permissions=discord.Permissions(administrator=True),
		guild_only=True,
		name_localizations=loc.group_names("gacha_admin"),
		description_localizations=loc.group_descriptions("gacha_admin"))

	currency = gacha_admin.create_subgroup("currency", "Admin currency management")
	currency.default_member_permissions=discord.Permissions(administrator=True)
	currency.guild_only = True,
	currency.name_localizations = loc.group_names("gacha_admin_currency")
	currency.description_localizations = loc.group_descriptions("gacha_admin_currency")

# ------------------------------------------------------------------------
# Commands
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# /gacha_admin currency name
# ------------------------------------------------------------------------
	@currency.command(name="name",
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
		
		await db.edit_guild(ctx.guild.id, "currencyname", name)

		res = loc.response("gacha_admin_currency", "name", "res1", ctx.interaction.locale).format(name)
		await ctx.respond(res)

# ------------------------------------------------------------------------
# /gacha_admin currency cost
# ------------------------------------------------------------------------
	@currency.command(name="cost",
		name_localizations=loc.command_names("gacha_admin_currency", "cost"),
		description_localizations=loc.command_descriptions("gacha_admin_currency", "cost"))
	@option("amount", int, min_value=1, max_value=999,
		description="1 to 999",
		name_localizations=loc.option_names("gacha_admin_currency", "cost", "amount"),
		description_localizations=loc.option_descriptions("gacha_admin_currency", "cost", "amount"))
	async def admin_currency_cost(self, ctx, amount):
		"""Set the cost of a single gacha use"""

		await db.edit_guild(ctx.guild.id, "GachaCost", amount)

		res = loc.response("gacha_admin_currency", "cost", "res1", ctx.interaction.locale).format(amount)
		await ctx.respond(res)

# ------------------------------------------------------------------------
# /gacha_admin currency give
# ------------------------------------------------------------------------
	@currency.command(name="give",
		name_localizations=loc.command_names("gacha_admin_currency", "give"),
		description_localizations=loc.command_descriptions("gacha_admin_currency", "give"))
	@option("player", discord.Member,
		name_localizations=loc.option_names("gacha_admin_currency", "give", "player"))
	@option("amount", int, min_value=1, max_value=999,
		description="Amount to give",
		name_localizations=loc.option_names("gacha_admin_currency", "give", "amount"),
		description_localizations=loc.option_descriptions("gacha_admin_currency", "give", "amount"))
	@option("name", str, default=None,
		description="The registered display name of the character, if not active",
		name_localizations=loc.common("inactive-char-name"),
		description_localizations=loc.common("inactive-char-desc"))
	async def admin_currency_give(self, ctx, player, amount, name):
		"""Give currency to an active character"""

		char_updated = await db.increase_currency_inactive(ctx.guild.id, player.id, amount, name) if name else await db.increase_currency_single(ctx.guild.id, player.id, amount)

		if (not char_updated):
			error = loc.response("gacha_admin_currency", "give", "error-missing", ctx.interaction.locale).format(player.name)
			await ctx.respond(error, ephemeral=True)
			return

		res = loc.response("gacha_admin_currency", "give", "res1", ctx.interaction.locale).format(amount=amount, name=player.name)
		await ctx.respond(res)

# ------------------------------------------------------------------------
# /gacha_admin currency take
# ------------------------------------------------------------------------
	@currency.command(name="take",
		name_localizations=loc.command_names("gacha_admin_currency", "take"),
		description_localizations=loc.command_descriptions("gacha_admin_currency", "take"))
	@option("player", discord.Member,
		name_localizations=loc.option_names("gacha_admin_currency", "take", "player"))
	@option("amount", int, min_value=1, max_value=999,
		description="Amount to take",
		name_localizations=loc.option_names("gacha_admin_currency", "take", "amount"),
		description_localizations=loc.option_descriptions("gacha_admin_currency", "take", "amount"))
	@option("name", str, default=None,
		description="The registered display name of the character, if not active",
		name_localizations=loc.common("inactive-char-name"),
		description_localizations=loc.common("inactive-char-desc"))
	async def admin_currency_take(self, ctx, player, amount, name):
		"""Take currency from an active character"""

		char_updated = await db.decrease_currency_inactive(ctx.guild.id, player.id, amount, name) if name else await db.decrease_currency_single(ctx.guild.id, player.id, amount)

		if (not char_updated):
			error = loc.response("gacha_admin_currency", "take", "error-missing", ctx.interaction.locale).format(player.name)
			await ctx.respond(error, ephemeral=True)
			return

		res = loc.response("gacha_admin_currency", "take", "res1", ctx.interaction.locale).format(amount=amount, name=player.name)
		await ctx.respond(res)

# ------------------------------------------------------------------------
# /gacha_admin currency give_all
# ------------------------------------------------------------------------
	@currency.command(name="give_all",
		name_localizations=loc.command_names("gacha_admin_currency", "give_all"),
		description_localizations=loc.command_descriptions("gacha_admin_currency", "give_all"))
	@option("amount", int, min_value=1, max_value=999,
		description="Amount to give",
		name_localizations=loc.option_names("gacha_admin_currency", "give_all", "amount"),
		description_localizations=loc.option_descriptions("gacha_admin_currency", "give_all", "amount"))
	async def admin_currency_give_all(self, ctx, amount):
		"""Give currency to all active characters"""

		chars = await db.get_all_chars(ctx.guild.id)

		# Seems suboptimal but asyncpg's 'executemany' fails if even one constraint violation occurs. The single increase method automatically corrects on constraint ciolation error.
		for char in chars:
			await db.increase_currency_inactive(ctx.guild.id, char["playerid"], amount, char["name"])

		res = loc.response("gacha_admin_currency", "give_all", "res1", ctx.interaction.locale).format(amount)
		await ctx.respond(res)

# ------------------------------------------------------------------------
# /gacha_admin currency view
# ------------------------------------------------------------------------
	@currency.command(name="view",
		name_localizations=loc.command_names("gacha_admin_currency", "view"),
		description_localizations=loc.command_descriptions("gacha_admin_currency", "view"))
	@option("player", discord.Member,
		name_localizations=loc.option_names("gacha_admin_currency", "view", "player"))
	@option("name", str, default=None,
		description="The registered display name of the character, if not active",
		name_localizations=loc.common("inactive-char-name"),
		description_localizations=loc.common("inactive-char-desc"))
	@option("visible", bool, default=False,
		description="Set to 'True' for a permanent, visible response.",
		name_localizations=loc.common("visible-name"),
		description_localizations=loc.common("visible-desc"))
	async def admin_currency_view(self, ctx, player, name, visible):
		"""View currency of an active character"""

		char = await db.get_character(ctx.guild.id, player.id, name) if name else await db.get_active_char(ctx.guild.id, player.id)

		guild_info = await db.get_guild_info(ctx.guild.id)
		currency_name = guild_info["currencyname"]

		try:
			res = loc.response("gacha_admin_currency", "view", "res1", ctx.interaction.locale).format(name=char["name"], amount=char["currency"], units=currency_name)
			await ctx.respond(res, ephemeral=not visible)
		except:
			error = loc.response("gacha_admin_currency", "view", "error-missing", ctx.interaction.locale).format(player.name)
			await ctx.respond(error, ephemeral=True)

# ------------------------------------------------------------------------
# /gacha_admin currency view_all
# ------------------------------------------------------------------------
	@currency.command(name="view_all",
		name_localizations=loc.command_names("gacha_admin_currency", "view_all"),
		description_localizations=loc.command_descriptions("gacha_admin_currency", "view_all"))
	@option("visible", bool, default=False,
		description="Set to 'True' for a permanent, visible response.",
		name_localizations=loc.common("visible-name"),
		description_localizations=loc.common("visible-desc"))
	async def admin_currency_view_all(self, ctx, visible):
		"""View currency for all characters (active and inactive)"""

		chars = await db.get_all_chars(ctx.guild.id)
		guild_info = await db.get_guild_info(ctx.guild.id)
		currency_name = guild_info["currencyname"]

		msg = f"__{currency_name}__\n"
		for char in chars:
			msg += f"{char['name']}: {char['currency']}\n"

		await ctx.respond(msg[:1800], ephemeral=not visible)

# ------------------------------------------------------------------------
# /gacha_admin add
# ------------------------------------------------------------------------
	@gacha_admin.command(name="add",
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
			await db.add_gacha(ctx.guild.id, name, desc, amount, thumbnail)
		except:
			error = loc.response("gacha_admin", "add", "error-duplicate", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		# Attempt to send gacha embed
		item = await db.get_single_gacha(ctx.guild.id, name)
		try:
			embed = utils.get_gacha_embed(item)
			if (not amount):
				amount = "unlimited"

			res = loc.response("gacha_admin", "add", "res1", ctx.interaction.locale).format(amount=amount)
			await ctx.respond(res, embed=embed, ephemeral=True)
		except discord.HTTPException:
			error = loc.response("gacha_admin", "add", "error-url", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			await db.remove_gacha_item(ctx.guild.id, name)

# ------------------------------------------------------------------------
# /gacha_admin rm
# ------------------------------------------------------------------------
	@gacha_admin.command(name="rm",
		name_localizations=loc.command_names("gacha_admin", "rm"),
		description_localizations=loc.command_descriptions("gacha_admin", "rm"))
	@option("name", str,
		description="The display name of item to remove",
		name_localizations=loc.option_names("gacha_admin", "rm", "name"),
		description_localizations=loc.option_descriptions("gacha_admin", "rm", "name"))
	async def gacha_admin_rm(self, ctx, name):
		"""Remove an item from gacha by name"""

		item_removed = await db.remove_gacha_item(ctx.guild.id, name)

		if (not item_removed):
			error = loc.response("gacha_admin", "rm", "error-missing", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		res = loc.response("gacha_admin", "rm", "res1", ctx.interaction.locale).format(name)
		await ctx.respond(res)

# ------------------------------------------------------------------------
# /gacha_admin list
# ------------------------------------------------------------------------
	@gacha_admin.command(name="list",
		name_localizations=loc.command_names("gacha_admin", "list"),
		description_localizations=loc.command_descriptions("gacha_admin", "list"))
	@option("visible", bool, default=False,
		description="Set to 'True' for a permanent, visible response.",
		name_localizations=loc.common("visible-name"),
		description_localizations=loc.common("visible-desc"))
	async def gacha_admin_list(self, ctx, visible):
		"""List all gacha items"""

		items = await db.get_all_gacha(ctx.guild.id)

		# Handle no items case
		if (len(items) == 0):
			error = loc.response("gacha_admin", "list", "error-none", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		# Order chars by name, error if no characters
		items = sorted(items, key=lambda d: d["name"])

		# To stay safely within limits, we'll allow up to 35 items per embed
		n_embeds = math.ceil(len(items) / 35)
		embeds = [discord.Embed(title=f"{i+1}/{n_embeds}") for i in range(n_embeds)]

		for i in range(n_embeds):
			msg_i = ""
			for _ in range(35):
				try:
					item = items.pop(0)
				except IndexError:
					break

				if (item["amount"]):
					amnt_str = f"({item['amountremaining']} / {item['amount']})"
				else:
					amnt_str = ""

				msg_i += f"**{item['name']}** {amnt_str} - {item['description'][:32]} \n"

			embeds[i].description = msg_i[:3900]

		await ctx.respond(view=EmbedList(embeds, ctx.interaction), ephemeral=not visible, embed=embeds[0])

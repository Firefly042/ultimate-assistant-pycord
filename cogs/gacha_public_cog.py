"""
Author @Firefly#7113
Public gacha commands
"""

import discord
from discord import slash_command, option
from discord.commands import SlashCommandGroup
from discord.ext import commands

from db import db
from localization import loc

from utils import utils


# ------------------------------------------------------------------------
# COG
# ------------------------------------------------------------------------
def setup(bot):
	bot.add_cog(GachaPublicCog(bot))

# pylint: disable=no-self-use
class GachaPublicCog(commands.Cog):
	"""Gacha currency and pulling for players"""

	def __init__(self, bot):
		self.bot = bot
		print(f"Added {self.__class__.__name__}")


# ------------------------------------------------------------------------
# Command groups
# Change the decorator to @<name>.command()
# ------------------------------------------------------------------------
	currency = SlashCommandGroup("currency", "Gacha currency",
		guild_only=True,
		name_localizations=loc.group_names("currency"),
		description_localizations=loc.group_descriptions("currency"))


# ------------------------------------------------------------------------
# Commands
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# /gacha
# ------------------------------------------------------------------------
	@slash_command(name="gacha",
		name_localizations=loc.nongroup_names("gacha"),
		description_localizations=loc.nongroup_descriptions("gacha"))
	@option("visible", bool, default=True,
		description="Set to 'True' for a permanent, visible response.",
		name_localizations=loc.common("visible-name"),
		description_localizations=loc.common("visible-desc"))
	async def gacha(self, ctx, visible):
		"""Draw an item from the gacha. Costs at least 1 currency"""

		# Character info
		char = await db.get_active_char(ctx.guild.id, ctx.interaction.user.id)

		# Guild info
		guild_info = await db.get_guild_info(ctx.guild.id)
		currency_name = guild_info["currencyname"]
		cost = guild_info["gachacost"]

		# Get currency amount, returns TypeError if no character
		try:
			currency = char["currency"]
		except TypeError:
			error = loc.common_res("no-character", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		# Check if player has any currency
		if (currency < cost):
			error = loc.nongroup_res("gacha", "error-currency", ctx.interaction.locale).format(units=currency_name)
			await ctx.respond(error, ephemeral=True)
			return

		# Proceed
		try:
			item = await db.get_random_item(ctx.guild.id)

			msg = loc.nongroup_res("gacha", "res1", ctx.interaction.locale).format(amount=str(currency-cost), units=currency_name)

			try:
				await ctx.respond(content=msg, embed=utils.get_gacha_embed(item), ephemeral=not visible)
			except discord.HTTPException:
				await ctx.respond(content=msg+"\n[IMAGE URL ERROR]", ephemeral=not visible)

			# Reduce currency
			await db.decrease_currency_single(ctx.guild.id, ctx.interaction.user.id, cost)

		# No items
		except TypeError as error:
			error = loc.nongroup_res("gacha", "error-none", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		# Add to player inventory
		await db.add_item(ctx.guild.id, ctx.interaction.user.id, item["name"], desc=item["description"])

# ------------------------------------------------------------------------
# /currency view
# ------------------------------------------------------------------------
	@currency.command(name="view",
		name_localizations=loc.command_names("currency", "view"),
		description_localizations=loc.command_descriptions("currency", "view"))
	@option("visible", bool, default=False,
		description="Set to 'True' for a permanent, visible response.",
		name_localizations=loc.common("visible-name"),
		description_localizations=loc.common("visible-desc"))
	async def currency_view(self, ctx, visible):
		"""View how much currency you have"""

		char = await db.get_active_char(ctx.guild.id, ctx.interaction.user.id)

		try:
			amount = char['currency']
		except TypeError:
			error = loc.common_res("no-character", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		guild_info = await db.get_guild_info(ctx.guild.id)
		currency_name = guild_info['currencyname']

		res = loc.response("currency", "view", "res1", ctx.interaction.locale).format(name=char["name"], amount=amount, units=currency_name)
		await ctx.respond(res, ephemeral=not visible)

# ------------------------------------------------------------------------
# /currency give
# ------------------------------------------------------------------------
	@currency.command(name="give",
		name_localizations=loc.command_names("currency", "give"),
		description_localizations=loc.command_descriptions("currency", "give"))
	@option("recipient", discord.Member,
		description="The recipient",
		name_localizations=loc.option_names("currency", "give", "recipient"),
		description_localizations=loc.option_descriptions("currency", "give", "recipient"))
	@option("amount", int, min_value=1, max_value=999,
		description="How much you will give",
		name_localizations=loc.option_names("currency", "give", "amount"),
		description_localizations=loc.option_descriptions("currency", "give","amount"))
	@option("recipient_name", str, default=None,
		description="The registered display name of the character, if not active",
		name_localizations=loc.common("inactive-recipient-name"),
		description_localizations=loc.common("inactive-char-desc"))
	@option("visible", bool, default=False,
		description="Set to 'True' for a permanent, visible response.",
		name_localizations=loc.common("visible-name"),
		description_localizations=loc.common("visible-desc"))
	async def currency_give(self, ctx, recipient, amount, recipient_name, visible):
		"""Give another active character some of your own currency."""

		# Get values
		sender = await db.get_active_char(ctx.guild.id, ctx.interaction.user.id)
		receiver = await db.get_character(ctx.guild.id, recipient.id, recipient_name) if recipient_name else await db.get_active_char(ctx.guild.id, recipient.id)

		# Check that sender is valid
		try:
			sender_amount = sender['currency']
		except TypeError:
			error = loc.common_res("no-character", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		guild_info = await db.get_guild_info(ctx.guild.id)
		currency_name = guild_info['currencyname']

		# Check if amount is valid
		if (sender_amount < amount):
			error = loc.response("currency", "give", "error-amount", ctx.interaction.locale).format(amount=sender_amount, units=currency_name)
			await ctx.respond(error, ephemeral=True)
			return

		# Check if recipient is valid
		try:
			_ = receiver['currency']
		except TypeError:
			error = loc.response("currency", "give", "error-missingrecipient", ctx.interaction.locale).format(recipient.name)
			await ctx.respond(error, ephemeral=True)
			return

		# Adjust DB
		if (recipient_name):
			await db.increase_currency_inactive(ctx.guild.id, recipient.id, amount, recipient_name)
		else:
			await db.increase_currency_single(ctx.guild.id, recipient.id, amount)
		
		await db.decrease_currency_single(ctx.guild.id, ctx.interaction.user.id, amount)

		# Send response
		res = loc.response("currency", "give", "res1", ctx.interaction.locale).format(sender=sender["name"], recipient=receiver["name"], amount=amount, units=currency_name)
		await ctx.respond(res, ephemeral=not visible)
 
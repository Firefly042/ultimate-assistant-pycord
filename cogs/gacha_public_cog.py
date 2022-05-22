"""
Author @Firefly#7113
Public gacha commands
"""

import discord
from discord import slash_command, option
from discord.commands import SlashCommandGroup
from discord.ext import commands

import db

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
	currency = SlashCommandGroup("currency", "Gacha currency")


# ------------------------------------------------------------------------
# Commands
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# /gacha
# ------------------------------------------------------------------------
	@slash_command(name="gacha")
	@option("visible", bool, default=False, description="Set true for public result")
	async def gacha(self, ctx, visible):
		"""Draw an item from the gacha. Costs at least 1 currency"""

		# Character info
		char = db.get_active_char(ctx.guild.id, ctx.interaction.user.id)

		# Guild info
		guild_info = db.get_guild_info(ctx.guild.id)
		currency_name = guild_info["CurrencyName"]
		cost = guild_info["GachaCost"]

		# Get currency amount, returns TypeError if no character
		try:
			currency = char["Currency"]
		except TypeError:
			await ctx.respond("You do not have an active character!", ephemeral=True)
			return

		# Check if player has any currency
		if (currency < cost):
			await ctx.respond(f"You do not have enough {currency_name}!", ephemeral=True)
			return

		# Proceed
		try:
			item = db.get_random_item(ctx.guild.id)
			msg = f"You have {currency-cost} {currency_name} remaining."
			await ctx.respond(content=msg, embed=utils.get_gacha_embed(item), ephemeral=not visible)

			# Reduce currency
			db.decrease_currency_single(ctx.guild.id, ctx.interaction.user.id, cost)

		# No items
		except TypeError as error:
			print(error)
			await ctx.respond("This server has no gacha items!", ephemeral=True)
			return

		# Add to player inventory
		db.add_item(ctx.guild.id, ctx.interaction.user.id, item["Name"], desc=item["Desc"])

# ------------------------------------------------------------------------
# /currency view
# ------------------------------------------------------------------------
	@currency.command(name="view")
	@option("visible", bool, default=False, description="Set true for public result")
	async def currency_view(self, ctx, visible):
		"""View how much currency you have"""

		char = db.get_active_char(ctx.guild.id, ctx.interaction.user.id)

		try:
			amount = char['Currency']
		except TypeError:
			await ctx.respond("You do not have an active character in this server!", ephemeral=True)
			return

		currency_name = db.get_guild_info(ctx.guild.id)['CurrencyName']

		await ctx.respond(f"{char['Name']} has {amount} {currency_name}", ephemeral=not visible)

# ------------------------------------------------------------------------
# /currency give
# ------------------------------------------------------------------------
	@currency.command(name="give")
	@option("recipient", discord.Member, description="The recipient")
	@option("amount", int, description="How much you will give", min_value=1, max_value=999)
	@option("visible", bool, default=True, description="Set false for hidden result")
	async def currency_give(self, ctx, recipient, amount, visible):
		"""Give another active character some of your own currency."""

		# Get values
		sender = db.get_active_char(ctx.guild.id, ctx.interaction.user.id)
		receiver= db.get_active_char(ctx.guild.id, recipient.id)

		# Check that sender is valid
		try:
			sender_amount = sender['Currency']
		except TypeError:
			await ctx.respond("You do not have an active character in this server!", ephemeral=True)
			return

		currency_name = db.get_guild_info(ctx.guild.id)['CurrencyName']

		# Check if amount is valid
		if (sender_amount < amount):
			await ctx.respond(f"{sender['Name']} only has {sender_amount} {currency_name}!", ephemeral=True)
			return

		# Check if recipient is valid
		try:
			_ = receiver['Currency']
		except TypeError:
			await ctx.respond(f"{recipient.name} does not have an active character in this server!", ephemeral=True)
			return

		# Adjust DB
		db.increase_currency_single(ctx.guild.id, recipient.id, amount)
		db.decrease_currency_single(ctx.guild.id, ctx.interaction.user.id, amount)

		# Send response
		await ctx.respond(f"{sender['Name']} gives {receiver['Name']} {amount} {currency_name}", ephemeral=not visible)

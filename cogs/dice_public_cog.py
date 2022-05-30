"""
Author @Firefly#7113
Public/Player dice commands
"""

import discord
from discord import option
from discord.commands import SlashCommandGroup
from discord.ext import commands

import d20

import db

from utils import utils
from localization import loc


# ------------------------------------------------------------------------
# COMPONENT CLASSES AND CONSTANTS
# ------------------------------------------------------------------------


# ------------------------------------------------------------------------
# COG
# ------------------------------------------------------------------------
def setup(bot):
	bot.add_cog(DicePublicCog(bot))

# pylint: disable=no-self-use
class DicePublicCog(commands.Cog):
	"""Player/public dice commands"""

	def __init__(self, bot):
		self.bot = bot
		print(f"Added {self.__class__.__name__}")


# ------------------------------------------------------------------------
# Command groups
# Change the decorator to @<name>.command()
# ------------------------------------------------------------------------
	dice = SlashCommandGroup("roll", "Dice rolling (d20 and custom)",
		name_localizations=loc.group_names("roll"),
		description_localizations=loc.group_descriptions("roll"))


# ------------------------------------------------------------------------
# Commands
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# /roll dice
# ------------------------------------------------------------------------
	@dice.command(name="dice",
		name_localizations=loc.command_names("roll", "dice"),
		description_localizations=loc.command_descriptions("roll", "dice"))
	@option("dice", str,
		description="d20 notation",
		name_localizations=loc.option_names("roll", "dice", "dice"),
		description_localizations=loc.option_descriptions("roll", "dice", "dice"))
	@option("visible", bool, default=False,
		description="Set to 'True' for a permanent, visible response.",
		name_localizations=loc.common("visible-name"),
		description_localizations=loc.common("visible-desc"))
	async def roll_dice(self, ctx, dice, visible):
		"""Roll with normal d20 notation"""

		try:
			res = d20.roll(dice)
		except d20.errors.RollSyntaxError:
			error = loc.response("roll", "dice", "error-format", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return
		except d20.errors.TooManyRolls:
			error = loc.response("roll", "dice", "error-amount", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		embed = discord.Embed(description=str(res)[:2048])
		await ctx.respond(embed=embed, ephemeral=not visible)

# ------------------------------------------------------------------------
# /roll new
# ------------------------------------------------------------------------
	@dice.command(name="new", guild_only=True,
		name_localizations=loc.command_names("roll", "new"),
		description_localizations=loc.command_descriptions("roll", "new"))
	@option("name", str,
		description="A short name for the roll. 16 characters max (lowercase)",
		name_localizations=loc.option_names("roll", "new", "name"),
		description_localizations=loc.option_descriptions("roll", "new", "name"))
	@option("dice", str,
		description="d20 notation. 64 characters max",
		name_localizations=loc.option_names("roll", "new", "dice"),
		description_localizations=loc.option_descriptions("roll", "new", "dice"))
	async def roll_new(self, ctx, name, dice):
		"""Add or edit a custom dice roll for your active character"""

		name = name[:16].lower()
		dice = dice[:64]

		# Check validity of roll
		try:
			d20.roll(dice)
		except d20.errors.RollSyntaxError:
			error = loc.response("roll", "new", "error-format", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return
		except d20.errors.TooManyRolls:
			error = loc.response("roll", "new", "error-amount", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		# Add to db
		try:
			updated = db.add_roll(ctx.guild.id, ctx.interaction.user.id, name, dice)
		except:
			error = loc.response("roll", "new", "error-limit", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		if (not updated):
			error = loc.common_res("no-character", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		res = loc.response("roll", "new", "res1", ctx.interaction.locale).format(name=name, dice=dice)
		await ctx.respond(res)

# ------------------------------------------------------------------------
# /roll rm
# ------------------------------------------------------------------------
	@dice.command(name="rm", guild_only=True,
		name_localizations=loc.command_names("roll", "rm"),
		description_localizations=loc.command_descriptions("roll", "rm"))
	@option("name", str,
		description="Name of existing roll",
		name_localizations=loc.option_names("roll", "rm", "name"),
		description_localizations=loc.option_descriptions("roll", "rm", "name"))
	async def roll_rm(self, ctx, name):
		"""Remove a custom dice roll for active character"""

		# Remove from db
		try:
			db.rm_roll(ctx.guild.id, ctx.interaction.user.id, name)
		except KeyError:
			error = loc.response("roll", "rm", "error-missing", ctx.interaction.locale).format(name.lower())
			await ctx.respond(error, ephemeral=True)
			return
		except TypeError:
			error = loc.common_res("no-character", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		res = loc.response("roll", "rm", "res1", ctx.interaction.locale).format(name.lower())
		await ctx.respond(res)

# ------------------------------------------------------------------------
# /roll custom
# ------------------------------------------------------------------------
	@dice.command(name="custom", guild_only=True,
		name_localizations=loc.command_names("roll", "custom"),
		description_localizations=loc.command_descriptions("roll", "custom"))
	@option("name", str,
		description="Name of existing roll",
		name_localizations=loc.option_names("roll", "custom", "name"),
		description_localizations=loc.option_descriptions("roll", "custom", "name"))
	@option("visible", bool, default=False,
		description="Set to 'True' for a permanent, visible response.",
		name_localizations=loc.common("visible-name"),
		description_localizations=loc.common("visible-desc"))
	async def roll_c(self, ctx, name, visible):
		"""Roll an existing custom roll by name"""

		name = name.lower()

		char = db.get_active_char(ctx.guild.id, ctx.interaction.user.id)

		try:
			rolls = utils.str_to_dict(char['CustomRolls'])
		except TypeError:
			error = loc.common_res("no-character", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		# Check if name in keys
		try:
			res = d20.roll(rolls[name])
		except KeyError:
			error = loc.response("roll", "custom", "error-missing", ctx.interaction.locale).format(name)
			await ctx.respond(error, ephemeral=True)
			return

		# Fancy stuff
		char = db.get_active_char(ctx.guild.id, ctx.interaction.user.id)
		hex_color = utils.hex_to_color(char['HexColor'])

		# Result
		desc = loc.response("roll", "custom", "res1", ctx.interaction.locale).format(name=char["Name"], dice=name)
		embed = discord.Embed(color=hex_color, title=f"**{desc}**"[:128], description=f"{str(res)[:2048]}")
		await ctx.respond(embed=embed, ephemeral=not visible)

# ------------------------------------------------------------------------
# /roll list
# ------------------------------------------------------------------------
	@dice.command(name="list", guild_only=True,
		name_localizations=loc.command_names("roll", "list"),
		description_localizations=loc.command_descriptions("roll", "list"))
	@option("visible", bool, default=False,
		description="Set to 'True' for a permanent, visible response.",
		name_localizations=loc.common("visible-name"),
		description_localizations=loc.common("visible-desc"))
	async def roll_list(self, ctx, visible):
		"""View your custom rolls"""

		char = db.get_active_char(ctx.guild.id, ctx.interaction.user.id)

		try:
			rolls = utils.str_to_dict(char['CustomRolls'])
		except TypeError:
			error = loc.common_res("no-character", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		msg = loc.response("roll", "list", "res1", ctx.interaction.locale)
		for name in sorted(rolls.keys()):
			msg += f"\n**{name}**: {rolls[name]}"

		await ctx.respond(msg[:1500], ephemeral=not visible)

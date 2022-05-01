"""
Original template by @Firefly#7113, April 2022
Commands for character registration and profile management
"""

import discord
from discord import slash_command, option
from discord.commands import permissions, SlashCommandGroup, CommandPermission
from discord.ext import commands

# import aiocron
import d20

# from config import ADMIN_ROLE, PLAYER_ROLE
import db

from utils import utils

# ------------------------------------------------------------------------
# COMPONENT CLASSES AND CONSTANTS
# ------------------------------------------------------------------------


# ------------------------------------------------------------------------
# COG
# ------------------------------------------------------------------------
def setup(bot):
	"""Setup. Change TemplateCog to Class name"""
	bot.add_cog(DicePublicCog(bot))

# pylint: disable=no-self-use
class DicePublicCog(commands.Cog):
	"""Massaging management for mods"""

	def __init__(self, bot):
		self.bot = bot
		print(f"Added {self.__class__.__name__}")


# ------------------------------------------------------------------------
# Command groups
# Change the decorator to @<name>.command()
# ------------------------------------------------------------------------
	dice = SlashCommandGroup("roll", "Dice rolling")


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
# /roll d
# ------------------------------------------------------------------------
	@dice.command(name="d")
	@option("roll", str, description="d20 notation")
	@option("visible", bool, default=False, description="Set to True for public response")
	async def roll_d(self, ctx, roll, visible):
		"""Roll with normal d20 notation"""
		
		try:
			res = d20.roll(roll)
		except d20.errors.RollSyntaxError:
			await ctx.respond("Invalid dice format!", ephemeral=True)
			return
		except d20.errors.TooManyRolls:
			await ctx.respond("Too many rolls!", ephemeral=True)
			return

		embed = discord.Embed(title=str(res)[:256])
		await ctx.respond(embed=embed, ephemeral=not visible)

# ------------------------------------------------------------------------
# /roll new
# ------------------------------------------------------------------------
	@dice.command(name="new")
	@option("name", str, description="A short name for the roll. 16 characters max (lowercase)")
	@option("roll", str, description="d20 notation. 64 characters max")
	async def roll_new(self, ctx, name, roll):
		"""Add or edit a custom dice roll for active character"""

		name = name[:16].lower()
		roll = roll[:64]

		# Check validity of roll
		try:
			res = d20.roll(roll)
		except d20.errors.RollSyntaxError:
			await ctx.respond("Invalid dice format!", ephemeral=True)
			return
		except d20.errors.TooManyRolls:
			await ctx.respond("Too many rolls!", ephemeral=True)
			return

		# Add to db
		try:
			updated = db.add_roll(ctx.guild.id, ctx.interaction.user.id, name, roll)
		except:
			await ctx.reply("You have hit the limit of 25 rolls!", ephemeral=True)

		if (not updated):
			await ctx.respond("You do not have an active character!", ephemeral=True)
			return

		await ctx.respond(f"Added/Edited custom roll **{name}: {roll}**")

# ------------------------------------------------------------------------
# /roll rm
# ------------------------------------------------------------------------
	@dice.command(name="rm")
	@option("name", str, description="Name of existing roll")
	async def roll_rm(self, ctx, name):
		"""Remove a custom dice roll for active character"""

		# Remove from db
		try:
			db.rm_roll(ctx.guild.id, ctx.interaction.user.id, name)
		except KeyError:
			await ctx.respond(f"You do not have a roll named {name.lower()}", ephemeral=True)
			return
		except TypeError:
			await ctx.respond("You do not have an active character!", ephemeral=True)
			return

		await ctx.respond(f"Removed custom roll {name.lower()}")

# ------------------------------------------------------------------------
# /roll c
# ------------------------------------------------------------------------
	@dice.command(name="c")
	@option("name", str, description="Name of existing roll")
	@option("visible", bool, default=False, description="Set to True for public response")
	async def roll_c(self, ctx, name, visible):
		"""Roll an existing custom roll by name"""

		name = name.lower()

		char = db.get_active_char(ctx.guild.id, ctx.interaction.user.id)

		try:
			rolls = utils.str_to_dict(char['CustomRolls'])
		except TypeError:
			await ctx.respond("You do not have an active character!", ephemeral=True)
			return

		# Check if name in keys
		try:
			res = d20.roll(rolls[name])
		except KeyError:
			await ctx.respond(f"You do not have a roll named {name}!", ephemeral=True)
			return

		# Fancy stuff
		char = db.get_active_char(ctx.guild.id, ctx.interaction.user.id)
		hex_color = utils.hex_to_color(char['HexColor'])

		# Result
		embed = discord.Embed(color=hex_color, description=f"*{char['Name']} rolls {name}*", title=f"{str(res)[:128]}")
		await ctx.respond(embed=embed, ephemeral=not visible)

# ------------------------------------------------------------------------
# /roll list
# ------------------------------------------------------------------------
	@dice.command(name="list")
	@option("visible", bool, default=False, description="Set to True for permanent response")
	async def roll_list(self, ctx, visible):
		"""View your custom rolls"""

		char = db.get_active_char(ctx.guild.id, ctx.interaction.user.id)

		try:
			rolls = utils.str_to_dict(char['CustomRolls'])
		except TypeError:
			await ctx.respond("You do not have an active character!", ephemeral=True)
			return

		msg = "__Custom Rolls__"
		for name in sorted(rolls.keys()):
			msg += f"\n**{name}**: {rolls[name]}"

		await ctx.respond(msg[:1500], ephemeral=not visible)
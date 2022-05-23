"""
Author @Firefly#7113
Admin dice commands
"""

import discord
from discord import option
from discord.commands import SlashCommandGroup
from discord.ext import commands

import db

from utils import utils


# ------------------------------------------------------------------------
# COG
# ------------------------------------------------------------------------
def setup(bot):
	bot.add_cog(DiceAdminCog(bot))

# pylint: disable=no-self-use
class DiceAdminCog(commands.Cog):
	"""Dice viewing for mods"""

	def __init__(self, bot):
		self.bot = bot
		print(f"Added {self.__class__.__name__}")


# ------------------------------------------------------------------------
# Command groups
# Change the decorator to @<name>.command()
# ------------------------------------------------------------------------
	dice_admin = SlashCommandGroup("roll_admin", "Dice rolling (admin)")


# ------------------------------------------------------------------------
# Commands
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# /roll list
# ------------------------------------------------------------------------
	@dice_admin.command(name="list")
	@option("player", discord.Member, description="Active character to view")
	@option("visible", bool, default=False, description="Set to True for permanent response")
	async def roll_list(self, ctx, player, visible):
		"""View a player's active character's custom rolls"""

		char = db.get_active_char(ctx.guild.id, player.id)

		try:
			rolls = utils.str_to_dict(char['CustomRolls'])
		except TypeError:
			await ctx.respond("That player does not have an active character!", ephemeral=True)
			return

		msg = f"__Custom Rolls for {char['Name']}__"
		for name in sorted(rolls.keys()):
			msg += f"\n**{name}**: {rolls[name]}"

		await ctx.respond(msg[:1500], ephemeral=not visible)

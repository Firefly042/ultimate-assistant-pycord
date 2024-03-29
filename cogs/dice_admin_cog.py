"""
Author @Firefly#7113
Admin dice commands
"""

import discord
from discord import option
from discord.commands import SlashCommandGroup
from discord.ext import commands

from db import db

from utils import utils
from localization import loc

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
	dice_admin = SlashCommandGroup("roll_admin", "Dice rolling (admin)",
		default_member_permissions=discord.Permissions(administrator=True),
		guild_only=True,
		name_localizations=loc.group_names("roll_admin"),
		description_localizations=loc.group_descriptions("roll_admin"))


# ------------------------------------------------------------------------
# Commands
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# /roll_admin list
# ------------------------------------------------------------------------
	@dice_admin.command(name="list",
		name_localizations=loc.command_names("roll_admin", "list"),
		description_localizations=loc.command_descriptions("roll_admin", "list"))
	@option("player", discord.Member,description="Active character to view",
		name_localizations=loc.option_names("roll_admin", "list", "player"),
		description_localizations=loc.option_descriptions("roll_admin", "list", "player"))
	@option("name", str, default=None,
		description="The registered display name of the character, if not active",
		name_localizations=loc.common("inactive-char-name"),
		description_localizations=loc.common("inactive-char-desc"))
	@option("visible", bool, default=False,
		description="Set to 'True' for a permanent, visible response.",
		name_localizations=loc.common("visible-name"),
		description_localizations=loc.common("visible-desc"))
	async def roll_list(self, ctx, player, name, visible):
		"""View a player's active character's custom rolls"""

		char = await db.get_character(ctx.guild.id, player.id, name) if name else await db.get_active_char(ctx.guild.id, player.id)

		try:
			rolls = utils.str_to_dict(char['customrolls'])
		except TypeError:
			error = loc.response("roll_admin", "list", "error-missing", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		msg = loc.response("roll_admin", "list", "res1", ctx.interaction.locale).format(char["name"])
		for name in sorted(rolls.keys()):
			msg += f"\n**{name}**: {rolls[name]}"

		await ctx.respond(msg[:1500], ephemeral=not visible)

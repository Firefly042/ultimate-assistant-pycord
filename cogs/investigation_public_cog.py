"""
Author @Firefly#7113
Player investigation commands
"""

from discord import option
from discord.commands import SlashCommandGroup
from discord.ext import commands

import db
from localization import loc


# ------------------------------------------------------------------------
# COG
# ------------------------------------------------------------------------
def setup(bot):
	bot.add_cog(InvestigationPublicCog(bot))

# pylint: disable=no-self-use, too-many-arguments
class InvestigationPublicCog(commands.Cog):
	"""Investigation commands for players"""

	def __init__(self, bot):
		self.bot = bot
		print(f"Added {self.__class__.__name__}")


# ------------------------------------------------------------------------
# Command groups
# Change the decorator to @<name>.command()
# ------------------------------------------------------------------------
	investigate = SlashCommandGroup("investigate", "Player investigation",
		name_localizations=loc.group_names("investigate"),
		description_localizations=loc.group_descriptions("investigate"))


# ------------------------------------------------------------------------
# Commands
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# /investigate here
# ------------------------------------------------------------------------
	@investigate.command(name="here",
		name_localizations=loc.command_names("investigate", "here"),
		description_localizations=loc.command_descriptions("investigate", "here"))
	@option("name", str,
		description="Name of object",
		name_localizations=loc.option_names("investigate", "here", "name"),
		description_localizations=loc.option_descriptions("investigate", "here", "name"))
	@option("visible", bool, default=False,
		description="Set to 'True' for a permanent, visible response.",
		name_localizations=loc.common("visible-name"),
		description_localizations=loc.common("visible-desc"))
	async def here(self, ctx, name, visible):
		"""Investigate an item in current channel"""

		item = db.get_investigation(ctx.guild.id, ctx.channel.id, name)

		# Nonexistent item, or taken item
		if (not item or item["TakenBy"]):
			error = loc.response("investigate", "here", "error-missing", ctx.interaction.locale).format(name)
			await ctx.respond(error, ephemeral=True)
			return

		message = f"**{name}**\n{item['Desc']}"
		await ctx.respond(message, ephemeral=not visible)


# ------------------------------------------------------------------------
# /investigate take
# ------------------------------------------------------------------------
	@investigate.command(name="take",
		name_localizations=loc.command_names("investigate", "take"),
		description_localizations=loc.command_descriptions("investigate", "take"))
	@option("name", str,
		description="Name of object",
		name_localizations=loc.option_names("investigate", "take", "name"),
		description_localizations=loc.option_descriptions("investigate", "take", "name"))
	@option("visible", bool, default=False,
		description="Set to 'True' for a permanent, visible response.",
		name_localizations=loc.common("visible-name"),
		description_localizations=loc.common("visible-desc"))
	async def take(self, ctx, name, visible):
		"""Take an item in current channel, if allowed"""

		item = db.get_investigation(ctx.guild.id, ctx.channel.id, name)

		if (not item):
			error = loc.response("investigate", "take", "error-missing", ctx.interaction.locale).format(name)
			await ctx.respond(error, ephemeral=True)
			return

		if (not item["Stealable"]):
			error = loc.response("investigate", "take", "error-forbidden", ctx.interaction.locale).format(name)
			await ctx.respond(error, ephemeral=True)
			return

		# Add to player inventory
		updated = db.add_item(ctx.guild.id, ctx.interaction.user.id, name, desc=item["Desc"])

		if (not updated):
			error = loc.common_res("no-character", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		# Update the investigation
		db.set_investigation_taken(ctx.guild.id, ctx.channel.id, name, ctx.interaction.user.id)

		# Respond
		res = loc.response("investigate", "take", "res1", ctx.interaction.locale).format(name)
		await ctx.respond(res, ephemeral=not visible)

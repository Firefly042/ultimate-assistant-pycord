"""
Author @Firefly#7113
Player investigation commands
"""

from discord import option
from discord.commands import SlashCommandGroup
from discord.ext import commands

import db


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
	investigate = SlashCommandGroup("investigate", "Player investigation")


# ------------------------------------------------------------------------
# Commands
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# /investigate here
# ------------------------------------------------------------------------
	@investigate.command(name="here")
	@option("name", str, description="Name of object")
	@option("visible", bool, default=False, description="Set True for public response")
	async def here(self, ctx, name, visible):
		"""Investigate an item in current channel"""

		item = db.get_investigation(ctx.guild.id, ctx.channel.id, name)

		# Nonexistent item, or taken item
		if (not item or item["TakenBy"]):
			await ctx.respond(f"{name} does not exist in this channel!", ephemeral=True)
			return

		message = f"**{name}**\n{item['Desc']}"
		await ctx.respond(message, ephemeral=not visible)


# ------------------------------------------------------------------------
# /investigate take
# ------------------------------------------------------------------------
	@investigate.command(name="take")
	@option("name", str, description="Name of object")
	@option("visible", bool, default=False, description="Set True for public response")
	async def take(self, ctx, name, visible):
		"""Take an item in current channel, if allowed"""

		item = db.get_investigation(ctx.guild.id, ctx.channel.id, name)

		if (not item):
			await ctx.respond(f"{name} does not exist in this channel!", ephemeral=True)
			return

		if (not item["Stealable"]):
			await ctx.respond(f"{name} cannot be taken!", ephemeral=True)
			return

		# Add to player inventory
		updated = db.add_item(ctx.guild.id, ctx.interaction.user.id, name, desc=item["Desc"])

		if (not updated):
			await ctx.respond("You do not have an active character!", ephemeral=True)
			return

		# Update the investigation
		db.set_investigation_taken(ctx.guild.id, ctx.channel.id, name, ctx.interaction.user.id)

		# Respond
		await ctx.respond(f"Took {name}", ephemeral=not visible)

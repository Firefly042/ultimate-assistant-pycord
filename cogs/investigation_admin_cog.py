"""
Author @Firefly#7113
Admin investigation commands
"""

import math

import discord
from discord import option
from discord.commands import SlashCommandGroup
from discord.ext import commands

import db

from utils import utils
from utils.embed_list import EmbedList


# ------------------------------------------------------------------------
# COG
# ------------------------------------------------------------------------
def setup(bot):
	bot.add_cog(InvestigationAdminCog(bot))

# pylint: disable=no-self-use, too-many-arguments
class InvestigationAdminCog(commands.Cog):
	"""Investigation management for admins"""

	def __init__(self, bot):
		self.bot = bot
		print(f"Added {self.__class__.__name__}")


# ------------------------------------------------------------------------
# Command groups
# Change the decorator to @<name>.command()
# ------------------------------------------------------------------------
	investigate_admin = SlashCommandGroup("investigate_admin", "Admin investigation management")


# ------------------------------------------------------------------------
# Commands
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# /investigate_admin new
# ------------------------------------------------------------------------
	@investigate_admin.command(name="new")
	@option("channel", discord.TextChannel, description="Channel that this investigation is in")
	@option("desc", str, description="Text shown to investigator")
	@option("name", str, description="Default name")
	@option("name_2", str, default=None, description="Alternate name")
	@option("name_3", str, default=None, description="Alternate name")
	@option("name_4", str, default=None, description="Alternate name")
	@option("name_5", str, default=None, description="Alternate name")
	@option("name_6", str, default=None, description="Alternate name")
	@option("name_7", str, default=None, description="Alternate name")
	@option("name_8", str, default=None, description="Alternate name")
	@option("stealable", bool, default=False, description="Set to True to allow players to take item")
	async def new(self, ctx, channel, desc, name, name_2, name_3, name_4, name_5, name_6, name_7, name_8, stealable):
		"""Define an investigatable object for a specified channel. Up to 8 aliases"""

		names = [name, name_2, name_3, name_4, name_5, name_6, name_7, name_8]
		names = utils.dict_to_str([name for name in names if name])

		db.add_investigation(ctx.guild.id, channel.id, names, desc, stealable)
		await ctx.respond(f"Added {names} to <#{channel.id}>")


# ------------------------------------------------------------------------
# /investigate_admin rm
# ------------------------------------------------------------------------
	@investigate_admin.command(name="rm")
	@option("channel", discord.TextChannel, description="Channel that this investigation is in")
	@option("name", str, description="Item name (default or alternate)")
	async def remove(self, ctx, channel, name):
		"""Remove an investigatable item from a specified channel by name"""

		removed = db.remove_investigation(ctx.guild.id, channel.id, name)
		if (not removed):
			await ctx.respond(f"Could not find {name} in <#{channel.id}>!", ephemeral=True)
			return

		await ctx.respond(f"Removed {name} from <#{channel.id}>")


# ------------------------------------------------------------------------
# /investigate_admin list
# ------------------------------------------------------------------------
	@investigate_admin.command(name="list")
	@option("visible", bool, default=False, description="Set to true for permanent response.")
	async def list(self, ctx, visible):
		"""List investigations"""

		items = db.get_all_investigations(ctx.guild.id)

		channels = list(set([item["ChannelID"] for item in items]))

		# To stay safely within limits, we'll allow up to 10 items per embed
		n_embeds = math.ceil(len(channels) / 10)
		embeds = [discord.Embed(title=f"{i+1}/{n_embeds}") for i in range(n_embeds)]

		for i in range(0, n_embeds):
			for j in range(0, 10):
				try:
					channel_name = await ctx.guild.fetch_channel(channels[j])
				except discord.Forbidden:
					channel_name = channels[i]
				except IndexError:
					break

				title = f"#{channel_name}"

				channel_items = [item for item in items if item["ChannelID"] == channels[j]]

				desc = ""
				for item in channel_items:
					if (item["TakenBy"]):
						desc += f"(Taken by <@{item['TakenBy']}>) "

					desc += item["Names"] + "\n"

				embeds[i].add_field(name=title, value=desc[:256], inline=False)

		await ctx.respond(view=EmbedList(embeds, ctx.interaction), ephemeral=not visible, embed=embeds[0])

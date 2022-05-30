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
from localization import loc

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
	investigate_admin = SlashCommandGroup("investigate_admin", "Admin investigation management",
		name_localizations=loc.group_names("investigate_admin"),
		description_localizations=loc.group_descriptions("investigate_admin"))


# ------------------------------------------------------------------------
# Commands
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# /investigate_admin new
# ------------------------------------------------------------------------
	@investigate_admin.command(name="new", guild_only=True,
		name_localizations=loc.command_names("investigate_admin", "new"),
		description_localizations=loc.command_descriptions("investigate_admin", "new"))
	@option("channel", discord.TextChannel,
		description="Channel that this investigation is in",
		name_localizations=loc.option_names("investigate_admin", "new", "channel"),
		description_localizations=loc.option_descriptions("investigate_admin", "new", "channel"))
	@option("desc", str,
		description="Text shown to investigator",
		name_localizations=loc.option_names("investigate_admin", "new", "desc"),
		description_localizations=loc.option_descriptions("investigate_admin", "new", "desc"))
	@option("name", str,
		description="Default name",
		name_localizations=loc.option_names("investigate_admin", "new", "name"),
		description_localizations=loc.option_descriptions("investigate_admin", "new", "name"))
	@option("name_2", str, default=None,
		description="Alternate name",
		name_localizations=loc.option_names("investigate_admin", "new", "name_2"),
		description_localizations=loc.option_descriptions("investigate_admin", "new", "name_2"))
	@option("name_3", str, default=None,
		description="Alternate name",
		name_localizations=loc.option_names("investigate_admin", "new", "name_3"),
		description_localizations=loc.option_descriptions("investigate_admin", "new", "name_3"))
	@option("name_4", str, default=None,
		description="Alternate name",
		name_localizations=loc.option_names("investigate_admin", "new", "name_4"),
		description_localizations=loc.option_descriptions("investigate_admin", "new", "name_4"))
	@option("name_5", str, default=None,
		description="Alternate name",
		name_localizations=loc.option_names("investigate_admin", "new", "name_5"),
		description_localizations=loc.option_descriptions("investigate_admin", "new", "name_5"))
	@option("name_6", str, default=None,
		description="Alternate name",
		name_localizations=loc.option_names("investigate_admin", "new", "name_6"),
		description_localizations=loc.option_descriptions("investigate_admin", "new", "name_6"))
	@option("name_7", str, default=None,
		description="Alternate name",
		name_localizations=loc.option_names("investigate_admin", "new", "name_7"),
		description_localizations=loc.option_descriptions("investigate_admin", "new", "name_7"))
	@option("name_8", str, default=None,
		description="Alternate name",
		name_localizations=loc.option_names("investigate_admin", "new", "name_8"),
		description_localizations=loc.option_descriptions("investigate_admin", "new", "name_8"))
	@option("stealable", bool, default=False,
		description="Set to 'True' to allow players to take item",
		name_localizations=loc.option_names("investigate_admin", "new", "stealable"),
		description_localizations=loc.option_descriptions("investigate_admin", "new", "stealable"))
	async def new(self, ctx, channel, desc, name, name_2, name_3, name_4, name_5, name_6, name_7, name_8, stealable):
		"""Define an investigatable object for a specified channel. Up to 8 aliases"""

		names = [name, name_2, name_3, name_4, name_5, name_6, name_7, name_8]
		names = utils.dict_to_str([name for name in names if name])

		db.add_investigation(ctx.guild.id, channel.id, names, desc, stealable)

		res = loc.response("investigate_admin", "new", "res1", ctx.interaction.locale).format(names=names, channel=channel.id)
		await ctx.respond(res)


# ------------------------------------------------------------------------
# /investigate_admin rm
# ------------------------------------------------------------------------
	@investigate_admin.command(name="rm", guild_only=True,
		name_localizations=loc.command_names("investigate_admin", "rm"),
		description_localizations=loc.command_descriptions("investigate_admin", "rm"))
	@option("channel", discord.TextChannel,
		description="Channel that the investigation is in",
		name_localizations=loc.option_names("investigate_admin", "rm", "channel"),
		description_localizations=loc.option_descriptions("investigate_admin", "rm", "channel"))
	@option("name", str,
		description="Item name (default or alternative)",
		name_localizations=loc.option_names("investigate_admin", "rm", "name"),
		description_localizations=loc.option_descriptions("investigate_admin", "rm", "name"))
	async def remove(self, ctx, channel, name):
		"""Remove an investigatable item from a specified channel by name"""

		removed = db.remove_investigation(ctx.guild.id, channel.id, name)
		if (not removed):
			error = loc.response("investigate_admin", "rm", "error-missing", ctx.interaction.locale).format(name=name, channel=channel.id)
			await ctx.respond(error, ephemeral=True)
			return

		res = loc.response("investigate_admin", "rm", "res1", ctx.interaction.locale).format(name=name, channel=channel.id)
		await ctx.respond(res)


# ------------------------------------------------------------------------
# /investigate_admin list
# ------------------------------------------------------------------------
	@investigate_admin.command(name="list", guild_only=True,
		name_localizations=loc.command_names("investigate_admin", "list"),
		description_localizations=loc.command_descriptions("investigate_admin", "list"))
	@option("visible", bool, default=False,
		description="Set to 'True' for a permanent, visible response.",
		name_localizations=loc.common("visible-name"),
		description_localizations=loc.common("visible-desc"))
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
				except discord.HTTPException:
					channel_name = loc.response("investigate_admin", "list", "warning-nochannel", ctx.interaction.locale)
				except discord.NotFound:
					channel_name = loc.response("investigate_admin", "list", "warning-nochannel", ctx.interaction.locale)
				except IndexError:
					break

				title = f"#{channel_name}"

				channel_items = [item for item in items if item["ChannelID"] == channels[j]]

				desc = ""
				for item in channel_items:
					if (item["TakenBy"]):
						desc += loc.response("investigate_admin", "list", "item-taken", ctx.interaction.locale).format(item["TakenBy"])

					desc += item["Names"] + "\n"

				embeds[i].add_field(name=title, value=desc[:256], inline=False)

		await ctx.respond(view=EmbedList(embeds, ctx.interaction), ephemeral=not visible, embed=embeds[0])

"""
Author @Firefly#7113
Commands for automated posting management
"""

from datetime import datetime
from datetime import timedelta

import discord
from discord import option
from discord.commands import SlashCommandGroup
from discord.ext import commands

import aiocron

import db
from localization import loc

# ------------------------------------------------------------------------
# COMPONENT CLASSES AND CONSTANTS
# ------------------------------------------------------------------------
DATE_STRING = "%Y%m%d%H%M"

class InputModal(discord.ui.Modal):
	def __init__(self, ctx, channel, start_year, start_month, start_day, start_hour, start_minute, interval):
		super().__init__(title=loc.response("announcements", "new", "modal-title", ctx.interaction.locale))

		self.ctx = ctx
		self.channel = channel
		self.start_year = start_year
		self.start_month = start_month
		self.start_day = start_day
		self.start_hour = start_hour
		self.start_minute = start_minute
		self.interval = interval

		self.add_item(discord.ui.InputText(
			style=discord.InputTextStyle.multiline,
			label=loc.response("announcements", "new", "modal-placeholder", ctx.interaction.locale),
			min_length=1,
			max_length=1024))


	async def callback(self, interaction):
		"""Validate input and add to database"""

		message = self.children[0].value

		# Limit announcements to 25 per guild
		existing_announcements = db.get_guild_announcements(self.ctx.guild.id)

		if (len(existing_announcements) == 25):
			error = loc.response("announcements", "new", "error-limit", self.ctx.interaction.locale)
			await interaction.response.send_message(error, ephemeral=True)
			return

		# Get guild timezone
		guild_info = db.get_guild_info(self.ctx.guild.id)
		guild_tz = guild_info["Timezone"]

		# Create datetime object in guild's tz. Exception for ValueError
		try:
			guild_time = datetime(year=self.start_year, month=self.start_month, day=self.start_day, hour=self.start_hour, minute=self.start_minute)
		except ValueError:
			error = loc.response("announcements", "new", "error-date", self.ctx.interaction.locale)
			await interaction.response.send_message(error, ephemeral=True)
			return

		# Convert to utc
		utc_time = guild_time - timedelta(hours=guild_tz)

		# Confirm that this is a later time
		utc_now = datetime.utcnow()
		if (utc_time <= utc_now):
			error = loc.response("announcements", "new", "error-past", self.ctx.interaction.locale)
			await interaction.response.send_message(error, ephemeral=True)
			return

		# Add to db using interaction snowflake as ID
		db.add_announcement(self.ctx.interaction.id, self.ctx.guild.id, self.channel.id, message[:1024], self.interval, int(utc_time.strftime(DATE_STRING)))

		res = loc.response("announcements", "new", "res1", self.ctx.interaction.locale).format(self.ctx.interaction.id)
		await interaction.response.send_message(res, ephemeral=True)


# ------------------------------------------------------------------------
# COG
# ------------------------------------------------------------------------
def setup(bot):
	bot.add_cog(AnnouncementsAdminCog(bot))

# pylint: disable=no-self-use
class AnnouncementsAdminCog(commands.Cog):
	"""Announcement management for mods"""

	def __init__(self, bot):
		self.bot = bot

		# Crontab to use self parameter, so it's gotta be defined in here.
		@aiocron.crontab('*/30 * * * *')
		async def on_half_hour():
			await self.send_announcements()

		print(f"Added {self.__class__.__name__}")


# ------------------------------------------------------------------------
# Command groups
# Change the decorator to @<name>.command()
# ------------------------------------------------------------------------
	announcements = SlashCommandGroup("announcements", "Automated posting",
		default_member_permissions=discord.Permissions(administrator=True),
		guild_only=True,
		name_localizations=loc.group_names("announcements"),
		description_localizations=loc.group_descriptions("announcements"))


# ------------------------------------------------------------------------
# Crontabs
# https://crontab.cronhub.io/
# Crontabs appear to execute in a LIFO stack order
# Do not need to be explicitly started
# ------------------------------------------------------------------------
	async def send_announcements(self):
		"""Send out announcements to channels"""

		utc_now = datetime.utcnow()
		announcements = db.get_current_announcements(utc_now)

		for announcement in announcements:
			# Check if announcements enabled
			guild_id = announcement["GuildID"]

			try:
				enabled = db.get_guild_info(guild_id)["AnnouncementsEnabled"]
			# Announcement registered but guild not in guildinfo
			except TypeError: 
				continue

			# Skip if disabled
			if (not enabled):
				continue

			# Attempt to fetch channel
			try:
				channel = await self.bot.fetch_channel(announcement["ChannelID"])
			except discord.HTTPException:
				continue

			# Attempt to post
			try:
				await channel.send(content=announcement["Message"])
			finally:
				continue


# ------------------------------------------------------------------------
# Listeners
# ------------------------------------------------------------------------
	@commands.Cog.listener()
	async def on_connect(self):
		"""TODO Updates NextPostings if bot went offline"""
		return


# ------------------------------------------------------------------------
# Commands
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# /announcements tz
# ------------------------------------------------------------------------
	@announcements.command(name="tz",
		name_localizations=loc.command_names("announcements", "tz"),
		description_localizations=loc.command_descriptions("announcements", "tz"))
	@option("utc_offset", int, min_value=-12, max_value=14,
		name_localizations=loc.option_names("announcements", "tz", "utc_offset"),
		description_localizations=loc.option_descriptions("announcements", "tz", "utc_offset"))
	async def timezone(self, ctx, utc_offset):
		"""Set timezone for server relative to UTC/GMT. Half/Quarter hours not supported"""

		db.edit_guild(ctx.guild.id, "Timezone", utc_offset)

		tz_str = f"UTC+{utc_offset}" if (utc_offset >= 0) else f"UTC{utc_offset}"
		res = loc.response("announcements", "tz", "res1", ctx.interaction.locale).format(tz_str)
		await ctx.respond(res)

# ------------------------------------------------------------------------
# /announcements new
# ------------------------------------------------------------------------
	@announcements.command(name="new",
		name_localizations=loc.command_names("announcements", "new"),
		description_localizations=loc.command_descriptions("announcements", "new"))
	@option("channel", discord.TextChannel,
		description="Channel to post in",
		name_localizations=loc.option_names("announcements", "new", "channel"),
		description_localizations=loc.option_descriptions("announcements", "new", "channel"))
	@option("start_year", int, min_value=2022,
		description="Year to begin",
		name_localizations=loc.option_names("announcements", "new", "start_year"),
		description_localizations=loc.option_descriptions("announcements", "new", "start_year"))
	@option("start_month", int, choices=list(range(1, 13)),
		description="Month to begin",
		name_localizations=loc.option_names("announcements", "new", "start_month"),
		description_localizations=loc.option_descriptions("announcements", "new", "start_month"))
	@option("start_day", int, min_value=1, max_value=31,
		description="Day to begin",
		name_localizations=loc.option_names("announcements", "new", "start_day"),
		description_localizations=loc.option_descriptions("announcements", "new", "start_day"))
	@option("start_hour", int, choices=list(range(24)),
		description="Hour to begin (24 hour format)",
		name_localizations=loc.option_names("announcements", "new", "start_hour"),
		description_localizations=loc.option_descriptions("announcements", "new", "start_hour"))
	@option("start_minute", int, choices=[0, 30],
		description="On the hour or on the half hour",
		name_localizations=loc.option_names("announcements", "new", "start_minute"),
		description_localizations=loc.option_descriptions("announcements", "new", "start_minute"))
	@option("interval", int, min_value=1, max_value=5040,
		description="Posting interval between 1 hour and 30 days (5040 hours)",
		name_localizations=loc.option_names("announcements", "new", "interval"),
		description_localizations=loc.option_descriptions("announcements", "new", "interval"))
	@option("message", str,
		description="Message, maximum 1024 characters",
		name_localizations=loc.option_names("announcements", "new", "message"),
		description_localizations=loc.option_descriptions("announcements", "new", "message"))
	async def new(self, ctx, channel, start_year, start_month, start_day, start_hour, start_minute, interval, message):
		"""Define a new scheduled/repeated announcement (using your server's set timezone)"""

		# Modal input for content
		modal = InputModal(ctx, channel, start_year, start_month, start_day, start_hour, start_minute, interval)
		await ctx.send_modal(modal)


# ------------------------------------------------------------------------
# /announcements rm
# ------------------------------------------------------------------------
	@announcements.command(name="rm",
		name_localizations=loc.command_names("announcements", "rm"),
		description_localizations=loc.command_descriptions("announcements", "rm"))
	@option("announcement_id", str,
		description="The ID associated with the announcement (found with list command)",
		name_localizations=loc.option_names("announcements", "rm", "announcement_id"),
		description_localizations=loc.option_descriptions("announcements", "rm", "announcement_id"))
	async def remove(self, ctx, announcement_id):
		"""Remove an announcement by its id (obtained with /announcements list)"""

		announcement_removed = db.remove_announcement(ctx.guild.id, int(announcement_id))

		if (not announcement_removed):
			error = loc.response("announcements", "rm", "error-id", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		res = loc.response("announcements", "rm", "res1", ctx.interaction.locale)
		await ctx.respond(res, ephemeral=True)

# ------------------------------------------------------------------------
# /announcements list
# ------------------------------------------------------------------------
	@announcements.command(name="list",
		name_localizations=loc.command_names("announcements", "list"),
		description_localizations=loc.command_descriptions("announcements", "list"))
	@option("visible", bool, default=False,
		description="Set to 'True' for a permanent, visible response.",
		name_localizations=loc.common("visible-name"),
		description_localizations=loc.common("visible-desc"))
	async def list(self, ctx, visible):
		"""List your server's automated posts in chronological order"""

		announcements = db.get_guild_announcements(ctx.guild.id)

		# Return if no announcements
		if (len(announcements) == 0):
			error = loc.response("announcements", "list", "error-noposts", ctx.interaction.locale)
			await ctx.respond(error, ephemeral=True)
			return

		# Get timezone for conversion
		timezone = db.get_guild_info(ctx.guild.id)["Timezone"]

		# Order announcements by next posting
		announcements = sorted(announcements, key=lambda d: d["NextPosting"])

		# Embed
		res_title = loc.response("announcements", "list", "res-title", ctx.interaction.locale).format(ctx.guild.name)
		embed = discord.Embed(title=res_title[:128])
		for announcement in announcements:
			post_time_utc = datetime.strptime(str(announcement['NextPosting']), DATE_STRING)
			post_time_guild = post_time_utc + timedelta(hours=timezone)
			post_time_str = post_time_guild.strftime("%d %b %Y, %H:%M")

			title = loc.response("announcements", "list", "res-field", ctx.interaction.locale).format(start_time=post_time_str, amount=announcement["Interval"], id=announcement["ID"])
			value = loc.response("announcements", "list", "res-value", ctx.interaction.locale).format(announcement["ChannelID"]) + "\n" + announcement["Message"][:128]

			embed.add_field(name=title, value=value, inline=False)

		# Send
		await ctx.respond(embed=embed, ephemeral=not visible)

# ------------------------------------------------------------------------
# /announcements toggle
# ------------------------------------------------------------------------
	@announcements.command(name="toggle",
		name_localizations=loc.command_names("announcements", "toggle"),
		description_localizations=loc.command_descriptions("announcements", "toggle"))
	@option("state", str,
		choices=loc.choices("announcements", "toggle", "state"),
		description="Run or Pause",
		name_localizations=loc.option_names("announcements", "toggle", "state"),
		description_localizations=loc.option_descriptions("announcements", "toggle", "state"))
	async def toggle(self, ctx, state):
		"""Disable announcements from being posted until turned back on"""

		if (state == "RUN"):
			val =1
			res = loc.response("announcements", "toggle", "res1", ctx.interaction.locale)
		else:
			val = 0
			res = loc.response("announcements", "toggle", "res2", ctx.interaction.locale)

		db.toggle_guild_announcements(ctx.guild.id, val)
		await ctx.respond(res)

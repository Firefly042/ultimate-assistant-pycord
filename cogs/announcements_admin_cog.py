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


# ------------------------------------------------------------------------
# COMPONENT CLASSES AND CONSTANTS
# ------------------------------------------------------------------------
DATE_STRING = "%Y%m%d%H%M"


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
	announcements = SlashCommandGroup("announcements", "Automated posting")


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
			enabled = db.get_guild_info(guild_id)["AnnouncementsEnabled"]

			# Skip if disabled
			if (not enabled):
				continue

			# Attempt to fetch channel
			try:
				channel = await self.bot.fetch_channel(announcement["ChannelID"])
			except discord.NotFound:
				continue
			except discord.Forbidden:
				continue
			except discord.HTTPException:
				continue
			finally:
				continue

			# Attempt to post
			try:
				await channel.send(content=announcement["Message"])
			except discord.Forbidden:
				continue
			except discord.HTTPException:
				continue
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
	@announcements.command(name="tz")
	@option("utc_offset", int, description="Your offset from UTC/GMT", min_value=-12, max_value=14)
	async def timezone(self, ctx, utc_offset):
		"""Set timezone for server relative to UTC/GMT. Half/Quarter hours not supported"""

		db.edit_guild(ctx.guild.id, "Timezone", utc_offset)

		if (utc_offset >= 0):
			tz_str = f"UTC+{utc_offset}"
		else:
			tz_str = f"UTC{utc_offset}"

		await ctx.respond(f"Set timezone to **{tz_str}**")

# ------------------------------------------------------------------------
# /announcements new
# ------------------------------------------------------------------------
	@announcements.command(name="new")
	@option("channel", discord.TextChannel, description="Channel to post in")
	@option("start_year", int, min_value=2022, description="Year to begin")
	@option("start_month", int, choices=list(range(1, 13)), description="Month to begin")
	@option("start_day", int, min_value=1, max_value=31, description="Day to begin")
	@option("start_hour", int, choices=list(range(0, 24)), description="The hour to begin this post")
	@option("start_minute", int, choices=[0, 30], description="On the hour or on the half hour")
	@option("interval", int, min_value=1, max_value=5040, description="Posting interval between 1 hour and 30 days (5040 hours)")
	@option("message", str, description="Message, maximum 1024 characters")
	async def new(self, ctx, channel, start_year, start_month, start_day, start_hour, start_minute, interval, message):
		"""Define a new scheduled/repeated announcement (using your server's set timezone)"""

		# Limit announcements to 25 per guild
		existing_announcements = db.get_guild_announcements(ctx.guild.id)

		if (len(existing_announcements) == 25):
			await ctx.respond("You may not have more than 25 automatic posts!", ephemeral=True)
			return

		# Get guild timezone
		guild_info = db.get_guild_info(ctx.guild.id)
		guild_tz = guild_info["Timezone"]

		# Create datetime object in guild's tz. Exception for ValueError
		try:
			guild_time = datetime(year=start_year, month=start_month, day=start_day, hour=start_hour, minute=start_minute)
		except ValueError:
			await ctx.respond("Please enter a valid date! Did you enter a nonexistent day like 30th Feb?", ephemeral=True)
			return

		# Convert to utc
		utc_time = guild_time - timedelta(hours=guild_tz)

		# Confirm that this is a later time
		utc_now = datetime.utcnow()
		if (utc_time <= utc_now):
			await ctx.respond("Please enter a time and date in the future!", ephemeral=True)
			return

		# Add to db using interaction snowflake as ID
		db.add_announcement(ctx.interaction.id, ctx.guild.id, channel.id, message, interval, int(utc_time.strftime(DATE_STRING)))

		await ctx.respond(f"Set automatic post (id {ctx.interaction.id})", ephemeral=True)

# ------------------------------------------------------------------------
# /announcements rm
# ------------------------------------------------------------------------
	@announcements.command(name="rm")
	@option("announcement_id", str, description="The id associated with the announcement (can be found with list command)")
	async def remove(self, ctx, announcement_id):
		"""Remove an announcement by its id (obtained with /announcements list)"""

		announcement_removed = db.remove_announcement(ctx.guild.id, int(announcement_id))

		if (not announcement_removed):
			await ctx.respond("There is no announcement with that ID!", ephemeral=True)
			return

		await ctx.respond("Removed announcement", ephemeral=True)

# ------------------------------------------------------------------------
# /announcements list
# ------------------------------------------------------------------------
	@announcements.command(name="list")
	@option("visible", bool, default=False, description="Set True for permanent response")
	async def list(self, ctx, visible):
		"""List your server's automated posts in chronological order"""

		announcements = db.get_guild_announcements(ctx.guild.id)

		# Return if no announcements
		if (len(announcements) == 0):
			await ctx.respond("You have no scheduled posts!", ephemeral=True)
			return

		# Get timezone for conversion
		timezone = db.get_guild_info(ctx.guild.id)["Timezone"]

		# Order announcements by next posting
		announcements = sorted(announcements, key=lambda d: d["NextPosting"])

		# Embed
		embed = discord.Embed(title=f"Automatic Posts in {ctx.guild.name}"[:128])
		for announcement in announcements:
			post_time_utc = datetime.strptime(str(announcement['NextPosting']), DATE_STRING)
			post_time_guild = post_time_utc + timedelta(hours=timezone)
			post_time_str = post_time_guild.strftime("%d %b %Y, %H:%M")

			title = f"{post_time_str}, every {announcement['Interval']} hours (id: {announcement['ID']})"
			value = f"In <#{announcement['ChannelID']}>\n" + announcement['Message'][:128]
			embed.add_field(name=title, value=value, inline=False)

		# Send
		await ctx.respond(embed=embed, ephemeral=not visible)

# ------------------------------------------------------------------------
# /announcements toggle
# ------------------------------------------------------------------------
	@announcements.command(name="toggle")
	@option("state", str, choices=["RUN", "PAUSE"], description="Run or Pause")
	async def toggle(self, ctx, state):
		"""Disable announcements from being posted until turned back on"""

		if (state == "RUN"):
			val =1
		else:
			val = 0

		db.toggle_guild_announcements(ctx.guild.id, val)

		await ctx.respond(f"Automatic posts set to {state}")

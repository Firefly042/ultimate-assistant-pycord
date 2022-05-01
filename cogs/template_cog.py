"""
Original template by @Firefly#7113, April 2022
"""

# import discord
from discord import slash_command, option #, ApplicationContext
from discord.commands import permissions, SlashCommandGroup
from discord.ext import commands

import aiocron

# from config import ADMIN_ROLE, PLAYER_ROLE
# import db

# import utils.xxx as yyy

# ------------------------------------------------------------------------
# COMPONENT CLASSES AND CONSTANTS
# ------------------------------------------------------------------------


# ------------------------------------------------------------------------
# COG
# ------------------------------------------------------------------------
def setup(bot):
	"""Setup. Change TemplateCog to Class name"""
	bot.add_cog(TemplateCog(bot))

# pylint: disable=no-self-use
class TemplateCog(commands.Cog):
	"""Change Class name and add description here"""

	def __init__(self, bot):
		self.bot = bot
		print(f"Added {self.__class__.__name__}")


# ------------------------------------------------------------------------
# Command groups
# Change the decorator to @<name>.command()
# ------------------------------------------------------------------------
	group = SlashCommandGroup("group", "Slash Command Group")
	subgroup = group.create_subgroup("subgroup", "A subgroup")


# ------------------------------------------------------------------------
# Crontabs
# https://crontab.cronhub.io/
# Crontabs appear to execute in a LIFO stack order
# Do not need to be explicitly started
# ------------------------------------------------------------------------
	@staticmethod
	@aiocron.crontab('*/1 * * * *')
	async def cron_example1():
		"""Cron example 1"""
		print("cron-example1")

	@staticmethod
	@aiocron.crontab('*/2 * * * *')
	async def cron_example2():
		"""Cron example 2"""
		print("cron-example2")


# ------------------------------------------------------------------------
# Listeners
# ------------------------------------------------------------------------
	@commands.Cog.listener()
	async def on_member_join(self, member):
		"""Listener example. Line exists so linter doesn't complain"""
		print(member)
		return


	@commands.Cog.listener()
	async def on_message(self, msg):
		"""Listener example"""

		if (msg.author.bot):
			return


# ------------------------------------------------------------------------
# Commands
# ------------------------------------------------------------------------
	@slash_command(name="test", description="test description")
	async def test(self, ctx):
		"""Basic response test"""
		await ctx.respond("Test")

	# @test.error
	# async def test_error(self, ctx, error):
	#   return


	@slash_command(name="admintest")
	@commands.has_permissions(administrator=True)
	async def admintest(self, ctx):
		"""Basic admin perms test"""
		await ctx.respond("Admin Test")


	@slash_command(name="roletest")
	@permissions.has_role("Not Firefly")
	async def roletest(self, ctx):
		"""Basic role test"""
		await ctx.respond("Role Test")


	@slash_command(name="cooldowntest")
	@commands.cooldown(1, 30, commands.BucketType.user)
	async def cooldowntest(self, ctx):
		"""Basic cooldown test"""
		await ctx.respond("Cooldown Test")


	@slash_command(name="option_example")
	@option("option_name", str, description="Example option")
	async def optionexample(self, ctx, *, option_name):
		"""Basic option example"""
		await ctx.respond(option_name)

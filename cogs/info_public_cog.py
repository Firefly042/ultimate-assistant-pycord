"""
Original template by @Firefly#7113, April 2022
"""

import discord
from discord import slash_command, option #, ApplicationContext
from discord.commands import permissions, SlashCommandGroup
from discord.ext import commands

import aiocron
import math

# from config import ADMIN_ROLE, PLAYER_ROLE
# import db

# import utils.xxx as yyy

# ------------------------------------------------------------------------
# COMPONENT CLASSES AND CONSTANTS
# ------------------------------------------------------------------------
HELP_EMBEDS = {
	"Info": {
		"Description": "All command descriptions and instructions can be found by typing `/`into discord and selecting UA in the menu! Parameter hints are also provided by selecting the parameter's box. Use this menu to see overviews and command categories. If anything is unclear or buggy, feel free to ask in the developer's server.",
		"Fields": {
			"Full Instructions": "[Github](https://github.com/Firefly042). Stars and contributions are welcome!",
			
			"Questions, Answers, and Suggestions": "[Discord Server](https://discord.gg/VZYKBptWFJ)", 
			
			"Support the Developer": "[Ko-fi](https://ko-fi.com/firefly42)", 
			
			"Commissions": "[I can make other things too.](https://docs.google.com/document/d/1kM7qFBWqGsHktgrQHdCSf0HYJCfrTAa9MVsGPE8xF6A/edit?usp=sharing)",
			
			"Basic Usage": "1. Set application permissions for moderator and player roles in your server settings (Integrations). Here's an official [guide](https://discord.com/blog/slash-commands-permissions-discord-apps-bots) from Discord.\n\n2. Set up character profiles with `/profile_admin` commands. If you plan to use the Messaging features, you will need designated player channels.\n\n3. Players may customize their profiles further with `/profile` commands.\n\n4. Multiple characters can be registered for a single player, but only one may be active at a time (set with `/profile swap`).", 

			"Optional Parameters": "Many commands have optional arguments that may be of interest! Make note of the `visible` parameter that makes use of temporary/single-user messages."
		}, 
		"Footer": "This bot is written by discord user @Firefly#7113. If this code is not running on bot user 517165856933937153, it is being hosted by someone else and should only be used if you trust that person."
	}, 

	"Profiles": {
		"Description": "A single player may not have more than one character with the same display name. Individual associated channels are required to use Messaging commands.", 
		"Fields": {
			"Admin": "`/profile_admin` - Register, remove, and disable characters. Edit names, surnames, and associated channels.", 
			
			"Player": "`/profile` - Edit your character's embed images, fields, descriptions, and colors. View or switch your active character", 
			
			"Public": "`/profile view|list` - View an individual profile or list all registered characters."
		}
	}, 

	"Gacha": {
		"Description": "All item names must be unique within a server.", 
		"Fields": {
			"Admin": "`/gacha_admin` - Register items with `add`, with optional parameters to limit the amount of the item. Remove items by name with `rm`. Edit currency name or increase the cost of a single pull. Give and take currency to/from individual (active) characters or in bulk.", 
			
			"Player": "`/gacha` - Pull from the gacha, view your currency, and give currency to another (active) character."
		}
	}, 

	"Inventory": {
		"Description": "Item management for players and moderators. You may hold up to 9999 of a single item (case sensitive).",
		"Fields": {
			"Admin": "`/inv_admin` - View inventories for players and give/take items.", 

			"Player": "`/inv` - View and manage your own inventory, give items to another active character."
		}
	}, 

	"Messaging": {
		"Description": "Private and anonymous messaging for players. The latter must be enabled by a moderator, and players will need a set channel (see Profiles) to receive these messages",
		"Fields": { 
			"Admin": "`/msg_admin` - Toggle anonymous messaging with `anon` command and view a list of players and channels.", 

			"Player": "`/msg whisper|anon` - Send signed or anonymous messages to another active character's private channel."
		}
	}, 

	"Dice": {
		"Description": "Rolling with d20 notation and custom rolls",
		"Fields": {
			"Admin": "`/roll_admin list` - List rolls for a specified player",

			"Player": "`/roll` - Manage a set of up to 25 named rolls", 

			"Public": "`/roll d` - Roll with normal d20 notation"
		}
	}, 

	"Automated Posts": {
		"Description": "A set of commands to automate regular posts such as time announcements. Be sure to set your **timezone** (`/announcements tz`)! Slash commands do not support line breaks at the time of writing.",
		"Fields": {
			"Admin": "`/announcements` - Add, remove, and view automated posts. Toggle them on or off. PAUSED announcements will still tick forward in time, but will not be posted."
		}
	}
}


class HelpMenu(discord.ui.View):
	def __init__(self, embeds):
		# Is it possible to generate button callbacks according to embed titles?
		super().__init__(timeout=120)
		self.embeds = embeds


	# TODO - Figure out how to update view. interaction/message aren't accessible
	async def on_timeout(self):
		# await interaction.response.edit_message(content="Timed out", view=self)
		self.stop()


	# Row 0 - Info, Profiles, Gacha, Inventory
	@discord.ui.button(label="Info", row=0, style = discord.ButtonStyle.green)
	async def info_button_callback(self, button, interaction):
		await interaction.response.edit_message(embed=self.embeds["Info"], view=self)

	# Row 0 - Info, Profiles, Gacha, Inventory
	@discord.ui.button(label="Profiles", row=0, style = discord.ButtonStyle.green)
	async def profile_button_callback(self, button, interaction):
		await interaction.response.edit_message(embed=self.embeds["Profiles"], view=self)

	# Row 0 - Info, Profiles, Gacha, Inventory
	@discord.ui.button(label="Gacha", row=0, style = discord.ButtonStyle.green)
	async def gacha_button_callback(self, button, interaction):
		await interaction.response.edit_message(embed=self.embeds["Gacha"], view=self)

	# Row 0 - Info, Profiles, Gacha, Inventory
	@discord.ui.button(label="Inventory", row=0, style = discord.ButtonStyle.green)
	async def inventory_button_callback(self, button, interaction):
		await interaction.response.edit_message(embed=self.embeds["Inventory"], view=self)

	# Row 1 - Messaging, Dice, Automated Posts
	@discord.ui.button(label="Messaging", row=1, style = discord.ButtonStyle.green)
	async def messaging_button_callback(self, button, interaction):
		await interaction.response.edit_message(embed=self.embeds["Messaging"], view=self)

	# Row 1 - Messaging, Dice, Automated Posts
	@discord.ui.button(label="Dice", row=1, style = discord.ButtonStyle.green)
	async def dice_button_callback(self, button, interaction):
		await interaction.response.edit_message(embed=self.embeds["Dice"], view=self)

	# Row 1 - Messaging, Dice, Automated Posts
	@discord.ui.button(label="Automated Posts", row=1, style = discord.ButtonStyle.green)
	async def posting_button_callback(self, button, interaction):
		await interaction.response.edit_message(embed=self.embeds["Automated Posts"], view=self)


# ------------------------------------------------------------------------
# COG
# ------------------------------------------------------------------------
def setup(bot):
	"""Setup. Change TemplateCog to Class name"""
	bot.add_cog(InfoPublicCog(bot))

# pylint: disable=no-self-use
class InfoPublicCog(commands.Cog):
	"""Change Class name and add description here"""

	def __init__(self, bot):
		self.bot = bot

		# Initiate embeds to pass into View
		self.embeds = {}
		for embed_title in HELP_EMBEDS.keys():
			embed = discord.Embed(title=embed_title)
			embed.description = HELP_EMBEDS[embed_title]["Description"]

			for field in HELP_EMBEDS[embed_title]["Fields"].keys():
				embed.add_field(name=field, value=HELP_EMBEDS[embed_title]["Fields"][field], inline=False)

			try:
				embed.set_footer(text=HELP_EMBEDS[embed_title]["Footer"])
			except KeyError:
				pass

			self.embeds[embed_title] = embed

		print(f"Added {self.__class__.__name__}")


# ------------------------------------------------------------------------
# Command groups
# Change the decorator to @<name>.command()
# ------------------------------------------------------------------------


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
	@slash_command(name="help")
	@option("visible", bool, default=False, description="Set True for public response")
	async def help(self, ctx, visible):
		"""Helpful information and links"""

		await ctx.respond(embed=self.embeds["Info"], view=HelpMenu(self.embeds), ephemeral=not visible)

	# @test.error
	# async def test_error(self, ctx, error):
	#   return

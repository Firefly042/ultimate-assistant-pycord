import discord
import json

import db


# def admin_check(ctx):
# 	"""Returns true if interaction user has admin role"""

# 	admin_role = db.get_guild_info(ctx.guild.id)["AdminRole"]
# 	if (admin_role in ctx.interaction.user.roles):
# 		return True
# 	return False


# def player_check(ctx):
# 	"""Returns true if interaction user has player role"""
	
# 	player_role = db.get_guild_info(ctx.guild.id)["PlayerRole"]
# 	if (player_role in ctx.interaction.user.roles):
# 		return True
# 	return False


def str_to_dict(json_str):
	"""JSON compatible string to python dict"""
	return json.loads(json_str)


def dict_to_str(d):
	"""Python dict to JSON compatible str"""
	return json.dumps(d)


def hex_to_color(hex_code):
	"""Takes a hex string (without #) and converts it to an int B16"""
	return int(hex_code, 16)


def get_profile_embed(guild_id, player_id, name):
	"""Queries database and returns a discord.Embed"""

	char = db.get_character(guild_id, player_id, name)

	# Check that anything was returned
	try:
		name = char["Name"]
	except TypeError as error:
		raise Exception("Cannot find character") from error

	# Title and color
	if (char["Surname"]):
		name += " " + char["Surname"]

	embed = discord.Embed(title=name, color=hex_to_color(char["HexColor"]))

	# Description if it exists
	if (char["ProfileDesc"]):
		embed.description = char["ProfileDesc"]

	# Thumbnail and image if they exist
	if (char["ThumbnailURL"]):
		embed.set_thumbnail(url=char["ThumbnailURL"])
	if (char["ImageURL"]):
		embed.set_image(url=char["ImageURL"])

	# Fields
	profile_fields = str_to_dict(char["ProfileFields"])
	for key in profile_fields.keys():
		embed.add_field(name=key, value=profile_fields[key], inline=False)

	# Can't seem to catch HTTPException, so throw an Exception here after checking length
	items = [embed.title, embed.description, embed.footer.text, embed.author.name]
	items.extend([field.name for field in embed.fields])
	items.extend([field.value for field in embed.fields])

	length = 0
	for item in items:
		length += len(str(item)) if str(item) != 'Embed.Empty' else 0

	if (length > 6000):
		raise Exception("Embed too long")

	# If all checks out, return the embed
	return embed


def get_gacha_embed(item):
	"""Does not query db, returns embed"""

	embed = discord.Embed(title=item["Name"])
	embed.description = item["Desc"]

	if (item["ThumbnailURL"]):
		embed.set_thumbnail(url=item["ThumbnailURL"])

	return embed


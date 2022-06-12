"""
Author @Firefly#7113
Various utility functions
"""

import json

import discord


def str_to_dict(json_str):
	"""JSON compatible string to python dict"""
	return json.loads(json_str)


def dict_to_str(dictionary):
	"""Python dict to JSON compatible str"""
	return json.dumps(dictionary)


def hex_to_color(hex_code):
	"""Takes a hex string (without #) and converts it to an int B16"""
	return int(hex_code, 16)


def get_profile_embed(char):
	"""Returns a discord.Embed (char from queried database)"""

	# char = await db.get_character(guild_id, player_id, name)

	# Check that anything was returned
	try:
		name = char["name"]
	except TypeError as error:
		raise Exception("Cannot find character") from error

	# Title and color
	if (char["surname"]):
		name += " " + char["surname"]

	embed = discord.Embed(title=name, color=hex_to_color(char["hexcolor"]))

	# Description if it exists
	if (char["profiledesc"]):
		embed.description = char["profiledesc"]

	# Thumbnail and image if they exist
	if (char["thumbnailurl"]):
		embed.set_thumbnail(url=char["thumbnailurl"])
	if (char["imageurl"]):
		embed.set_image(url=char["imageurl"])

	# Fields
	profile_fields = str_to_dict(char["profilefields"])
	for key in profile_fields.keys():
		embed.add_field(name=key, value=profile_fields[key], inline=False)

	# Can't seem to catch HTTPException, so throw an Exception here after checking length
	if len(embed) > 6000:
		raise Exception("Embed too long")

	# If all checks out, return the embed
	return embed


def get_gacha_embed(item):
	"""Does not query db, returns embed"""

	embed = discord.Embed(title=item["name"])
	embed.description = item["description"]

	if (item["thumbnailurl"]):
		embed.set_thumbnail(url=item["thumbnailurl"])

	return embed

"""String localization"""

strings = {
	"common": {
		"no-character": {
			"en-US": "You do not have an active character in this server! Do you need to use `/profile scambio`?",
			"it": "Non hai un personaggio attivo in questo server! Hai bisogno di usare `/profile scambio`?",
		},
		"visible-desc": {
			"en-US": "Set to 'True' for a permanent, visible response.",
			"it": "Imposta a 'True' per una risposta visibile e permanente.",
		},
		"visible-name": {
			"en-US": "visible",
			"it": "visibile",
		},
	},

	"profile_admin": {
		"group_name": {
			"en-US": "profile_admin",
		},
		"group_description": {
			"en-US": "Admin profile setup",
		},
		"commands": {
			"new": {
				"name": {
					"en-US": "new",
				},
				"description": {
					"en-US": "Register a player, character, and name to the bot",
				},
				"options": {
					"player": {
						"name": {
							"en-US": "player",
						},
						"description": {
							"en-US": "Who will play this character",
						},
					},
					"name": {
						"name": {
							"en-US": "name",
						},
						"description": {
							"en-US": "The character's given/default name to display. 32 character max",
						},
					},
					"surname": {
						"name": {
							"en-US": "surname",
						},
						"description": {
							"en-US": "The rest of the character's name, if any. 32 character max",
						},
					},
					"channel": {
						"name": {
							"en-US": "channel",
						},
						"description": {
							"en-US": "Where anonymous messages and whispers will be sent",
						},
					},
				},
				"responses": {
					"error1": {
						"en-US": "Cannot add {} without causing a duplicate!",
					},
					"res1": {
						"en-US": "Added {} {}",
					},
				},
			},

			"rm": {
				"name": {
					"en-US": "rm",
				},
				"description": {
					"en-US": "Unregister a character",
				},
				"options": {
					"player": {
						"name": {
							"en-US": "player",
						},
						"description": {
							"en-US": "Who played this character",
						},
					},
					"name": {
						"name": {
							"en-US": "name",
						},
						"description": {
							"en-US": "The character's display name",
						},
					},
				},
				"responses": {
					"error1": {
						"en-US": "Could not find that character under that player!",
					},
					"res1": {
						"en-US": "Removed {}. This player may not have an active character anymore, but can `/profile swap` to another!",
					},
				},
			},

			"disable": {
				"name": {
					"en-US": "disable",
				},
				"description": {
					"en-US": "Set a character to inactive (disabling the player's ability to use commands)",
				},
				"options": {
					"name": {
						"name": {
							"en-US": "name",
						},
						"description": {
							"en-US": "The character's display name",
						},
					},
					"player": {
						"name": {
							"en-US": "player",
						},
						"description": {
							"en-US": "Who plays this character",
						},
					},
				},
				"responses": {
					"error1": {
						"en-US": "Could not find that character under that player!",
					},
					"res1": {
						"en-US": "Disabled character for {}.",
					},
				},
			},
		},
	},

	"profile_admin_edit": {
		"group_name": {
			"en-US": "edit",
		},
		"group_description": {
			"en-US": "Admin profile editing",
		},
		"commands": {
			"text": {
				"name": {
					"en-US": "text",
				},
				"description": {
					"en-US": "Edit a character's name or surname",
				},
				"options": {
					"player": {
						"name": {
							"en-US": "player",
						},
						"description": {
							"en-US": "Who plays this character",
						},
					},
					"name": {
						"name": {
							"en-US": "name",
						},
						"description": {
							"en-US": "The character's display name",
						},
					},
					"field_to_change": {
						"name": {
							"en-US": "field_to_change",
						},
						"description": {
							"en-US": "Specify Name or Surname",
						},
						"choices": {
							"Name": {
								"en-US": "Name",
							},
							"Surname": {
								"en-US": "Surname",
							},
						},
					},
					"new_value": {
						"name": {
							"en-US": "new_value",
						},
						"description": {
							"en-US": "New name or surname. 32 character maximum",
						},
					},
				},
				"responses": {
					"error-duplicate": {
						"en-US": "Cannot edit {} without causing a duplicate!",
					},
					"error1": {
						"en-US": "Could not find that character under that player!",
					},
					"res1": {
						"en-US": "Updated character for {}.",
					},
				},
			},

			"channel": {
				"name": {
					"en-US": "channel",
				},
				"description": {
					"en-US": "Add or edit a character's associated channel",
				},
				"options": {
					"player": {
						"name": {
							"en-US": "player",
						},
						"description": {
							"en-US": "Who plays this character",
						},
					},
					"name": {
						"name": {
							"en-US": "name",
						},
						"description": {
							"en-US": "The character's display name",
						},
					},
				},
				"responses": {
					"error1": {
						"en-US": "Could not find that character under that player!",
					},
					"res1": {
						"en-US": "Updated character for {}.",
					},
				},
			},
		}
	},

	"profile": {
		"group_name": {
			"en-US": "profile",
			"it": "profilo",
		},
		"group_description": {
			"en-US": "Character profiles",
		},
		"commands": {
			"view": {
				"name": {
					"en-US": "view",
					"it": "visualizza",
				},
				"description": {
					"en-US": "View a character's profile",
					"it": "Visualizza il profilo di un personaggio",
				},
				"options": {
					"player": {
						"name": {
							"en-US": "player",
							"it": "giocatore",
						},
						"description": {
							"en-US": "The user who plays this character",
							"it": "L'utente che usa questo personaggio",
						},
					},
					"name": {
						"name": {
							"en-US": "name",
							"it": "nome"
						},
						"description": {
							"en-US": "Character's display name (usually given name)",
							"it": "Il nome da display del personaggio",
						},
					}
				},
				"responses": {
					"error1": {
						"en-US": "Cannot find that character for that player!",
						"it": "Non riesco a trovare quel personaggio per quel giocatore!",
					},
				},
			},

			"list": {
				"name": {
					"en-US": "list",
					"it": "lista",
				},
				"description": {
					"en-US": "List all registered characters for this server",
					"it": "Lista tutti i personaggi registrati per questo server",
				},
				"responses": {
					"res1": {
						"en-US": "Characters in {}",
						"it": "Personaggi in {}"
					},
					"error1": {
						"en-US": "This server has no registered characters!",
						"it": "Questo server non ha personaggi registrati!",
					},
				}
			},

			"swap": {
				"name": {
					"en-US": "swap",
				},
				"description": {
					"en-US":  "Set your active character",
				},
				"options": {
					"name": {
						"name": {
							"en-US": "name",
						},
						"description": {
							"en-US": "Display name of character to swap to",
						},
					},
				},
				"responses": {
					"error1": {
						"en-US": "Cannot find a character named {} for you!",
					},
					"res1": {
						"Swapped character to {}",
					},
				},
			},

			"current": {
				"name": {
					"en-US": "current",
				},
				"description": {
					"en-US": "Check your active character",
				},
				"responses": {
					"res1": {
						"en-US": "You are currently playing as **{}**",
					},
				},
			},
		},
	},

	"profile_embed": {
		"group_name": {
			"en-US": "embed",
			"it": "embed",
		},
		"group_description": {
			"en-US": "Profile editing",
			"it": "italiano embed desc",
		},
		"commands": {
			"edit": {
				"name": {
					"en-US": "edit",
				},
				"description": {
					"en-US": "Edit profile embed fields (color, thumbnail, or image)",
				},
				"options": {
					"name": {
						"name": {
							"en-US": "name",
						},
						"description": {
							"en-US": "Your character's display name",
						},
					},
					"field_to_change": {
						"name": {
							"en-US": "field_to_change",
						},
					},
					"new_value": {
						"name": {
							"en-US": "new_value",
						},
						"description": {
							"en-US": "Hex code (without #) or image url",
						},
					},
				},
				"responses": {
					"error-hex": {
						"en-US": "#{} is not a valid hex!",
					},
					"error1": {
						"en-US": "Could not find a character with that name for you!",
					},
					"error-url": {
						"en-US": "I cannot display that image URL! Reverting.",
					},
					"res1": {
						"en-US": "Updated",
					},
				},
			},

			"field": {
				"name": {
					"en-US": "field",
				},
				"description": {
					"en-US": "Add or edit up to 25 fields to your character's profile embed",
				},
				"options": {
					"name": {
						"name": {
							"en-US": "name",
						},
						"description": {
							"en-US": "Your character's display name",
						},
					},
					"field_title": {
						"name": {
							"en-US": "field_title",
						},
						"description": {
							"en-US": "Up to 256 characters",
						},
					},
					"field_content": {
						"name": {
							"en-US": "field_content",
						},
						"description": {
							"en-US": "Up to 1024 characters",
						},
					},
				},
				"responses": {
					"error-limit": {
						"en-US": "You must remove a field before adding a new one!",
					},
					"error1": {
						"en-US": "Could not find a character with that name for you!",
					},
					"error-length": {
						"en-US": "Your embed has exceeded the maximum length of 6000. Reverting.",
					},
					"res1": {
						"en-US": "Updated",
					},
				}
			},

			"desc": {
				"name": {
					"en-US": "desc",
				},
				"description": {
					"en-US": "Add or edit profile embed description",
				},
				"options": {
					"name": {
						"name": {
							"en-US": "name",
						},
						"description": {
							"en-US": "Your character's display name",
						},
					},
					"content": {
						"name": {
							"en-US": "content",
						},
						"description": {
							"en-US": "Up to 4096 characters",
						},
					},
				},
				"responses": {
					"error1": {
						"en-US": "Could not find a character with that name for you!",
					},
					"error-length": {
						"en-US": "Your embed has exceeded the maximum length of 6000. Reverting.",
					},
					"res1": {
						"en-US": "Updated",
					},
				},
			},
		},
	},
}



def common(tag):
	return strings["common"][tag]


def group_names(group):
	return strings[group]["group_name"]


def group_descriptions(group):
	return strings[group]["group_description"]


def command_names(group, command):
	return strings[group]["commands"][command]["name"]


def command_descriptions(group, command):
	return strings[group]["commands"][command]["description"]


def option_names(group, command, option):
	return strings[group]["commands"][command]["options"][option]["name"]


def option_descriptions(group, command, option):
	return strings[group]["commands"][command]["options"][option]["description"]


def response(group, command, res_tag, locale):
	"""Requires locale parameter (ctx.interaction.locale)"""

	try:
		res = strings[group]["commands"][command]["responses"][res_tag][locale]
	except KeyError:
		return strings[group]["commands"][command]["responses"][res_tag]["en-US"]

	return res

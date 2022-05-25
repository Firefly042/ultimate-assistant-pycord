"""String localization"""

strings = {
	"common": {
		"no-character": {
			"en-US": "You do not have an active character in this server! Do you need to use `/profile scambio`?",
			"it": "Non hai un personaggio attivo in questo server! Hai bisogno di usare `/profile scambio`?"
		},
		"visible-desc": {
			"en-US": "Set to 'True' for a permanent, visible response.",
			"it": "Imposta a 'True' per una risposta visibile e permanente."
		},
		"visible-name": {
			"en-US": "visible",
			"it": "visibile"
		}
	},

	"profile": {
		"group_name": {
			"en-US": "profile",
			"it": "profilo"
		},
		"group_description": {
			"en-US": "Character profiles"
		},
		"commands": {
			"view": {
				"name": {
					"en-US": "view",
					"it": "visualizza"
				},
				"description": {
					"en-US": "View a character's profile",
					"it": "Visualizza il profilo di un personaggio"
				},
				"options": {
					"player": {
						"name": {
							"en-US": "player",
							"it": "giocatore"
						},
						"description": {
							"en-US": "The user who plays this character",
							"it": "L'utente che usa questo personaggio"
						}
					},
					"name": {
						"name": {
							"en-US": "name",
							"it": "nome"
						},
						"description": {
							"en-US": "Character's display name (usually given name)",
							"it": "Il nome da display del personaggio"
						}
					}
				},
				"responses": {
					"error1": {
						"en-US": "Cannot find that character for that player!",
						"it": "Non riesco a trovare quel personaggio per quel giocatore!"
					}
				}
			},

			"list": {
				"name": {
					"en-US": "list",
					"it": "lista"
				},
				"description": {
					"en-US": "List all registered characters for this server",
					"it": "Lista tutti i personaggi registrati per questo server"
				},
				"responses": {
					"res1": {
						"en-US": "Characters in {}",
						"it": "Personaggi in {}"
					},
					"error1": {
						"en-US": "This server has no registered characters!",
						"it": "Questo server non ha personaggi registrati!"
					}
				}
			},

			"swap": {
				"name": {
					"en-US": "swap"
				},
				"description": {
					"en-US":  "Set your active character"
				},
				"options": {
					"name": {
						"name": {
							"en-US": "name"
						},
						"description": {
							"en-US": "Display name of character to swap to"
						}
					}
				},
				"responses": {
					"error1": {
						"en-US": "Cannot find a character named {} for you!"
					},
					"res1": {
						"Swapped character to {}"
					}
				}
			},

			"current": {
				"name": {
					"en-US": "current"
				},
				"description": {
					"en-US": "Check your active character"
				},
				"responses": {
					"res1": {
						"en-US": "You are currently playing as **{}**"
					}
				}
			}
		}
	},

	"profile_embed": {
		"group_name": {
			"en-US": "embed",
			"it": "italiano_embed"
		},
		"group_description": {
			"en-US": "Profile editing",
			"it": "italiano embed desc"
		},
		"commands": {
			"edit": {
				"name": {
					"en-US": "edit"
				},
				"description": {
					"en-US": "Edit profile embed fields (color, thumbnail, or image)"
				},
				"options": {
					"name": {
						"name": {
							"en-US": "name"
						},
						"description": {
							"en-US": "Your character's display name"
						}
					},
					"field_to_change": {
						"name": {
							"en-US": "field_to_change"
						}
					},
					"new_value": {
						"name": {
							"en-US": "new_value"
						},
						"description": {
							"en-US": "Hex code (without #) or image url"
						}
					}
				},
				"responses": {
					"error-hex": {
						"en-US": "#{} is not a valid hex!"
					},
					"error1": {
						"en-US": "Could not find a character with that name for you!"
					},
					"error-url": {
						"en-US": "I cannot display that image URL! Reverting."
					},
					"res1": {
						"en-US": "Updated"
					}
				}
			},

			"field": {
				"name": {
					"en-US": "field"
				},
				"description": {
					"en-US": "Add or edit up to 25 fields to your character's profile embed"
				},
				"options": {
					"name": {
						"name": {
							"en-US": "name"
						},
						"description": {
							"en-US": "Your character's display name"
						}
					},
					"field_title": {
						"name": {
							"en-US": "field_title"
						},
						"description": {
							"en-US": "Up to 256 characters"
						}
					},
					"field_content": {
						"name": {
							"en-US": "field_content"
						},
						"description": {
							"en-US": "Up to 1024 characters"
						}
					}
				},
				"responses": {
					"error-limit": {
						"en-US": "You must remove a field before adding a new one!"
					},
					"error1": {
						"en-US": "Could not find a character with that name for you!"
					},
					"error-length": {
						"en-US": "Your embed has exceeded the maximum length of 6000. Reverting."
					},
					"res1": {
						"en-US": "Updated"
					}
				}
			},

			"desc": {
				"name": {
					"en-US": "desc"
				},
				"description": {
					"en-US": "Add or edit profile embed description"
				},
				"options": {
					"name": {
						"name": {
							"en-US": "name"
						},
						"description": {
							"en-US": "Your character's display name"
						}
					},
					"content": {
						"name": {
							"en-US": "content"
						},
						"description": {
							"en-US": "Up to 4096 characters"
						}
					},
				},
				"responses": {
					"error1": {
						"en-US": "Could not find a character with that name for you!"
					},
					"error-length": {
						"en-US": "Your embed has exceeded the maximum length of 6000. Reverting."
					},
					"res1": {
						"en-US": "Updated"
					}
				}
			}
		}
	}
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

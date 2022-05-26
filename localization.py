"""String localization"""

strings = {
	"common": {
		"no-character": {
			"en-US": "You do not have an active character in this server! Do you need to use `/profile swap`?",
			"it": "Non hai un personaggio attivo in questo server! Hai bisogno di usare `/profile cambio`?"
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
					"it": "cambio"
				},
				"description": {
					"en-US":  "Set your active character"
					"it": "Imposta il tuo personaggio attivo"
				},
				"options": {
					"name": {
						"name": {
							"en-US": "name"
							"it": "nome"
						},
						"description": {
							"en-US": "Display name of character to swap to"
							"it": "Il nome del personaggio con cui scambiarti"
						}
					}
				},
				"responses": {
					"error1": {
						"en-US": "Cannot find a character named {} for you!"
						"it": "Non riesco a trovare un personaggio di nome {}!"
					},
					"res1": {
						"Swapped character to {}"
						"Personaggio cambiato in {}"
					}
				}
			},

			"current": {
				"name": {
					"en-US": "current"
					"it": "attuale"
				},
				"description": {
					"en-US": "Check your active character"
					"it": "Controlla il tuo personaggio attivo"
				},
				"responses": {
					"res1": {
						"en-US": "You are currently playing as **{}**"
						"it": "Al momento stai usando **{}**"
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
			"it": "Modifica profilo"
		},
		"commands": {
			"edit": {
				"name": {
					"en-US": "edit"
					"it": "modifica"
				},
				"description": {
					"en-US": "Edit profile embed fields (color, thumbnail, or image)"
					"it": "Modifica l'embed del profilo (colore, copertina o immagine)"
				},
				"options": {
					"name": {
						"name": {
							"en-US": "name"
							"it": "nome"
						},
						"description": {
							"en-US": "Your character's display name"
							"it": "Il nome del tuo personaggio"
						}
					},
					"field_to_change": {
						"name": {
							"en-US": "field_to_change"
							"it": "campo_da_cambiare"
						}
					},
					"new_value": {
						"name": {
							"en-US": "new_value"
							"it": "nuovo_valore"
						},
						"description": {
							"en-US": "Hex code (without #) or image url"
							"it": "Codice Hex (senza #) o l'url dell'immagine"
						}
					}
				},
				"responses": {
					"error-hex": {
						"en-US": "#{} is not a valid hex!"
						"it": "#{} non è un hex valido!"
					},
					"error1": {
						"en-US": "Could not find a character with that name for you!"
						"it": "Non riesco a trovare un personaggio con quel nome!"
					},
					"error-url": {
						"en-US": "I cannot display that image URL! Reverting."
						"it": "Non posso mostrare quell'immagine! Ripristino."
					},
					"res1": {
						"en-US": "Updated"
						"it": "Aggiornato"
					}
				}
			},

			"field": {
				"name": {
					"en-US": "field"
					"it": "campo"
				},
				"description": {
					"en-US": "Add or edit up to 25 fields to your character's profile embed"
					"it": "Aggiungi o modifica fino a 25 campi per l'embed del profilo del tuo personaggio"
				},
				"options": {
					"name": {
						"name": {
							"en-US": "name"
							"it": "nome"
						},
						"description": {
							"en-US": "Your character's display name"
							"it": "Il nome del tuo personaggio"
						}
					},
					"field_title": {
						"name": {
							"en-US": "field_title"
							"it": "campo_titolo"
						},
						"description": {
							"en-US": "Up to 256 characters"
							"it": "Fino a 256 caratteri"
						}
					},
					"field_content": {
						"name": {
							"en-US": "field_content"
							"it": "campo_contenuti"
						},
						"description": {
							"en-US": "Up to 1024 characters"
							"it": "Fino a 1024 caratteri"
						}
					}
				},
				"responses": {
					"error-limit": {
						"en-US": "You must remove a field before adding a new one!"
						"it": "Devi rimuovere un campo prima di poterne aggiugere un altro!"
					},
					"error1": {
						"en-US": "Could not find a character with that name for you!"
						"it": "Non sono riuscito a trovare un personaggio con quel nome!"
					},
					"error-length": {
						"en-US": "Your embed has exceeded the maximum length of 6000. Reverting."
						"it": "Il tuo embed ha superato la lunghezza massima di 6000. Ripristino."
					},
					"res1": {
						"en-US": "Updated"
						"it": "Aggiornato"
					}
				}
			},

			"desc": {
				"name": {
					"en-US": "desc"
					"it": "desc"
				},
				"description": {
					"en-US": "Add or edit profile embed description"
					"it": "Aggiungi o modifica la descrizione nell'embed del profilo"
				},
				"options": {
					"name": {
						"name": {
							"en-US": "name"
							"it": "nome"
						},
						"description": {
							"en-US": "Your character's display name"
							"it": "Il nome del tuo personaggio"
						}
					},
					"content": {
						"name": {
							"en-US": "content"
							"it": "contenuti"
						},
						"description": {
							"en-US": "Up to 4096 characters"
							"it": "Fino a 4096 caratteri"
						}
					},
				},
				"responses": {
					"error1": {
						"en-US": "Could not find a character with that name for you!"
						"it": "Non sono riuscito a trovare un personaggio con quel nome!"
					},
					"error-length": {
						"en-US": "Your embed has exceeded the maximum length of 6000. Reverting."
						"it": "Il tuo embed ha superato la lunghezza massima di 6000. Ripristino."
					},
					"res1": {
						"en-US": "Updated"
						"it": "Aggiornato"
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

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
	    }
	}
    }
}


def group_names(group):
    return strings[group]["group_name"]


def group_descriptions(group):
    return strings[group]["group_descriptions"]


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

    res = strings[group]["commands"][command]["responses"][res_tag][locale]

    if (not res):
	return strings[group]["commands"][command]["responses"][res_tag]["en-US"]

    return res

print(group_names("profile"))

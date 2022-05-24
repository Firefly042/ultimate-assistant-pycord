strings = {
    "common": {
        "no-character": {
            "en-US": "You do not have an active character in this server! Do you need to use `/profile swap`?",
            "it": "<it>"
        },
        "visible-desc": {
            "en-US": "Set to 'True' for a permanent, visible response.",
            "it": "<it>"
        },
        "visible-name": {
            "en-US": "visible",
            "it": "<it>"
        }
    },

    "profile": {
        "view": {
            "name": {
                "en-US": "view",
                "it": "<it>"
            },
            "description": {
                "en-US": "View a character's profile",
                "it": "<it>"
            },
            "options": {
                "player": {
                    "name": {
                        "en-US": "name",
                        "it": "<it>"
                    },
                    "description": {
                        "en-US": "The user who plays this character",
                        "it": "<it>"
                    }
                },
                "name": {
                    "name": {
                        "en-US": "name",
                        "it": "<it>"
                    },
                    "description": {
                        "en-US": "Character's display name (usually given name)",
                        "it": "<it>"
                    }
                }
            },
            "responses": {
                "error1": {
                    "en-US": "Cannot find that character for that player!",
                    "it": "<it>"
                }
            }
        },

        "list": {
            "name": {
                "en-US": "list",
                "it": "<it>"
            },
            "description": {
                "en-US": "List all registered characters for this server",
                "it": "<it>"
            },
            "responses": {
                "res1": {
                    "en-US": "Characters in {}",
                    "it": "<it>"
                },
                "error1": {
                    "en-US": "This server has no registered characters!",
                    "it": "<it>"
                }
            }
        }
    }
}



def command_names(group, command):
	return strings[group][command]["name"]


def command_descriptions(group, command):
	return strings[group][command]["description"]


def option_names(group, command, option):
	return strings[group][command]["options"][option]["name"]


def option_descriptions(group, command, option):
	return strings[group][command]["options"][option]["description"]


def response(group, command, res_tag, locale):
	res = strings[group][command]["responses"][res_tag][locale]

	if (not res):
		return strings[group][command]["responses"][res_tag]["en-US"]

	return res
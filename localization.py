"""String localization"""

import os
import json

from discord import OptionChoice

class Localization:
	"""Data encapsulation of .jsons in ./localization"""

	def __new__(cls):
		if not hasattr(cls, 'instance'):
			cls.instance = super(Localization, cls).__new__(cls)
		return cls.instance


	def __init__(self):
		self.strings = {}
		self.keys = []
		# Iterate through files in ./localization
		for fname in os.listdir("./localization"):
			locale = fname[:-5]
			self.keys.append(locale)

			fobject = open(f"./localization/{fname}", "r", encoding="utf-8")
			self.strings[locale] = json.load(fobject)

			fobject.close()

		print("Initialized localizations")


	def common(self, tag):
		"""Dictionary for a common name/description"""

		res = {}
		for locale in self.keys:
			res[locale] = self.strings[locale]["common"][tag]

		return res


	def common_res(self, tag, locale):
		"""String for a common response"""

		try:
			res = self.strings[locale]["common"][tag]
		except KeyError:
			return self.strings["en-US"]["common"][tag]

		return res


	def group_names(self, group):
		"""Command group name"""

		res = {}
		for locale in self.keys:
			res[locale] = self.strings[locale][group]["group_name"]

		return res


	def group_descriptions(self, group):
		"""Command group description"""

		res = {}
		for locale in self.keys:
			res[locale] = self.strings[locale][group]["group_description"]

		return res


	def command_names(self, group, command):
		"""Command name (in group)"""

		res = {}
		for locale in self.keys:
			res[locale] = self.strings[locale][group]["commands"][command]["name"]

		return res


	def command_descriptions(self, group, command):
		"""Command description (in group)"""

		res = {}
		for locale in self.keys:
			res[locale] = self.strings[locale][group]["commands"][command]["description"]

		return res


	def nongroup_names(self, command):
		"""Command name (not in group)"""

		res = {}
		for locale in self.keys:
			res[locale] = self.strings[locale][command]["name"]

		return res


	def nongroup_descriptions(self, command):
		"""Command description (not in group)"""

		res = {}
		for locale in self.keys:
			res[locale] = self.strings[locale][command]["description"]

		return res


	def nongroup_option_names(self, command, option):
		"""Command option name (not in group)"""

		res = {}
		for locale in self.keys:
			res[locale] = self.strings[locale][command]["options"][option]["name"]

		return res


	def nongroup_option_descriptions(self, command, option):
		"""Command option description (not in group)"""

		res = {}
		for locale in self.keys:
			res[locale] = self.strings[locale][command]["options"][option]["description"]

		return res


	def nongroup_choices(self, command, option):
		"""Returns array of OptionChoice"""

		# Get number of choices fron en-US
		en_choices = self.strings["en-US"][command]["options"][option]["choices"]
		n_choices = len(en_choices)

		choices = [OptionChoice(name=en_choices[i], value=en_choices[i]) for i in range(n_choices)]

		for i in range(n_choices):
			choice = choices[i]
			locales = {}

			for locale in self.keys:
				locales[locale] = self.strings[locale][command]["options"][option]["choices"][i]

			choice.name_localizations = locales

		return choices


	def nongroup_res(command, tag, locale):
		try:
			res = self.strings[locale][command]["responses"][tag]
		except KeyError:
			return self.strings["en-US"][command]["responses"][tag]

		return res


	def option_names(self, group, command, option):
		"""Command option name (in group)"""

		res = {}
		for locale in self.keys:
			res[locale] = self.strings[locale][group]["commands"][command]["options"][option]["name"]

		return res


	def option_descriptions(self, group, command, option):
		"""Command option description (in group)"""

		res = {}
		for locale in self.keys:
			res[locale] = self.strings[locale][group]["commands"][command]["options"][option]["description"]

		return res


	def choices(self, group, command, option):
		"""Returns array of OptionChoice"""

		# Get number of choices fron en-US
		en_choices = self.strings["en-US"][group]["commands"][command]["options"][option]["choices"]
		n_choices = len(en_choices)

		choices = [OptionChoice(name=en_choices[i], value=en_choices[i]) for i in range(n_choices)]

		for i in range(n_choices):
			choice = choices[i]
			locales = {}

			for locale in self.keys:
				locales[locale] = self.strings[locale][group]["commands"][command]["options"][option]["choices"][i]

			choice.name_localizations = locales

		return choices


	def response(self, group, command, tag, locale):
		"""Requires locale parameter (ctx.interaction.locale)"""

		try:
			res = self.strings[locale][group]["commands"][command]["responses"][tag]
		except KeyError:
			return self.strings["en-US"][group]["commands"][command]["responses"][tag]

		return res


# Instantiate singleton
loc = Localization()

"""
Author @Firefly#7113
A UI View class that will display a list of embeds given at instantiation. A forward and a back button are provided.
"""

import discord

class EmbedList(discord.ui.View):
	"""Two buttons that shift through an array of embeds"""

	def __init__(self, embeds, interaction):
		super().__init__(timeout=60)

		self.embeds = embeds
		self.interaction = interaction

		self.prev_button = [c for c in self.children if c.label == "Previous"][0]
		self.next_button = [c for c in self.children if c.label == "Next"][0]

		if (len(embeds) > 1):
			self.next_button.disabled = False

		self.current_page = 0
		self.max_pages = len(embeds)


	async def on_timeout(self):
		"""Disable and stop listening for interaction"""

		try:
			self.disable_all_items()
			await self.interaction.edit_original_message(view=self)
		except discord.errors.NotFound:
			return


	# Previous page
	@discord.ui.button(label="Previous",
		style = discord.ButtonStyle.red,
		disabled = True,
	)
	async def button_prev_callback(self, _, interaction):
		"""Previous embed"""

		self.current_page -= 1
		self.next_button.disabled = False
		if (self.current_page == 0):
			self.prev_button.disabled = True

		await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)


	# Next page
	@discord.ui.button(label="Next",
		style = discord.ButtonStyle.green,
		disabled = True
	)
	async def button_next_callback(self, _, interaction):
		"""Next embed"""

		self.current_page += 1
		self.prev_button.disabled = False
		if (self.current_page == len(self.embeds)-1):
			self.next_button.disabled = True
		await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)

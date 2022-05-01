"""
A UI View class that will display a list of embeds given at instantiation. A forward and a back button are provided.
"""

import discord

class EmbedList(discord.ui.View):
	def __init__(self, embeds):
		super().__init__(timeout=60)
		
		self.embeds = embeds

		self.prev_button = [c for c in self.children if c.label == "Previous"][0]
		self.next_button = [c for c in self.children if c.label == "Next"][0]

		if (len(embeds) > 1):
			self.next_button.disabled = False

		self.current_page = 0
		self.max_pages = len(embeds)


	# TODO - Figure out how to update view. interaction/message aren't accessible
	async def on_timeout(self):
		self.prev_button.disabled = True
		self.next_button.disabled = True
		# await interaction.response.edit_message(content="Timed out", view=self)
		self.stop()


	# Previous page
	@discord.ui.button(label="Previous",
		style = discord.ButtonStyle.red,
		disabled = True,
	)
	async def button_prev_callback(self, button, interaction):
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
	async def button_next_callback(self, button, interaction):
		self.current_page += 1
		self.prev_button.disabled = False
		if (self.current_page == len(self.embeds)-1):
			self.next_button.disabled = True
		await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)

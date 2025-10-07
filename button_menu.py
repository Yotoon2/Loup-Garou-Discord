import discord

class ButtonMenu(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View

    def __init__(self, potion_vie, cible_lg):
        self.potion_vie = potion_vie
        self.cible_lg = cible_lg
        super().__init__(timeout=180)

    @discord.ui.button(label="Sauver", row=0, style=discord.ButtonStyle.green) # Create a button with the label "😎 Click me!" with color Blurple
    async def button_callback1(self, interaction, button):
        if self.potion_vie == False:
            await interaction.response.send(f"Vous avez déjà utilisé la potion de vie.")
        else:
            for i in range(len(self.children)):
                self.children[i].disabled = True
            await interaction.response.edit_message(view=self)
            await interaction.followup.send(f"Vous avez décidé de ***sauver*** **{self.cible_lg.name}**.") # Send a message when the button is clicked
            self.cible_lg = None
        self.potion_vie = False



    @discord.ui.button(label="Ne rien faire", row=0, style=discord.ButtonStyle.red)
    async def button_callback2(self, interaction, button):
        for i in range(len(self.children)):
            self.children[i].disabled = True
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(f"Vous avez décidé de ne rien faire.")
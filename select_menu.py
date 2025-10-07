import discord

class SelectVote(discord.ui.Select):
    """menu deroulant (25 options max)"""
    print("select vote")
    def __init__(self, players: list, player = None, dico_players: dict = None):
        self.players = players
        self.player = player
        self.dico_players = dico_players
        options = []
        for player in self.players:
            options.append(discord.SelectOption(label=f"{player.member.display_name}", value=f"{player.name}"))
        super().__init__(placeholder="Select an option",max_values=1,min_values=1,options=options)

    async def callback(self, interaction: discord.Interaction):
        """renvoie une réponse à la selection d'un choix """
        await interaction.response.defer()
        choice = self.values[0]  # ce qui est renvoyé au clic du bouton (personne votee) (type str)
        voteur = self.dico_players[interaction.user.name]
        personne_votee = self.dico_players[choice]
        await self.sys_vote(interaction, choice, personne_votee, voteur)

    async def sys_vote(self, interaction, choice, personne_votee, voteur):
        #VOTEUR A DEJA VOTER QLQN D'AUTRE
        if voteur.state == True and voteur.previous_vote != None and (self.player == None or voteur.role == self.player.role):
            voteur.previous_vote.nvote -= 1
            personne_votee.nvote += 1
            if self.player == None:
                await interaction.followup.send(f"<@{voteur.id}> a voté pour <@{personne_votee.id}>. **{personne_votee.nvote}** vote(s)")
                await interaction.followup.send(f"<@{voteur.previous_vote.id}> ne possède maintenant que **{voteur.previous_vote.nvote}** vote(s)")
            elif self.player.role == "Voyante":
                await interaction.followup.send(f"Vous avez décidé d'espionner **{personne_votee.name}**.")
            elif self.player.role == "Loup Garou":
                await interaction.followup.send(f"<@{voteur.id}> veut dévorer **{personne_votee.name}**. **{personne_votee.nvote}** vote(s)")
            elif self.player.role == "Sorciere":
                await interaction.followup.send(f"Vous avez décidé de tuer **{personne_votee.name}**.")
            elif self.player.role == "Chasseur":
                await interaction.followup.send(f"<@{voteur.id}> a décidé de tirer sur **<@{personne_votee.id}>**")
            voteur.previous_vote = personne_votee

        #VOTEUR N'A VOTER PERSONNE
        elif voteur.state == True and voteur.previous_vote == None and (self.player == None or voteur.role == self.player.role):
            voteur.previous_vote = personne_votee
            personne_votee.nvote += 1
            if self.player == None:
                await interaction.followup.send(f"<@{voteur.id}> a voté pour <@{personne_votee.id}>. **{personne_votee.nvote}** vote(s)")
            elif self.player.role == "Voyante":
                await interaction.followup.send(f"Vous avez décidé d'espionner **{personne_votee.name}**.")
            elif self.player.role == "Loup Garou":
                await interaction.followup.send(f"<@{voteur.id}> veut dévorer **{personne_votee.name}**. **{personne_votee.nvote}** vote(s)")
            elif self.player.role == "Sorciere":
                await interaction.followup.send(f"Vous avez décidé de tuer **{personne_votee.name}**.")
            elif self.player.role == "Chasseur":
                await interaction.followup.send(f"<@{voteur.id}> a décidé de tirer sur **<@{personne_votee.id}>**")

        #PREMIERE INTERACTION
        elif voteur.state == True and interaction.response.is_done() == False and (self.player == None or voteur.role == self.player.role):
            if choice == f"{personne_votee.name}" and personne_votee.previous_vote == None:
                voteur.previous_vote = personne_votee
                personne_votee.nvote += 1
                if self.player.role == None:
                    await interaction.response.send_message(f"<@{voteur.id}> a voté pour <@{personne_votee.id}>. **{personne_votee.nvote}** vote(s)", ephemeral=False)
                elif self.player.role == "Voyante":
                    await interaction.response.send_message(f"Vous avez décidé d'espionner **{personne_votee.name}**.", ephemeral=False)
                elif self.player.role == "Loup Garou":
                    await interaction.response.send_message(f"<@{voteur.id}> veut dévorer **{personne_votee.name}**. **{personne_votee.nvote}** vote(s)", ephemeral=False)
                elif self.player.role == "Sorciere":
                    await interaction.response.send_message(f"Vous avez décidé de tuer **{personne_votee.name}**.", ephemeral=False)
                elif self.player.role == "Chasseur":
                    await interaction.response.send_message(f"<@{voteur.id}> a décidé de tirer sur **<@{personne_votee.id}>**")

        else:
            await interaction.followup.send(f"Vous n'avez pas la permission d'intéragir.", ephemeral=True)

class SelectView(discord.ui.View):
    """permet d'afficher le menu deroulant"""
    print("select view")
    def __init__(self, players, player=None, dico_players = None, *, timeout = 180): #Select est la classe a afficher
        super().__init__(timeout=timeout)
        self.add_item(SelectVote(players, player, dico_players))
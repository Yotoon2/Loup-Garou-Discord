import discord

class SelectLove(discord.ui.Select):
    """menu deroulant (25 options max)"""
    print("select vote")
    def __init__(self, players: list, dico: dict):
        self.players = players
        self.dico = dico
        self.couple = []
        options = []
        for player in self.players:
            options.append(discord.SelectOption(label=f"{player.member.display_name}", value=f"{player.name}"))
        super().__init__(placeholder="Select an option",max_values=2,min_values=2,options=options)

    async def callback(self, interaction: discord.Interaction):
        """renvoie une réponse à la selection d'un choix """
        await interaction.response.defer()
        choice = self.values[0] # type str
        print(f"valeur1: {choice}, valeur2: {self.values[1]}")
        voteur = self.dico[interaction.user.name]
        personne_votee = self.dico[choice]
        print(personne_votee)
        await self.sys_vote(interaction, choice, personne_votee, voteur)

    async def sys_vote(self, interaction, choice, personne_votee, voteur):
        if choice == f"{personne_votee.name}" and voteur.previous_vote != None:
            await interaction.followup.send(f"Vous avez décidé que **{personne_votee.name}** et **{self.values[1]}** seront en couple.")
            self.couple = [personne_votee, self.dico[self.values[1]]]

        elif interaction.response.is_done() == False:
            if choice == f"{personne_votee.name}" and personne_votee.previous_vote == None:
                await interaction.response.send(f"Vous avez décidé que **{personne_votee.name}** et **{self.values[1]}** seront en couple.")
                self.couple = [personne_votee, self.dico[self.values[1]]]

        else:
            if choice == f"{personne_votee.name}" and personne_votee.previous_vote == None:
                await interaction.followup.send(f"Vous avez décidé que **{personne_votee.name}** et **{self.values[1]}** seront en couple.")
                self.couple = [personne_votee, self.dico[self.values[1]]]

class SelectViewCupi(discord.ui.View):
    """permet d'afficher le menu deroulant"""
    print("select view")
    def __init__(self, players: list, dico: dict, *, timeout = 180): #Select est la classe a afficher
        super().__init__(timeout=timeout)
        self.selectlove = SelectLove(players, dico)
        self.add_item(self.selectlove)



async def user_to_player(user, players: list):
    for player in players:
        if player.name == str(user):
            return player

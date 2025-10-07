import discord
class Player():
    """Classe joueur"""
    def __init__(self, name, id: int, role, state: bool, member: discord.Member, nvote: int = 0, previous_vote = None, amour = None, camp = None):
        self.name = name
        self.id = id
        self.role = role
        self.state = state
        self.member = member
        self.nvote = nvote
        self.previous_vote = previous_vote
        self.amour = amour
        self.camp = camp


    async def is_alive(self):
        if self.state:
            return self.state
        else:
            await self.name.edit(mute=True)

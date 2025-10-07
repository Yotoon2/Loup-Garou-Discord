from select_menu import SelectView
import asyncio

class Timer():
    def __init__(self, context, time: int, n_jours: int = None):
        self.context = context
        self.time = time
        self.n_jours = n_jours

    async def start_timer(self):
        """Timer de début de partie"""
        msg = await self.context.send(f"Il reste **{self.time}** secondes avant le début de la partie.")
        for i in range(0, self.time):
            await asyncio.sleep(1)
            await msg.edit(content=f"Il reste **{self.time - 1 - i}** secondes avant le début de la partie.")
        await asyncio.sleep(1/2)
        for i in range(1):
            await msg.edit(content="La partie commence")
            await asyncio.sleep(1/2)
            await msg.edit(content="La partie commence.")
            await asyncio.sleep(1/2)
            await msg.edit(content="La partie commence..")
            await asyncio.sleep(3/41/2)
            await msg.edit(content="La partie commence...")
            await asyncio.sleep(3/41/2)
        await msg.delete()

    async def discussion(self):
        """Timer de début de jour et de phase de discussion"""
        await self.context.send(content=f"# Jour {self.n_jours}")
        await self.context.send(content=f"## Phase de discussion")
        msg = await self.context.send(content=f"### Il vous reste **{self.time}** secondes pour discuter.")
        for i in range(0, self.time):
            await asyncio.sleep(1)
            await msg.edit(content=f"### Il vous reste **{self.time-1-i}** secondes pour discuter.")
        await msg.edit(content=f"## La phase de discussion est terminée.")
        await asyncio.sleep(1)

    async def vote_village(self, players: list, dico_players: dict):
        """Timer de début de jour et de phase de discussion"""
        await self.context.send(f"Phase de vote")
        msg = await self.context.send(content=f"Il vous reste **{self.time}** secondes pour voter.")
        vote_menu = await menu(self.context, players, text="Vote du Jour", dico_players=dico_players, player=None)
        for i in range(0, self.time):
            await asyncio.sleep(1)
            await msg.edit(content=f"Il vous reste **{self.time - 1 - i}** secondes pour voter.")
        await msg.delete()
        await vote_menu.delete()
        await asyncio.sleep(1)
        await self.context.send(content=f"La phase de vote est terminée.")
        await asyncio.sleep(1)

    async def role_timer(self):
        """Timer de nuit"""
        await self.context.send(content=f"## Nuit {self.n_jours}")
        msg = await self.context.send(f"Il vous reste **{self.time}** secondes pour faire un choix.")
        for i in range(0, self.time):
            await asyncio.sleep(1)
            await msg.edit(content=f"Il vous reste **{self.time-1-i}** secondes pour faire un choix.")
        await asyncio.sleep(1)
        await msg.delete()
        await self.context.send("## Fin de votre tour.")

    async def night_timer(self):
        """Timer de nuit"""
        msg = await self.context.send(f"Il reste **{self.time}** secondes avant la fin de la nuit.")
        for i in range(0, self.time):
            await asyncio.sleep(1)
            await msg.edit(content=f"Il reste **{self.time-1-i}** secondes avant la fin de la nuit.")
        await asyncio.sleep(1)
        await msg.delete()
        await self.context.send("## Le jour se lève.")

async def menu(context, players: list, text: str, dico_players: dict, player=None): #Select est la classe a afficher, player est le joueur avec un role qui agit de nuit s'il y en a un
    """commande pour menu deroulant"""
    print("menu (appelle select view)")
    vote_menu = await context.send(content=text, view=SelectView(players=players, player=player, dico_players=dico_players))
    return vote_menu

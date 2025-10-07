import discord
from discord.ext import commands, tasks
import asyncio
import random
from ast import literal_eval
from timer import Timer
from select_menu import SelectView, SelectVote
from cupi_select import SelectViewCupi, SelectLove
from player import Player
from button_menu import ButtonMenu

token = 'INSERT YOUR TOKEN'

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)


threads = {}
dico_lg = {}


# @bot.command() # Create a slash command
async def button(context, potion_vie, cible_lg):
    bouton_soso = ButtonMenu(potion_vie=potion_vie, cible_lg=cible_lg)
    potion_vie = await context.send(content=f"**{cible_lg.name}** est visé(e) par les loups-garous ce soir.",
                                    view=bouton_soso) # Send a message with our View class that contains the button
    potion_vie = bouton_soso.potion_vie
    return bouton_soso

async def menu(context, players: list, text: str, dico_players: dict, player=None): #Select est la classe a afficher, player est le joueur avec un role qui agit de nuit s'il y en a un
    """fonction pour menu deroulant"""
    vote_menu = await context.send(content=text, view=SelectView(players=players, player=player, dico_players=dico_players))
    return vote_menu

async def cupi_menu(context, players: list, dico, text: str):
    """fonction pour menu deroulant du cupi"""
    menu_cupi = SelectViewCupi(players=players, dico=dico)
    message_menu = await context.send(content=text, view=menu_cupi)
    return message_menu, menu_cupi


async def user_to_player(user, players: list):
    for player in players:
        if player.name == str(user):
            return player

@commands.has_permissions(administrator=True)
@bot.command(aliases=["compo"])
async def composition(context, nb_players: int, *, compo: literal_eval = []):
    """Commande pour afficher ou changer une composition de rôles"""
    nb_players = int(nb_players)
    compo = list(compo)
    if compo == []:
        with open(f"./compos/compo{nb_players}.txt", "r") as f:
            await context.send(f"Composition actuelle pour {nb_players} joueurs: {f.read()}")
    elif nb_players < 6 or nb_players > 12:
        await context.send('Veuillez choisir un chiffre entre 6 et 12')
        raise IndexError("6 <= int <= 12")
    elif len(compo) != nb_players:
        await context.send("Il faut le même nombre de rôles que de joueurs")
        raise IndexError("n players don't match n roles")
    else:
        open(f"./compos/compo{nb_players}.txt").close()
        with open(f"compo{nb_players}.txt", "w") as f:
            f.write(str(compo))
        await context.send(f"{compo}")
        return compo

async def get_compo(context, nb_players: int):
    """Récupère une composition de rôles dont on a besoin"""
    # if nb_players < 6 or nb_players > 12: #enlever commentaire pour vrai test
    #     raise IndexError("6 <= int <= 12")
    with open(f"./compos/compo{nb_players}.txt", "r") as f:
        return literal_eval(f.read())

async def role_assign(context, nb_players, members: literal_eval):
    """Assigne un role au hasard pour chaque joueur de la partie"""
    liste = []
    roles = await get_compo(context, nb_players)
    for _ in range(len(members)):
        role = random.choice(roles)
        roles.remove(role)
        member = members[0]
        members.remove(member)
        if role == "Loup Garou":
            liste.append(Player(member.name, member.id, role, True, member = member, camp="LG"))
        elif role == "Cupidon":
            liste.append(Player(member.name, member.id, role, True, member=member, camp="Couple"))
        else:
            liste.append(Player(member.name, member.id, role, True, member=member, camp="Village"))
    return liste


async def vc_members(context):
    """Renvoie tous les membres présents dans le vocal de la personne qui a lancé la commande"""
    vc = []
    for guild in bot.guilds:
        if guild.id == context.author.guild.id:
            for member in guild.members:
                if member.voice == None:
                    continue
                elif member.voice.channel.id == context.author.voice.channel.id:
                    vc.append(member)
    return vc

async def thread(context, name: str):
    """Créé un thread privé et renvoie son ID"""
    channel = context.channel
    thread = await channel.create_thread(name=f"{name}", auto_archive_duration=60)
    await thread.edit(invitable=False)
    threads[f'{name.lower()}_thread'] = thread.id  # Stocker l'ID du thread dans le dictionnaire
    return thread.id

async def create_channel_mort(context, name:str):
    """Créé le channel mort privé et renvoie son ID"""
    cat = context.category
    pos_channel = context.position
    guild = context.guild
    role_mort_id = None
    for role in guild.roles:
        if role.name == "Morts":
            role_mort = role
            role_mort_id = role.id
            break
    if role_mort_id == None:
        role_mort = await guild.create_role(name="Morts", colour=0x010000)
        role_mort_id = role_mort.id

    overwrites = {guild.default_role: discord.PermissionOverwrite(read_messages = False, send_messages=False),
                  guild.get_role(role_mort_id): discord.PermissionOverwrite(read_messages = True, send_messages = True)}
    channel = await cat.create_text_channel(name=name, overwrites=overwrites , position=pos_channel)

    for i in range(len(guild.categories)):
        await guild.categories[i].set_permissions(role_mort, read_messages=True, send_messages=False, send_messages_in_threads=False)

    with open("compos/role_mort_id.txt", "w") as f:
        f.write(str(role_mort_id))
        f.close()



async def reset_votes(context, players: list):
    for player in players:
        player.nvote = 0
        player.previous_vote = None

def temps_nuit(cupidon, voyante, lgs, sorciere, n_nuits):
    counter = 0
    if cupidon != None and n_nuits == 1:
        counter += 1
    if voyante != None and voyante.state == True:
        counter += 1
    if sorciere != None and sorciere.state == True:
        counter += 1
    for lg in lgs:
        if lg.state == True:
            counter += 1
            break
    with open("counter.txt", 'w') as f:
        f.write(f"{counter}")
        f.close()


async def action_cupidon(context, cupi_chat, cupidon, players: list, dico: dict, n_nuits, potion_mort, dico_players):
    if cupidon is not None and cupidon.state == True:
        await context.send("C'est au tour du **Cupidon**.")
        message_menu, affichage_menu = await cupi_menu(cupi_chat, players, dico,
                                            text="Choisissez les deux joueurs qui deviendront les membres du couple. Si vous ne choisissez pas, il sera choisi aléatoirement.")
        await cupi_chat.edit(locked=False)
        cupi_timer = Timer(cupi_chat, 30, n_nuits)
        await cupi_timer.role_timer()
        await message_menu.delete()

        if affichage_menu.selectlove.couple == []:
            random_choice = []
            for i in players:
                random_choice.append(i)
            for i in range(2):
                amoureux = random.choice(random_choice)
                affichage_menu.selectlove.couple.append(amoureux)
                random_choice.remove(amoureux)
            await cupi_chat.send(f'Vous avez décidé de laisser le hasard choisir votre couple.')
            await cupi_chat.send(f'Le couple choisi aléatoirement est : **{affichage_menu.selectlove.couple[0].name}** :revolving_hearts: **{affichage_menu.selectlove.couple[1].name}**')
        return affichage_menu.selectlove

async def action_voyante(context, vovo_chat, voyante, players, n_nuits, dico_players):
    if voyante != None and voyante.state == True:
        await context.send("C'est au tour de la **Voyante**.")
        bdc = await menu(vovo_chat, players,"Choisissez la personne dont vous voulez révéler le rôle.", dico_players, voyante)
        await vovo_chat.edit(locked=False)
        vovo_timer = Timer(vovo_chat, 20, n_nuits)
        await vovo_timer.role_timer()
        await bdc.delete()

async def action_lg(context, lg_chat, lgs, players, n_nuits, dico_players):
    counter = len(lgs)
    for lg in lgs:
        if lg.state == False:
            counter -= 1
    if counter >= 1:
        await context.send("C'est au tour des **Loups-Garous**.")
        kill_menu = await menu(lg_chat, players,"Choisissez la personne que vous voulez dévorer.", dico_players, lgs[0])
        await lg_chat.edit(locked=False)
        lg_timer = Timer(lg_chat, 30, n_nuits)
        await lg_timer.role_timer()
        await kill_menu.delete()
        del kill_menu

async def action_sorciere(context, soso_chat, sorciere, players, n_nuits, potion_vie, potion_mort, cible_lg, cupidon, dico_players):
    pdv_menu = None
    cible_soso = None
    pdm_menu = None
    if sorciere == None:
        return cible_lg, potion_vie, potion_mort, cible_soso
    elif sorciere.state == False:
        return cible_lg, potion_vie, potion_mort, cible_soso
    elif potion_vie is True or potion_mort is True:
        await context.send("C'est au tour de la **Sorcière**.")
        soso_timer = Timer(soso_chat, 30, n_nuits)
        if cible_lg is None:
            await soso_chat.send(f"Aucune personne n'a été ciblé ce soir.")
        else:
            if potion_vie == False:  # potion vie deja utilisé
                pdv_menu = None
                await soso_chat.send(content=f"Vous avez déjà utilisé la potion de vie.")

            else: #potion vie pas encore utilisé
                pdv_menu = await button(context=soso_chat, potion_vie=potion_vie, cible_lg=cible_lg)

        if potion_mort == False: #potion mort deja utilisé
            pdm_menu = None
            await soso_chat.send(content=f"Vous avez déjà utilisé la potion de mort.")
        else: #potion mort pas encore utilisé
            pdm_menu = await menu(soso_chat, players, "Selectionnez la personne qui recevra la potion de mort.", dico_players, sorciere) #potion de mort

        await soso_chat.edit(locked=False)
        await soso_timer.role_timer()
        cible_soso = await cible_vote(soso_chat, players, sorciere, potion_mort, cupidon, dico_players, n_nuits)
        if pdm_menu is not None:
            del pdm_menu
        if pdv_menu is not None:
            cible_lg, potion_vie = pdv_menu.cible_lg, pdv_menu.potion_vie
            del pdv_menu
        if cible_soso is not None:
            return cible_lg, potion_vie, False, cible_soso
    return cible_lg, potion_vie, potion_mort, cible_soso

async def action_chasseur(context, players, dico_players, chasseur, n_nuits, potion_mort, cupidon):
    chasseur_timer = Timer(context, 10, n_nuits)
    balle = await menu(context, players, "Selectionnez la personne sur laquelle vous allez tirer dessus.", dico_players,
                          chasseur)  # Sélection de qui va mourir du chasseur
    await chasseur_timer.role_timer()
    cible_chasseur = await cible_vote(context, players, chasseur, potion_mort, cupidon, dico_players, n_nuits)
    del balle
    if cible_chasseur is not None:
        await death(context, players, cible_chasseur, "Chasseur", dico_players, n_nuits, potion_mort, cupidon)
    else:
        await context.send(content=f"Le chasseur a décidé de ne pas tirer")
    return cible_chasseur

async def dico_joueurs(context, players):
    dico = {}
    for player in players:
        dico[player.name] = player
    return dico



async def annonce_role(context, players: list):
    """Envoie le role de chacun des! joueurs par dm et ajoute les joueurs au thread privé"""

    for player in players: #parcours de tous les joueurs en jeu
        await context.send(f"<@{player.id}>") #mentions des joueurs dans le thread privé "Le Village"
        user = await bot.fetch_user(player.id) #trouve l'utilisateur discord du joueur a partir de l'ID
        channel = await user.create_dm() #créé le dm avec le joueur
        with open(f"./roles_desc/{player.role}_desc.txt", "r") as f:
            desc = f.read()
        f.close()
        await channel.send(f"{desc}", file=discord.File(f'./cartes/{player.role}.png')) #envoie du role au joueur par dm

def maxi_vote(players: list):
    """trouve le maximum d'un vote"""
    maxi = 0
    for player in players:
        if player.nvote > maxi:
            maxi = player.nvote
    return maxi


async def cible_vote(context, players, voteur, potion_mort, cupidon, dico_players, n_nuits):
    """renvoie la cible du vote"""
    cible = []
    maxi = maxi_vote(players)
    counter = 0
    for i in range(len(players)):
        if players[i].nvote == maxi:
            counter += 1
            cible.append(players[i])
    morts = []

    if maxi == 0: #aucun vote
        if voteur == None:
            await context.send(content=f"Le **Village** a décidé de ne pas voter.")
            return []
        elif type(voteur) == list:  # LG
            await context.send(content=f"Vous avez décidé de ne rien faire cette nuit.")
        elif voteur.role == "Voyante" and voteur.state == True:
            await context.send(content=f"Vous avez décidé de ne rien faire cette nuit.")
            return None
        elif voteur.role == "Sorciere" and potion_mort == True and voteur.state == True:
            await context.send(content=f"Vous avez décidé conserver votre potion de mort pour une prochaine nuit.")


    elif counter == 1: #1 personne voté en majorité
        #VOTE VILLAGE
        if voteur == None:
            l_mort = await death(context, players, cible[0], 'Village', dico_players, n_nuits, potion_mort, cupidon, maxi)
            return l_mort
        #VOTE LG
        elif type(voteur) == list:
            await context.send(content=f"La personne qui va mourir est **{cible[0].name}**.")
            return cible[0]
        #VOTE VOVO
        elif voteur.role == "Voyante":
            return cible[0]
        #VOTE SOSO
        elif voteur.role == "Sorciere":
            await context.send(content=f"La personne qui recevra la potion de mort est **{cible[0].name}**.")
            return cible[0]
        #VOTE CHASSEUR
        elif voteur.role == "Chasseur":
            return cible[0]

    #EGALITE
    else:
        if voteur == None:
            await context.send(content=f"Personne n'est mort. (Égalité)")
            return []
        elif type(voteur) == list:  # LG
            tie_breaker = random.choice(cible)
            await context.send(content=f"La personne qui va mourir est **{tie_breaker.name}**.")
            return tie_breaker

async def call(role_chat, player):
    if player == None:
        pass
    elif type(player) == list:
        # if lgs == []:
        #     raise ValueError("Pas de lgs dans la partie")
        for lg in player:
            await role_chat.send(f"<@{lg.id}>")
    else:
        await role_chat.send(f"<@{player.id}>")

async def lock(role_chats):
    for role_chat in role_chats:
        await role_chat.edit(locked=True)


async def ping_couple(couple_chat, select_love):
    if select_love is not None:
        select_love.couple[0].amour = select_love.couple[1]
        select_love.couple[0].camp = 'Couple'
        select_love.couple[1].amour = select_love.couple[0]
        select_love.couple[1].camp = 'Couple'
        for i in range(2):
            await call(couple_chat, select_love.couple[i])
        await couple_chat.send(content=f"Le **Cupidon**, vous a choisi pour son **Couple**, vous avez accès à ce chat privé afin de communiquer jour comme nuit.")


async def annonce_jour(context, dico_players, n_nuits, potion_mort, cible_lg=None, cible_soso=None, players=[], cupidon=None):
    morts = []
    if cible_lg is not None and cible_lg in players: #cible lg existe
        print(f"<@{cible_lg.name}> s'est fait(e) dévoré(e) par les Loups cette nuit.")
        l_morts = await death(context, players, cible_lg, 'Loup Garou', dico_players, n_nuits, potion_mort, cupidon)
        morts += l_morts
    if cible_soso is not None and cible_soso in players: #cible soso existe
        print(f"<@{cible_soso.name}> s'est fait tué(e) par la sorcière cette nuit.")
        l_morts = await death(context, players, cible_soso, 'Sorciere', dico_players, n_nuits, potion_mort, cupidon)
        morts += l_morts
    if morts == []: #cas où personne n'a été ciblé
        await context.send(content=f"Personne n'est mort cette nuit.")
    return morts

async def death(context, players, mort, tueur, dico_players, n_nuits, potion_mort, cupidon, nbr_votes=None):
    players.remove(mort)
    l_morts = [mort]
    if tueur == 'Sorciere' or tueur == 'Loup Garou':
        await context.send(content=f"<@{mort.id}> est mort(e) cette nuit.")
    elif tueur == 'Village':
        await context.send(content=f"<@{mort.id}> a été tué par le village. ({nbr_votes} vote(s))")
    elif tueur == "Chasseur":
        await context.send(content=f"<@{mort.id}> s'est fait tiré dessus par le chasseur")
    elif tueur == "Couple":
        await context.send(content=f"<@{mort.id}> est mort par chagrin d'amour.")
    await asyncio.sleep(2)
    await context.send(content=f"Il était **{mort.role}**")
    if mort.amour is not None and mort.amour in players:
        l_morts.append(mort.amour)
        await death(context, players, mort.amour, "Couple", dico_players, n_nuits, potion_mort, cupidon, nbr_votes)
        cupidon.camp = "Village"
    if mort.role == 'Chasseur':
        await context.edit(locked=False)
        cible_chasseur = await action_chasseur(context, players, dico_players, mort, n_nuits, potion_mort, cupidon)
        if cible_chasseur is not None:
            l_morts.append(cible_chasseur)
        await context.edit(locked=True)
    with open("compos/role_mort_id.txt", "r") as f:
        guild = context.guild
        role_mort_id = int(f.read())
        role_mort = guild.get_role(role_mort_id)
        try:
            await mort.member.edit(mute=True)
        except discord.errors.HTTPException:
            print('User not in vc')
        await mort.member.edit(roles=mort.member.roles + [role_mort])
    mort.state = False
    return l_morts


async def nom_façade(context, lgs):
    noms = ["Loup-Garou Gentil",
            "Loup-Garou Bourré",
            "Loup-Garou Affamé",
            'Loup-Garou Romantique',
            "Loup-Garoux",
            "Loup-Garou Féministe",
            "Loup-Garou Ikea",
            "Loup-Garou Séducteur",
            "Loup-Garou Dealer",
            "Loup-Garou Platiste",
            "Loup-Garou Sismographe",
            "Loup-Garou Hypopotomonstrosesquipédaliophobique",
            "Loup-Garou Albinos"
            ]
    for lg in lgs:
        nom = random.choice(noms)
        noms.remove(nom)
        dico_lg[lg.name] = nom

@commands.has_permissions(administrator=True)
@bot.command()
async def start(context):
    """Starts the game"""
    dico_lg = {}
    morts = []
    await clear_threads(context)
    vc = await vc_members(context) #liste des personnes présentes dans le voc
    n_players = len(vc) #nombre de joueurs dans la partie

    main_thread = await thread(context, "Le Village") #creation du thread privé et renvoie son id
    cupi_thread = await thread(context, "Cupidon")  # créé thread privé du cupidon
    vovo_thread = await thread(context, "Voyante")  # créé thread privé de la voyante
    lg_thread = await thread(context, "Loups-Garous")  # créé thread privé des loups
    pf_thread = await thread(context, "Petite Fille") #créé thread privé de la PF
    soso_thread = await thread(context, "Sorcière")  # créé thread privé de la sorciere
    couple_thread = await thread(context, "Couple")
    channel_mort = await create_channel_mort(context.channel, "Morts")
    channel = context
    context = bot.get_channel(main_thread) #changement de context: channel -> thread
    players = await role_assign(context, n_players, vc) #liste de joueur de type class Player
    dico_players = await dico_joueurs(context, players)

    cupidon, voyante, lgs, pf, sorciere = None, None, [], None, None
    for player in players:
        if player.role == "Loup Garou":
            lgs.append(player)
        elif player.role == "Cupidon":
            cupidon = player
        elif player.role == "Voyante":
            voyante = player
        elif player.role == "Petite Fille":
            pf = player
        elif player.role == "Sorciere":
            sorciere = player
        elif player.role == "Chasseur":
            chasseur = player

    roles_nuit = [cupidon, voyante, lgs, pf, sorciere]
    await annonce_role(context, players) #annonce des roles par dm

    await nom_façade(context, lgs)

    cupi_chat = bot.get_channel(cupi_thread) #thread id (cupidon) -> channel (cupidon)
    vovo_chat = bot.get_channel(vovo_thread) #thread id (voyante) -> channel (voyante)
    lg_chat = bot.get_channel(lg_thread) #thread id (loups) -> channel (loups)
    pf_chat = bot.get_channel(pf_thread) #thread id (PF) -> channel (PF)
    soso_chat = bot.get_channel(soso_thread) #thread id (sorciere) -> channel (sorciere)
    couple_chat = bot.get_channel(couple_thread)
    role_chats = [cupi_chat, vovo_chat, lg_chat, pf_chat, soso_chat]
    await lock(role_chats) #lock tous les chats sauf le main

    for i in range(len(role_chats)):
        await call(role_chats[i], roles_nuit[i]) #ajoute les roles a leur thread

    #DEPART DU JEU
    start = Timer(context, 5, None)
    await start.start_timer() # compteur de départ

    n_jours = 1
    potion_vie = True
    potion_mort = True
    temps_discussion = 15
    temps_nuit(cupidon, voyante, lgs, sorciere, n_jours)
    await asyncio.sleep(1)


    #PREMIER ROUND

    #DISCUSSION
    tdiscu = Timer(context, temps_discussion-10, n_jours)
    await tdiscu.discussion()
    await asyncio.sleep(1)

    #NUIT
    await mute_all(context, players)
    await context.send(content=f"# Nuit {n_jours}")
    await context.edit(locked=True) #lock le chat du village pour la nuit
    await asyncio.sleep(1)
    await context.typing() #event qui va déclencher le timer de nuit
    await asyncio.sleep(1)

    #CUPIDON
    select_love = await action_cupidon(context, cupi_chat, cupidon, players, dico_players, n_jours, potion_mort, dico_players) #renvoie l'objet de la class selectviewcupi
    await cupi_chat.edit(locked=True)
    await ping_couple(couple_chat, select_love)


    #VOYANTE
    await action_voyante(context, vovo_chat, voyante, players, n_jours, dico_players) #vovo choisis cible
    await vovo_chat.edit(locked=True) #lock le chat de la vovo
    if voyante is not None:
        cible_vovo = await cible_vote(vovo_chat, players, voyante, potion_mort, cupidon, dico_players, n_jours)
        if cible_vovo is not None:
            await vovo_chat.send(f"La personne que vous avez espionné est **{cible_vovo.role}**.")#cible est récup ici (type class player)
            await reset_votes(context, players) #vote reset

    #LOUP GAROU
    await action_lg(context, lg_chat, lgs, players, n_jours, dico_players) #lgs choisissent cible
    await lg_chat.edit(locked=True) #lock chat des lgs
    cible_lg = await cible_vote(lg_chat, players, lgs, potion_mort, cupidon, dico_players, n_jours)
    await reset_votes(context, players) #vote reset

    #SORCIERE
    if sorciere is not None:
        cible_lg, potion_vie, potion_mort, cible_soso = await action_sorciere(context=context, soso_chat=soso_chat, sorciere=sorciere, players=players, n_nuits=n_jours,
                                         potion_vie=potion_vie, potion_mort=potion_mort, cible_lg=cible_lg, cupidon=cupidon, dico_players=dico_players)
    await soso_chat.edit(locked=True)
    await reset_votes(context, players)

    #ANNONCE DES MORTS ET DIVERS
    await unmute_all(context, players)
    await asyncio.sleep(1)
    morts += await annonce_jour(context, dico_players, n_jours, potion_mort, cible_lg, cible_soso, players, cupidon)

    n_jours += 1
    game_state = await is_game_over(context, players)  # True = le jeu est en cours, False = le jeu est fini

    #BOUCLE DE JEU
    while game_state == True:
        temps_nuit(cupidon, voyante, lgs, sorciere, n_jours)
        #DISCUSSION
        await context.edit(locked=False)
        tdiscu = Timer(context, temps_discussion-10, n_jours)
        await tdiscu.discussion()
        await asyncio.sleep(1)

        #VOTE
        vote = Timer(context, 60, n_jours=0)
        await vote.vote_village(players=players, dico_players=dico_players) #commence le vote du village
        await asyncio.sleep(1)
        morts += await cible_vote(context, players, None, potion_mort, cupidon, dico_players, n_jours) #annonce les résultats et la mort de la personne voté
        await reset_votes(context, players) #remet les compteurs de vote a 0

        #GAME OVER?
        game_state = await is_game_over(context, players)
        #YES
        if game_state == False:
            break

        await asyncio.sleep(5)

        #NUIT
        await mute_all(context, players)
        await context.send(content=f"# Nuit {n_jours}")
        await context.edit(locked=True) #lock le chat du village pour la nuit
        await asyncio.sleep(1)
        await context.typing() #event qui va déclencher le timer de nuit
        await asyncio.sleep(1)

        #VOYANTE
        await action_voyante(context, vovo_chat, voyante, players, n_jours, dico_players) #vovo choisis cible
        await vovo_chat.edit(locked=True) #lock le chat de la vovo
        if voyante is not None:
            cible_vovo = await cible_vote(vovo_chat, players, voyante, potion_mort, cupidon, dico_players, n_jours)
            if cible_vovo is not None:
                await vovo_chat.send(f"La personne que vous avez espionné est **{cible_vovo.role}**.")#cible est récup ici (type class player)
                await reset_votes(context, players) #vote reset


        #LOUP GAROU
        await action_lg(context, lg_chat, lgs, players, n_jours, dico_players) #lgs choisissent cible
        await lg_chat.edit(locked=True) #lock chat des lgs
        cible_lg = await cible_vote(lg_chat, players, lgs, potion_mort, cupidon, dico_players, n_jours)
        await reset_votes(context, players) #vote reset

        #SORCIERE
        if sorciere is not None:
            cible_lg, potion_vie, potion_mort, cible_soso = await action_sorciere(context=context, soso_chat=soso_chat, sorciere=sorciere, players=players, n_nuits=n_jours,
                                           potion_vie=potion_vie, potion_mort=potion_mort, cible_lg=cible_lg, cupidon=cupidon, dico_players=dico_players)
        await soso_chat.edit(locked=True)
        await reset_votes(context, players)

        #ANNONCE DES MORTS
        await unmute_all(context, players)
        await asyncio.sleep(1)
        morts += await annonce_jour(context, dico_players, n_jours, potion_mort, cible_lg, cible_soso, players, cupidon)


        game_state = await is_game_over(context, players)
        n_jours += 1
    await unmute_all(context, morts)
    with open("compos/role_mort_id.txt", "r") as f:
        guild = context.guild
        role_mort = guild.get_role(int(f.read()))

        for mort in morts:
            for role in mort.member.roles:
                if role == role_mort:
                    await mort.member.remove_roles(role_mort)

        f.close()
    await context.send(content="Vous pouvez relancer une partie ou éteindre le bot.")
    print("Program has ended without errors.")


async def is_game_over(context, players):
    if players == []:
        await context.send('Bah ils sont cons vos potes ils se sont crosskill ces abrutis')
        return False
    first_team = players[0].camp
    for joueur in players:
        if joueur.camp != first_team:
            return True
    if first_team == 'Couple':
        await context.send(f"# Victoire du **Couple** !")
        await context.send("## Gagnants:")
        for gagnant in players:
            await context.send(f"<@{gagnant.id}>")
    elif first_team == 'Village':
        await context.send(f"# Victoire du **Village** !")
        await context.send("## Gagnants:")
        for gagnant in players:
            await context.send(f"<@{gagnant.id}>")
    elif first_team == 'LG':
        await context.send(f"# Victoire des **Loups-Garous** !")
        await context.send("## Gagnants:")
        for gagnant in players:
            await context.send(f"<@{gagnant.id}>")
    return False


@bot.event
async def on_typing(context, user, when): #night timer
    bot_id = 1359518949041115320
    if user.id == bot_id:
        with open("counter.txt", "r") as f:
            counter = f.read()
            temps = int(counter) * 32
            f.close()
        night = Timer(context, temps)
        await night.night_timer()

@commands.has_permissions(administrator=True)
@bot.command(aliases=["ct", "cleart", "clear"])
async def clear_threads(context):
    print("Clearing Threads...")
    l_threads = context.channel.threads
    pos = context.channel.category.position
    channel_morts = None

    for loop in range(len(context.channel.category.channels)-pos):
        n = pos + loop
        channel_morts = context.channel.category.channels[n]
        if channel_morts.name == 'morts':
            await channel_morts.delete()
            break

    threads = {}
    with open("counter.txt", "w") as f: #compteur nuit
        f.write("0")
        f.close()
    for thread in l_threads:
        try:
            print(f"Deleting thread: {thread.name} (ID: {thread.id})")
            await thread.delete()
        except discord.errors.NotFound:
            print(f"Thread {thread.id} not found, skipping...")
        except discord.errors.Forbidden:
            print(f"Permission denied for thread {thread.id}, skipping...")
        except Exception as e:
            print(f"Error deleting thread {thread.id}: {e}")

    print("Cleared.")



async def mute_all(context, players: list):
    for player in players:
        try:
            await player.member.edit(mute=True)
        except discord.errors.HTTPException:
            print('User not in vc')


async def unmute_all(context, players: list):
    for player in players:
        try:
            await player.member.edit(mute=False)
        except discord.errors.HTTPException:
            print('User not in vc')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Vérifiez si le message est une commande
    if message.content.startswith('!start') or message.content.startswith('!ct') or message.content.startswith('!compo'):
        await bot.process_commands(message)
        return

    # Vérifiez si le message provient du thread "lg"
    if message.channel.id == threads['loups-garous_thread']:
        # Retransmettre le message dans le thread "pf"
        pf_channel = bot.get_channel(threads.get('petite fille_thread'))
        if pf_channel:
            await pf_channel.send(f"**{dico_lg[message.author.name]}**: \n {message.content} \n ‎ ")


@bot.event
async def on_ready():
    print(f'Connecté en tant que {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'{len(synced)} commande(s) synchronisée(s)')
    except Exception as e:
        print(e)
def main():
    bot.run(token=token)

if __name__ == '__main__':
    main()
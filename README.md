# NSI-Project-2025-LG-Discord-Bot

Pour pouvoir utiliser le bot suivez ces étapes :

Commencez par décompresser le fichier puis ouvrez le fichier main et insérez votre token (que vous pouvez récupérer en créant une application sur https://discord.com/developers/applications). 

Le programme require l'installation de discord.py :
```
pip install discord.py
```
Vous n'avez plus qu'à lancer le fichier main et le bot sera fonctionnel. 

**À noter que le bot a besoin des permissions d'administrateur pour fonctionner.**

## Commandes:

Préfix par défaut: "**!**"

*start* - Permet de lancer la partie. Les joueurs seront ceux qui se trouveront dans le même channel vocal que celui qui à effectuer la commande.

**ATTENTION!** Effectuer cette commande effacera tous les threads attachés au channel textuel dans lequel la commande a été envoyé. 

**ATTENTION!** Si vous avez un channel nommé "Morts" il risque également d'être supprimé.

*composition* {**int**} - Permet d'afficher la composition des rôles pour un nombre de joueurs donnés. (6 < int < 12)
(alias: *compo*)

*composition* {**int** /AND/ class type: **list**} - Permet à l'utilisateur de changer la composition des rôles pour un nombre de joueurs donnés. (6 < int < 12)
(alias: *compo*)


## Roles:
Simple Villageois,
Voyante,
Sorciere,
Cupidon,
Petite Fille,
Chasseur,
Loup Garou.

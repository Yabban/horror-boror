# Journal de bord — Survie jusqu'à l'aube

## Description du projet

Jeu de survie horror 2D en vue de dessus.  
Le joueur doit survivre jusqu'à l'aube (6h00 in-game) dans un bâtiment obscur, en gérant sa santé, sa paranoïa, l'électricité et des ennemis de plus en plus agressifs.

## Technologies

- Langage : Python 3.x
- Bibliothèque principale : Pygame
- Génération procédurale du monde

## Architecture

| Fichier | Rôle |
|---------|------|
| `main.py` | Boucle principale, gestion des événements |
| `config.py` | Constantes et paramètres |
| `entities.py` | Joueur, Monstre (avec sprites), Objet, Boite, Brique |
| `world.py` | Génération procédurale (murs, objets, boîtes, monstres) |
| `game_state.py` | État global du jeu |
| `game_logic.py` | Logique : déplacements, quêtes, agressivité |
| `renderer.py` | Rendu graphique (mode normal / obscurité) |
| `ui.py` | HUD, overlay inventaire, écrans fin |

## Fonctionnalités implémentées

- [x] Système d'obscurité avec panneaux électriques (2 à activer)
- [x] Batterie à changer toutes les 1h30 in-game
- [x] Inventaire (max 4 objets) — touche R
- [x] Boîtes mystères (1/3 objet / 1/3 vide / 1/3 Boogeyman +50 paranoïa)
- [x] Brique lançable (clic gauche) — stun 30s sur les ennemis
- [x] Monstres avec sprites dessinés programmatiquement
- [x] Agressivité des monstres croissante avec le temps
- [x] Positions des objets/monstres garanties hors des murs

## Utilisation de l'IA

Ce projet a utilisé une IA générative (Claude) pour :
- Refactorisation de l'architecture en modules
- Aide à la conception du système de sprites

Toutes les décisions de conception et l'intégration finale ont été réalisées par l'équipe.

---
*Compléter ce fichier avec vos Flash-CR de fin de séance.*

"""Configuration du jeu — constantes et parametres"""

import os

LARGEUR  = 1200
HAUTEUR  = 800
FPS      = 60

NOIR        = (0,   0,   0)
BLANC       = (255, 255, 255)
ROUGE       = (220,  30,  30)
VERT        = ( 30, 200,  80)
BLEU        = ( 30, 100, 220)
JAUNE       = (255, 220,  30)
GRIS        = ( 50,  50,  50)
GRIS_CLAIR  = (160, 160, 160)
GRIS_FONCE  = ( 25,  25,  25)
ORANGE      = (255, 140,   0)
VIOLET      = (160,  30, 210)
MARRON      = (110,  60,  20)
BLEU_NUIT   = ( 10,  10,  30)
SANG        = (140,   0,   0)

JOUEUR_LARGEUR   = 32
JOUEUR_HAUTEUR   = 32
JOUEUR_VITESSE   = 4
JOUEUR_SANTE_MAX = 100
PARANOIA_TICK    = 0.008

MONSTRE_LARGEUR      = 40
MONSTRE_HAUTEUR      = 40
MONSTRE_VITESSE_BASE = 1.5
MONSTRE_VITESSE_MAX  = 5.0
MONSTRE_DEGATS_BASE  = 0.6
MONSTRE_DEGATS_MAX   = 3.0

LARGEUR_MONDE  = 2400
HAUTEUR_MONDE  = 2400

HEURE_DEBUT        = 0
HEURE_VICTOIRE_MIN = 6

# Durees frames reelles (60fps)
DUREE_BATTERIE      = 5400    # ~1h30 in-game
DUREE_STUN_BRIQUE   = 1800    # 30s
TALISMAN_DUREE      = 10800   # 3h in-game
INVENTAIRE_MAX      = 4
DUREE_MAX_NOIR      = 30 * 60 * 60  # 30 minutes reelles a 60fps = 108000 frames

NB_NUITS        = 3
TACHES_PAR_NUIT = 3

DOSSIER_SOURCES = os.path.dirname(os.path.abspath(__file__))
DOSSIER_ASSETS  = os.path.join(DOSSIER_SOURCES, "assets")
FICHIER_SAVE    = os.path.join(DOSSIER_SOURCES, "savegame.json")

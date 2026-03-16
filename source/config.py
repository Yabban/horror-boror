# Projet : Survie jusqu'à l'aube
# Auteurs : [Prénoms Noms]
"""Configuration du jeu - Constantes et paramètres"""

import os

LARGEUR = 1200
HAUTEUR = 800
FPS = 60

NOIR        = (0, 0, 0)
BLANC       = (255, 255, 255)
ROUGE       = (255, 0, 0)
VERT        = (0, 255, 0)
BLEU        = (0, 100, 255)
JAUNE       = (255, 255, 0)
GRIS        = (50, 50, 50)
GRIS_CLAIR  = (150, 150, 150)
ORANGE      = (255, 165, 0)
VIOLET      = (200, 0, 255)
MARRON      = (139, 90, 43)

JOUEUR_LARGEUR  = 30
JOUEUR_HAUTEUR  = 30
JOUEUR_VITESSE  = 4
JOUEUR_SANTE_MAX = 100
JOUEUR_PARANOIA_AUGMENTATION = 0.01

MONSTRE_LARGEUR       = 35
MONSTRE_HAUTEUR       = 35
MONSTRE_VITESSE_BASE  = 2
MONSTRE_VITESSE_MAX   = 6
MONSTRE_DEGATS_BASE   = 1
MONSTRE_DEGATS_MAX    = 4

LARGEUR_MONDE = 2000
HAUTEUR_MONDE = 2000

HEURE_DEBUT        = 0
HEURE_VICTOIRE_MIN = 6
HEURE_VICTOIRE_MAX = 22

DUREE_BATTERIE    = int(1.5 * 3600)
DUREE_STUN_BRIQUE = 30 * 60
INVENTAIRE_MAX    = 4

DOSSIER_SOURCES = os.path.dirname(os.path.abspath(__file__))
DOSSIER_ASSETS  = os.sep.join([DOSSIER_SOURCES, "assets"])

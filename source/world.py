# Projet : Survie jusqu'à l'aube
# Auteurs : [Prénoms Noms]
"""Génération procédurale du monde"""

import pygame
import random
from config import *
from entities import Objet, Monstre, Boite


class WorldGenerator:
    def __init__(self, largeur, hauteur):
        self.largeur = largeur
        self.hauteur = hauteur
        self._murs   = None

    def generer_murs(self):
        murs = [
            pygame.Rect(0, 0, self.largeur, 20),
            pygame.Rect(0, self.hauteur-20, self.largeur, 20),
            pygame.Rect(0, 0, 20, self.hauteur),
            pygame.Rect(self.largeur-20, 0, 20, self.hauteur),
        ]
        for _ in range(30):
            x = random.randint(100, self.largeur-200)
            y = random.randint(100, self.hauteur-200)
            murs.append(pygame.Rect(x, y,
                                    random.randint(50, 200),
                                    random.randint(50, 200)))
        self._murs = murs
        return murs

    def _position_libre(self, marge=60):
        for _ in range(200):
            x = random.randint(60, self.largeur-60)
            y = random.randint(60, self.hauteur-60)
            zone = pygame.Rect(x-marge//2, y-marge//2, marge, marge)
            if self._murs and any(zone.colliderect(m) for m in self._murs):
                continue
            return x, y
        return 80, 80   # fallback

    def generer_objets(self):
        types = {
            "Clé": 1, "Médicament": 2, "Fusible": 1,
            "Talisman": 1, "Batterie": 4, "Brique": 5,
        }
        objets = []
        for t, n in types.items():
            for _ in range(n):
                x, y = self._position_libre(40)
                objets.append(Objet(x, y, t))
        return objets

    def generer_boites(self):
        """30 boîtes mystères réparties dans le monde"""
        boites = []
        for _ in range(30):
            x, y = self._position_libre(30)
            boites.append(Boite(x, y))
        return boites

    def generer_monstres(self):
        monstres = []
        for _ in range(2):
            x, y = self._position_libre(100)
            monstres.append(Monstre(x, y, "traqueur"))
        for _ in range(5):
            x, y = self._position_libre(80)
            monstres.append(Monstre(x, y, "errant"))
        return monstres

    def generer_panneaux(self):
        panneaux = []
        for i in range(2):
            x, y = self._position_libre(80)
            panneaux.append({'x': x, 'y': y, 'largeur': 40,
                              'hauteur': 60, 'actif': False,
                              'nom': f'Panneau {i+1}'})
        return panneaux


class Camera:
    def __init__(self, largeur_monde, hauteur_monde):
        self.x = self.y = 0
        self.largeur_monde = largeur_monde
        self.hauteur_monde = hauteur_monde

    def centrer_sur(self, joueur):
        self.x = max(0, min(joueur.x - LARGEUR//2, self.largeur_monde - LARGEUR))
        self.y = max(0, min(joueur.y - HAUTEUR//2, self.hauteur_monde - HAUTEUR))

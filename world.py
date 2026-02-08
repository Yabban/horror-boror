"""Module de génération et gestion du monde du jeu"""

import pygame
import random
from config import *
from entities import Objet, Monstre


class WorldGenerator:
    """Générateur de monde procédural"""
    
    def __init__(self, largeur, hauteur):
        self.largeur = largeur
        self.hauteur = hauteur
    
    def generer_murs(self):
        """Génère les murs du niveau"""
        murs = []
        
        # Bordures
        murs.extend(self._generer_bordures())
        
        # Murs intérieurs aléatoires
        for _ in range(30):
            x = random.randint(100, self.largeur - 200)
            y = random.randint(100, self.hauteur - 200)
            largeur = random.randint(50, 200)
            hauteur = random.randint(50, 200)
            murs.append(pygame.Rect(x, y, largeur, hauteur))
        
        return murs
    
    def _generer_bordures(self):
        """Génère les bordures du monde"""
        return [
            pygame.Rect(0, 0, self.largeur, 20),  # Haut
            pygame.Rect(0, self.hauteur - 20, self.largeur, 20),  # Bas
            pygame.Rect(0, 0, 20, self.hauteur),  # Gauche
            pygame.Rect(self.largeur - 20, 0, 20, self.hauteur)  # Droite
        ]
    
    def generer_objets(self):
        """Génère les objets dans le monde"""
        objets = []
        
        types_objets = ["Lampe", "Clé", "Médicament", "Fusible", "Talisman"]
        
        for type_objet in types_objets:
            nombre = 3 if type_objet == "Lampe" else 2 if type_objet == "Médicament" else 1
            
            for _ in range(nombre):
                x = random.randint(100, self.largeur - 100)
                y = random.randint(100, self.hauteur - 100)
                objets.append(Objet(x, y, type_objet))
        
        return objets
    
    def generer_monstres(self):
        """Génère les monstres dans le monde"""
        monstres = []
        
        # Traqueurs
        for _ in range(2):
            x = random.randint(300, self.largeur - 300)
            y = random.randint(300, self.hauteur - 300)
            monstres.append(Monstre(x, y, "traqueur"))
        
        # Errants
        for _ in range(5):
            x = random.randint(200, self.largeur - 200)
            y = random.randint(200, self.hauteur - 200)
            monstres.append(Monstre(x, y, "errant"))
        
        return monstres


class Camera:
    """Gestion de la caméra du jeu"""
    
    def __init__(self, largeur_monde, hauteur_monde):
        self.x = 0
        self.y = 0
        self.largeur_monde = largeur_monde
        self.hauteur_monde = hauteur_monde
    
    def centrer_sur(self, joueur):
        """Centre la caméra sur le joueur"""
        self.x = joueur.x - LARGEUR // 2
        self.y = joueur.y - HAUTEUR // 2
        
        # Limites de la caméra
        self.x = max(0, min(self.x, self.largeur_monde - LARGEUR))
        self.y = max(0, min(self.y, self.hauteur_monde - HAUTEUR))

"""Module de rendu graphique"""

import pygame
from config import *


class Renderer:
    """Gère le rendu graphique du jeu"""
    
    def __init__(self, screen):
        self.screen = screen
    
    def dessiner_monde(self, game_state):
        """Dessine le monde du jeu"""
        # Fond
        self.screen.fill(NOIR)
        
        # Sol
        pygame.draw.rect(self.screen, GRIS, (0, 0, LARGEUR, HAUTEUR))
        
        # Murs
        self._dessiner_murs(game_state.murs, game_state.camera)
        
        # Objets
        self._dessiner_objets(game_state.objets, game_state.camera)
        
        # Monstres
        self._dessiner_monstres(game_state.monstres, game_state.camera)
        
        # Joueur
        game_state.joueur.dessiner(self.screen, game_state.camera.x, game_state.camera.y)
    
    def _dessiner_murs(self, murs, camera):
        """Dessine tous les murs"""
        for mur in murs:
            pygame.draw.rect(self.screen, GRIS_CLAIR, 
                           (mur.x - camera.x, mur.y - camera.y, 
                            mur.width, mur.height))
    
    def _dessiner_objets(self, objets, camera):
        """Dessine tous les objets"""
        for objet in objets:
            objet.dessiner(self.screen, camera.x, camera.y)
    
    def _dessiner_monstres(self, monstres, camera):
        """Dessine tous les monstres"""
        for monstre in monstres:
            monstre.dessiner(self.screen, camera.x, camera.y)

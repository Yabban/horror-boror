"""
Jeu d'horreur/survie - Version modulaire
Survivez jusqu'à l'aube en collectant des objets et en évitant les monstres
"""

import pygame
from config import *
from game_state import GameState
from game_logic import GameLogic
from renderer import Renderer
from ui import UI


class Jeu:
    """Classe principale du jeu"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((LARGEUR, HAUTEUR))
        pygame.display.set_caption("Survie jusqu'à l'aube")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Composants du jeu
        self.state = GameState()
        self.logic = GameLogic(self.state)
        self.renderer = Renderer(self.screen)
        self.ui = UI()
    
    def gerer_evenements(self):
        """Gère tous les événements du jeu"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    self.logic.gerer_evenement_ramassage()
    
    def mettre_a_jour(self):
        """Met à jour l'état du jeu"""
        # Entrées
        self.logic.gerer_entrees()
        
        # Monstres
        self.logic.mettre_a_jour_monstres()
        
        # Paranoïa
        self.logic.mettre_a_jour_paranoia()
        
        # Conditions de fin
        condition, raison = self.logic.verifier_conditions_fin()
        if condition == "game_over":
            self.game_over(raison)
        elif condition == "victoire":
            self.victoire()
        
        # Temps et caméra
        self.state.incrementer_temps()
        self.state.mettre_a_jour_messages()
        self.state.mettre_a_jour_camera()
    
    def dessiner(self):
        """Dessine tout le jeu"""
        # Monde
        self.renderer.dessiner_monde(self.state)
        
        # Interface
        self.ui.dessiner_interface(
            self.screen,
            self.state.joueur,
            self.state.temps,
            self.state.quetes,
            self.state.quete_actuelle,
            self.state.messages
        )
        
        pygame.display.flip()
    
    def game_over(self, raison):
        """Gère la fin de partie (défaite)"""
        self.ui.afficher_game_over(self.screen, raison)
        self.running = False
    
    def victoire(self):
        """Gère la fin de partie (victoire)"""
        self.ui.afficher_victoire(self.screen)
        self.running = False
    
    def run(self):
        """Boucle principale du jeu"""
        while self.running:
            self.clock.tick(FPS)
            self.gerer_evenements()
            self.mettre_a_jour()
            self.dessiner()
        
        pygame.quit()


if __name__ == "__main__":
    jeu = Jeu()
    jeu.run()

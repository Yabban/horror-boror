"""Module de logique du jeu"""

import pygame
from config import *


class GameLogic:
    """Gère la logique du jeu"""
    
    def __init__(self, game_state):
        self.state = game_state
    
    def gerer_entrees(self):
        """Gère les entrées clavier pour le déplacement"""
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        
        if keys[pygame.K_z] or keys[pygame.K_w]:
            dy = -1
        if keys[pygame.K_s]:
            dy = 1
        if keys[pygame.K_q] or keys[pygame.K_a]:
            dx = -1
        if keys[pygame.K_d]:
            dx = 1
        
        if dx != 0 or dy != 0:
            self.state.joueur.deplacer(dx, dy, self.state.murs)
    
    def gerer_evenement_ramassage(self):
        """Gère le ramassage d'objets"""
        for objet in self.state.objets:
            if not objet.ramasse and objet.collision_joueur(self.state.joueur):
                self.state.joueur.ramasser_objet(objet.type)
                objet.ramasse = True
                self.state.ajouter_message(f"Vous avez ramassé: {objet.type}")
                self._verifier_quetes(objet.type)
                return True
        return False
    
    def _verifier_quetes(self, type_objet):
        """Vérifie et complète les quêtes"""
        if type_objet == "Clé" and not self.state.quetes[0].complete:
            self.state.quetes[0].complete = True
            self.state.ajouter_message("QUÊTE COMPLÉTÉE: Trouver la sortie!")
            self.state.quete_actuelle = 1
        
        elif type_objet == "Fusible" and not self.state.quetes[1].complete:
            self.state.quetes[1].complete = True
            self.state.ajouter_message("QUÊTE COMPLÉTÉE: Électricité rétablie!")
            self.state.ajouter_message("⚠️ ATTENTION! Les monstres se réveillent...")
            self.state.activer_monstres()
            self.state.quete_actuelle = 2
    
    def mettre_a_jour_monstres(self):
        """Met à jour le comportement des monstres"""
        if not self.state.monstres_actives:
            return
        
        for monstre in self.state.monstres:
            monstre.deplacer(self.state.joueur.x, self.state.joueur.y, self.state.murs)
            
            if monstre.collision_joueur(self.state.joueur):
                self.state.joueur.sante -= 1
                self.state.joueur.paranoia += 0.5
    
    def mettre_a_jour_paranoia(self):
        """Met à jour le niveau de paranoïa du joueur"""
        # Augmentation naturelle
        self.state.joueur.paranoia += JOUEUR_PARANOIA_AUGMENTATION
        
        # Réduction avec talisman
        if "Talisman" in self.state.joueur.inventaire:
            self.state.joueur.paranoia = max(0, self.state.joueur.paranoia - 0.02)
    
    def verifier_conditions_fin(self):
        """Vérifie les conditions de fin de partie"""
        # Game Over - Mort
        if self.state.joueur.sante <= 0:
            return "game_over", "Vous êtes mort..."
        
        # Game Over - Folie
        if self.state.joueur.paranoia >= 100:
            return "game_over", "La folie vous a consumé..."
        
        # Victoire
        heures, _ = self.state.obtenir_heure_actuelle()
        if (HEURE_VICTOIRE_MIN <= heures < HEURE_VICTOIRE_MAX and 
            self.state.quetes[1].complete):
            return "victoire", None
        
        return None, None

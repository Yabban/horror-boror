"""Module de l'interface utilisateur"""

import pygame
from config import *


class UI:
    """Gestionnaire de l'interface utilisateur"""
    
    def __init__(self):
        self.font_petite = pygame.font.Font(None, 24)
        self.font_moyenne = pygame.font.Font(None, 36)
        self.font_grande = pygame.font.Font(None, 72)
    
    def dessiner_interface(self, screen, joueur, temps, quetes, quete_actuelle, messages):
        """Dessine l'interface complète"""
        self._dessiner_fond_interface(screen)
        self._dessiner_barres_stats(screen, joueur)
        self._dessiner_temps(screen, temps)
        self._dessiner_inventaire(screen, joueur)
        self._dessiner_quete_actuelle(screen, quetes, quete_actuelle)
        self._dessiner_controles(screen)
        self._dessiner_messages(screen, messages)
    
    def _dessiner_fond_interface(self, screen):
        """Dessine le fond semi-transparent de l'interface"""
        interface_bg = pygame.Surface((LARGEUR, 150))
        interface_bg.set_alpha(200)
        interface_bg.fill(NOIR)
        screen.blit(interface_bg, (0, HAUTEUR - 150))
    
    def _dessiner_barres_stats(self, screen, joueur):
        """Dessine les barres de santé et paranoïa"""
        # Santé
        couleur_sante = self._obtenir_couleur_sante(joueur.sante)
        pygame.draw.rect(screen, GRIS, (20, HAUTEUR - 130, 200, 25))
        pygame.draw.rect(screen, couleur_sante, 
                        (20, HAUTEUR - 130, joueur.sante * 2, 25))
        texte_sante = self.font_petite.render(f"Santé: {int(joueur.sante)}%", True, BLANC)
        screen.blit(texte_sante, (25, HAUTEUR - 127))
        
        # Paranoïa
        couleur_paranoia = self._obtenir_couleur_paranoia(joueur.paranoia)
        pygame.draw.rect(screen, GRIS, (20, HAUTEUR - 100, 200, 25))
        pygame.draw.rect(screen, couleur_paranoia, 
                        (20, HAUTEUR - 100, min(200, joueur.paranoia * 2), 25))
        texte_paranoia = self.font_petite.render(f"Paranoïa: {int(joueur.paranoia)}%", True, BLANC)
        screen.blit(texte_paranoia, (25, HAUTEUR - 97))
    
    def _obtenir_couleur_sante(self, sante):
        """Retourne la couleur appropriée pour la barre de santé"""
        if sante > 50:
            return VERT
        elif sante > 25:
            return ORANGE
        return ROUGE
    
    def _obtenir_couleur_paranoia(self, paranoia):
        """Retourne la couleur appropriée pour la barre de paranoïa"""
        if paranoia < 40:
            return VERT
        elif paranoia < 70:
            return ORANGE
        return ROUGE
    
    def _dessiner_temps(self, screen, temps):
        """Dessine l'heure actuelle"""
        heures = (temps // 3600) % 24
        minutes = (temps // 60) % 60
        texte_temps = self.font_moyenne.render(f"Heure: {heures:02d}:{minutes:02d}", True, JAUNE)
        screen.blit(texte_temps, (20, HAUTEUR - 65))
    
    def _dessiner_inventaire(self, screen, joueur):
        """Dessine l'inventaire du joueur"""
        texte_inv = self.font_petite.render("Inventaire:", True, BLANC)
        screen.blit(texte_inv, (250, HAUTEUR - 130))
        for i, objet in enumerate(joueur.inventaire):
            texte_objet = self.font_petite.render(f"• {objet}", True, JAUNE)
            screen.blit(texte_objet, (250, HAUTEUR - 105 + i * 20))
    
    def _dessiner_quete_actuelle(self, screen, quetes, quete_actuelle):
        """Dessine la quête en cours"""
        if quete_actuelle < len(quetes):
            quete = quetes[quete_actuelle]
            texte_quete = self.font_petite.render(f"Quête: {quete.nom}", True, ORANGE)
            screen.blit(texte_quete, (550, HAUTEUR - 130))
            texte_desc = self.font_petite.render(quete.description, True, BLANC)
            screen.blit(texte_desc, (550, HAUTEUR - 105))
    
    def _dessiner_controles(self, screen):
        """Dessine les contrôles du jeu"""
        texte_ctrl = self.font_petite.render("ZQSD: Bouger | E: Ramasser", True, GRIS_CLAIR)
        screen.blit(texte_ctrl, (LARGEUR - 300, HAUTEUR - 30))
    
    def _dessiner_messages(self, screen, messages):
        """Dessine les messages temporaires"""
        for i, (texte, duree) in enumerate(messages[-3:]):
            alpha = min(255, duree * 2)
            surface_msg = self.font_moyenne.render(texte, True, JAUNE)
            surface_msg.set_alpha(alpha)
            screen.blit(surface_msg, (LARGEUR // 2 - 300, 50 + i * 40))
    
    def afficher_game_over(self, screen, raison):
        """Affiche l'écran de game over"""
        screen.fill(NOIR)
        texte_go = self.font_grande.render("GAME OVER", True, ROUGE)
        texte_raison = self.font_moyenne.render(raison, True, BLANC)
        screen.blit(texte_go, (LARGEUR // 2 - 150, HAUTEUR // 2 - 50))
        screen.blit(texte_raison, (LARGEUR // 2 - 200, HAUTEUR // 2 + 20))
        pygame.display.flip()
        pygame.time.wait(5000)
    
    def afficher_victoire(self, screen):
        """Affiche l'écran de victoire"""
        screen.fill(NOIR)
        texte_vic = self.font_grande.render("VICTOIRE !", True, VERT)
        texte_msg = self.font_moyenne.render("Vous avez survécu jusqu'à l'aube !", True, BLANC)
        screen.blit(texte_vic, (LARGEUR // 2 - 150, HAUTEUR // 2 - 50))
        screen.blit(texte_msg, (LARGEUR // 2 - 250, HAUTEUR // 2 + 20))
        pygame.display.flip()
        pygame.time.wait(5000)

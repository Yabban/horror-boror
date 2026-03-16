# Projet : Survie jusqu'à l'aube
# Auteurs : [Prénoms Noms]
"""Logique du jeu : déplacements, quêtes, monstres, paranoïa"""

import pygame
from config import *


class GameLogic:
    def __init__(self, game_state):
        self.state = game_state

    def gerer_entrees(self):
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_z] or keys[pygame.K_w]: dy = -1
        if keys[pygame.K_s]: dy = 1
        if keys[pygame.K_q] or keys[pygame.K_a]: dx = -1
        if keys[pygame.K_d]: dx = 1
        if dx or dy:
            self.state.joueur.deplacer(dx, dy, self.state.murs)

    def gerer_ramassage_objet(self):
        """Ramasse un objet au sol (touche E)"""
        j = self.state.joueur
        total = sum(i['quantite'] for i in j.inventaire)
        if total >= INVENTAIRE_MAX:
            self.state.ajouter_message("Inventaire plein ! (max 4)", 120)
            return False
        for obj in self.state.objets:
            if not obj.ramasse and obj.collision_joueur(j):
                if j.ramasser_objet(obj.type):
                    obj.ramasse = True
                    self.state.ajouter_message(f"Ramassé : {obj.type}")
                    self._verifier_quetes(obj.type)
                    return True
                else:
                    self.state.ajouter_message("Inventaire plein !", 120)
        return False

    def gerer_ouverture_boite(self):
        """Ouvre une boîte mystère (touche E)"""
        j = self.state.joueur
        for boite in self.state.boites:
            if not boite.ouverte and boite.collision_joueur(j):
                boite.ouvrir(j, self.state.ajouter_message)
                return True
        return False

    def _verifier_quetes(self, type_objet):
        if type_objet == "Clé" and not self.state.quetes[0].complete:
            self.state.quetes[0].complete = True
            self.state.ajouter_message("QUÊTE COMPLÉTÉE : Trouver la sortie !")
            self.state.quete_actuelle = 1
        elif type_objet == "Fusible" and not self.state.quetes[1].complete:
            self.state.quetes[1].complete = True
            self.state.ajouter_message("QUÊTE COMPLÉTÉE : Électricité rétablie !")
            self.state.ajouter_message("⚠️ Les monstres se réveillent...")
            self.state.activer_monstres()
            self.state.quete_actuelle = 2

    def mettre_a_jour_monstres(self):
        if not self.state.monstres_actives:
            return
        j = self.state.joueur
        for m in self.state.monstres:
            # Mise à jour de l'agressivité selon le temps
            m.mettre_a_jour_agressivite(self.state.temps)
            m.deplacer(j.x, j.y, self.state.murs)
            if m.collision_joueur(j):
                j.sante    -= m.degats
                j.paranoia = min(100, j.paranoia + m.degats * 0.5)

    def mettre_a_jour_paranoia(self):
        j = self.state.joueur
        j.paranoia += JOUEUR_PARANOIA_AUGMENTATION
        if j.a_objet("Talisman"):
            j.paranoia = max(0, j.paranoia - 0.02)

    def verifier_conditions_fin(self):
        j = self.state.joueur
        if j.sante <= 0:
            return "game_over", "Vous êtes mort..."
        if j.paranoia >= 100:
            return "game_over", "La folie vous a consumé..."
        h, _ = self.state.obtenir_heure_actuelle()
        if HEURE_VICTOIRE_MIN <= h < HEURE_VICTOIRE_MAX and self.state.quetes[1].complete:
            return "victoire", None
        return None, None

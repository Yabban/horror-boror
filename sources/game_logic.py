# Projet : Survie jusqu'à l'aube
# Auteurs : [Prénoms Noms]
"""Logique du jeu : déplacements, quêtes, monstres, paranoïa, tâches"""

import pygame
from config import *


class GameLogic:
    def __init__(self, state):
        self.state = state

    def gerer_entrees(self):
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_z] or keys[pygame.K_w] or keys[pygame.K_UP]:    dy = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:                       dy =  1
        if keys[pygame.K_q] or keys[pygame.K_a] or keys[pygame.K_LEFT]:   dx = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:                      dx =  1
        if dx or dy:
            self.state.joueur.deplacer(dx, dy, self.state.murs)

    def tenir_e_tache(self):
        """Appelé chaque frame si E est maintenu -> avance la tache proche."""
        j = self.state.joueur
        for tache in self.state.taches:
            if not tache.complete and tache.collision_joueur(j):
                if tache.interagir():
                    self.state.taches_completees += 1
                    self.state.ajouter_message(f"Tâche accomplie : {tache.nom} !", 200)
                    j.paranoia = max(0, j.paranoia - 10)
                else:
                    self.state.ajouter_message(
                        f"{tache.description} ({int(tache.pct * 100)}%)", 4)
                return True
        return False

    def gerer_ramassage_objet(self):
        j = self.state.joueur
        if sum(i['quantite'] for i in j.inventaire) >= INVENTAIRE_MAX:
            self.state.ajouter_message("Inventaire plein ! (max 4)", 120)
            return False
        for obj in self.state.objets:
            if not obj.ramasse and obj.collision_joueur(j):
                if j.ramasser_objet(obj.type):
                    obj.ramasse = True
                    self.state.ajouter_message(f"Ramasse : {obj.type}")
                    self._verifier_quetes(obj.type)
                    return True
        return False

    def gerer_ouverture_boite(self):
        j = self.state.joueur
        for boite in self.state.boites:
            if not boite.ouverte and boite.collision_joueur(j):
                boite.ouvrir(j, self.state.ajouter_message)
                return True
        return False

    def utiliser_depuis_inventaire(self, type_objet):
        j = self.state.joueur
        if j.utiliser_objet(type_objet):
            self.state.ajouter_message(f"Utilise : {type_objet}", 120)
            self._verifier_quetes(type_objet)

    def jeter_depuis_inventaire(self, type_objet):
        if self.state.joueur.jeter_objet(type_objet):
            self.state.ajouter_message(f"Jete : {type_objet}", 100)

    def _verifier_quetes(self, type_objet):
        s = self.state
        if type_objet == "Cle" and not s.quetes[0].complete:
            s.quetes[0].complete = True
            s.ajouter_message("QUETE : Sortie trouvee !")
            s.quete_actuelle = 1
        elif type_objet == "Fusible" and not s.quetes[1].complete:
            s.quetes[1].complete = True
            s.ajouter_message("QUETE : Electricite retablie !")
            s.ajouter_message("Les monstres se reveillent...")
            s.activer_monstres()
            s.quete_actuelle = 2

    def mettre_a_jour_monstres(self):
        j = self.state.joueur
        for m in self.state.monstres:
            m.mettre_a_jour_agressivite(self.state.temps)
            m.deplacer(j.x, j.y, self.state.murs)
            # Degats seulement si monstres actives (apres fusible)
            if self.state.monstres_actives and m.collision_joueur(j):
                j.sante    -= m.degats
                j.paranoia  = min(100, j.paranoia + m.degats * 0.4)

    def mettre_a_jour_paranoia(self):
        j = self.state.joueur
        j.paranoia = min(100, j.paranoia + PARANOIA_TICK)
        if j.talisman_timer > 0:
            j.paranoia = max(0, j.paranoia - 0.015)
        event = j.mettre_a_jour_talisman()
        if event == "talisman_casse":
            self.state.ajouter_message("Votre Talisman s'est brise !", 200)

    def verifier_conditions_fin(self):
        j = self.state.joueur
        if j.sante <= 0:
            return "game_over", "Vous etes mort..."
        if j.paranoia >= 100:
            return "game_over", "La folie vous a consume..."
        h, _ = self.state.obtenir_heure()
        if h >= HEURE_VICTOIRE_MIN and self.state.quetes[1].complete:
            return "victoire", None
        return None, None

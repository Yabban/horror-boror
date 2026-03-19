"""Point d'entrée principal du jeu"""

import pygame
from config import *
from game_state import GameState
from game_logic import GameLogic
from renderer import Renderer
from ui import UI
from entities import Brique


class Jeu:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((LARGEUR, HAUTEUR))
        pygame.display.set_caption("Survie jusqu'à l'aube")
        self.clock   = pygame.time.Clock()
        self.running = True

        self.state    = GameState()
        self.logic    = GameLogic(self.state)
        self.renderer = Renderer(self.screen)
        self.ui       = UI()

        # Électricité
        self.lumiere_eteinte  = True
        self.panneaux_actives = 0
        self.timer_batterie   = DUREE_BATTERIE
        self.batterie_morte   = False

        # Briques en vol
        self.briques = []

        # Inventaire overlay
        self.inventaire_ouvert = False

        self.state.ajouter_message(
            "Il fait noir ! Trouvez les 2 panneaux électriques !", 300)
        self.state.ajouter_message(
            "Ouvrez les boîtes (E) — attention aux surprises !", 300)

    # ── ÉVÉNEMENTS ──────────────────────────────────────────
    def gerer_evenements(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.running = False

            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_r:
                    self.inventaire_ouvert = not self.inventaire_ouvert

                elif ev.key == pygame.K_e and not self.inventaire_ouvert:
                    # Priorité : panneau → batterie morte → boîte → objet
                    if not self._activer_panneau():
                        if self.batterie_morte:
                            self._remplacer_batterie()
                        elif not self.logic.gerer_ouverture_boite():
                            self.logic.gerer_ramassage_objet()

            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                self._lancer_brique(ev.pos)

    def _activer_panneau(self):
        j = self.state.joueur
        for p in self.state.panneaux_electricite:
            if p['actif']: continue
            dx, dy = p['x']-j.x, p['y']-j.y
            if (dx**2+dy**2)**0.5 < 65:
                p['actif'] = True
                self.panneaux_actives += 1
                if self.panneaux_actives >= 2:
                    self.lumiere_eteinte = False
                    self.batterie_morte  = False
                    self.timer_batterie  = DUREE_BATTERIE
                    self.state.ajouter_message("Lumières revenues ! Batterie : 100%", 200)
                else:
                    self.state.ajouter_message(
                        f"Panneau activé ! ({self.panneaux_actives}/2)", 120)
                return True
        return False

    def _remplacer_batterie(self):
        j = self.state.joueur
        if j.a_objet("Batterie"):
            j.utiliser_objet("Batterie")
            self.batterie_morte  = False
            self.lumiere_eteinte = False
            self.timer_batterie  = DUREE_BATTERIE
            self.state.ajouter_message("Batterie remplacée ! Lumières revenues !", 200)
        else:
            self.state.ajouter_message(
                "Batterie morte ! Trouvez une Batterie de rechange !", 150)

    def _lancer_brique(self, pos_ecran):
        j = self.state.joueur
        if not j.a_objet("Brique"): return
        cam = self.state.camera
        brique = Brique(j.x + j.largeur//2, j.y + j.hauteur//2,
                        pos_ecran[0] + cam.x, pos_ecran[1] + cam.y)
        self.briques.append(brique)
        j.utiliser_objet("Brique")
        self.state.ajouter_message("Brique lancée !", 60)

    # ── MISE À JOUR ─────────────────────────────────────────
    def mettre_a_jour(self):
        self.logic.gerer_entrees()
        self.logic.mettre_a_jour_monstres()
        self.logic.mettre_a_jour_paranoia()
        self._update_briques()
        self._update_batterie()

        c, r = self.logic.verifier_conditions_fin()
        if c == "game_over": self.game_over(r)
        elif c == "victoire": self.victoire()

        self.state.incrementer_temps()
        self.state.mettre_a_jour_messages()
        self.state.mettre_a_jour_camera()

    def _update_briques(self):
        for b in self.briques:
            b.update(self.state.murs)
            for m in self.state.monstres:
                if b.collision_monstre(m):
                    m.stunner()
                    b.active = False
                    self.state.ajouter_message("Monstre étourdi 30s !", 120)
        self.briques = [b for b in self.briques if b.active]

    def _update_batterie(self):
        if not self.lumiere_eteinte and not self.batterie_morte:
            self.timer_batterie -= 1
            if self.timer_batterie <= 0:
                self.batterie_morte  = True
                self.lumiere_eteinte = True
                self.state.ajouter_message(
                    "⚠️ BATTERIE MORTE ! Trouvez une Batterie puis appuyez E !", 300)

    # ── DESSIN ──────────────────────────────────────────────
    def dessiner(self):
        if self.lumiere_eteinte:
            self.renderer.dessiner_monde_obscur(self.state)
        else:
            self.renderer.dessiner_monde(self.state)

        self.renderer.dessiner_panneaux(
            self.screen, self.state.panneaux_electricite,
            self.state.camera, self.state.joueur)

        for b in self.briques:
            b.dessiner(self.screen, self.state.camera.x, self.state.camera.y)

        self.ui.dessiner_hud(
            self.screen, self.state.joueur, self.state.temps,
            self.state.quetes, self.state.quete_actuelle, self.state.messages,
            self.panneaux_actives, self.timer_batterie, self.batterie_morte)

        if self.inventaire_ouvert:
            self.ui.dessiner_inventaire_overlay(self.screen, self.state.joueur)

        pygame.display.flip()

    # ── FIN DE PARTIE ───────────────────────────────────────
    def game_over(self, raison):
        self.ui.afficher_game_over(self.screen, raison)
        self.running = False

    def victoire(self):
        self.ui.afficher_victoire(self.screen)
        self.running = False

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.gerer_evenements()
            self.mettre_a_jour()
            self.dessiner()
        pygame.quit()


if __name__ == "__main__":
    jeu = Jeu()
    jeu.run()

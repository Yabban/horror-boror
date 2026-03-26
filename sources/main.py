"""Point d'entree principal du jeu"""

import pygame
import sys
import json
import os
import math
from config import *
from game_state import GameState
from game_logic import GameLogic
from renderer import Renderer
from ui import UI
from entities import Brique
from intro_scene import run_intro


class Jeu:
    def __init__(self, nuit=1, charger_save=False):
        self.screen   = pygame.display.get_surface()
        self.clock    = pygame.time.Clock()
        self.running  = True
        self.resultat = None

        self.state    = GameState(nuit=nuit, charger_save=charger_save)
        self.logic    = GameLogic(self.state)
        self.renderer = Renderer(self.screen)
        self.ui       = UI()

        self.lumiere_eteinte  = True
        self.panneaux_actives = 0
        self.timer_batterie   = DUREE_BATTERIE
        self.batterie_morte   = False

        # Timer dans le noir (mort si trop long)
        self.timer_noir = 0

        self.briques = []
        self.inventaire_ouvert = False
        self._e_maintenu = False

        self.state.ajouter_message("Il fait noir ! Trouvez les 2 panneaux !", 300)
        self.state.ajouter_message("Ouvrez les boites (E) — surprises garanties !", 300)

    # ── ÉVÉNEMENTS ──────────────────────────────────────────

    def gerer_evenements(self):
        mouse_pos = pygame.mouse.get_pos()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.resultat = "quitter"
                self.running  = False
                return

            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    if self.state.sauvegarder():
                        self.state.ajouter_message("Partie sauvegardee !", 150)
                    self.resultat = "menu"
                    self.running  = False
                    return

                elif ev.key == pygame.K_r:
                    self.inventaire_ouvert = not self.inventaire_ouvert

                elif ev.key == pygame.K_e and not self.inventaire_ouvert:
                    self._e_maintenu = True
                    # Priorite : panneau -> puis selon etat
                    if not self._activer_panneau():
                        # BUG FIX : si batterie morte ET panneau actif on tente de la remplacer
                        # sinon on essaie quand meme boite/objet
                        if self.batterie_morte and self.panneaux_actives >= 2:
                            if not self._remplacer_batterie_si_possible():
                                # Pas de batterie -> essaie quand meme ramassage
                                if not self.logic.gerer_ouverture_boite():
                                    self.logic.gerer_ramassage_objet()
                        else:
                            if not self.logic.gerer_ouverture_boite():
                                self.logic.gerer_ramassage_objet()

            elif ev.type == pygame.KEYUP:
                if ev.key == pygame.K_e:
                    self._e_maintenu = False

            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if self.inventaire_ouvert:
                    action, type_obj = self.ui.traiter_clic_inventaire(
                        self.state.joueur, mouse_pos)
                    if action == "utiliser":
                        self.logic.utiliser_depuis_inventaire(type_obj)
                    elif action == "jeter":
                        self.logic.jeter_depuis_inventaire(type_obj)
                else:
                    self._lancer_brique(mouse_pos)

    def _activer_panneau(self):
        j = self.state.joueur
        for p in self.state.panneaux:
            if p['actif']:
                continue
            if math.hypot(p['x'] - j.x, p['y'] - j.y) < 70:
                p['actif'] = True
                self.panneaux_actives += 1
                if self.panneaux_actives >= 2:
                    self.lumiere_eteinte = False
                    self.batterie_morte  = False
                    self.timer_batterie  = DUREE_BATTERIE
                    self.timer_noir      = 0
                    self.state.ajouter_message("Lumieres revenues ! Batterie : 100%", 200)
                else:
                    self.state.ajouter_message(
                        "Panneau active ! (%d/2)" % self.panneaux_actives, 120)
                return True
        return False

    def _remplacer_batterie_si_possible(self):
        """Remplace la batterie si le joueur en a une. Retourne True si fait."""
        j = self.state.joueur
        if j.a_objet("Batterie"):
            j.jeter_objet("Batterie")
            self.batterie_morte  = False
            self.lumiere_eteinte = False
            self.timer_batterie  = DUREE_BATTERIE
            self.timer_noir      = 0
            self.state.ajouter_message("Batterie remplacee ! Lumieres revenues !", 200)
            return True
        else:
            self.state.ajouter_message("Batterie morte ! Trouvez une Batterie puis E !", 150)
            return False

    def _lancer_brique(self, pos_ecran):
        j = self.state.joueur
        if not j.a_objet("Brique"):
            return
        cam = self.state.camera
        b = Brique(j.x + j.largeur // 2, j.y + j.hauteur // 2,
                   pos_ecran[0] + cam.x, pos_ecran[1] + cam.y)
        self.briques.append(b)
        j.jeter_objet("Brique")
        self.state.ajouter_message("Brique lancee !", 60)

    # ── MISE À JOUR ─────────────────────────────────────────

    def mettre_a_jour(self):
        self.logic.gerer_entrees()
        self.logic.mettre_a_jour_monstres()
        self.logic.mettre_a_jour_paranoia()

        if self._e_maintenu and not self.inventaire_ouvert:
            self.logic.tenir_e_tache()

        self._update_briques()
        self._update_batterie()
        self._update_timer_noir()

        c, r = self.logic.verifier_conditions_fin()
        if c == "game_over":
            self._game_over(r)
        elif c == "victoire":
            self._victoire_nuit()

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
                    self.state.ajouter_message("Monstre etourdi 30s !", 120)
        self.briques = [b for b in self.briques if b.active]

    def _update_batterie(self):
        if not self.lumiere_eteinte and not self.batterie_morte:
            self.timer_batterie -= 1
            if self.timer_batterie <= 0:
                self.batterie_morte  = True
                self.lumiere_eteinte = True
                self.timer_noir      = 0  # repart depuis 0
                self.state.ajouter_message("BATTERIE MORTE ! Trouvez une Batterie puis E !", 300)

    def _update_timer_noir(self):
        """Si dans le noir, incremente le timer. Mort a DUREE_MAX_NOIR."""
        if self.lumiere_eteinte:
            self.timer_noir += 1
            if self.timer_noir >= DUREE_MAX_NOIR:
                # Mort par le noir
                self.ui.animation_mort_noir(self.screen, self.clock)
                self.resultat = "game_over"
                self.running  = False
        else:
            # Lumiere allumee : reset progressif
            if self.timer_noir > 0:
                self.timer_noir = max(0, self.timer_noir - 3)

    # ── DESSIN ──────────────────────────────────────────────

    def dessiner(self):
        if self.lumiere_eteinte:
            self.renderer.dessiner_monde_obscur(self.state)
        else:
            self.renderer.dessiner_monde(self.state)

        self.renderer.dessiner_panneaux(
            self.screen, self.state.panneaux,
            self.state.camera, self.state.joueur)

        for b in self.briques:
            b.dessiner(self.screen, self.state.camera.x, self.state.camera.y)

        self.ui.dessiner_hud(
            self.screen, self.state.joueur, self.state.temps,
            self.state.quetes, self.state.quete_actuelle, self.state.messages,
            self.panneaux_actives, self.timer_batterie, self.batterie_morte,
            self.state.taches_completees, self.state.nuit,
            timer_noir=self.timer_noir)

        if self.inventaire_ouvert:
            self.ui.dessiner_inventaire_overlay(
                self.screen, self.state.joueur, pygame.mouse.get_pos())

        pygame.display.flip()

    # ── FIN / TRANSITION ────────────────────────────────────

    def _game_over(self, raison):
        if "folie" in raison or "paranoia" in raison.lower() or "consume" in raison.lower():
            self.ui.animation_mort_paranoia(self.screen, self.clock)
        elif "mort" in raison.lower() or "devore" in raison.lower():
            self.ui.animation_jumpscare_monstre(self.screen, self.clock)
        else:
            self.ui.afficher_game_over(self.screen, raison)
        self.resultat = "game_over"
        self.running  = False

    def _victoire_nuit(self):
        nuit = self.state.nuit
        if nuit >= NB_NUITS:
            self.ui.afficher_victoire(self.screen)
            self.resultat = "victoire_finale"
            self.running  = False
        else:
            self.ui.afficher_transition_nuit(self.screen, nuit)
            self.resultat = "nuit_suivante"
            self.running  = False

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.gerer_evenements()
            if self.running:
                self.mettre_a_jour()
                self.dessiner()
        return self.resultat


# ════════════════════════════════════════════════════════════
#  BOUCLE PRINCIPALE
# ════════════════════════════════════════════════════════════

def lancer_jeu():
    pygame.init()
    screen = pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption("Survie jusqu'a l'aube")
    clock  = pygame.time.Clock()
    ui     = UI()

    while True:
        action_menu = None
        while action_menu is None:
            clock.tick(FPS)
            mouse_pos = pygame.mouse.get_pos()
            ui.dessiner_menu(screen, GameState.save_exists(), mouse_pos)
            pygame.display.flip()
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    action_menu = ui.clic_menu(GameState.save_exists(), mouse_pos)
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

        if action_menu == "quitter":
            pygame.quit(); sys.exit()

        charger = (action_menu == "continuer")
        nuit_depart = 1

        if charger and GameState.save_exists():
            try:
                with open(FICHIER_SAVE) as f:
                    data = json.load(f)
                nuit_depart = data.get("nuit", 1)
            except Exception:
                pass
        else:
            if not run_intro(screen, clock):
                continue

        nuit = nuit_depart
        charger_save = charger
        resultat = None
        while nuit <= NB_NUITS:
            jeu = Jeu(nuit=nuit, charger_save=charger_save)
            resultat = jeu.run()
            charger_save = False

            if resultat in ("game_over", "quitter", "menu"):
                break
            elif resultat == "nuit_suivante":
                nuit += 1
            elif resultat == "victoire_finale":
                break

        if resultat in ("victoire_finale", "game_over"):
            try:
                os.remove(FICHIER_SAVE)
            except Exception:
                pass


if __name__ == "__main__":
    lancer_jeu()

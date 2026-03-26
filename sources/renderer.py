"""Rendu graphique du jeu"""

import pygame
import math
from config import *


class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self._sol   = None   # surface sol pré-générée

    def _get_sol(self, lm, hm):
        """Génère une surface de sol avec texture grossière (une seule fois)."""
        if self._sol is not None:
            return self._sol
        import random
        sol = pygame.Surface((lm, hm))
        sol.fill((30, 28, 22))
        rng = random.Random(42)
        for _ in range(4000):
            x = rng.randint(0, lm - 1)
            y = rng.randint(0, hm - 1)
            g = rng.randint(20, 45)
            pygame.draw.rect(sol, (g, g - 5, g - 10), (x, y, 4, 4))
        self._sol = sol
        return self._sol

    # ── Mode normal ──────────────────────────────────────────

    def dessiner_monde(self, gs):
        # Sol
        sol = self._get_sol(LARGEUR_MONDE, HAUTEUR_MONDE)
        self.screen.blit(sol, (-gs.camera.x, -gs.camera.y))

        self._decors(gs)
        self._murs(gs.murs, gs.camera)
        self._boites(gs.boites, gs.camera)
        self._objets(gs.objets, gs.camera)
        self._taches(gs.taches, gs.camera)
        self._monstres(gs.monstres, gs.camera)
        gs.joueur.dessiner(self.screen, gs.camera.x, gs.camera.y)

    # ── Mode obscurité ───────────────────────────────────────

    def dessiner_monde_obscur(self, gs):
        self.screen.fill((5, 5, 10))

        # Murs à peine visibles
        for mur in gs.murs:
            pygame.draw.rect(self.screen, (18, 15, 12),
                             (mur.x - gs.camera.x, mur.y - gs.camera.y,
                              mur.width, mur.height))

        self._decors(gs)
        self._boites(gs.boites, gs.camera)
        self._objets(gs.objets, gs.camera)
        self._taches(gs.taches, gs.camera)

        # Monstres : aura rouge proche
        for m in gs.monstres:
            if m.actif:
                d = math.hypot(m.x - gs.joueur.x, m.y - gs.joueur.y)
                if d < 150:
                    pygame.draw.circle(self.screen, (60, 0, 0),
                                       (int(m.x - gs.camera.x + 20),
                                        int(m.y - gs.camera.y + 20)), 30)
                    m.dessiner(self.screen, gs.camera.x, gs.camera.y)

        gs.joueur.dessiner(self.screen, gs.camera.x, gs.camera.y)

        # Halo joueur
        surf = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 220))
        rayon = 90 - int(gs.joueur.paranoia * 0.4)   # rétrécit avec la paranoïa
        rayon = max(30, rayon)
        jx = int(gs.joueur.x - gs.camera.x + JOUEUR_LARGEUR // 2)
        jy = int(gs.joueur.y - gs.camera.y + JOUEUR_HAUTEUR // 2)
        pygame.draw.circle(surf, (0, 0, 0, 0), (jx, jy), rayon)
        # Dégradé : cercle intermédiaire semi-transparent
        pygame.draw.circle(surf, (0, 0, 0, 100), (jx, jy), rayon + 30)
        self.screen.blit(surf, (0, 0))

    # ── Helpers ──────────────────────────────────────────────

    def _decors(self, gs):
        for d in gs.decors:
            d.dessiner(self.screen, gs.camera.x, gs.camera.y)

    def _murs(self, murs, cam):
        for m in murs:
            sx, sy = m.x - cam.x, m.y - cam.y
            if sx > LARGEUR or sy > HAUTEUR or sx + m.width < 0 or sy + m.height < 0:
                continue
            pygame.draw.rect(self.screen, (55, 45, 35), (sx, sy, m.width, m.height))
            pygame.draw.rect(self.screen, (80, 65, 50), (sx, sy, m.width, m.height), 1)

    def _objets(self, objets, cam):
        for o in objets:
            o.dessiner(self.screen, cam.x, cam.y)

    def _boites(self, boites, cam):
        for b in boites:
            b.dessiner(self.screen, cam.x, cam.y)

    def _monstres(self, monstres, cam):
        for m in monstres:
            m.dessiner(self.screen, cam.x, cam.y)

    def _taches(self, taches, cam):
        for t in taches:
            t.dessiner(self.screen, cam.x, cam.y)

    # ── Panneaux électriques ─────────────────────────────────

    def dessiner_panneaux(self, screen, panneaux, camera, joueur):
        font = pygame.font.Font(None, 22)
        for p in panneaux:
            xe = p['x'] - camera.x
            ye = p['y'] - camera.y
            if xe < -60 or xe > LARGEUR + 20 or ye < -60 or ye > HAUTEUR + 20:
                continue
            couleur = (20, 160, 20) if p['actif'] else (60, 55, 50)
            pygame.draw.rect(screen, couleur, (xe, ye, p['largeur'], p['hauteur']),
                             border_radius=3)
            pygame.draw.rect(screen, GRIS_CLAIR, (xe, ye, p['largeur'], p['hauteur']), 2,
                             border_radius=3)
            led = VERT if p['actif'] else ROUGE
            pygame.draw.circle(screen, led, (int(xe + 20), int(ye + 12)), 6)
            # Étiquette
            if not p['actif']:
                d = math.hypot(p['x'] - joueur.x, p['y'] - joueur.y)
                if d < 80:
                    t = font.render("E : Activer panneau", True, BLANC)
                    screen.blit(t, t.get_rect(center=(LARGEUR // 2, 58)))

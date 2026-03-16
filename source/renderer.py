# Projet : Survie jusqu'à l'aube
# Auteurs : [Prénoms Noms]
"""Rendu graphique du jeu"""

import pygame
from config import *


class Renderer:
    def __init__(self, screen):
        self.screen = screen

    # ── MODE NORMAL ──────────────────────────────────────────
    def dessiner_monde(self, gs):
        self.screen.fill(NOIR)
        pygame.draw.rect(self.screen, GRIS, (0, 0, LARGEUR, HAUTEUR))
        self._murs(gs.murs, gs.camera)
        self._boites(gs.boites, gs.camera)
        self._objets(gs.objets, gs.camera)
        self._monstres(gs.monstres, gs.camera)
        gs.joueur.dessiner(self.screen, gs.camera.x, gs.camera.y)

    # ── MODE OBSCURITÉ ───────────────────────────────────────
    def dessiner_monde_obscur(self, gs):
        self.screen.fill((0, 0, 0))
        for mur in gs.murs:
            pygame.draw.rect(self.screen, (25, 25, 25),
                             (mur.x - gs.camera.x, mur.y - gs.camera.y,
                              mur.width, mur.height))
        # Boîtes visibles (légèrement)
        self._boites(gs.boites, gs.camera)
        # Objets visibles
        self._objets(gs.objets, gs.camera)
        # Monstres : aura si proches
        for m in gs.monstres:
            if m.actif:
                d = ((m.x-gs.joueur.x)**2 + (m.y-gs.joueur.y)**2)**0.5
                if d < 130:
                    pygame.draw.circle(self.screen, (50, 0, 0),
                                       (int(m.x-gs.camera.x), int(m.y-gs.camera.y)), 32)
        gs.joueur.dessiner(self.screen, gs.camera.x, gs.camera.y)
        # Halo de lumière autour du joueur
        surf = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 215))
        jx = int(gs.joueur.x - gs.camera.x + 15)
        jy = int(gs.joueur.y - gs.camera.y + 15)
        pygame.draw.circle(surf, (0, 0, 0, 0), (jx, jy), 85)
        self.screen.blit(surf, (0, 0))

    # ── HELPERS ──────────────────────────────────────────────
    def _murs(self, murs, cam):
        for m in murs:
            pygame.draw.rect(self.screen, GRIS_CLAIR,
                             (m.x-cam.x, m.y-cam.y, m.width, m.height))

    def _objets(self, objets, cam):
        for o in objets:
            o.dessiner(self.screen, cam.x, cam.y)

    def _boites(self, boites, cam):
        for b in boites:
            b.dessiner(self.screen, cam.x, cam.y)

    def _monstres(self, monstres, cam):
        for m in monstres:
            m.dessiner(self.screen, cam.x, cam.y)

    # ── PANNEAUX ─────────────────────────────────────────────
    def dessiner_panneaux(self, screen, panneaux, camera, joueur):
        font = pygame.font.Font(None, 24)
        for p in panneaux:
            couleur = (0, 200, 0) if p['actif'] else (70, 70, 70)
            xe, ye = p['x']-camera.x, p['y']-camera.y
            pygame.draw.rect(screen, couleur, (xe, ye, p['largeur'], p['hauteur']))
            pygame.draw.rect(screen, BLANC,   (xe, ye, p['largeur'], p['hauteur']), 2)
            led = VERT if p['actif'] else ROUGE
            pygame.draw.circle(screen, led, (int(xe+20), int(ye+15)), 5)
            if not p['actif']:
                dx, dy = p['x']-joueur.x, p['y']-joueur.y
                if (dx**2+dy**2)**0.5 < 65:
                    txt = font.render("E : Activer panneau", True, BLANC)
                    screen.blit(txt, txt.get_rect(center=(LARGEUR//2, 55)))

"""Scene d'introduction : exterieur avec voiture et dialogue"""

import pygame
import math
from config import *


def dessiner_voiture(screen, x, y):
    """Dessine une voiture vue de dessus."""
    # Carrosserie principale
    pygame.draw.rect(screen, (60, 60, 75), (x, y + 8, 70, 36), border_radius=4)
    # Toit (plus fonce)
    pygame.draw.rect(screen, (40, 40, 55), (x + 10, y + 12, 50, 26), border_radius=3)
    # Pare-chocs avant/arriere
    pygame.draw.rect(screen, (80, 80, 95), (x - 4, y + 14, 8, 22), border_radius=2)
    pygame.draw.rect(screen, (80, 80, 95), (x + 66, y + 14, 8, 22), border_radius=2)
    # Phares
    pygame.draw.rect(screen, (220, 220, 160), (x - 2, y + 15, 6, 8), border_radius=1)
    pygame.draw.rect(screen, (220, 220, 160), (x - 2, y + 29, 6, 8), border_radius=1)
    # Feux arriere
    pygame.draw.rect(screen, (180, 30, 30), (x + 66, y + 15, 5, 7), border_radius=1)
    pygame.draw.rect(screen, (180, 30, 30), (x + 66, y + 30, 5, 7), border_radius=1)
    # Vitres
    pygame.draw.rect(screen, (120, 160, 200, 180), (x + 12, y + 14, 22, 24), border_radius=2)
    pygame.draw.rect(screen, (120, 160, 200, 180), (x + 36, y + 14, 22, 24), border_radius=2)
    # Roues
    for wy in [y + 6, y + 34]:
        for wx in [x + 4, x + 54]:
            pygame.draw.ellipse(screen, (20, 20, 20), (wx, wy, 14, 10))
            pygame.draw.ellipse(screen, (60, 60, 60), (wx + 2, wy + 1, 10, 8))


def dessiner_batiment(screen, x, y, w, h):
    """Dessine la facade de l'urbex (vue de dessus -> mur du bas visible)."""
    # Sol de l'urbex
    pygame.draw.rect(screen, (35, 30, 25), (x, y, w, h))
    # Murs exterieurs
    ep = 16
    pygame.draw.rect(screen, (65, 55, 45), (x, y, w, ep))          # haut
    pygame.draw.rect(screen, (65, 55, 45), (x, y + h - ep, w, ep)) # bas
    pygame.draw.rect(screen, (65, 55, 45), (x, y, ep, h))           # gauche
    pygame.draw.rect(screen, (65, 55, 45), (x + w - ep, y, ep, h))  # droite
    # Fenêtres bouchées
    for fx in [x + 40, x + w - 80]:
        for fy in [y + 25, y + h - 60]:
            pygame.draw.rect(screen, (20, 15, 10), (fx, fy, 30, 20))
            pygame.draw.rect(screen, (50, 40, 30), (fx, fy, 30, 20), 1)


def run_intro(screen, clock) -> bool:
    """
    Lance la scene d'intro.
    Retourne True si le joueur veut continuer, False si quitte.
    """
    LARGEUR_CARTE = LARGEUR
    HAUTEUR_CARTE = HAUTEUR

    # Positions
    bat_x, bat_y = 300, 60
    bat_w, bat_h = 600, 300
    porte_x = bat_x + bat_w // 2 - 20
    porte_y = bat_y + bat_h - 16
    porte_w, porte_h = 40, 16

    voiture_x, voiture_y = 100, 560

    # Joueur : commence pres de la voiture
    joueur_x, joueur_y = float(voiture_x + 90), float(voiture_y + 14)
    joueur_vitesse = 3.0

    # Dialogue voiture
    dialogue_voiture = [
        "Ami(e) dans la voiture :",
        "\"Hey, mauvaise nouvelle...",
        " Les routes sont coupees.",
        " Tu vas devoir passer la nuit ici.\"",
        "",
        "\"Ce batiment abandonné...",
        " Survie jusqu'a 6h00 du matin.",
        " Je reviens te chercher.\"",
        "",
        "[Appuie sur ENTREE pour entrer]",
    ]

    # Murs de la carte intro
    murs_intro = [
        # Bords
        pygame.Rect(0, 0, LARGEUR_CARTE, 10),
        pygame.Rect(0, HAUTEUR_CARTE - 10, LARGEUR_CARTE, 10),
        pygame.Rect(0, 0, 10, HAUTEUR_CARTE),
        pygame.Rect(LARGEUR_CARTE - 10, 0, 10, HAUTEUR_CARTE),
        # Murs du batiment (sauf ouverture porte)
        pygame.Rect(bat_x, bat_y, bat_w, 16),
        pygame.Rect(bat_x, bat_y, 16, bat_h),
        pygame.Rect(bat_x + bat_w - 16, bat_y, 16, bat_h),
        # Bas : deux segments avec porte au milieu
        pygame.Rect(bat_x, bat_y + bat_h - 16, porte_x - bat_x, 16),
        pygame.Rect(porte_x + porte_w, bat_y + bat_h - 16,
                    bat_x + bat_w - (porte_x + porte_w), 16),
    ]

    dialogue_actif = False
    dialogue_ok    = False
    font_d  = pygame.font.Font(None, 24)
    font_m  = pygame.font.Font(None, 20)
    frame   = 0

    running = True
    while running:
        clock.tick(FPS)
        frame += 1
        mouse_pos = pygame.mouse.get_pos()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return False
                if ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and dialogue_actif:
                    return True   # entre dans l'urbex

        # Déplacement joueur intro
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_z] or keys[pygame.K_w] or keys[pygame.K_UP]:    dy = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:                       dy =  1
        if keys[pygame.K_q] or keys[pygame.K_a] or keys[pygame.K_LEFT]:   dx = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:                      dx =  1
        if dx and dy:
            dx *= 0.707; dy *= 0.707
        nx = joueur_x + dx * joueur_vitesse
        ny = joueur_y + dy * joueur_vitesse
        rect_j = pygame.Rect(int(nx), int(ny), JOUEUR_LARGEUR, JOUEUR_HAUTEUR)
        if not any(rect_j.colliderect(m) for m in murs_intro):
            joueur_x, joueur_y = nx, ny

        # Clamp dans l'écran
        joueur_x = max(10, min(LARGEUR_CARTE - JOUEUR_LARGEUR - 10, joueur_x))
        joueur_y = max(10, min(HAUTEUR_CARTE - JOUEUR_HAUTEUR - 10, joueur_y))

        # Détection proximité voiture
        dist_voiture = math.hypot(joueur_x - (voiture_x + 35), joueur_y - (voiture_y + 25))
        dialogue_actif = dist_voiture < 80

        # ── Dessin ──
        # Fond : asphalte / bitume
        screen.fill((28, 28, 22))

        # Herbe autour
        pygame.draw.rect(screen, (25, 40, 20), (0, 0, LARGEUR_CARTE, bat_y + bat_h - 16))
        # Route
        pygame.draw.rect(screen, (45, 45, 40), (0, bat_y + bat_h, LARGEUR_CARTE, HAUTEUR_CARTE))
        # Ligne de route
        for rx in range(0, LARGEUR_CARTE, 80):
            pygame.draw.rect(screen, (200, 180, 60), (rx, HAUTEUR_CARTE // 2 + 100, 50, 6))

        # Batiment
        dessiner_batiment(screen, bat_x, bat_y, bat_w, bat_h)

        # Porte (surlignée)
        porte_c = (80, 55, 30) if not dialogue_actif else (60, 40, 20)
        pygame.draw.rect(screen, porte_c, (porte_x, porte_y, porte_w, porte_h))
        pygame.draw.rect(screen, (120, 80, 40), (porte_x, porte_y, porte_w, porte_h), 2)

        # Voiture (avec léger balancement)
        bob = int(math.sin(frame * 0.04) * 1)
        dessiner_voiture(screen, voiture_x, voiture_y + bob)

        # Lumières voiture si proche
        if dist_voiture < 200:
            for lix, liy in [(voiture_x - 2, voiture_y + 15 + bob),
                              (voiture_x - 2, voiture_y + 29 + bob)]:
                surf_l = pygame.Surface((60, 30), pygame.SRCALPHA)
                pygame.draw.polygon(surf_l, (255, 255, 180, 40),
                                    [(0, 8), (60, 0), (60, 30), (0, 22)])
                screen.blit(surf_l, (lix - 60, liy - 8))

        # Joueur
        pygame.draw.ellipse(screen, (50, 80, 200),
                            (int(joueur_x), int(joueur_y), JOUEUR_LARGEUR, JOUEUR_HAUTEUR))
        pygame.draw.ellipse(screen, BLANC,
                            (int(joueur_x), int(joueur_y), JOUEUR_LARGEUR, JOUEUR_HAUTEUR), 1)

        # Dialogue voiture
        if dialogue_actif:
            bx, by_ = 50, HAUTEUR_CARTE - 230
            bw, bh  = LARGEUR_CARTE - 100, 210
            bg_d = pygame.Surface((bw, bh), pygame.SRCALPHA)
            bg_d.fill((5, 5, 20, 220))
            screen.blit(bg_d, (bx, by_))
            pygame.draw.rect(screen, (80, 80, 160), (bx, by_, bw, bh), 2, border_radius=6)
            for li, ligne in enumerate(dialogue_voiture):
                c = JAUNE if li == 0 else BLANC if ligne else GRIS_CLAIR
                t = font_d.render(ligne, True, c)
                screen.blit(t, (bx + 18, by_ + 14 + li * 22))

        # Hint touche si pas encore près
        if not dialogue_actif:
            hint = font_m.render("Approche-toi de la voiture (en bas a gauche)", True, GRIS_CLAIR)
            screen.blit(hint, hint.get_rect(center=(LARGEUR_CARTE // 2, HAUTEUR_CARTE - 20)))

        # Indicateur porte si dialogue ok
        if dialogue_actif:
            arr = font_m.render("^ Porte de l'urbex (rejoins-la et ENTREE)", True, ORANGE)
            screen.blit(arr, arr.get_rect(center=(LARGEUR_CARTE // 2, 20)))

        pygame.display.flip()

    return False

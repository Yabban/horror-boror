"""Sprites dessinés programmatiquement — joueur, monstres, décoration"""

import pygame
import math
from config import *

_CACHE = {}


# ─────────────────────────────────────────────
#  JOUEUR  (apparence change selon paranoïa)
# ─────────────────────────────────────────────

def sprite_joueur(paranoia: float) -> pygame.Surface:
    """Retourne un sprite 32×32 dont l'aspect évolue avec la paranoïa (0-100)."""
    key = f"joueur_{int(paranoia // 10)}"
    if key in _CACHE:
        return _CACHE[key]

    s = pygame.Surface((JOUEUR_LARGEUR, JOUEUR_HAUTEUR), pygame.SRCALPHA)
    p = paranoia / 100.0  # 0..1

    # Couleur peau qui vire au violet-grisâtre
    r = int(220 - p * 130)
    g = int(180 - p * 140)
    b = int(140 + p * 80)
    chair = (max(0, r), max(0, g), min(255, b))

    # Corps
    pygame.draw.ellipse(s, chair, (8, 12, 18, 20))
    # Tête
    tete_c = (max(0, r - 20), max(0, g - 20), min(255, b + 20))
    pygame.draw.ellipse(s, tete_c, (8, 1, 18, 18))

    # Yeux — deviennent rouges et exorbités
    oeil_c = (int(p * 255), int((1 - p) * 200), int((1 - p) * 200))
    r_oeil = 2 + int(p * 3)
    pygame.draw.circle(s, oeil_c, (13, 8), r_oeil)
    pygame.draw.circle(s, oeil_c, (20, 8), r_oeil)
    pygame.draw.circle(s, BLANC,  (13, 8), 1)
    pygame.draw.circle(s, BLANC,  (20, 8), 1)

    # Bouche — sourit puis grimace
    if paranoia < 40:
        pygame.draw.arc(s, (80, 30, 30), (11, 12, 10, 6), math.pi, 2 * math.pi, 2)
    elif paranoia < 70:
        pygame.draw.line(s, (80, 30, 30), (11, 15), (21, 15), 2)
    else:
        pygame.draw.arc(s, SANG, (11, 13, 10, 6), 0, math.pi, 2)
        # Veines sur la tête
        for i in range(3):
            sx_ = 10 + i * 4
            pygame.draw.line(s, (180, 0, 60),
                             (sx_, 2), (sx_ + 2, 6), 1)

    # Contour
    pygame.draw.ellipse(s, (max(0, r - 40), max(0, g - 40), min(255, b + 40)),
                        (8, 1, 18, 18), 1)
    pygame.draw.ellipse(s, (max(0, r - 40), max(0, g - 40), min(255, b + 40)),
                        (8, 12, 18, 20), 1)

    _CACHE[key] = s
    return s


# ─────────────────────────────────────────────
#  MONSTRE TRAQUEUR
# ─────────────────────────────────────────────

def sprite_traqueur(stun: bool = False) -> pygame.Surface:
    key = f"traqueur_{'stun' if stun else 'ok'}"
    if key in _CACHE:
        return _CACHE[key]

    W, H = MONSTRE_LARGEUR, MONSTRE_HAUTEUR
    s = pygame.Surface((W, H), pygame.SRCALPHA)

    # Corps principal — silhouette trapue et menaçante
    corps_c = (60, 0, 0) if not stun else (40, 40, 100)
    contour_c = (200, 20, 20) if not stun else (100, 100, 255)

    # Jambes
    pygame.draw.rect(s, corps_c, (6, 28, 8, 12))
    pygame.draw.rect(s, corps_c, (26, 28, 8, 12))
    # Griffes de pieds
    for gx in [4, 8, 12, 24, 28, 32]:
        pygame.draw.line(s, contour_c, (gx, 40), (gx - 2, 40), 2)

    # Torse
    pygame.draw.rect(s, corps_c, (4, 14, 32, 18))
    pygame.draw.rect(s, contour_c, (4, 14, 32, 18), 1)

    # Bras avec griffes
    pygame.draw.rect(s, corps_c, (0, 16, 6, 14))
    pygame.draw.rect(s, corps_c, (34, 16, 6, 14))
    for gy in [16, 20, 24]:
        pygame.draw.line(s, contour_c, (0, gy), (-2, gy - 2), 1)
        pygame.draw.line(s, contour_c, (40, gy), (42, gy - 2), 1)

    # Tête — large et plate
    tete_c = (80, 0, 0) if not stun else (60, 60, 140)
    pygame.draw.ellipse(s, tete_c, (4, 0, 32, 20))
    pygame.draw.ellipse(s, contour_c, (4, 0, 32, 20), 2)

    # Yeux brillants
    if not stun:
        pygame.draw.circle(s, (255, 40, 0), (14, 8), 5)
        pygame.draw.circle(s, (255, 200, 50), (14, 8), 3)
        pygame.draw.circle(s, (255, 40, 0), (26, 8), 5)
        pygame.draw.circle(s, (255, 200, 50), (26, 8), 3)
        pygame.draw.circle(s, BLANC, (15, 7), 1)
        pygame.draw.circle(s, BLANC, (27, 7), 1)
    else:
        # Yeux X quand stunné
        for ex, ey in [(14, 8), (26, 8)]:
            pygame.draw.line(s, (200, 200, 255), (ex - 3, ey - 3), (ex + 3, ey + 3), 2)
            pygame.draw.line(s, (200, 200, 255), (ex + 3, ey - 3), (ex - 3, ey + 3), 2)

    # Bouche avec dents
    pygame.draw.arc(s, contour_c, (10, 12, 20, 8), math.pi, 2 * math.pi, 2)
    for tx in [14, 18, 22, 26]:
        pygame.draw.line(s, BLANC, (tx, 16), (tx, 19), 1)

    # Cicatrices
    pygame.draw.line(s, contour_c, (8, 4), (12, 10), 1)
    pygame.draw.line(s, contour_c, (30, 3), (27, 9), 1)

    _CACHE[key] = s
    return s


# ─────────────────────────────────────────────
#  MONSTRE ERRANT (fantôme)
# ─────────────────────────────────────────────

def sprite_errant(stun: bool = False, frame: int = 0) -> pygame.Surface:
    key = f"errant_{'stun' if stun else 'ok'}_{frame % 4}"
    if key in _CACHE:
        return _CACHE[key]

    W, H = MONSTRE_LARGEUR, MONSTRE_HAUTEUR
    s = pygame.Surface((W, H), pygame.SRCALPHA)

    flottaison = int(math.sin(frame * 0.3) * 2)
    fy = 2 + flottaison

    c_corps = (60, 60, 140, 200) if not stun else (100, 100, 200, 160)
    c_bord  = (140, 140, 255, 220) if not stun else (180, 180, 255, 180)

    # Corps fantôme
    pygame.draw.ellipse(s, c_corps, (4, fy, 32, 26))
    pygame.draw.ellipse(s, c_bord,  (4, fy, 32, 26), 2)

    # Queue ondulée
    bob = int(math.sin(frame * 0.5) * 3)
    points_queue = [
        (4, fy + 26),
        (10, fy + 32 + bob),
        (16, fy + 28 - bob),
        (22, fy + 32 + bob),
        (28, fy + 28 - bob),
        (36, fy + 26),
    ]
    if len(points_queue) >= 3:
        pygame.draw.polygon(s, c_corps, points_queue)
        pygame.draw.lines(s, c_bord, False, points_queue, 2)

    if not stun:
        # Yeux creux noirs
        pygame.draw.ellipse(s, (0, 0, 20, 230), (11, fy + 6, 8, 10))
        pygame.draw.ellipse(s, (0, 0, 20, 230), (21, fy + 6, 8, 10))
        # Lueur violette dans les yeux
        pygame.draw.ellipse(s, (180, 0, 255, 180), (13, fy + 8, 4, 6))
        pygame.draw.ellipse(s, (180, 0, 255, 180), (23, fy + 8, 4, 6))
        # Bouche hurlante
        pygame.draw.ellipse(s, (0, 0, 30, 200), (14, fy + 17, 12, 8))
    else:
        for ex, ey in [(15, fy + 10), (25, fy + 10)]:
            pygame.draw.line(s, (200, 200, 255), (ex - 3, ey - 3), (ex + 3, ey + 3), 2)
            pygame.draw.line(s, (200, 200, 255), (ex + 3, ey - 3), (ex - 3, ey + 3), 2)

    # Traînée lumineuse
    for i in range(3):
        alpha = 60 - i * 20
        trail = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.ellipse(trail, (100, 100, 200, alpha),
                            (4 + i, fy + i, 32 - i * 2, 26 - i * 2))
        s.blit(trail, (0, 0))

    _CACHE[key] = s
    return s


# ─────────────────────────────────────────────
#  DÉCORATION URBEX
# ─────────────────────────────────────────────

def sprite_crane() -> pygame.Surface:
    if "crane" in _CACHE:
        return _CACHE["crane"]
    s = pygame.Surface((28, 28), pygame.SRCALPHA)
    # Crâne
    pygame.draw.ellipse(s, (220, 210, 190), (2, 0, 24, 20))
    pygame.draw.ellipse(s, (150, 140, 120), (2, 0, 24, 20), 1)
    # Mâchoire
    pygame.draw.rect(s, (210, 200, 180), (6, 16, 16, 10))
    pygame.draw.rect(s, (150, 140, 120), (6, 16, 16, 10), 1)
    # Orbites
    pygame.draw.ellipse(s, (20, 15, 10), (5, 5, 8, 8))
    pygame.draw.ellipse(s, (20, 15, 10), (15, 5, 8, 8))
    # Dents
    for tx in [8, 12, 16, 20]:
        pygame.draw.rect(s, BLANC, (tx, 22, 3, 5))
        pygame.draw.rect(s, (150, 140, 120), (tx, 22, 3, 5), 1)
    # Fissures
    pygame.draw.line(s, (150, 140, 120), (14, 0), (12, 8), 1)
    pygame.draw.line(s, (150, 140, 120), (20, 2), (18, 7), 1)
    _CACHE["crane"] = s
    return s


def sprite_toile(taille: int = 40) -> pygame.Surface:
    key = f"toile_{taille}"
    if key in _CACHE:
        return _CACHE[key]
    s = pygame.Surface((taille, taille), pygame.SRCALPHA)
    cx, cy = taille // 2, taille // 2
    c = (200, 200, 200, 160)
    # Rayons
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        ex = cx + int(math.cos(rad) * (taille // 2 - 2))
        ey = cy + int(math.sin(rad) * (taille // 2 - 2))
        pygame.draw.line(s, c, (cx, cy), (ex, ey), 1)
    # Cercles concentriques
    for r in range(5, taille // 2, 8):
        pygame.draw.circle(s, c, (cx, cy), r, 1)
    # Araignée centrale
    pygame.draw.circle(s, (30, 30, 30, 220), (cx, cy), 4)
    pygame.draw.circle(s, (60, 60, 60, 200), (cx, cy), 4, 1)
    _CACHE[key] = s
    return s


def sprite_flaque_sang(rayon: int = 18) -> pygame.Surface:
    key = f"sang_{rayon}"
    if key in _CACHE:
        return _CACHE[key]
    s = pygame.Surface((rayon * 2, rayon * 2), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (100, 0, 0, 180), (0, 0, rayon * 2, rayon * 2))
    # Éclaboussures
    import random
    rng = random.Random(rayon)
    for _ in range(6):
        ax = rayon + rng.randint(-rayon, rayon)
        ay = rayon + rng.randint(-rayon // 2, rayon // 2)
        pygame.draw.circle(s, (120, 0, 0, 140), (ax, ay), rng.randint(3, 7))
    _CACHE[key] = s
    return s


def sprite_bougie() -> pygame.Surface:
    if "bougie" in _CACHE:
        return _CACHE["bougie"]
    s = pygame.Surface((12, 28), pygame.SRCALPHA)
    # Cire
    pygame.draw.rect(s, (240, 230, 200), (3, 8, 6, 20))
    pygame.draw.rect(s, (200, 190, 160), (3, 8, 6, 20), 1)
    # Flamme
    pygame.draw.ellipse(s, (255, 180, 0, 230), (3, 0, 6, 12))
    pygame.draw.ellipse(s, (255, 240, 100, 180), (4, 1, 4, 8))
    _CACHE["bougie"] = s
    return s


def sprite_boite(ouverte: bool = False) -> pygame.Surface:
    key = f"boite_{'open' if ouverte else 'closed'}"
    if key in _CACHE:
        return _CACHE[key]
    s = pygame.Surface((28, 26), pygame.SRCALPHA)
    if not ouverte:
        pygame.draw.rect(s, (100, 65, 20), (0, 8, 28, 18))
        pygame.draw.rect(s, (70, 40, 8), (0, 8, 28, 18), 2)
        pygame.draw.rect(s, (130, 85, 30), (0, 0, 28, 10))
        pygame.draw.rect(s, (70, 40, 8), (0, 0, 28, 10), 2)
        pygame.draw.line(s, (70, 40, 8), (14, 0), (14, 10), 2)
        pygame.draw.line(s, (70, 40, 8), (0, 5), (28, 5), 2)
        # Point d'interrogation
        font = pygame.font.Font(None, 18)
        txt = font.render("?", True, JAUNE)
        s.blit(txt, (10, 10))
    else:
        pygame.draw.rect(s, (70, 40, 8), (0, 8, 28, 18))
        pygame.draw.rect(s, (50, 25, 4), (0, 8, 28, 18), 2)
        # Couvercle ouvert (rabattu)
        pygame.draw.rect(s, (100, 65, 20), (0, 0, 28, 8))
        pygame.draw.rect(s, (70, 40, 8), (0, 0, 28, 8), 1)
    _CACHE[key] = s
    return s


def sprite_objet(type_obj: str) -> pygame.Surface:
    key = f"obj_{type_obj}"
    if key in _CACHE:
        return _CACHE[key]

    s = pygame.Surface((22, 22), pygame.SRCALPHA)
    ICONS = {
        "Clé":        _icon_cle,
        "Médicament": _icon_medicament,
        "Fusible":    _icon_fusible,
        "Talisman":   _icon_talisman,
        "Batterie":   _icon_batterie,
        "Brique":     _icon_brique,
    }
    fn = ICONS.get(type_obj)
    if fn:
        fn(s)
    else:
        pygame.draw.rect(s, BLANC, (0, 0, 22, 22))
        f = pygame.font.Font(None, 18)
        s.blit(f.render(type_obj[0], True, NOIR), (6, 4))
    _CACHE[key] = s
    return s


def _icon_cle(s):
    pygame.draw.circle(s, ORANGE, (8, 8), 6, 2)
    pygame.draw.rect(s, ORANGE, (12, 7, 10, 3))
    pygame.draw.rect(s, ORANGE, (18, 10, 3, 3))
    pygame.draw.rect(s, ORANGE, (14, 10, 3, 3))

def _icon_medicament(s):
    pygame.draw.rect(s, (200, 200, 240), (4, 4, 14, 14), border_radius=3)
    pygame.draw.rect(s, (160, 160, 200), (4, 4, 14, 14), 1, border_radius=3)
    pygame.draw.rect(s, ROUGE, (9, 6, 4, 10))
    pygame.draw.rect(s, ROUGE, (6, 9, 10, 4))

def _icon_fusible(s):
    pygame.draw.rect(s, (200, 180, 60), (7, 2, 8, 18), border_radius=2)
    pygame.draw.rect(s, (150, 130, 30), (7, 2, 8, 18), 1, border_radius=2)
    pygame.draw.line(s, (240, 200, 0), (11, 6), (11, 16), 2)

def _icon_talisman(s):
    points = [(11, 1), (14, 8), (21, 8), (15, 13), (17, 21), (11, 16), (5, 21), (7, 13), (1, 8), (8, 8)]
    pygame.draw.polygon(s, VIOLET, points)
    pygame.draw.polygon(s, (220, 100, 255), points, 1)

def _icon_batterie(s):
    pygame.draw.rect(s, (0, 180, 220), (2, 5, 16, 12), border_radius=2)
    pygame.draw.rect(s, (0, 120, 160), (2, 5, 16, 12), 1, border_radius=2)
    pygame.draw.rect(s, (0, 180, 220), (18, 8, 3, 6))
    pygame.draw.line(s, (0, 255, 100), (6, 11), (10, 7), 2)
    pygame.draw.line(s, (0, 255, 100), (10, 7), (10, 11), 2)
    pygame.draw.line(s, (0, 255, 100), (10, 11), (14, 7), 2)

def _icon_brique(s):
    pygame.draw.rect(s, MARRON, (1, 5, 20, 12))
    pygame.draw.rect(s, (80, 40, 10), (1, 5, 20, 12), 1)
    pygame.draw.line(s, (80, 40, 10), (1, 11), (21, 11), 1)
    pygame.draw.line(s, (80, 40, 10), (8, 5), (8, 17), 1)
    pygame.draw.line(s, (80, 40, 10), (14, 5), (14, 17), 1)

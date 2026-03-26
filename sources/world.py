"""Génération procédurale du monde — urbex avec décoration d'ambiance"""

import pygame
import random
import math
from config import *
from entities import Objet, Monstre, Boite, Quete
from sprites import sprite_crane, sprite_toile, sprite_flaque_sang, sprite_bougie


# ─────────────────────────────────────────────
#  CAMERA
# ─────────────────────────────────────────────

class Camera:
    def __init__(self, lm, hm):
        self.x = self.y = 0
        self.lm, self.hm = lm, hm

    def centrer_sur(self, joueur):
        self.x = max(0, min(int(joueur.x) - LARGEUR // 2, self.lm - LARGEUR))
        self.y = max(0, min(int(joueur.y) - HAUTEUR // 2, self.hm - HAUTEUR))


# ─────────────────────────────────────────────
#  TACHE (among-us style)
# ─────────────────────────────────────────────

class Tache:
    """Mini-tâche à effectuer dans une pièce pour faire passer le temps."""
    def __init__(self, x, y, nom, description, duree_frames=300):
        self.x, self.y     = x, y
        self.largeur       = 36
        self.hauteur       = 36
        self.nom           = nom
        self.description   = description
        self.duree         = duree_frames  # frames à rester appuyé sur E
        self.progression   = 0
        self.complete      = False
        self._bob          = random.uniform(0, math.pi * 2)

    def interagir(self):
        """Retourne True quand la tâche est terminée."""
        if self.complete:
            return False
        self.progression += 1
        if self.progression >= self.duree:
            self.complete = True
            return True
        return False

    @property
    def pct(self):
        return self.progression / self.duree

    def dessiner(self, screen, cx, cy):
        if self.complete:
            return
        self._bob += 0.04
        dy = int(math.sin(self._bob) * 2)
        sx = int(self.x - cx)
        sy = int(self.y - cy) + dy

        if sx < -60 or sx > LARGEUR + 20 or sy < -60 or sy > HAUTEUR + 20:
            return

        # Icône tâche : engrenage stylisé
        pygame.draw.circle(screen, (0, 200, 150), (sx + 18, sy + 18), 14)
        pygame.draw.circle(screen, (0, 150, 110), (sx + 18, sy + 18), 14, 2)
        pygame.draw.circle(screen, (0, 100, 80),  (sx + 18, sy + 18), 8)
        # Dents engrenage
        for a in range(0, 360, 45):
            rad = math.radians(a)
            gx = sx + 18 + int(math.cos(rad) * 16)
            gy = sy + 18 + int(math.sin(rad) * 16)
            pygame.draw.circle(screen, (0, 200, 150), (gx, gy), 4)

        # Barre de progression si en cours
        if self.progression > 0:
            pygame.draw.rect(screen, GRIS, (sx, sy + 38, 36, 6))
            pygame.draw.rect(screen, VERT, (sx, sy + 38, int(36 * self.pct), 6))

    def collision_joueur(self, joueur):
        return pygame.Rect(int(self.x), int(self.y), self.largeur, self.largeur).colliderect(
               joueur.rect())


# ─────────────────────────────────────────────
#  DECOR
# ─────────────────────────────────────────────

class Decor:
    """Élément décoratif statique : crâne, toile, flaque, bougie…"""
    def __init__(self, x, y, type_decor):
        self.x, self.y    = x, y
        self.type_decor   = type_decor
        self._surf        = None

    def _get_surf(self):
        if self._surf is None:
            if self.type_decor == "crane":
                self._surf = sprite_crane()
            elif self.type_decor == "toile":
                self._surf = sprite_toile(random.randint(30, 60))
            elif self.type_decor == "sang":
                self._surf = sprite_flaque_sang(random.randint(14, 26))
            elif self.type_decor == "bougie":
                self._surf = sprite_bougie()
            else:
                self._surf = pygame.Surface((10, 10), pygame.SRCALPHA)
        return self._surf

    def dessiner(self, screen, cx, cy):
        sx, sy = int(self.x - cx), int(self.y - cy)
        if sx < -80 or sx > LARGEUR + 40 or sy < -80 or sy > HAUTEUR + 40:
            return
        screen.blit(self._get_surf(), (sx, sy))


# ─────────────────────────────────────────────
#  WORLD GENERATOR
# ─────────────────────────────────────────────

LISTE_TACHES = [
    ("Réparer le générateur",    "Maintiens E pour réparer...",   360),
    ("Fouiller les décombres",   "Maintiens E pour fouiller...",  280),
    ("Barricader la porte",      "Maintiens E pour barricader...",320),
    ("Trouver la carte du bâtiment","Maintiens E pour chercher...",300),
    ("Allumer les bougies",      "Maintiens E pour allumer...",   240),
    ("Vérifier les cages",       "Maintiens E pour vérifier...",  300),
    ("Brancher le câble",        "Maintiens E pour brancher...",  340),
    ("Nettoyer le passage",      "Maintiens E pour dégager...",   260),
]

class WorldGenerator:
    def __init__(self, largeur=LARGEUR_MONDE, hauteur=HAUTEUR_MONDE, nuit=1):
        self.largeur = largeur
        self.hauteur = hauteur
        self.nuit    = nuit
        self._murs   = []

    # ── Murs ──
    def generer_murs(self):
        murs = [
            # Bords
            pygame.Rect(0, 0, self.largeur, 24),
            pygame.Rect(0, self.hauteur - 24, self.largeur, 24),
            pygame.Rect(0, 0, 24, self.hauteur),
            pygame.Rect(self.largeur - 24, 0, 24, self.hauteur),
        ]
        # Pièces (rectangles intérieurs = murs avec ouvertures)
        pieces = self._generer_pieces()
        for p in pieces:
            murs.extend(self._murs_piece(p))
        # Murs intérieurs additionnels
        rng = random.Random(self.nuit * 7)
        for _ in range(20):
            x = rng.randint(200, self.largeur - 400)
            y = rng.randint(200, self.hauteur - 400)
            w = rng.randint(60, 220)
            h = rng.randint(20, 60)
            if rng.random() < 0.5:
                w, h = h, w
            murs.append(pygame.Rect(x, y, w, h))
        self._murs = murs
        return murs

    def _generer_pieces(self):
        """Génère 8 à 12 pièces rectangulaires aléatoires."""
        pieces = []
        rng = random.Random(self.nuit * 13)
        for _ in range(10):
            x = rng.randint(100, self.largeur - 500)
            y = rng.randint(100, self.hauteur - 500)
            w = rng.randint(200, 500)
            h = rng.randint(180, 400)
            pieces.append(pygame.Rect(x, y, w, h))
        return pieces

    def _murs_piece(self, p):
        """Génère 4 murs avec une ouverture aléatoire sur chaque côté."""
        ep  = 20
        murs = []
        rng  = random.Random(p.x + p.y)
        # Haut
        ow = 80
        ox = rng.randint(p.x + 40, p.x + p.width - ow - 40)
        murs.append(pygame.Rect(p.x, p.y, ox - p.x, ep))
        murs.append(pygame.Rect(ox + ow, p.y, p.x + p.width - ox - ow, ep))
        # Bas
        ox2 = rng.randint(p.x + 40, p.x + p.width - ow - 40)
        murs.append(pygame.Rect(p.x, p.y + p.height, ox2 - p.x, ep))
        murs.append(pygame.Rect(ox2 + ow, p.y + p.height, p.x + p.width - ox2 - ow, ep))
        # Gauche
        oh = 80
        oy = rng.randint(p.y + 40, p.y + p.height - oh - 40)
        murs.append(pygame.Rect(p.x, p.y, ep, oy - p.y))
        murs.append(pygame.Rect(p.x, oy + oh, ep, p.y + p.height - oy - oh))
        # Droite
        oy2 = rng.randint(p.y + 40, p.y + p.height - oh - 40)
        murs.append(pygame.Rect(p.x + p.width, p.y, ep, oy2 - p.y))
        murs.append(pygame.Rect(p.x + p.width, oy2 + oh, ep, p.y + p.height - oy2 - oh))
        return [m for m in murs if m.width > 0 and m.height > 0]

    # ── Position libre ──
    def _position_libre(self, marge=60):
        for _ in range(300):
            x = random.randint(80, self.largeur - 80)
            y = random.randint(80, self.hauteur - 80)
            zone = pygame.Rect(x - marge // 2, y - marge // 2, marge, marge)
            if not any(zone.colliderect(m) for m in self._murs):
                return x, y
        return 120, 120

    # ── Objets (peu, dans boites principalement) ──
    def generer_objets(self):
        """Quelques objets posés au sol par pièce (1-2 par zone)."""
        objets = []
        # Toujours : 1 Clé, 1 Fusible, garantis quelque part
        for t in ["Clé", "Fusible"]:
            x, y = self._position_libre(50)
            objets.append(Objet(x, y, t))
        # Objets bonus rares
        bonus = ["Médicament", "Batterie", "Batterie", "Brique", "Brique",
                 "Médicament", "Talisman"]
        for t in bonus:
            if random.random() < 0.6:
                x, y = self._position_libre(40)
                objets.append(Objet(x, y, t))
        return objets

    def generer_boites(self):
        boites = []
        nb = 20 + self.nuit * 5
        for _ in range(nb):
            x, y = self._position_libre(30)
            boites.append(Boite(x, y))
        return boites

    def generer_monstres(self):
        monstres = []
        nb_traqueur = 1 + self.nuit
        nb_errant   = 3 + self.nuit * 2
        for _ in range(nb_traqueur):
            x, y = self._position_libre(150)
            monstres.append(Monstre(x, y, "traqueur"))
        for _ in range(nb_errant):
            x, y = self._position_libre(100)
            monstres.append(Monstre(x, y, "errant"))
        return monstres

    def generer_panneaux(self):
        panneaux = []
        for i in range(2):
            x, y = self._position_libre(80)
            panneaux.append({'x': x, 'y': y, 'largeur': 40,
                              'hauteur': 60, 'actif': False,
                              'nom': f'Panneau {i+1}'})
        return panneaux

    def generer_taches(self):
        taches = []
        pool = random.sample(LISTE_TACHES, min(TACHES_PAR_NUIT + 1, len(LISTE_TACHES)))
        for nom, desc, duree in pool[:TACHES_PAR_NUIT]:
            x, y = self._position_libre(60)
            taches.append(Tache(x, y, nom, desc, duree + self.nuit * 30))
        return taches

    def generer_decors(self):
        decors = []
        types = ["crane", "toile", "sang", "bougie"]
        poids = [0.2, 0.35, 0.25, 0.2]
        nb = 80 + self.nuit * 20
        for _ in range(nb):
            x, y = self._position_libre(20)
            t = random.choices(types, weights=poids)[0]
            decors.append(Decor(x, y, t))
        return decors

# Projet : Survie jusqu'à l'aube
# Auteurs : [Prénoms Noms]
"""Entités du jeu : Joueur, Monstre, Objet, Boite, Brique"""

import pygame
import random
import math
from config import *


# ──────────────────────────────────────────────────────────────
#  SPRITES (surfaces dessinées programmatiquement)
# ──────────────────────────────────────────────────────────────

def _creer_sprite_traqueur():
    """Crée une surface 'traqueur' : silhouette noire avec yeux rouges brillants"""
    s = pygame.Surface((MONSTRE_LARGEUR, MONSTRE_HAUTEUR), pygame.SRCALPHA)
    # Corps sombre avec contour rouge
    pygame.draw.ellipse(s, (30, 0, 0), (0, 10, 35, 25))
    pygame.draw.ellipse(s, (180, 0, 0), (0, 10, 35, 25), 2)
    # Tête
    pygame.draw.ellipse(s, (20, 0, 0), (7, 0, 21, 18))
    pygame.draw.ellipse(s, (180, 0, 0), (7, 0, 21, 18), 2)
    # Yeux rouges lumineux
    pygame.draw.circle(s, (255, 50, 0), (13, 8), 4)
    pygame.draw.circle(s, (255, 200, 0), (13, 8), 2)
    pygame.draw.circle(s, (255, 50, 0), (22, 8), 4)
    pygame.draw.circle(s, (255, 200, 0), (22, 8), 2)
    # Griffes
    pygame.draw.line(s, (180, 0, 0), (4, 35), (0, 30), 2)
    pygame.draw.line(s, (180, 0, 0), (31, 35), (35, 30), 2)
    return s


def _creer_sprite_errant():
    """Crée une surface 'errant' : fantôme blafard semi-transparent"""
    s = pygame.Surface((MONSTRE_LARGEUR, MONSTRE_HAUTEUR), pygame.SRCALPHA)
    # Corps fantôme ondulé
    pygame.draw.ellipse(s, (180, 180, 220, 180), (3, 0, 29, 28))
    # Bas ondulé
    for i in range(3):
        pygame.draw.circle(s, (180, 180, 220, 180), (7 + i*10, 30), 6)
    # Contour bleuté
    pygame.draw.ellipse(s, (100, 100, 200, 200), (3, 0, 29, 28), 2)
    # Yeux creux noirs
    pygame.draw.ellipse(s, (0, 0, 40), (9, 8, 7, 9))
    pygame.draw.ellipse(s, (0, 0, 40), (19, 8, 7, 9))
    # Bouche creux
    pygame.draw.arc(s, (0, 0, 40), (10, 18, 15, 8), math.pi, 2*math.pi, 2)
    return s


def _creer_sprite_boite(etat="fermee"):
    """Crée une surface représentant une boîte mystère"""
    s = pygame.Surface((24, 22), pygame.SRCALPHA)
    couleur = (120, 80, 30) if etat == "fermee" else (60, 40, 15)
    pygame.draw.rect(s, couleur, (0, 6, 24, 16))
    pygame.draw.rect(s, (80, 50, 10), (0, 6, 24, 16), 2)
    # Couvercle
    pygame.draw.rect(s, (140, 95, 35), (0, 0, 24, 8))
    pygame.draw.rect(s, (80, 50, 10), (0, 0, 24, 8), 2)
    # Croix sur le couvercle
    pygame.draw.line(s, (80, 50, 10), (12, 0), (12, 8), 2)
    pygame.draw.line(s, (80, 50, 10), (0, 4), (24, 4), 2)
    return s


# Cache des sprites (initialisé après pygame.init())
_SPRITES = {}

def get_sprite(nom):
    if nom not in _SPRITES:
        if nom == "traqueur":
            _SPRITES[nom] = _creer_sprite_traqueur()
        elif nom == "errant":
            _SPRITES[nom] = _creer_sprite_errant()
        elif nom == "boite":
            _SPRITES[nom] = _creer_sprite_boite()
        elif nom == "boite_ouverte":
            _SPRITES[nom] = _creer_sprite_boite("ouverte")
    return _SPRITES[nom]


# ──────────────────────────────────────────────────────────────
#  JOUEUR
# ──────────────────────────────────────────────────────────────

class Joueur:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.largeur  = JOUEUR_LARGEUR
        self.hauteur  = JOUEUR_HAUTEUR
        self.vitesse  = JOUEUR_VITESSE
        self.sante    = JOUEUR_SANTE_MAX
        self.paranoia = 0
        self.inventaire = []   # [{'type': str, 'quantite': int}]
        self.direction = "bas"
        self.en_mouvement = False

    def deplacer(self, dx, dy, murs):
        nx = self.x + dx * self.vitesse
        ny = self.y + dy * self.vitesse
        rect = pygame.Rect(nx, ny, self.largeur, self.hauteur)
        for mur in murs:
            if rect.colliderect(mur):
                return
        self.x, self.y = nx, ny
        self.en_mouvement = True
        if dx > 0:   self.direction = "droite"
        elif dx < 0: self.direction = "gauche"
        elif dy > 0: self.direction = "bas"
        elif dy < 0: self.direction = "haut"

    def dessiner(self, screen, camera_x, camera_y):
        couleur = VIOLET if self.paranoia > 70 else ORANGE if self.paranoia > 40 else BLEU
        pygame.draw.rect(screen, couleur,
                         (self.x - camera_x, self.y - camera_y, self.largeur, self.hauteur))
        ox = self.x - camera_x + self.largeur // 2
        oy = self.y - camera_y + self.hauteur // 2
        positions = {
            "droite": [(ox+5, oy-3), (ox+5, oy+3)],
            "gauche": [(ox-5, oy-3), (ox-5, oy+3)],
            "haut":   [(ox-3, oy-5), (ox+3, oy-5)],
            "bas":    [(ox-3, oy+5), (ox+3, oy+5)],
        }
        for pos in positions.get(self.direction, positions["bas"]):
            pygame.draw.circle(screen, BLANC, pos, 3)

    def ramasser_objet(self, type_objet):
        total = sum(i['quantite'] for i in self.inventaire)
        if total >= INVENTAIRE_MAX:
            return False
        for item in self.inventaire:
            if item['type'] == type_objet:
                item['quantite'] += 1
                self._appliquer_effet(type_objet)
                return True
        self.inventaire.append({'type': type_objet, 'quantite': 1})
        self._appliquer_effet(type_objet)
        return True

    def utiliser_objet(self, type_objet):
        for item in self.inventaire:
            if item['type'] == type_objet:
                item['quantite'] -= 1
                if item['quantite'] <= 0:
                    self.inventaire.remove(item)
                return True
        return False

    def a_objet(self, type_objet):
        return any(i['type'] == type_objet for i in self.inventaire)

    def quantite_objet(self, type_objet):
        for i in self.inventaire:
            if i['type'] == type_objet:
                return i['quantite']
        return 0

    def _appliquer_effet(self, objet):
        if objet == "Médicament":
            self.paranoia = max(0, self.paranoia - 30)
            self.sante    = min(100, self.sante + 30)
        elif objet == "Talisman":
            self.paranoia = max(0, self.paranoia - 50)


# ──────────────────────────────────────────────────────────────
#  BRIQUE
# ──────────────────────────────────────────────────────────────

class Brique:
    def __init__(self, x, y, cible_x, cible_y):
        self.x, self.y = float(x), float(y)
        self.largeur = 12
        self.hauteur = 10
        dist = math.sqrt((cible_x-x)**2 + (cible_y-y)**2)
        v = 10
        self.vx = (cible_x-x)/dist*v if dist > 0 else v
        self.vy = (cible_y-y)/dist*v if dist > 0 else 0
        self.active = True
        self.timer_vie = 140

    def update(self, murs):
        if not self.active: return
        self.x += self.vx
        self.y += self.vy
        self.timer_vie -= 1
        if self.timer_vie <= 0:
            self.active = False; return
        rect = pygame.Rect(self.x, self.y, self.largeur, self.hauteur)
        for mur in murs:
            if rect.colliderect(mur):
                self.active = False; return

    def dessiner(self, screen, cx, cy):
        if not self.active: return
        pygame.draw.rect(screen, MARRON,
                         (int(self.x-cx), int(self.y-cy), self.largeur, self.hauteur))
        pygame.draw.rect(screen, (80,40,10),
                         (int(self.x-cx), int(self.y-cy), self.largeur, self.hauteur), 1)

    def collision_monstre(self, monstre):
        if not self.active or not monstre.actif: return False
        return pygame.Rect(self.x,self.y,self.largeur,self.hauteur).colliderect(
               pygame.Rect(monstre.x,monstre.y,monstre.largeur,monstre.hauteur))


# ──────────────────────────────────────────────────────────────
#  MONSTRE
# ──────────────────────────────────────────────────────────────

class Monstre:
    def __init__(self, x, y, type_monstre="errant"):
        self.x, self.y = x, y
        self.largeur  = MONSTRE_LARGEUR
        self.hauteur  = MONSTRE_HAUTEUR
        self.type     = type_monstre
        self.vitesse  = MONSTRE_VITESSE_BASE
        self.degats   = MONSTRE_DEGATS_BASE
        self.direction_x = random.choice([-1, 1])
        self.direction_y = random.choice([-1, 1])
        self.timer_changement = 0
        self.actif      = False
        self.stun_timer = 0
        # Sprite
        self._sprite = None  # chargé au premier dessin

    def _get_sprite(self):
        if self._sprite is None:
            self._sprite = get_sprite(self.type)
        return self._sprite

    def mettre_a_jour_agressivite(self, temps_jeu):
        """Augmente vitesse et dégâts avec le temps (toutes les ~60s réelles)"""
        progression = min(1.0, temps_jeu / (60 * 60 * 8))  # max à 8h in-game
        self.vitesse = MONSTRE_VITESSE_BASE + (MONSTRE_VITESSE_MAX - MONSTRE_VITESSE_BASE) * progression
        self.degats  = MONSTRE_DEGATS_BASE  + (MONSTRE_DEGATS_MAX  - MONSTRE_DEGATS_BASE)  * progression

    def deplacer(self, joueur_x, joueur_y, murs):
        if not self.actif or self.stun_timer > 0:
            if self.stun_timer > 0: self.stun_timer -= 1
            return
        if self.type == "traqueur":
            self._deplacer_traqueur(joueur_x, joueur_y, murs)
        else:
            self._deplacer_errant(murs)

    def _deplacer_traqueur(self, jx, jy, murs):
        dx, dy = jx - self.x, jy - self.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist > 0:
            nx = self.x + dx/dist * self.vitesse
            ny = self.y + dy/dist * self.vitesse
            if self._libre(nx, ny, murs):
                self.x, self.y = nx, ny

    def _deplacer_errant(self, murs):
        self.timer_changement += 1
        if self.timer_changement > 60:
            self.direction_x = random.choice([-1, 0, 1])
            self.direction_y = random.choice([-1, 0, 1])
            self.timer_changement = 0
        nx = self.x + self.direction_x * self.vitesse
        ny = self.y + self.direction_y * self.vitesse
        if self._libre(nx, ny, murs):
            self.x, self.y = nx, ny
        else:
            self.direction_x *= -1
            self.direction_y *= -1

    def _libre(self, nx, ny, murs):
        r = pygame.Rect(nx, ny, self.largeur, self.hauteur)
        return not any(r.colliderect(m) for m in murs)

    def stunner(self):
        self.stun_timer = DUREE_STUN_BRIQUE

    def dessiner(self, screen, cx, cy):
        if not self.actif: return
        sx = int(self.x - cx)
        sy = int(self.y - cy)
        if self.stun_timer > 0:
            # Effet bleuté quand stunné
            surf = self._get_sprite().copy()
            bleu_overlay = pygame.Surface((self.largeur, self.hauteur), pygame.SRCALPHA)
            bleu_overlay.fill((80, 80, 255, 120))
            surf.blit(bleu_overlay, (0, 0))
            screen.blit(surf, (sx, sy))
            font = pygame.font.Font(None, 18)
            screen.blit(font.render("zZz", True, (200, 200, 255)), (sx, sy - 16))
        else:
            screen.blit(self._get_sprite(), (sx, sy))

    def collision_joueur(self, joueur):
        if self.stun_timer > 0: return False
        return pygame.Rect(self.x,self.y,self.largeur,self.hauteur).colliderect(
               pygame.Rect(joueur.x,joueur.y,joueur.largeur,joueur.hauteur))


# ──────────────────────────────────────────────────────────────
#  BOITE MYSTERE
# ──────────────────────────────────────────────────────────────

class Boite:
    """Boîte dans le sol : 1/3 objet, 1/3 vide, 1/3 boogeyman (+50 paranoia)"""

    CONTENU_POSSIBLE = ["Médicament", "Batterie", "Brique", "Clé", "Talisman", "Fusible"]

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.largeur = 24
        self.hauteur = 22
        self.ouverte = False
        self._contenu = self._tirer_contenu()
        self._sprite      = None
        self._sprite_open = None

    def _tirer_contenu(self):
        tirage = random.randint(1, 3)
        if tirage == 1:
            return random.choice(self.CONTENU_POSSIBLE)
        elif tirage == 2:
            return "vide"
        else:
            return "monstre"

    def ouvrir(self, joueur, messages_callback):
        if self.ouverte:
            return
        self.ouverte = True
        if self._contenu == "monstre":
            joueur.paranoia = min(100, joueur.paranoia + 50)
            messages_callback("💀 BOOGEYMAN ! +50 Paranoïa !", 180)
        elif self._contenu == "vide":
            messages_callback("Boîte vide...", 120)
        else:
            succes = joueur.ramasser_objet(self._contenu)
            if succes:
                messages_callback(f"Boîte : vous trouvez {self._contenu} !", 150)
            else:
                messages_callback("Inventaire plein ! Boîte ignorée.", 120)
                self.ouverte = False  # peut réessayer après

    def dessiner(self, screen, cx, cy):
        if self.ouverte: return
        if self._sprite is None:
            self._sprite = get_sprite("boite")
        screen.blit(self._sprite, (int(self.x - cx), int(self.y - cy)))

    def collision_joueur(self, joueur):
        return pygame.Rect(self.x,self.y,self.largeur,self.hauteur).colliderect(
               pygame.Rect(joueur.x,joueur.y,joueur.largeur,joueur.hauteur))


# ──────────────────────────────────────────────────────────────
#  OBJET RAMASSABLE
# ──────────────────────────────────────────────────────────────

class Objet:
    COULEURS = {
        "Clé":       ORANGE,
        "Médicament": VERT,
        "Fusible":   ROUGE,
        "Talisman":  VIOLET,
        "Batterie":  (0, 200, 255),
        "Brique":    MARRON,
    }

    def __init__(self, x, y, type_objet):
        self.x, self.y  = x, y
        self.type       = type_objet
        self.largeur    = 20
        self.hauteur    = 20
        self.ramasse    = False

    def dessiner(self, screen, cx, cy):
        if self.ramasse: return
        couleur = self.COULEURS.get(self.type, BLANC)
        pygame.draw.rect(screen, couleur,
                         (self.x-cx, self.y-cy, self.largeur, self.hauteur))
        pygame.draw.rect(screen, BLANC,
                         (self.x-cx, self.y-cy, self.largeur, self.hauteur), 2)
        font = pygame.font.Font(None, 18)
        screen.blit(font.render(self.type[0], True, NOIR),
                    (self.x-cx+6, self.y-cy+4))

    def collision_joueur(self, joueur):
        return pygame.Rect(self.x,self.y,self.largeur,self.hauteur).colliderect(
               pygame.Rect(joueur.x,joueur.y,joueur.largeur,joueur.hauteur))


class Quete:
    def __init__(self, nom, description):
        self.nom, self.description = nom, description
        self.complete = False

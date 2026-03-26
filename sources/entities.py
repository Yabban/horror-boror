"""Entites du jeu : Joueur, Monstre, Objet, Boite, Brique, Quete"""

import pygame
import random
import math
from config import *
from sprites import (sprite_joueur, sprite_traqueur, sprite_errant,
                     sprite_boite, sprite_objet)


# ─────────────────────────────────────────────
#  JOUEUR
# ─────────────────────────────────────────────

class Joueur:
    def __init__(self, x, y):
        self.x, self.y    = float(x), float(y)
        self.largeur      = JOUEUR_LARGEUR
        self.hauteur      = JOUEUR_HAUTEUR
        self.vitesse      = JOUEUR_VITESSE
        self.sante        = float(JOUEUR_SANTE_MAX)
        self.paranoia     = 0.0
        self.inventaire   = []
        self.direction    = "bas"
        self.talisman_timer = 0

    def deplacer(self, dx, dy, murs):
        vitesse = self.vitesse
        if dx and dy:
            vitesse *= 0.707
        nx = self.x + dx * vitesse
        ny = self.y + dy * vitesse
        rect = pygame.Rect(int(nx), int(ny), self.largeur, self.hauteur)
        for mur in murs:
            if rect.colliderect(mur):
                rx = pygame.Rect(int(self.x + dx * vitesse), int(self.y), self.largeur, self.hauteur)
                if not any(rx.colliderect(m) for m in murs):
                    self.x += dx * vitesse
                    self._update_dir(dx, 0)
                    return
                ry = pygame.Rect(int(self.x), int(self.y + dy * vitesse), self.largeur, self.hauteur)
                if not any(ry.colliderect(m) for m in murs):
                    self.y += dy * vitesse
                    self._update_dir(0, dy)
                    return
                return
        self.x, self.y = nx, ny
        self._update_dir(dx, dy)

    def _update_dir(self, dx, dy):
        if dx > 0:    self.direction = "droite"
        elif dx < 0:  self.direction = "gauche"
        elif dy > 0:  self.direction = "bas"
        elif dy < 0:  self.direction = "haut"

    def dessiner(self, screen, cx, cy):
        sx, sy = int(self.x - cx), int(self.y - cy)
        surf = sprite_joueur(self.paranoia)
        angles = {"bas": 0, "haut": 180, "droite": 270, "gauche": 90}
        angle = angles.get(self.direction, 0)
        if angle:
            surf = pygame.transform.rotate(surf, angle)
        screen.blit(surf, (sx, sy))

    def ramasser_objet(self, type_objet):
        total = sum(i['quantite'] for i in self.inventaire)
        if total >= INVENTAIRE_MAX:
            return False
        for item in self.inventaire:
            if item['type'] == type_objet:
                item['quantite'] += 1
                return True
        self.inventaire.append({'type': type_objet, 'quantite': 1})
        return True

    def utiliser_objet(self, type_objet):
        for item in self.inventaire:
            if item['type'] == type_objet:
                item['quantite'] -= 1
                if item['quantite'] <= 0:
                    self.inventaire.remove(item)
                self._appliquer_effet(type_objet)
                return True
        return False

    def jeter_objet(self, type_objet):
        for item in self.inventaire:
            if item['type'] == type_objet:
                item['quantite'] -= 1
                if item['quantite'] <= 0:
                    self.inventaire.remove(item)
                return True
        return False

    def mettre_a_jour_talisman(self):
        if self.talisman_timer > 0:
            self.talisman_timer -= 1
            if self.talisman_timer == 0:
                self.jeter_objet("Talisman")
                return "talisman_casse"
        return None

    def a_objet(self, type_objet):
        return any(i['type'] == type_objet for i in self.inventaire)

    def quantite_objet(self, type_objet):
        for i in self.inventaire:
            if i['type'] == type_objet:
                return i['quantite']
        return 0

    def _appliquer_effet(self, objet):
        if objet == "Medicament":
            self.sante    = min(100, self.sante + 30)
            self.paranoia = max(0,   self.paranoia - 30)
        elif objet == "Talisman":
            self.paranoia       = max(0, self.paranoia - 50)
            self.talisman_timer = TALISMAN_DUREE

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.largeur, self.hauteur)


# ─────────────────────────────────────────────
#  BRIQUE
# ─────────────────────────────────────────────

class Brique:
    def __init__(self, x, y, cible_x, cible_y):
        self.x, self.y = float(x), float(y)
        self.largeur = 12
        self.hauteur = 10
        dist = math.hypot(cible_x - x, cible_y - y)
        v = 12
        self.vx = (cible_x - x) / dist * v if dist > 0 else v
        self.vy = (cible_y - y) / dist * v if dist > 0 else 0
        self.active    = True
        self.timer_vie = 120

    def update(self, murs):
        if not self.active:
            return
        self.x += self.vx
        self.y += self.vy
        self.timer_vie -= 1
        if self.timer_vie <= 0:
            self.active = False
            return
        r = pygame.Rect(int(self.x), int(self.y), self.largeur, self.hauteur)
        if any(r.colliderect(m) for m in murs):
            self.active = False

    def dessiner(self, screen, cx, cy):
        if not self.active:
            return
        pygame.draw.rect(screen, MARRON,
                         (int(self.x - cx), int(self.y - cy), self.largeur, self.hauteur))
        pygame.draw.rect(screen, (80, 40, 10),
                         (int(self.x - cx), int(self.y - cy), self.largeur, self.hauteur), 1)

    def collision_monstre(self, monstre):
        if not self.active or not monstre.actif:
            return False
        return pygame.Rect(int(self.x), int(self.y), self.largeur, self.hauteur).colliderect(
               pygame.Rect(int(monstre.x), int(monstre.y), monstre.largeur, monstre.hauteur))


# ─────────────────────────────────────────────
#  MONSTRE
# ─────────────────────────────────────────────

class Monstre:
    def __init__(self, x, y, type_monstre="errant"):
        self.x, self.y   = float(x), float(y)
        self.largeur     = MONSTRE_LARGEUR
        self.hauteur     = MONSTRE_HAUTEUR
        self.type        = type_monstre
        self.vitesse     = MONSTRE_VITESSE_BASE
        self.degats      = MONSTRE_DEGATS_BASE
        self.direction_x = random.choice([-1, 1])
        self.direction_y = random.choice([-1, 1])
        self.timer_dir   = 0
        self.actif       = True   # visible des le debut, degats actives par fusible
        self.stun_timer  = 0
        self.frame       = 0
        self._cap_x      = 0.0
        self._cap_y      = 0.0
        self._timer_cap  = 0

    def mettre_a_jour_agressivite(self, temps_jeu):
        prog = min(1.0, temps_jeu / (60 * 60 * 6))
        self.vitesse = MONSTRE_VITESSE_BASE + (MONSTRE_VITESSE_MAX - MONSTRE_VITESSE_BASE) * prog
        self.degats  = MONSTRE_DEGATS_BASE  + (MONSTRE_DEGATS_MAX  - MONSTRE_DEGATS_BASE)  * prog

    def deplacer(self, jx, jy, murs):
        if not self.actif:
            return
        if self.stun_timer > 0:
            self.stun_timer -= 1
            return
        self.frame += 1
        if self.type == "traqueur":
            self._deplacer_traqueur(jx, jy, murs)
        else:
            self._deplacer_errant(jx, jy, murs)

    def _deplacer_traqueur(self, jx, jy, murs):
        dx, dy = jx - self.x, jy - self.y
        dist   = math.hypot(dx, dy)
        if dist < 1:
            return
        self._timer_cap -= 1
        if self._timer_cap <= 0:
            self._cap_x = dx / dist
            self._cap_y = dy / dist
            self._timer_cap = 90
        nx = self.x + self._cap_x * self.vitesse
        ny = self.y + self._cap_y * self.vitesse
        if self._libre(nx, ny, murs):
            self.x, self.y = nx, ny
            return
        base_angle = math.atan2(self._cap_y, self._cap_x)
        for delta in [30, -30, 60, -60, 90, -90, 120, -120]:
            a  = base_angle + math.radians(delta)
            tx = self.x + math.cos(a) * self.vitesse
            ty = self.y + math.sin(a) * self.vitesse
            if self._libre(tx, ty, murs):
                self.x, self.y  = tx, ty
                self._cap_x     = math.cos(a)
                self._cap_y     = math.sin(a)
                self._timer_cap = 45
                return

    def _deplacer_errant(self, jx, jy, murs):
        self.timer_dir += 1
        if self.timer_dir > random.randint(40, 100):
            dx, dy = jx - self.x, jy - self.y
            dist = math.hypot(dx, dy)
            if dist > 0 and random.random() < 0.3:
                self.direction_x = math.copysign(1, dx)
                self.direction_y = math.copysign(1, dy)
            else:
                self.direction_x = random.choice([-1, 0, 1])
                self.direction_y = random.choice([-1, 0, 1])
            self.timer_dir = 0
        nx = self.x + self.direction_x * self.vitesse
        ny = self.y + self.direction_y * self.vitesse
        if self._libre(nx, ny, murs):
            self.x, self.y = nx, ny
        else:
            self.direction_x = random.choice([-1, 0, 1])
            self.direction_y = random.choice([-1, 0, 1])

    def _libre(self, nx, ny, murs):
        r = pygame.Rect(int(nx), int(ny), self.largeur, self.hauteur)
        return not any(r.colliderect(m) for m in murs)

    def stunner(self):
        self.stun_timer = DUREE_STUN_BRIQUE

    def dessiner(self, screen, cx, cy):
        if not self.actif:
            return
        sx = int(self.x - cx)
        sy = int(self.y - cy)
        if sx < -60 or sx > LARGEUR + 20 or sy < -60 or sy > HAUTEUR + 20:
            return
        if self.type == "traqueur":
            surf = sprite_traqueur(self.stun_timer > 0)
        else:
            surf = sprite_errant(self.stun_timer > 0, self.frame)
        screen.blit(surf, (sx, sy))
        if self.stun_timer > 0:
            font = pygame.font.Font(None, 18)
            screen.blit(font.render("zZz", True, (180, 180, 255)), (sx, sy - 16))

    def collision_joueur(self, joueur):
        if self.stun_timer > 0:
            return False
        return pygame.Rect(int(self.x), int(self.y), self.largeur, self.hauteur).colliderect(
               joueur.rect())

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.largeur, self.hauteur)


# ─────────────────────────────────────────────
#  BOITE MYSTERE
# ─────────────────────────────────────────────

class Boite:
    CONTENU = ["Medicament", "Batterie", "Brique", "Talisman", "Brique", "Medicament"]

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.largeur   = 28
        self.hauteur   = 26
        self.ouverte   = False
        self._contenu  = self._tirer()

    def _tirer(self):
        t = random.randint(1, 3)
        if t == 1:
            return random.choice(self.CONTENU)
        elif t == 2:
            return "vide"
        else:
            return "monstre"

    def ouvrir(self, joueur, cb):
        if self.ouverte:
            return
        self.ouverte = True
        if self._contenu == "monstre":
            joueur.paranoia = min(100, joueur.paranoia + 50)
            cb("BOOGEYMAN ! +50 Paranoia !", 200)
        elif self._contenu == "vide":
            cb("Boite vide...", 120)
        else:
            if joueur.ramasser_objet(self._contenu):
                cb("Boite : " + self._contenu + " !", 150)
            else:
                cb("Inventaire plein !", 120)
                self.ouverte = False

    def dessiner(self, screen, cx, cy):
        if self.ouverte:
            return
        surf = sprite_boite(False)
        screen.blit(surf, (int(self.x - cx), int(self.y - cy)))

    def collision_joueur(self, joueur):
        return pygame.Rect(int(self.x), int(self.y), self.largeur, self.hauteur).colliderect(
               joueur.rect())


# ─────────────────────────────────────────────
#  OBJET RAMASSABLE
# ─────────────────────────────────────────────

class Objet:
    def __init__(self, x, y, type_objet):
        self.x, self.y = x, y
        self.type      = type_objet
        self.largeur   = 22
        self.hauteur   = 22
        self.ramasse   = False
        self._bob      = random.uniform(0, math.pi * 2)

    def dessiner(self, screen, cx, cy):
        if self.ramasse:
            return
        self._bob += 0.05
        dy_bob = int(math.sin(self._bob) * 2)
        surf = sprite_objet(self.type)
        sx = int(self.x - cx)
        sy = int(self.y - cy) + dy_bob
        screen.blit(surf, (sx, sy))

    def collision_joueur(self, joueur):
        return pygame.Rect(int(self.x), int(self.y), self.largeur, self.hauteur).colliderect(
               joueur.rect())


# ─────────────────────────────────────────────
#  QUETE
# ─────────────────────────────────────────────

class Quete:
    def __init__(self, nom, description):
        self.nom         = nom
        self.description = description
        self.complete    = False

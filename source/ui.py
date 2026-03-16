# Projet : Survie jusqu'à l'aube
# Auteurs : [Prénoms Noms]
"""Interface utilisateur : HUD, inventaire, messages"""

import pygame
from config import *

COULEURS_OBJETS = {
    "Clé": ORANGE, "Médicament": VERT, "Fusible": ROUGE,
    "Talisman": VIOLET, "Batterie": (0, 200, 255), "Brique": MARRON,
}
DESCRIPTIONS_OBJETS = {
    "Clé":       "Ouvre la sortie",
    "Médicament":"+30 santé / -30 paranoia",
    "Fusible":   "Rétablit l'électricité",
    "Talisman":  "-50 paranoia instantané",
    "Batterie":  "Recharge les panneaux (E près d'un panneau)",
    "Brique":    "Clic gauche pour lancer → stun 30s",
}


class UI:
    def __init__(self):
        self.fp = pygame.font.Font(None, 24)
        self.fm = pygame.font.Font(None, 36)
        self.fg = pygame.font.Font(None, 72)

    # ── HUD PRINCIPAL ────────────────────────────────────────
    def dessiner_hud(self, screen, joueur, temps, quetes, quete_actuelle,
                     messages, panneaux_actives, timer_batterie, batterie_morte):
        self._fond_hud(screen)
        self._barres(screen, joueur)
        self._mini_inventaire(screen, joueur)
        self._temps(screen, temps)
        self._quete(screen, quetes, quete_actuelle)
        self._controles(screen)
        self._messages(screen, messages)
        self._compteur_panneaux(screen, panneaux_actives)
        self._batterie(screen, panneaux_actives, timer_batterie, batterie_morte)

    def _fond_hud(self, screen):
        bg = pygame.Surface((LARGEUR, 150))
        bg.set_alpha(200)
        bg.fill(NOIR)
        screen.blit(bg, (0, HAUTEUR-150))

    def _barres(self, screen, j):
        # Santé
        c = VERT if j.sante > 50 else ORANGE if j.sante > 25 else ROUGE
        pygame.draw.rect(screen, GRIS, (20, HAUTEUR-130, 200, 22))
        pygame.draw.rect(screen, c,    (20, HAUTEUR-130, j.sante*2, 22))
        screen.blit(self.fp.render(f"Santé : {int(j.sante)}%", True, BLANC), (25, HAUTEUR-128))
        # Paranoïa
        c2 = VERT if j.paranoia < 40 else ORANGE if j.paranoia < 70 else ROUGE
        pygame.draw.rect(screen, GRIS, (20, HAUTEUR-102, 200, 22))
        pygame.draw.rect(screen, c2,   (20, HAUTEUR-102, min(200, j.paranoia*2), 22))
        screen.blit(self.fp.render(f"Paranoïa : {int(j.paranoia)}%", True, BLANC), (25, HAUTEUR-100))

    def _mini_inventaire(self, screen, j):
        screen.blit(self.fp.render("Inv (R) :", True, BLANC), (20, HAUTEUR-70))
        for idx, item in enumerate(j.inventaire[:4]):
            c = COULEURS_OBJETS.get(item['type'], BLANC)
            rx = 100 + idx * 48
            ry = HAUTEUR - 73
            pygame.draw.rect(screen, c, (rx, ry, 34, 34))
            pygame.draw.rect(screen, BLANC, (rx, ry, 34, 34), 1)
            screen.blit(self.fp.render(item['type'][0], True, NOIR), (rx+10, ry+8))
            if item['quantite'] > 1:
                screen.blit(self.fp.render(str(item['quantite']), True, BLANC), (rx+22, ry+2))

    def _temps(self, screen, temps):
        h = (temps // 3600) % 24
        m = (temps // 60) % 60
        screen.blit(self.fm.render(f"Heure : {h:02d}:{m:02d}", True, JAUNE), (20, HAUTEUR-42))

    def _quete(self, screen, quetes, idx):
        if idx < len(quetes):
            q = quetes[idx]
            screen.blit(self.fp.render(f"Quête : {q.nom}", True, ORANGE), (550, HAUTEUR-130))
            screen.blit(self.fp.render(q.description, True, BLANC),        (550, HAUTEUR-105))

    def _controles(self, screen):
        screen.blit(self.fp.render(
            "ZQSD : Bouger | E : Action/Ouvrir | R : Inventaire | Clic G : Lancer brique",
            True, GRIS_CLAIR), (250, HAUTEUR-25))

    def _messages(self, screen, messages):
        for i, (txt, duree) in enumerate(messages[-3:]):
            s = self.fm.render(txt, True, JAUNE)
            s.set_alpha(min(255, duree * 2))
            screen.blit(s, (LARGEUR//2 - 320, 80 + i*42))

    def _compteur_panneaux(self, screen, actives):
        c = VERT if actives >= 2 else JAUNE
        screen.blit(pygame.font.Font(None, 28).render(f"Panneaux : {actives}/2", True, c),
                    (LARGEUR-210, 10))

    def _batterie(self, screen, actives, timer, morte):
        if actives < 2: return
        f = pygame.font.Font(None, 24)
        if morte:
            screen.blit(f.render("BATTERIE MORTE — appuyez E+Batterie", True, ROUGE),
                        (LARGEUR-310, 36))
        else:
            ratio = timer / DUREE_BATTERIE
            c = (0,200,255) if ratio > 0.5 else ORANGE if ratio > 0.25 else ROUGE
            screen.blit(f.render(f"Batterie : {int(ratio*100)}%", True, c),
                        (LARGEUR-210, 36))

    # ── OVERLAY INVENTAIRE ──────────────────────────────────
    def dessiner_inventaire_overlay(self, screen, joueur):
        OW, OH = 440, 320
        ox, oy = LARGEUR//2 - OW//2, HAUTEUR//2 - OH//2
        bg = pygame.Surface((OW, OH), pygame.SRCALPHA)
        bg.fill((10, 10, 30, 225))
        screen.blit(bg, (ox, oy))
        pygame.draw.rect(screen, (100, 100, 210), (ox, oy, OW, OH), 2)

        screen.blit(self.fm.render("INVENTAIRE", True, JAUNE), (ox+20, oy+14))
        total = sum(i['quantite'] for i in joueur.inventaire)
        screen.blit(self.fp.render(f"{total}/{INVENTAIRE_MAX} objets  —  R pour fermer",
                                   True, GRIS_CLAIR), (ox+20, oy+50))

        if not joueur.inventaire:
            screen.blit(self.fp.render("(vide)", True, GRIS_CLAIR), (ox+20, oy+100))
        else:
            for i, item in enumerate(joueur.inventaire):
                iy = oy + 80 + i * 52
                c = COULEURS_OBJETS.get(item['type'], BLANC)
                pygame.draw.rect(screen, c, (ox+20, iy, 34, 34))
                pygame.draw.rect(screen, BLANC, (ox+20, iy, 34, 34), 1)
                screen.blit(self.fp.render(item['type'][0], True, NOIR), (ox+29, iy+8))
                screen.blit(self.fp.render(f"{item['type']}  ×{item['quantite']}",
                                           True, BLANC), (ox+64, iy+4))
                screen.blit(self.fp.render(DESCRIPTIONS_OBJETS.get(item['type'], ""),
                                           True, GRIS_CLAIR), (ox+64, iy+22))

        # Slots visuels
        by = oy + OH - 28
        for s in range(INVENTAIRE_MAX):
            c = VERT if s < total else GRIS
            pygame.draw.rect(screen, c, (ox+20+s*48, by, 38, 14))
            pygame.draw.rect(screen, BLANC, (ox+20+s*48, by, 38, 14), 1)

    # ── ÉCRANS FIN ───────────────────────────────────────────
    def afficher_game_over(self, screen, raison):
        screen.fill(NOIR)
        screen.blit(self.fg.render("GAME OVER", True, ROUGE),
                    (LARGEUR//2-150, HAUTEUR//2-50))
        screen.blit(self.fm.render(raison, True, BLANC),
                    (LARGEUR//2-200, HAUTEUR//2+20))
        pygame.display.flip()
        pygame.time.wait(5000)

    def afficher_victoire(self, screen):
        screen.fill(NOIR)
        screen.blit(self.fg.render("VICTOIRE !", True, VERT),
                    (LARGEUR//2-150, HAUTEUR//2-50))
        screen.blit(self.fm.render("Vous avez survécu jusqu'à l'aube !", True, BLANC),
                    (LARGEUR//2-250, HAUTEUR//2+20))
        pygame.display.flip()
        pygame.time.wait(5000)

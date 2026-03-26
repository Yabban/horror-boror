# Projet : Survie jusqu'a l'aube
# Auteurs : [Prenoms Noms]
"""Interface utilisateur : HUD, inventaire, menus, animations de mort"""

import pygame
import math
import random
from config import *
from sprites import sprite_objet

COULEURS_OBJETS = {
    "Cle": ORANGE, "Medicament": VERT, "Fusible": ROUGE,
    "Talisman": VIOLET, "Batterie": (0, 200, 255), "Brique": MARRON,
    "Cle": ORANGE,
}
DESCRIPTIONS_OBJETS = {
    "Cle":        "Ouvre la sortie",
    "Medicament": "+30 sante / -30 paranoia",
    "Fusible":    "Retablit l'electricite",
    "Talisman":   "-50 paranoia (se casse apres 3h in-game)",
    "Batterie":   "Recharge les panneaux (E pres d'un panneau)",
    "Brique":     "Clic gauche pour lancer -> stun 30s",
}


def _generer_son_bruit(frequence=440, duree_ms=500, volume=0.8):
    """Genere un son synthesise avec pygame (bruit blanc + tone)."""
    try:
        import numpy as np
        sample_rate = 44100
        n = int(sample_rate * duree_ms / 1000)
        t = np.linspace(0, duree_ms / 1000, n, False)
        # Melange bruit + tone basse frequence
        bruit = (np.random.random(n) * 2 - 1) * 0.3
        tone  = np.sin(2 * math.pi * frequence * t) * 0.7
        onde  = np.sin(2 * math.pi * 60 * t) * 0.5  # grondement
        signal = (bruit + tone + onde) * volume
        signal = np.clip(signal, -1, 1)
        signal_16 = (signal * 32767).astype(np.int16)
        stereo = np.column_stack([signal_16, signal_16])
        son = pygame.sndarray.make_sound(stereo)
        return son
    except Exception:
        return None


def _generer_son_jumpscare():
    """Son de jumpscare : crescendo bruit blanc strident."""
    try:
        import numpy as np
        sample_rate = 44100
        duree_ms = 1200
        n = int(sample_rate * duree_ms / 1000)
        t = np.linspace(0, duree_ms / 1000, n, False)
        # Enveloppe crescendo brutal
        env = np.linspace(0, 1, n) ** 0.3
        bruit = (np.random.random(n) * 2 - 1)
        # Harmoniques aiguees
        cri   = (np.sin(2 * math.pi * 880 * t) +
                 np.sin(2 * math.pi * 1760 * t) * 0.5 +
                 np.sin(2 * math.pi * 3520 * t) * 0.3)
        signal = (bruit * 0.4 + cri * 0.6) * env * 0.9
        signal = np.clip(signal, -1, 1)
        signal_16 = (signal * 32767).astype(np.int16)
        stereo = np.column_stack([signal_16, signal_16])
        return pygame.sndarray.make_sound(stereo)
    except Exception:
        return None


class UI:
    def __init__(self):
        self.fp  = pygame.font.Font(None, 22)
        self.fm  = pygame.font.Font(None, 32)
        self.fg  = pygame.font.Font(None, 72)
        self.fb  = pygame.font.Font(None, 48)
        self.inv_hover = -1
        # Sons pre-generes (None si numpy absent)
        pygame.mixer.pre_init(44100, -16, 2, 512)
        try:
            pygame.mixer.init()
        except Exception:
            pass

    # ══════════════════════════════════════════
    #  HUD principal
    # ══════════════════════════════════════════

    def dessiner_hud(self, screen, joueur, temps, quetes, quete_actuelle,
                     messages, panneaux_actives, timer_batterie, batterie_morte,
                     taches_completees, nuit, timer_noir=0):

        self._fond_hud(screen)
        self._barres(screen, joueur)
        self._mini_inv(screen, joueur)
        self._temps_nuit_centre(screen, temps, nuit)
        self._quete(screen, quetes, quete_actuelle)
        self._taches_hud(screen, taches_completees)
        self._controles(screen)
        self._messages(screen, messages)
        self._panneaux_batterie(screen, panneaux_actives, timer_batterie, batterie_morte)
        if timer_noir > 0:
            self._avertissement_noir(screen, timer_noir)

    def _fond_hud(self, screen):
        bg = pygame.Surface((LARGEUR, 150))
        bg.set_alpha(210)
        bg.fill((5, 5, 15))
        screen.blit(bg, (0, HAUTEUR - 150))

    def _barres(self, screen, j):
        c = VERT if j.sante > 50 else ORANGE if j.sante > 25 else ROUGE
        pygame.draw.rect(screen, (40, 40, 40), (20, HAUTEUR - 132, 180, 20), border_radius=4)
        pygame.draw.rect(screen, c, (20, HAUTEUR - 132, int(j.sante * 1.8), 20), border_radius=4)
        screen.blit(self.fp.render("Sante : %d%%" % int(j.sante), True, BLANC), (24, HAUTEUR - 130))

        cp = VERT if j.paranoia < 40 else ORANGE if j.paranoia < 70 else ROUGE
        pygame.draw.rect(screen, (40, 40, 40), (20, HAUTEUR - 106, 180, 20), border_radius=4)
        pygame.draw.rect(screen, cp, (20, HAUTEUR - 106, int(min(j.paranoia, 100) * 1.8), 20), border_radius=4)
        screen.blit(self.fp.render("Paranoia : %d%%" % int(j.paranoia), True, BLANC), (24, HAUTEUR - 104))

    def _mini_inv(self, screen, j):
        screen.blit(self.fp.render("Inv (R) :", True, GRIS_CLAIR), (20, HAUTEUR - 72))
        for idx, item in enumerate(j.inventaire[:4]):
            couleur = COULEURS_OBJETS.get(item['type'], BLANC)
            rx = 100 + idx * 52
            ry = HAUTEUR - 75
            pygame.draw.rect(screen, couleur, (rx, ry, 38, 38), border_radius=4)
            pygame.draw.rect(screen, BLANC, (rx, ry, 38, 38), 1, border_radius=4)
            ic = sprite_objet(item['type'])
            ic_s = pygame.transform.scale(ic, (26, 26))
            screen.blit(ic_s, (rx + 6, ry + 6))
            if item['quantite'] > 1:
                screen.blit(self.fp.render(str(item['quantite']), True, BLANC), (rx + 26, ry + 2))

    def _temps_nuit_centre(self, screen, temps, nuit):
        """Heure au centre en haut de l'ecran."""
        h = (temps // 3600) % 24
        m = (temps // 60) % 60
        heure_txt = "%02d:%02d" % (h, m)
        # Fond semi-transparent
        bg = pygame.Surface((160, 44), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 160))
        screen.blit(bg, (LARGEUR // 2 - 80, 6))
        # Heure centree
        t_h = self.fb.render(heure_txt, True, JAUNE)
        screen.blit(t_h, t_h.get_rect(center=(LARGEUR // 2, 28)))
        # Nuit en dessous
        t_n = self.fp.render("Nuit %d/%d" % (nuit, NB_NUITS), True, GRIS_CLAIR)
        screen.blit(t_n, t_n.get_rect(center=(LARGEUR // 2, 48)))

    def _quete(self, screen, quetes, idx):
        if idx < len(quetes):
            q = quetes[idx]
            screen.blit(self.fp.render("Quete : " + q.nom, True, ORANGE), (330, HAUTEUR - 130))
            screen.blit(self.fp.render(q.description, True, BLANC), (330, HAUTEUR - 110))

    def _taches_hud(self, screen, completees):
        txt = self.fp.render("Taches : %d/%d" % (completees, TACHES_PAR_NUIT), True,
                             VERT if completees >= TACHES_PAR_NUIT else GRIS_CLAIR)
        screen.blit(txt, (330, HAUTEUR - 88))

    def _controles(self, screen):
        screen.blit(self.fp.render(
            "ZQSD : Bouger | E : Action (maintenir=tache) | R : Inventaire | Clic G : Brique",
            True, (90, 90, 90)), (20, HAUTEUR - 18))

    def _messages(self, screen, messages):
        for i, (txt, duree) in enumerate(messages[-4:]):
            alpha = min(255, duree * 3)
            s = self.fm.render(txt, True, JAUNE)
            s.set_alpha(alpha)
            screen.blit(s, (LARGEUR // 2 - s.get_width() // 2, 75 + i * 40))

    def _panneaux_batterie(self, screen, actives, timer, morte):
        c = VERT if actives >= 2 else JAUNE
        screen.blit(self.fp.render("Panneaux : %d/2" % actives, True, c), (LARGEUR - 210, 12))
        if actives >= 2:
            if morte:
                screen.blit(self.fp.render("BATTERIE MORTE ! (E+Batterie)", True, ROUGE),
                            (LARGEUR - 290, 34))
            else:
                ratio = max(0, timer / DUREE_BATTERIE)
                bc = (0, 200, 255) if ratio > 0.5 else ORANGE if ratio > 0.25 else ROUGE
                screen.blit(self.fp.render("Batterie : %d%%" % int(ratio * 100), True, bc),
                            (LARGEUR - 210, 34))

    def _avertissement_noir(self, screen, timer_noir):
        """Barre rouge montrant le danger de rester dans le noir."""
        ratio = timer_noir / DUREE_MAX_NOIR
        if ratio < 0.3:
            return
        alpha = int((ratio - 0.3) / 0.7 * 180)
        # Vignette rouge sur les bords
        vign = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
        bord = int(60 * ratio)
        for i in range(bord):
            a = int(alpha * (1 - i / bord))
            pygame.draw.rect(vign, (150, 0, 0, a), (i, i, LARGEUR - 2*i, HAUTEUR - 2*i), 1)
        screen.blit(vign, (0, 0))
        if ratio > 0.6:
            warn = self.fp.render("DANGER : Trop longtemps dans le noir !", True, ROUGE)
            warn.set_alpha(200)
            screen.blit(warn, warn.get_rect(center=(LARGEUR // 2, HAUTEUR - 165)))

    # ══════════════════════════════════════════
    #  Overlay Inventaire
    # ══════════════════════════════════════════

    def dessiner_inventaire_overlay(self, screen, joueur, mouse_pos):
        OW, OH = 480, 360
        ox = LARGEUR // 2 - OW // 2
        oy = HAUTEUR // 2 - OH // 2

        bg = pygame.Surface((OW, OH), pygame.SRCALPHA)
        bg.fill((8, 8, 25, 240))
        screen.blit(bg, (ox, oy))
        pygame.draw.rect(screen, (80, 80, 180), (ox, oy, OW, OH), 2, border_radius=8)

        screen.blit(self.fb.render("INVENTAIRE", True, JAUNE), (ox + 20, oy + 14))
        total = sum(i['quantite'] for i in joueur.inventaire)
        screen.blit(self.fp.render("%d/%d  R pour fermer" % (total, INVENTAIRE_MAX),
                                   True, GRIS_CLAIR), (ox + 20, oy + 52))

        if not joueur.inventaire:
            screen.blit(self.fp.render("(vide)", True, GRIS_CLAIR), (ox + 20, oy + 90))

        for i, item in enumerate(joueur.inventaire):
            iy = oy + 78 + i * 62
            hover = (ox + 14 <= mouse_pos[0] <= ox + OW - 14 and
                     iy - 2 <= mouse_pos[1] <= iy + 54)
            bg_c = (30, 30, 60) if hover else (15, 15, 35)
            pygame.draw.rect(screen, bg_c, (ox + 14, iy, OW - 28, 52), border_radius=6)
            pygame.draw.rect(screen, (70, 70, 150), (ox + 14, iy, OW - 28, 52), 1, border_radius=6)

            couleur = COULEURS_OBJETS.get(item['type'], BLANC)
            pygame.draw.rect(screen, couleur, (ox + 20, iy + 9, 34, 34), border_radius=4)
            ic = sprite_objet(item['type'])
            ic_s = pygame.transform.scale(ic, (28, 28))
            screen.blit(ic_s, (ox + 23, iy + 12))

            screen.blit(self.fm.render("%s  x%d" % (item['type'], item['quantite']),
                                       True, BLANC), (ox + 62, iy + 8))
            screen.blit(self.fp.render(DESCRIPTIONS_OBJETS.get(item['type'], ""),
                                       True, GRIS_CLAIR), (ox + 62, iy + 30))

            bux = ox + OW - 180
            pygame.draw.rect(screen, (30, 120, 30), (bux, iy + 8, 70, 24), border_radius=4)
            screen.blit(self.fp.render("Utiliser", True, BLANC), (bux + 4, iy + 12))

            bjx = bux + 80
            pygame.draw.rect(screen, (120, 30, 30), (bjx, iy + 8, 50, 24), border_radius=4)
            screen.blit(self.fp.render("Jeter", True, BLANC), (bjx + 4, iy + 12))

        by = oy + OH - 26
        for s in range(INVENTAIRE_MAX):
            c = VERT if s < total else GRIS
            pygame.draw.rect(screen, c, (ox + 20 + s * 54, by, 44, 12), border_radius=3)
            pygame.draw.rect(screen, BLANC, (ox + 20 + s * 54, by, 44, 12), 1, border_radius=3)

        return None, None

    def traiter_clic_inventaire(self, joueur, mouse_pos):
        OW, OH = 480, 360
        ox = LARGEUR // 2 - OW // 2
        oy = HAUTEUR // 2 - OH // 2

        for i, item in enumerate(joueur.inventaire):
            iy = oy + 78 + i * 62
            bux = ox + OW - 180
            if bux <= mouse_pos[0] <= bux + 70 and iy + 8 <= mouse_pos[1] <= iy + 32:
                return "utiliser", item['type']
            bjx = bux + 80
            if bjx <= mouse_pos[0] <= bjx + 50 and iy + 8 <= mouse_pos[1] <= iy + 32:
                return "jeter", item['type']
        return None, None

    # ══════════════════════════════════════════
    #  Menu principal
    # ══════════════════════════════════════════

    def dessiner_menu(self, screen, save_exists, cursor_pos):
        screen.fill((5, 3, 15))
        titre = self.fg.render("Survie jusqu'a l'aube", True, (180, 20, 20))
        screen.blit(titre, titre.get_rect(center=(LARGEUR // 2, HAUTEUR // 3 - 30)))
        sous = self.fm.render("Jeu de survie horror", True, (120, 100, 80))
        screen.blit(sous, sous.get_rect(center=(LARGEUR // 2, HAUTEUR // 3 + 40)))
        self._deco_menu(screen)

        boutons = []
        if save_exists:
            boutons.append(("Continuer", "continuer"))
        boutons.append(("Nouvelle partie", "nouveau"))
        boutons.append(("Quitter", "quitter"))

        by = HAUTEUR // 2 + 20
        for label, action in boutons:
            bw, bh = 300, 50
            bx = LARGEUR // 2 - bw // 2
            hover = bx <= cursor_pos[0] <= bx + bw and by <= cursor_pos[1] <= by + bh
            bg_c = (120, 15, 15) if hover else (50, 8, 8)
            pygame.draw.rect(screen, bg_c, (bx, by, bw, bh), border_radius=8)
            pygame.draw.rect(screen, (180, 30, 30), (bx, by, bw, bh), 2, border_radius=8)
            t = self.fm.render(label, True, BLANC)
            screen.blit(t, t.get_rect(center=(LARGEUR // 2, by + bh // 2)))
            by += 68
        return None

    def clic_menu(self, save_exists, mouse_pos):
        boutons = []
        if save_exists:
            boutons.append(("Continuer", "continuer"))
        boutons.append(("Nouvelle partie", "nouveau"))
        boutons.append(("Quitter", "quitter"))

        by = HAUTEUR // 2 + 20
        for label, action in boutons:
            bw, bh = 300, 50
            bx = LARGEUR // 2 - bw // 2
            if bx <= mouse_pos[0] <= bx + bw and by <= mouse_pos[1] <= by + bh:
                return action
            by += 68
        return None

    def _deco_menu(self, screen):
        rng = random.Random(99)
        f = pygame.font.Font(None, 28)
        for _ in range(12):
            x = rng.randint(40, LARGEUR - 40)
            y = rng.randint(40, HAUTEUR - 40)
            sym = rng.choice(["#", "@", "%", "&"])
            t = f.render(sym, True, (40, 10, 10))
            screen.blit(t, (x, y))

    # ══════════════════════════════════════════
    #  ANIMATIONS DE MORT
    # ══════════════════════════════════════════

    def animation_mort_paranoia(self, screen, clock):
        """Personnage qui pleure et s'effondre — mort par paranoia."""
        fg_grand = pygame.font.Font(None, 90)
        fm2      = pygame.font.Font(None, 36)
        fp2      = pygame.font.Font(None, 24)

        # Son triste (low freq)
        son = _generer_son_bruit(180, 2000, 0.5)
        if son:
            try: son.play()
            except: pass

        duree_anim = 180  # 3s
        for frame in range(duree_anim + 60):
            clock.tick(60)
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return
                if ev.type == pygame.KEYDOWN and frame > 120:
                    return

            t = frame / duree_anim
            t = min(t, 1.0)

            # Fond qui vire au rouge-violet
            r = int(t * 60)
            screen.fill((r, 0, r // 2))

            cx, cy = LARGEUR // 2, HAUTEUR // 2 - 60

            # Corps du perso qui s'effondre
            inclinaison = int(t * 45)
            # Tete (cercle)
            tete_y = cy - int(t * 30)
            pygame.draw.circle(screen, (180, 140, 100), (cx, tete_y), 28)
            # Larmes
            if t > 0.2:
                nb_larmes = int((t - 0.2) / 0.8 * 8)
                for li in range(nb_larmes):
                    lx = cx - 12 + (li % 2) * 24 + random.randint(-2, 2)
                    ly = tete_y + 10 + (frame * 3 + li * 20) % 60
                    pygame.draw.ellipse(screen, (100, 160, 255), (lx, ly, 5, 9))
            # Corps penche
            corps_surf = pygame.Surface((30, 50), pygame.SRCALPHA)
            pygame.draw.rect(corps_surf, (160, 120, 80), (0, 0, 30, 50), border_radius=4)
            corps_rot = pygame.transform.rotate(corps_surf, -inclinaison)
            screen.blit(corps_rot, (cx - 15 + inclinaison // 2, tete_y + 28))

            # Yeux qui pleurent (X)
            oeil_c = (200, 50, 50)
            for ex in [cx - 10, cx + 10]:
                pygame.draw.line(screen, oeil_c, (ex - 5, tete_y - 8), (ex + 5, tete_y + 2), 3)
                pygame.draw.line(screen, oeil_c, (ex + 5, tete_y - 8), (ex - 5, tete_y + 2), 3)

            # Textes
            if frame > 40:
                alpha_txt = min(255, (frame - 40) * 8)
                t1 = fg_grand.render("GAME OVER", True, (200, 0, 0))
                t1.set_alpha(alpha_txt)
                screen.blit(t1, t1.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 + 60)))
            if frame > 80:
                t2 = fm2.render("La folie vous a consume...", True, (180, 100, 180))
                t2.set_alpha(min(255, (frame - 80) * 6))
                screen.blit(t2, t2.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 + 130)))
            if frame > 150:
                t3 = fp2.render("Appuyez sur une touche...", True, GRIS_CLAIR)
                screen.blit(t3, t3.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 + 175)))

            pygame.display.flip()

        self._attendre_touche()

    def animation_jumpscare_monstre(self, screen, clock):
        """Jumpscare brutal avec flash rouge et visage monstre."""
        # Son jumpscare strident
        son = _generer_son_jumpscare()
        if son:
            try: son.play()
            except: pass

        duree_anim = 150
        for frame in range(duree_anim + 60):
            clock.tick(60)
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return
                if ev.type == pygame.KEYDOWN and frame > 100:
                    return

            # Phase 1 : flash blanc brutal (0-15)
            if frame < 15:
                alpha = 255 - frame * 17
                screen.fill((255, 255, 255))
                overlay = pygame.Surface((LARGEUR, HAUTEUR))
                overlay.fill((255, 0, 0))
                overlay.set_alpha(alpha)
                screen.blit(overlay, (0, 0))

            # Phase 2 : visage monstre qui remplit l'ecran (15-80)
            elif frame < 80:
                screen.fill((0, 0, 0))
                scale_f = min(1.0, (frame - 15) / 40)
                # Dessin d'un visage monstre gigantesque
                self._dessiner_visage_monstre(screen, scale_f, frame)

            # Phase 3 : fondu au noir + textes (80+)
            else:
                noir_alpha = min(200, (frame - 80) * 5)
                screen.fill((0, 0, 0))
                if frame < 100:
                    self._dessiner_visage_monstre(screen, 1.0, frame)
                overlay2 = pygame.Surface((LARGEUR, HAUTEUR))
                overlay2.fill((0, 0, 0))
                overlay2.set_alpha(noir_alpha)
                screen.blit(overlay2, (0, 0))
                if frame > 110:
                    t1 = self.fg.render("GAME OVER", True, ROUGE)
                    t1.set_alpha(min(255, (frame - 110) * 8))
                    screen.blit(t1, t1.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 - 40)))
                if frame > 130:
                    t2 = self.fm.render("Vous avez ete devore...", True, (200, 80, 80))
                    t2.set_alpha(min(255, (frame - 130) * 8))
                    screen.blit(t2, t2.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 + 30)))
                if frame > 160:
                    t3 = self.fp.render("Appuyez sur une touche...", True, GRIS_CLAIR)
                    screen.blit(t3, t3.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 + 80)))

            pygame.display.flip()

        self._attendre_touche()

    def _dessiner_visage_monstre(self, screen, scale, frame):
        """Dessine un visage de monstre terrifiant qui zoom."""
        cx, cy = LARGEUR // 2, HAUTEUR // 2
        r_base = int(300 * scale)
        # Tete
        pygame.draw.ellipse(screen, (40, 0, 0),
                            (cx - r_base, cy - int(r_base * 0.9),
                             r_base * 2, int(r_base * 1.8)))
        # Yeux rouges brillants (clignotement)
        if frame % 6 < 5:
            for ex_off in [-r_base // 3, r_base // 3]:
                r_oeil = r_base // 5
                pygame.draw.circle(screen, (255, 30, 0), (cx + ex_off, cy - r_base // 5), r_oeil)
                pygame.draw.circle(screen, (255, 220, 50), (cx + ex_off, cy - r_base // 5), r_oeil // 2)
                # Lueur
                lueur = pygame.Surface((r_oeil * 4, r_oeil * 4), pygame.SRCALPHA)
                pygame.draw.circle(lueur, (255, 0, 0, 60),
                                   (r_oeil * 2, r_oeil * 2), r_oeil * 2)
                screen.blit(lueur, (cx + ex_off - r_oeil * 2, cy - r_base // 5 - r_oeil * 2))
        # Bouche ouverte avec dents
        bx = cx - r_base // 2
        by2 = cy + r_base // 4
        bw2 = r_base
        bh2 = r_base // 2
        pygame.draw.ellipse(screen, (10, 0, 0), (bx, by2, bw2, bh2))
        nb_dents = 8
        for di in range(nb_dents):
            dx2 = bx + di * (bw2 // nb_dents)
            pygame.draw.polygon(screen, (230, 220, 200),
                                [(dx2, by2),
                                 (dx2 + bw2 // (nb_dents * 2), by2 + bh2 // 2),
                                 (dx2 + bw2 // nb_dents, by2)])
        # Cicatrices
        pygame.draw.line(screen, (180, 0, 40),
                         (cx - r_base + 20, cy - r_base // 2),
                         (cx - r_base // 2, cy + r_base // 4), 4)
        pygame.draw.line(screen, (180, 0, 40),
                         (cx + r_base // 3, cy - r_base // 3),
                         (cx + r_base - 10, cy + r_base // 5), 3)

    def animation_mort_noir(self, screen, clock):
        """Le joueur est reste trop longtemps dans le noir — mort progressive."""
        son = _generer_son_bruit(60, 3000, 0.6)
        if son:
            try: son.play()
            except: pass

        duree_anim = 240
        for frame in range(duree_anim + 60):
            clock.tick(60)
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return
                if ev.type == pygame.KEYDOWN and frame > 180:
                    return

            t = min(1.0, frame / duree_anim)

            # Fond qui s'assombrit completement
            g = int((1 - t) * 15)
            screen.fill((g, g, g + 5))

            cx, cy = LARGEUR // 2, HAUTEUR // 2

            # Silhouette du joueur qui disparait
            if t < 0.7:
                alpha_perso = int((1 - t / 0.7) * 255)
                perso_s = pygame.Surface((32, 32), pygame.SRCALPHA)
                pygame.draw.ellipse(perso_s, (180, 140, 100, alpha_perso), (8, 0, 16, 16))
                pygame.draw.ellipse(perso_s, (160, 120, 80, alpha_perso), (6, 14, 20, 18))
                screen.blit(perso_s, (cx - 16, cy - 16))

            # Yeux dans le noir (les monstres regardent)
            if t > 0.3:
                nb_yeux = int((t - 0.3) / 0.7 * 12)
                rng2 = random.Random(frame // 10)
                for yi in range(nb_yeux):
                    ex2 = rng2.randint(50, LARGEUR - 50)
                    ey2 = rng2.randint(50, HAUTEUR - 200)
                    pygame.draw.circle(screen, (255, 30, 0), (ex2, ey2), 5)
                    pygame.draw.circle(screen, (255, 200, 0), (ex2, ey2), 2)

            # Textes
            if frame > 60:
                alpha_t = min(255, (frame - 60) * 5)
                t1 = self.fg.render("GAME OVER", True, (150, 0, 0))
                t1.set_alpha(alpha_t)
                screen.blit(t1, t1.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 + 60)))
            if frame > 100:
                t2 = self.fm.render("L'obscurite vous a englouti...", True, (100, 100, 150))
                t2.set_alpha(min(255, (frame - 100) * 5))
                screen.blit(t2, t2.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 + 130)))
            if frame > 200:
                t3 = self.fp.render("Appuyez sur une touche...", True, GRIS_CLAIR)
                t3.set_alpha(min(255, (frame - 200) * 8))
                screen.blit(t3, t3.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 + 180)))

            pygame.display.flip()

        self._attendre_touche()

    # ══════════════════════════════════════════
    #  Ecrans de fin / transition
    # ══════════════════════════════════════════

    def afficher_transition_nuit(self, screen, nuit):
        screen.fill((0, 0, 0))
        t1 = self.fg.render("Nuit %d terminee !" % nuit, True, ORANGE)
        t2 = self.fm.render("Vous avez survecu... pour l'instant.", True, BLANC)
        t3 = self.fm.render("La prochaine nuit commence...", True, GRIS_CLAIR)
        screen.blit(t1, t1.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 - 60)))
        screen.blit(t2, t2.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 + 10)))
        screen.blit(t3, t3.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 + 60)))
        pygame.display.flip()
        pygame.time.wait(3500)

    def afficher_game_over(self, screen, raison):
        screen.fill((0, 0, 0))
        t1 = self.fg.render("GAME OVER", True, ROUGE)
        t2 = self.fm.render(raison, True, BLANC)
        t3 = self.fp.render("Appuyez sur une touche...", True, GRIS_CLAIR)
        screen.blit(t1, t1.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 - 60)))
        screen.blit(t2, t2.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 + 10)))
        screen.blit(t3, t3.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 + 80)))
        pygame.display.flip()
        self._attendre_touche()

    def afficher_victoire(self, screen):
        screen.fill((0, 0, 0))
        t1 = self.fg.render("VICTOIRE !", True, VERT)
        t2 = self.fm.render("Vous avez survecu les 3 nuits !", True, BLANC)
        t3 = self.fp.render("Appuyez sur une touche...", True, GRIS_CLAIR)
        screen.blit(t1, t1.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 - 60)))
        screen.blit(t2, t2.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 + 10)))
        screen.blit(t3, t3.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 + 80)))
        pygame.display.flip()
        self._attendre_touche()

    def _attendre_touche(self):
        clock = pygame.time.Clock()
        waiting = True
        while waiting:
            clock.tick(30)
            for ev in pygame.event.get():
                if ev.type in (pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    waiting = False

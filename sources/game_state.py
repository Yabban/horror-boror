"""État global du jeu"""

import json, os
from entities import Joueur, Quete
from world import WorldGenerator, Camera
from config import *


class GameState:
    def __init__(self, nuit=1, charger_save=False):
        self.nuit            = nuit
        self.temps           = 0          # frames
        self.messages        = []         # [(texte, duree)]
        self.quete_actuelle  = 0
        self.monstres_actives = False

        self.joueur = Joueur(120, 120)

        if charger_save:
            self._charger()
        else:
            self._generer_monde()

        self.quetes = [
            Quete("Trouver une sortie",     "Cherchez une clé pour la porte"),
            Quete("Rétablir l'électricité", "Trouvez un fusible"),
            Quete("Survivre jusqu'à l'aube","Tenez jusqu'à 6h00"),
        ]
        self.camera = Camera(LARGEUR_MONDE, HAUTEUR_MONDE)
        self.taches_completees = 0

    def _generer_monde(self):
        g = WorldGenerator(nuit=self.nuit)
        self.murs      = g.generer_murs()
        self.objets    = g.generer_objets()
        self.boites    = g.generer_boites()
        self.monstres  = g.generer_monstres()
        self.panneaux  = g.generer_panneaux()
        self.taches    = g.generer_taches()
        self.decors    = g.generer_decors()

    # ── Messages ──
    def ajouter_message(self, texte, duree=180):
        # Évite les doublons immédiats
        if self.messages and self.messages[-1][0] == texte:
            return
        self.messages.append((texte, duree))
        if len(self.messages) > 6:
            self.messages.pop(0)

    def mettre_a_jour_messages(self):
        self.messages = [(t, d - 1) for t, d in self.messages if d > 1]

    # ── Temps ──
    def incrementer_temps(self):
        self.temps += 1

    def obtenir_heure(self):
        h = (self.temps // 3600) % 24
        m = (self.temps // 60) % 60
        return h, m

    # ── Camera ──
    def mettre_a_jour_camera(self):
        self.camera.centrer_sur(self.joueur)

    # ── Monstres ──
    def activer_monstres(self):
        self.monstres_actives = True
        # Les monstres sont deja actifs (visibles), on active juste leurs degats

    # ── Sauvegarde ──
    def sauvegarder(self):
        data = {
            "nuit":       self.nuit,
            "temps":      self.temps,
            "sante":      self.joueur.sante,
            "paranoia":   self.joueur.paranoia,
            "inventaire": self.joueur.inventaire,
            "joueur_x":   self.joueur.x,
            "joueur_y":   self.joueur.y,
            "quete":      self.quete_actuelle,
            "monstres_actives": self.monstres_actives,
            "taches_completees": self.taches_completees,
        }
        try:
            with open(FICHIER_SAVE, "w", encoding="utf-8") as f:
                json.dump(data, f)
            return True
        except Exception:
            return False

    def _charger(self):
        try:
            with open(FICHIER_SAVE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.nuit                = data.get("nuit", 1)
            self.temps               = data.get("temps", 0)
            self.joueur.sante        = data.get("sante", 100)
            self.joueur.paranoia     = data.get("paranoia", 0)
            self.joueur.inventaire   = data.get("inventaire", [])
            self.joueur.x            = data.get("joueur_x", 120)
            self.joueur.y            = data.get("joueur_y", 120)
            self.quete_actuelle      = data.get("quete", 0)
            self.monstres_actives    = data.get("monstres_actives", False)
            self.taches_completees   = data.get("taches_completees", 0)
            self._generer_monde()
            if self.monstres_actives:
                for m in self.monstres:
                    m.actif = True
        except Exception:
            self._generer_monde()

    @staticmethod
    def save_exists():
        return os.path.isfile(FICHIER_SAVE)

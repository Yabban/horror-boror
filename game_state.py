# Projet : Survie jusqu'à l'aube
# Auteurs : [Prénoms Noms]
"""État global du jeu"""

from entities import Joueur, Quete
from world import WorldGenerator, Camera
from config import *


class GameState:
    def __init__(self):
        self.temps    = 0
        self.messages = []
        self.quete_actuelle   = 0
        self.monstres_actives = False

        self.joueur = Joueur(100, 100)
        self._generer_monde()
        self.quetes = [
            Quete("Trouver une sortie",    "Cherchez une clé pour ouvrir la porte"),
            Quete("Rétablir l'électricité","Trouvez un fusible"),
            Quete("Survivre jusqu'à l'aube","Restez en vie jusqu'à 6h00"),
        ]
        self.camera = Camera(LARGEUR_MONDE, HAUTEUR_MONDE)

    def _generer_monde(self):
        g = WorldGenerator(LARGEUR_MONDE, HAUTEUR_MONDE)
        self.murs     = g.generer_murs()
        self.objets   = g.generer_objets()
        self.boites   = g.generer_boites()
        self.monstres = g.generer_monstres()
        self.panneaux_electricite = g.generer_panneaux()

    def ajouter_message(self, texte, duree=180):
        self.messages.append((texte, duree))

    def mettre_a_jour_camera(self):
        self.camera.centrer_sur(self.joueur)

    def incrementer_temps(self):
        self.temps += 1

    def obtenir_heure_actuelle(self):
        return (self.temps // 3600) % 24, (self.temps // 60) % 60

    def mettre_a_jour_messages(self):
        self.messages = [(t, d-1) for t, d in self.messages if d > 1]

    def activer_monstres(self):
        self.monstres_actives = True
        for m in self.monstres:
            m.actif = True

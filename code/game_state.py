"""Module de gestion de l'état du jeu"""

from entities import Joueur, Quete
from world import WorldGenerator, Camera
from config import *


class GameState:
    """Gère l'état global du jeu"""
    
    def __init__(self):
        self.temps = 0
        self.messages = []
        self.quete_actuelle = 0
        self.monstres_actives = False
        
        # Initialisation du joueur
        self.joueur = Joueur(100, 100)
        
        # Génération du monde
        self._generer_monde()
        
        # Quêtes
        self._initialiser_quetes()
        
        # Caméra
        self.camera = Camera(LARGEUR_MONDE, HAUTEUR_MONDE)
    
    def _generer_monde(self):
        """Génère le monde du jeu"""
        generator = WorldGenerator(LARGEUR_MONDE, HAUTEUR_MONDE)
        self.murs = generator.generer_murs()
        self.objets = generator.generer_objets()
        self.monstres = generator.generer_monstres()
    
    def _initialiser_quetes(self):
        """Initialise les quêtes du jeu"""
        self.quetes = [
            Quete("Trouver une sortie", "Cherchez une clé pour ouvrir la porte"),
            Quete("Rétablir l'électricité", "Trouvez un fusible"),
            Quete("Survivre jusqu'à l'aube", "Restez en vie jusqu'à 6h00")
        ]
    
    def ajouter_message(self, texte, duree=180):
        """Ajoute un message temporaire"""
        self.messages.append((texte, duree))
    
    def mettre_a_jour_camera(self):
        """Met à jour la position de la caméra"""
        self.camera.centrer_sur(self.joueur)
    
    def incrementer_temps(self):
        """Incrémente le temps du jeu"""
        self.temps += 1
    
    def obtenir_heure_actuelle(self):
        """Retourne l'heure actuelle du jeu"""
        heures = (self.temps // 3600) % 24
        minutes = (self.temps // 60) % 60
        return heures, minutes
    
    def mettre_a_jour_messages(self):
        """Met à jour la durée des messages"""
        for i, (texte, duree) in enumerate(self.messages):
            self.messages[i] = (texte, duree - 1)
        self.messages = [(t, d) for t, d in self.messages if d > 0]
    
    def activer_monstres(self):
        """Active tous les monstres"""
        self.monstres_actives = True
        for monstre in self.monstres:
            monstre.actif = True

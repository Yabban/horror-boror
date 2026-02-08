"""Module des entités du jeu - Joueur, Monstre, Objet"""

import pygame
import random
import math
from config import *


class Joueur:
    """Représente le personnage joueur"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.largeur = JOUEUR_LARGEUR
        self.hauteur = JOUEUR_HAUTEUR
        self.vitesse = JOUEUR_VITESSE
        self.sante = JOUEUR_SANTE_MAX
        self.paranoia = 0
        self.inventaire = []
        self.direction = "bas"
        self.en_mouvement = False
        self.animation_frame = 0
        self.animation_timer = 0
        
    def deplacer(self, dx, dy, murs):
        """Déplace le joueur en vérifiant les collisions"""
        nouveau_x = self.x + dx * self.vitesse
        nouveau_y = self.y + dy * self.vitesse
        
        rect_joueur = pygame.Rect(nouveau_x, nouveau_y, self.largeur, self.hauteur)
        
        peut_bouger = True
        for mur in murs:
            if rect_joueur.colliderect(mur):
                peut_bouger = False
                break
        
        if peut_bouger:
            self.x = nouveau_x
            self.y = nouveau_y
            self.en_mouvement = True
            self._mettre_a_jour_direction(dx, dy)
        else:
            self.en_mouvement = False
    
    def _mettre_a_jour_direction(self, dx, dy):
        """Met à jour la direction du joueur"""
        if dx > 0:
            self.direction = "droite"
        elif dx < 0:
            self.direction = "gauche"
        elif dy > 0:
            self.direction = "bas"
        elif dy < 0:
            self.direction = "haut"
    
    def dessiner(self, screen, camera_x, camera_y):
        """Dessine le joueur à l'écran"""
        couleur = self._obtenir_couleur()
            
        pygame.draw.rect(screen, couleur, 
                        (self.x - camera_x, self.y - camera_y, 
                         self.largeur, self.hauteur))
        
        self._dessiner_yeux(screen, camera_x, camera_y)
    
    def _obtenir_couleur(self):
        """Retourne la couleur du joueur en fonction de sa paranoïa"""
        if self.paranoia > 70:
            return VIOLET
        elif self.paranoia > 40:
            return ORANGE
        return BLEU
    
    def _dessiner_yeux(self, screen, camera_x, camera_y):
        """Dessine les yeux du joueur selon sa direction"""
        oeil_x = self.x - camera_x + self.largeur // 2
        oeil_y = self.y - camera_y + self.hauteur // 2
        
        positions = {
            "droite": [(oeil_x + 5, oeil_y - 3), (oeil_x + 5, oeil_y + 3)],
            "gauche": [(oeil_x - 5, oeil_y - 3), (oeil_x - 5, oeil_y + 3)],
            "haut": [(oeil_x - 3, oeil_y - 5), (oeil_x + 3, oeil_y - 5)],
            "bas": [(oeil_x - 3, oeil_y + 5), (oeil_x + 3, oeil_y + 5)]
        }
        
        for pos in positions.get(self.direction, positions["bas"]):
            pygame.draw.circle(screen, BLANC, pos, 3)
    
    def ramasser_objet(self, objet):
        """Ajoute un objet à l'inventaire et applique ses effets"""
        self.inventaire.append(objet)
        self._appliquer_effet_objet(objet)
    
    def _appliquer_effet_objet(self, objet):
        """Applique les effets d'un objet ramassé"""
        effets = {
            "Lampe": lambda: setattr(self, 'paranoia', max(0, self.paranoia - 20)),
            "Médicament": self._effet_medicament,
            "Talisman": lambda: setattr(self, 'paranoia', max(0, self.paranoia - 50))
        }
        
        if objet in effets:
            effets[objet]()
    
    def _effet_medicament(self):
        """Applique l'effet du médicament"""
        self.paranoia = max(0, self.paranoia - 30)
        self.sante = min(100, self.sante + 30)


class Monstre:
    """Représente un ennemi dans le jeu"""
    
    def __init__(self, x, y, type_monstre="errant"):
        self.x = x
        self.y = y
        self.largeur = MONSTRE_LARGEUR
        self.hauteur = MONSTRE_HAUTEUR
        self.vitesse = MONSTRE_VITESSE
        self.type = type_monstre
        self.direction_x = random.choice([-1, 1])
        self.direction_y = random.choice([-1, 1])
        self.timer_changement = 0
        self.actif = False
        
    def deplacer(self, joueur_x, joueur_y, murs):
        """Déplace le monstre selon son type"""
        if not self.actif:
            return
        
        if self.type == "traqueur":
            self._deplacer_traqueur(joueur_x, joueur_y, murs)
        else:
            self._deplacer_errant(murs)
    
    def _deplacer_traqueur(self, joueur_x, joueur_y, murs):
        """Déplacement intelligent qui poursuit le joueur"""
        dx = joueur_x - self.x
        dy = joueur_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            dx = dx / distance * self.vitesse
            dy = dy / distance * self.vitesse
            
            nouveau_x = self.x + dx
            nouveau_y = self.y + dy
            
            if self._peut_se_deplacer(nouveau_x, nouveau_y, murs):
                self.x = nouveau_x
                self.y = nouveau_y
    
    def _deplacer_errant(self, murs):
        """Déplacement aléatoire"""
        self.timer_changement += 1
        if self.timer_changement > 60:
            self.direction_x = random.choice([-1, 0, 1])
            self.direction_y = random.choice([-1, 0, 1])
            self.timer_changement = 0
        
        nouveau_x = self.x + self.direction_x * self.vitesse
        nouveau_y = self.y + self.direction_y * self.vitesse
        
        if self._peut_se_deplacer(nouveau_x, nouveau_y, murs):
            self.x = nouveau_x
            self.y = nouveau_y
        else:
            self.direction_x *= -1
            self.direction_y *= -1
    
    def _peut_se_deplacer(self, nouveau_x, nouveau_y, murs):
        """Vérifie si le monstre peut se déplacer à cette position"""
        rect_monstre = pygame.Rect(nouveau_x, nouveau_y, self.largeur, self.hauteur)
        
        for mur in murs:
            if rect_monstre.colliderect(mur):
                return False
        return True
    
    def dessiner(self, screen, camera_x, camera_y):
        """Dessine le monstre à l'écran"""
        if not self.actif:
            return
            
        couleur = ROUGE if self.type == "traqueur" else ORANGE
        
        # Corps du monstre
        pygame.draw.rect(screen, couleur, 
                        (self.x - camera_x, self.y - camera_y, 
                         self.largeur, self.hauteur))
        
        # Yeux rouges
        pygame.draw.circle(screen, (255, 0, 0), 
                          (int(self.x - camera_x + 10), int(self.y - camera_y + 10)), 4)
        pygame.draw.circle(screen, (255, 0, 0), 
                          (int(self.x - camera_x + 25), int(self.y - camera_y + 10)), 4)
    
    def collision_joueur(self, joueur):
        """Vérifie la collision avec le joueur"""
        rect_monstre = pygame.Rect(self.x, self.y, self.largeur, self.hauteur)
        rect_joueur = pygame.Rect(joueur.x, joueur.y, joueur.largeur, joueur.hauteur)
        return rect_monstre.colliderect(rect_joueur)


class Objet:
    """Représente un objet ramassable dans le jeu"""
    
    COULEURS = {
        "Lampe": JAUNE,
        "Clé": ORANGE,
        "Médicament": VERT,
        "Fusible": ROUGE,
        "Talisman": VIOLET
    }
    
    def __init__(self, x, y, type_objet):
        self.x = x
        self.y = y
        self.type = type_objet
        self.largeur = 20
        self.hauteur = 20
        self.ramasse = False
        
    def dessiner(self, screen, camera_x, camera_y):
        """Dessine l'objet à l'écran"""
        if self.ramasse:
            return
            
        couleur = self.COULEURS.get(self.type, BLANC)
        pygame.draw.rect(screen, couleur, 
                        (self.x - camera_x, self.y - camera_y, 
                         self.largeur, self.hauteur))
        pygame.draw.rect(screen, BLANC, 
                        (self.x - camera_x, self.y - camera_y, 
                         self.largeur, self.hauteur), 2)
    
    def collision_joueur(self, joueur):
        """Vérifie la collision avec le joueur"""
        rect_objet = pygame.Rect(self.x, self.y, self.largeur, self.hauteur)
        rect_joueur = pygame.Rect(joueur.x, joueur.y, joueur.largeur, joueur.hauteur)
        return rect_objet.colliderect(rect_joueur)


class Quete:
    """Représente une quête dans le jeu"""
    
    def __init__(self, nom, description):
        self.nom = nom
        self.description = description
        self.complete = False

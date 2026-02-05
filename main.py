import pygame
import random
import math
from sys import exit
from PIL import Image
# Initialisation de Pygame
pygame.init()

# Constantes
LARGEUR = 1200
HAUTEUR = 800
FPS = 60

# Couleurs
NOIR = (0, 0, 0)
BLANC = (255, 255, 255)
ROUGE = (255, 0, 0)
VERT = (0, 255, 0)
BLEU = (0, 100, 255)
JAUNE = (255, 255, 0)
GRIS = (50, 50, 50)
GRIS_CLAIR = (150, 150, 150)
ORANGE = (255, 165, 0)
VIOLET = (200, 0, 255)

class Joueur:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.largeur = 30
        self.hauteur = 30
        self.vitesse = 4
        self.sante = 100
        self.paranoia = 0
        self.inventaire = []
        self.direction = "bas"
        self.en_mouvement = False
        self.animation_frame = 0
        self.animation_timer = 0
        
    def deplacer(self, dx, dy, murs):
        # Vérifier les collisions avant de bouger
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
            
            # Direction
            if dx > 0:
                self.direction = "droite"
            elif dx < 0:
                self.direction = "gauche"
            elif dy > 0:
                self.direction = "bas"
            elif dy < 0:
                self.direction = "haut"
        else:
            self.en_mouvement = False
    
    def dessiner(self, screen, camera_x, camera_y):
        # Animation simple du personnage
        couleur = BLEU
        if self.paranoia > 70:
            couleur = VIOLET
        elif self.paranoia > 40:
            couleur = ORANGE
            
        pygame.draw.rect(screen, couleur, 
                        (self.x - camera_x, self.y - camera_y, 
                         self.largeur, self.hauteur))
        
        # Yeux (direction)
        oeil_x = self.x - camera_x + self.largeur // 2
        oeil_y = self.y - camera_y + self.hauteur // 2
        
        if self.direction == "droite":
            pygame.draw.circle(screen, BLANC, (oeil_x + 5, oeil_y - 3), 3)
            pygame.draw.circle(screen, BLANC, (oeil_x + 5, oeil_y + 3), 3)
        elif self.direction == "gauche":
            pygame.draw.circle(screen, BLANC, (oeil_x - 5, oeil_y - 3), 3)
            pygame.draw.circle(screen, BLANC, (oeil_x - 5, oeil_y + 3), 3)
        elif self.direction == "haut":
            pygame.draw.circle(screen, BLANC, (oeil_x - 3, oeil_y - 5), 3)
            pygame.draw.circle(screen, BLANC, (oeil_x + 3, oeil_y - 5), 3)
        else:  # bas
            pygame.draw.circle(screen, BLANC, (oeil_x - 3, oeil_y + 5), 3)
            pygame.draw.circle(screen, BLANC, (oeil_x + 3, oeil_y + 5), 3)
    
    def ramasser_objet(self, objet):
        self.inventaire.append(objet)
        
        # Effet des objets
        if objet == "Lampe":
            self.paranoia = max(0, self.paranoia - 20)
        elif objet == "Médicament":
            self.paranoia = max(0, self.paranoia - 30)
            self.sante = min(100, self.sante + 30)
        elif objet == "Clé":
            pass  # Utilisé pour les portes
        elif objet == "Fusible":
            pass  # Pour la quête
        elif objet == "Talisman":
            self.paranoia = max(0, self.paranoia - 50)

class Monstre:
    def __init__(self, x, y, type_monstre="errant"):
        self.x = x
        self.y = y
        self.largeur = 35
        self.hauteur = 35
        self.vitesse = 2
        self.type = type_monstre
        self.direction_x = random.choice([-1, 1])
        self.direction_y = random.choice([-1, 1])
        self.timer_changement = 0
        self.actif = False
        
    def deplacer(self, joueur_x, joueur_y, murs):
        if not self.actif:
            return
            
        if self.type == "traqueur":
            # Poursuit le joueur
            dx = joueur_x - self.x
            dy = joueur_y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance > 0:
                dx = dx / distance * self.vitesse
                dy = dy / distance * self.vitesse
                
                nouveau_x = self.x + dx
                nouveau_y = self.y + dy
                
                rect_monstre = pygame.Rect(nouveau_x, nouveau_y, self.largeur, self.hauteur)
                
                peut_bouger = True
                for mur in murs:
                    if rect_monstre.colliderect(mur):
                        peut_bouger = False
                        break
                
                if peut_bouger:
                    self.x = nouveau_x
                    self.y = nouveau_y
        else:
            # Errant aléatoire
            self.timer_changement += 1
            if self.timer_changement > 60:
                self.direction_x = random.choice([-1, 0, 1])
                self.direction_y = random.choice([-1, 0, 1])
                self.timer_changement = 0
            
            nouveau_x = self.x + self.direction_x * self.vitesse
            nouveau_y = self.y + self.direction_y * self.vitesse
            
            rect_monstre = pygame.Rect(nouveau_x, nouveau_y, self.largeur, self.hauteur)
            
            peut_bouger = True
            for mur in murs:
                if rect_monstre.colliderect(mur):
                    self.direction_x *= -1
                    self.direction_y *= -1
                    peut_bouger = False
                    break
            
            if peut_bouger:
                self.x = nouveau_x
                self.y = nouveau_y
    
    def dessiner(self, screen, camera_x, camera_y):
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
        rect_monstre = pygame.Rect(self.x, self.y, self.largeur, self.hauteur)
        rect_joueur = pygame.Rect(joueur.x, joueur.y, joueur.largeur, joueur.hauteur)
        return rect_monstre.colliderect(rect_joueur)

class Objet:
    def __init__(self, x, y, type_objet):
        self.x = x
        self.y = y
        self.type = type_objet
        self.largeur = 20
        self.hauteur = 20
        self.ramasse = False
        
        # Couleurs selon le type
        self.couleurs = {
            "Lampe": JAUNE,
            "Médicament": VERT,
            "Clé": ORANGE,
            "Fusible": BLEU,
            "Talisman": VIOLET
        }
    
    def dessiner(self, screen, camera_x, camera_y):
        if not self.ramasse:
            couleur = self.couleurs.get(self.type, BLANC)
            pygame.draw.rect(screen, couleur, 
                           (self.x - camera_x, self.y - camera_y, 
                            self.largeur, self.hauteur))
            pygame.draw.rect(screen, BLANC, 
                           (self.x - camera_x, self.y - camera_y, 
                            self.largeur, self.hauteur), 2)
    
    def collision_joueur(self, joueur):
        rect_objet = pygame.Rect(self.x, self.y, self.largeur, self.hauteur)
        rect_joueur = pygame.Rect(joueur.x, joueur.y, joueur.largeur, joueur.hauteur)
        return rect_objet.colliderect(rect_joueur)

class Quete:
    def __init__(self, nom, description, objectif, recompense):
        self.nom = nom
        self.description = description
        self.objectif = objectif
        self.progression = 0
        self.complete = False
        self.recompense = recompense

class Jeu:
    def __init__(self):
        self.screen = pygame.display.set_mode((LARGEUR, HAUTEUR))
        pygame.display.set_caption("L'Usine Maudite - Hamid")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Joueur
        self.joueur = Joueur(100, 100)
        
        # Monde
        self.largeur_monde = 2000
        self.hauteur_monde = 1500
        
        # Caméra
        self.camera_x = 0
        self.camera_y = 0
        
        # Murs de l'usine
        self.murs = self.creer_usine()
        
        # Objets
        self.objets = [
            Objet(300, 200, "Lampe"),
            Objet(150, 450, "Médicament"),
            Objet(800, 300, "Clé"),
            Objet(1200, 600, "Fusible"),
            Objet(1500, 800, "Médicament"),
            Objet(600, 900, "Talisman"),
            Objet(1700, 400, "Lampe"),
            Objet(400, 1100, "Médicament"),
        ]
        
        # Monstres (inactifs au début)
        self.monstres = [
            Monstre(700, 500, "errant"),
            Monstre(1000, 800, "traqueur"),
            Monstre(1400, 300, "errant"),
            Monstre(500, 1000, "traqueur"),
        ]
        
        # Quêtes
        self.quetes = [
            Quete("Trouver la sortie", 
                  "La porte est verrouillée. Trouvez un moyen de l'ouvrir.", 
                  "clé", None),
            Quete("Réparer l'électricité", 
                  "Trouvez le fusible pour rétablir l'électricité.", 
                  "fusible", "monstres_actifs"),
            Quete("Survivre jusqu'à l'aube", 
                  "Tenez bon jusqu'à 6h00. Ne laissez pas la paranoïa vous submerger.", 
                  "temps", None),
        ]
        
        self.quete_actuelle = 0
        self.temps = 22 * 3600  # 22h en secondes
        self.monstres_actives = False
        
        # Interface
        self.font_petite = pygame.font.Font(None, 24)
        self.font_moyenne = pygame.font.Font(None, 32)
        self.font_grande = pygame.font.Font(None, 48)
        
        # Messages
        self.messages = []
        self.afficher_intro()
    
    def creer_usine(self):
        murs = []
        
        # Bordures du monde
        murs.append(pygame.Rect(0, 0, self.largeur_monde, 10))  # Haut
        murs.append(pygame.Rect(0, 0, 10, self.hauteur_monde))  # Gauche
        murs.append(pygame.Rect(0, self.hauteur_monde - 10, self.largeur_monde, 10))  # Bas
        murs.append(pygame.Rect(self.largeur_monde - 10, 0, 10, self.hauteur_monde))  # Droite
        
        # Salles et couloirs (structure d'usine complexe)
        # Salle d'entrée
        murs.append(pygame.Rect(50, 50, 400, 10))
        murs.append(pygame.Rect(50, 250, 400, 10))
        murs.append(pygame.Rect(50, 50, 10, 200))
        
        # Atelier principal
        murs.append(pygame.Rect(500, 100, 10, 400))
        murs.append(pygame.Rect(500, 100, 300, 10))
        murs.append(pygame.Rect(790, 100, 10, 200))
        
        # Salle des machines
        murs.append(pygame.Rect(850, 50, 400, 10))
        murs.append(pygame.Rect(850, 350, 400, 10))
        murs.append(pygame.Rect(1240, 50, 10, 300))
        
        # Zone de stockage
        murs.append(pygame.Rect(100, 400, 600, 10))
        murs.append(pygame.Rect(100, 700, 600, 10))
        murs.append(pygame.Rect(690, 400, 10, 300))
        
        # Entrepôt
        murs.append(pygame.Rect(800, 450, 10, 400))
        murs.append(pygame.Rect(800, 840, 500, 10))
        murs.append(pygame.Rect(1290, 450, 10, 400))
        
        # Vestiaires
        murs.append(pygame.Rect(1350, 100, 300, 10))
        murs.append(pygame.Rect(1350, 300, 300, 10))
        murs.append(pygame.Rect(1640, 100, 10, 200))
        
        # Salle de contrôle
        murs.append(pygame.Rect(1400, 500, 400, 10))
        murs.append(pygame.Rect(1400, 900, 400, 10))
        murs.append(pygame.Rect(1790, 500, 10, 400))
        
        # Obstacles intérieurs (machines, caisses, etc.)
        murs.append(pygame.Rect(200, 150, 60, 60))
        murs.append(pygame.Rect(350, 140, 50, 80))
        murs.append(pygame.Rect(600, 250, 100, 40))
        murs.append(pygame.Rect(900, 180, 80, 80))
        murs.append(pygame.Rect(1100, 200, 60, 100))
        murs.append(pygame.Rect(300, 550, 70, 70))
        murs.append(pygame.Rect(500, 600, 90, 50))
        murs.append(pygame.Rect(1000, 650, 100, 100))
        murs.append(pygame.Rect(1500, 700, 80, 80))
        
        return murs
    
    def afficher_intro(self):
        self.messages.append(("Vous êtes Hamid. Vos amis vous ont mis au défi...", 180))
        self.messages.append(("Passer une nuit dans l'usine désaffectée.", 180))
        self.messages.append(("La porte se verrouille derrière vous...", 180))
    
    def ajouter_message(self, texte, duree=120):
        self.messages.append((texte, duree))
    
    def mettre_a_jour_camera(self):
        # Centrer la caméra sur le joueur
        self.camera_x = self.joueur.x - LARGEUR // 2
        self.camera_y = self.joueur.y - HAUTEUR // 2
        
        # Limites de la caméra
        self.camera_x = max(0, min(self.camera_x, self.largeur_monde - LARGEUR))
        self.camera_y = max(0, min(self.camera_y, self.hauteur_monde - HAUTEUR))
    
    def gerer_evenements(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    # Ramasser un objet proche
                    for objet in self.objets:
                        if not objet.ramasse and objet.collision_joueur(self.joueur):
                            self.joueur.ramasser_objet(objet.type)
                            objet.ramasse = True
                            self.ajouter_message(f"Vous avez ramassé: {objet.type}")
                            
                            # Vérifier quêtes
                            if objet.type == "Clé" and not self.quetes[0].complete:
                                self.quetes[0].complete = True
                                self.ajouter_message("QUÊTE COMPLÉTÉE: Trouver la sortie!")
                                self.quete_actuelle = 1
                            elif objet.type == "Fusible" and not self.quetes[1].complete:
                                self.quetes[1].complete = True
                                self.ajouter_message("QUÊTE COMPLÉTÉE: Électricité rétablie!")
                                self.ajouter_message("⚠️ ATTENTION! Les monstres se réveillent...")
                                self.monstres_actives = True
                                self.quete_actuelle = 2
                                for monstre in self.monstres:
                                    monstre.actif = True
    
    def mettre_a_jour(self):
        # Déplacement ZQSD
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0
        
        if keys[pygame.K_z] or keys[pygame.K_w]:
            dy = -1
        if keys[pygame.K_s]:
            dy = 1
        if keys[pygame.K_q] or keys[pygame.K_a]:
            dx = -1
        if keys[pygame.K_d]:
            dx = 1
        
        if dx != 0 or dy != 0:
            self.joueur.deplacer(dx, dy, self.murs)
        
        # Mise à jour monstres
        if self.monstres_actives:
            for monstre in self.monstres:
                monstre.deplacer(self.joueur.x, self.joueur.y, self.murs)
                
                # Collision avec joueur
                if monstre.collision_joueur(self.joueur):
                    self.joueur.sante -= 1
                    self.joueur.paranoia += 0.5
        
        # Paranoïa augmente avec le temps
        self.joueur.paranoia += 0.01
        
        # Réduction paranoïa avec objets spéciaux
        if "Talisman" in self.joueur.inventaire:
            self.joueur.paranoia = max(0, self.joueur.paranoia - 0.02)
        
        # Game Over conditions
        if self.joueur.sante <= 0:
            self.game_over("Vous êtes mort...")
        elif self.joueur.paranoia >= 100:
            self.game_over("La folie vous a consumé...")
        
        # Temps
        self.temps += 1.5
        heures = (self.temps // 3600) % 24
        
        # Victoire
        if heures >= 6 and heures < 22 and self.quetes[1].complete:
            self.victoire()
        
        # Messages
        for i, (texte, duree) in enumerate(self.messages):
            self.messages[i] = (texte, duree - 1)
        self.messages = [(t, d) for t, d in self.messages if d > 0]
        
        self.mettre_a_jour_camera()
    
    def dessiner(self):
        self.screen.fill(NOIR)
        
        # Sol
        pygame.draw.rect(self.screen, GRIS, (0, 0, LARGEUR, HAUTEUR))
        
        # Murs
        for mur in self.murs:
            pygame.draw.rect(self.screen, GRIS_CLAIR, 
                           (mur.x - self.camera_x, mur.y - self.camera_y, 
                            mur.width, mur.height))
        
        # Objets
        for objet in self.objets:
            objet.dessiner(self.screen, self.camera_x, self.camera_y)
        
        # Monstres
        for monstre in self.monstres:
            monstre.dessiner(self.screen, self.camera_x, self.camera_y)
        
        # Joueur
        self.joueur.dessiner(self.screen, self.camera_x, self.camera_y)
        
        # Interface
        self.dessiner_interface()
        
        pygame.display.flip()
    
    def dessiner_interface(self):
        # Fond semi-transparent pour l'interface
        interface_bg = pygame.Surface((LARGEUR, 150))
        interface_bg.set_alpha(200)
        interface_bg.fill(NOIR)
        self.screen.blit(interface_bg, (0, HAUTEUR - 150))
        
        # Santé
        couleur_sante = VERT if self.joueur.sante > 50 else ORANGE if self.joueur.sante > 25 else ROUGE
        pygame.draw.rect(self.screen, GRIS, (20, HAUTEUR - 130, 200, 25))
        pygame.draw.rect(self.screen, couleur_sante, 
                        (20, HAUTEUR - 130, self.joueur.sante * 2, 25))
        texte_sante = self.font_petite.render(f"Santé: {int(self.joueur.sante)}%", True, BLANC)
        self.screen.blit(texte_sante, (25, HAUTEUR - 127))
        
        # Paranoïa
        couleur_paranoia = VERT if self.joueur.paranoia < 40 else ORANGE if self.joueur.paranoia < 70 else ROUGE
        pygame.draw.rect(self.screen, GRIS, (20, HAUTEUR - 100, 200, 25))
        pygame.draw.rect(self.screen, couleur_paranoia, 
                        (20, HAUTEUR - 100, min(200, self.joueur.paranoia * 2), 25))
        texte_paranoia = self.font_petite.render(f"Paranoïa: {int(self.joueur.paranoia)}%", True, BLANC)
        self.screen.blit(texte_paranoia, (25, HAUTEUR - 97))
        
        # Temps
        heures = (self.temps // 3600) % 24
        minutes = (self.temps // 60) % 60
        texte_temps = self.font_moyenne.render(f"Heure: {heures:02d}:{minutes:02d}", True, JAUNE)
        self.screen.blit(texte_temps, (20, HAUTEUR - 65))
        
        # Inventaire
        texte_inv = self.font_petite.render("Inventaire:", True, BLANC)
        self.screen.blit(texte_inv, (250, HAUTEUR - 130))
        for i, objet in enumerate(self.joueur.inventaire):
            texte_objet = self.font_petite.render(f"• {objet}", True, JAUNE)
            self.screen.blit(texte_objet, (250, HAUTEUR - 105 + i * 20))
        
        # Quête actuelle
        if self.quete_actuelle < len(self.quetes):
            quete = self.quetes[self.quete_actuelle]
            texte_quete = self.font_petite.render(f"Quête: {quete.nom}", True, ORANGE)
            self.screen.blit(texte_quete, (550, HAUTEUR - 130))
            texte_desc = self.font_petite.render(quete.description, True, BLANC)
            self.screen.blit(texte_desc, (550, HAUTEUR - 105))
        
        # Contrôles
        texte_ctrl = self.font_petite.render("ZQSD: Bouger | E: Ramasser", True, GRIS_CLAIR)
        self.screen.blit(texte_ctrl, (LARGEUR - 300, HAUTEUR - 30))
        
        # Messages
        for i, (texte, duree) in enumerate(self.messages[-3:]):
            alpha = min(255, duree * 2)
            surface_msg = self.font_moyenne.render(texte, True, JAUNE)
            surface_msg.set_alpha(alpha)
            self.screen.blit(surface_msg, (LARGEUR // 2 - 300, 50 + i * 40))
    
    def game_over(self, raison):
        self.screen.fill(NOIR)
        texte_go = self.font_grande.render("GAME OVER", True, ROUGE)
        texte_raison = self.font_moyenne.render(raison, True, BLANC)
        self.screen.blit(texte_go, (LARGEUR // 2 - 150, HAUTEUR // 2 - 50))
        self.screen.blit(texte_raison, (LARGEUR // 2 - 200, HAUTEUR // 2 + 20))
        pygame.display.flip()
        pygame.time.wait(5000)
        self.running = False
    
    def victoire(self):
        self.screen.fill(NOIR)
        texte_vic = self.font_grande.render("VICTOIRE !", True, VERT)
        texte_msg = self.font_moyenne.render("Vous avez survécu jusqu'à l'aube !", True, BLANC)
        self.screen.blit(texte_vic, (LARGEUR // 2 - 150, HAUTEUR // 2 - 50))
        self.screen.blit(texte_msg, (LARGEUR // 2 - 250, HAUTEUR // 2 + 20))
        pygame.display.flip()
        pygame.time.wait(5000)
        self.running = False
    
    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.gerer_evenements()
            self.mettre_a_jour()
            self.dessiner()
        
        pygame.quit()

if __name__ == "__main__":
    jeu = Jeu()

    jeu.run()


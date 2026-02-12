# 🔦 QUÊTE ÉLECTRIQUE - Instructions d'installation

## ✅ Ce qui a été modifié dans main_refactored.py

### Nouvelles fonctionnalités ajoutées :

1. **Le jeu commence dans le NOIR** (`lumiere_eteinte = True`)
2. **2 panneaux électriques** à trouver et activer
3. **Système d'obscurité** - vous ne voyez presque rien
4. **Quand les 2 panneaux sont activés** → La lumière revient !

## 🎮 Comment jouer

### Au démarrage :
- Le jeu est très sombre
- Message : "Il fait noir ! Trouvez les 2 panneaux électriques"

### Trouver les panneaux :
- **Panneau 1** : Position x=150, y=400 (à gauche)
- **Panneau 2** : Position x=1250, y=600 (à droite en bas)

⚠️ **IMPORTANT** : Ajustez ces positions selon VOTRE carte dans le code !

### Activer un panneau :
1. Approchez-vous du panneau (dans un rayon de 60 pixels)
2. Vous verrez "Appuyez sur E"
3. Appuyez sur **E**
4. Le panneau devient VERT et la LED s'allume

### Quand les 2 panneaux sont activés :
✨ **La lumière revient !**
- L'obscurité disparaît
- Vous pouvez voir les monstres
- Message : "Les lumières sont revenues !"

## 🔧 Ajustements à faire dans VOTRE code

### 1. Positions des panneaux électriques

Ouvrez `main_refactored.py` et modifiez la fonction `_creer_panneaux_electricite()` :

```python
def _creer_panneaux_electricite(self):
    """Crée les 2 panneaux électriques à activer"""
    panneaux = []
    
    # Panneau 1 - AJUSTEZ x et y selon votre carte
    panneaux.append({
        'x': 150,      # ← Changez cette valeur
        'y': 400,      # ← Changez cette valeur
        'largeur': 40,
        'hauteur': 60,
        'actif': False,
        'nom': 'Panneau 1'
    })
    
    # Panneau 2 - AJUSTEZ x et y selon votre carte
    panneaux.append({
        'x': 1250,     # ← Changez cette valeur
        'y': 600,      # ← Changez cette valeur
        'largeur': 40,
        'hauteur': 60,
        'actif': False,
        'nom': 'Panneau 2'
    })
    
    return panneaux
```

### 2. Effet d'obscurité dans renderer.py (OPTIONNEL)

Si vous voulez un meilleur effet d'obscurité, ajoutez dans `renderer.py` :

```python
def dessiner_monde_obscur(self, state):
    """Dessine le monde dans l'obscurité"""
    # Fond noir
    self.screen.fill((0, 0, 0))
    
    # Murs très sombres
    for mur in state.murs:
        pygame.draw.rect(self.screen, (30, 30, 30),
                        (mur.x - state.camera.x, 
                         mur.y - state.camera.y,
                         mur.width, mur.height))
    
    # Joueur visible (faiblement)
    state.joueur.dessiner(self.screen, state.camera.x, state.camera.y)
    
    # Objets très faiblement visibles
    for objet in state.objets:
        if not objet.ramasse:
            # Dessiner avec couleur très sombre
            pass
    
    # Monstres INVISIBLES (ou juste une aura si proches)
    for monstre in state.monstres:
        if monstre.actif:
            distance = ((monstre.x - state.joueur.x)**2 + 
                       (monstre.y - state.joueur.y)**2)**0.5
            if distance < 100:
                # Dessiner une aura rouge
                pygame.draw.circle(self.screen, (50, 0, 0),
                                 (int(monstre.x - state.camera.x),
                                  int(monstre.y - state.camera.y)), 30)
```

⚠️ **Si vous n'avez pas le temps**, le code utilise automatiquement un fallback :
- Il dessine le monde normalement
- Puis ajoute une couche noire semi-transparente par dessus

## 📊 Indicateurs visuels

### Panneaux électriques :
- **Gris** = Non activé
- **Vert** = Activé
- **LED rouge** = Inactif
- **LED verte** = Actif

### Compteur en haut à droite :
- "Panneaux: 0/2" (jaune)
- "Panneaux: 1/2" (jaune)
- "Panneaux: 2/2" (vert) ✅

## 🐛 Résolution de problèmes

### "AttributeError: dessiner_monde_obscur"
→ C'est normal ! Le fallback s'active automatiquement avec la couche noire

### Les panneaux ne s'affichent pas
→ Vérifiez que les positions x, y sont dans votre carte (pas dans un mur)

### Le jeu reste noir même après activation
→ Vérifiez que `self.panneaux_actives >= 2` est True dans le code

### "Appuyez sur E" ne s'affiche pas
→ Rapprochez-vous plus du panneau (distance < 60)

## 🎯 Résumé

**Ce qui fonctionne automatiquement :**
✅ Jeu commence dans le noir
✅ 2 panneaux électriques à activer
✅ Compteur affiché
✅ Messages de progression
✅ Lumière revient après activation des 2 panneaux
✅ Effet d'obscurité (avec fallback automatique)

**Ce que VOUS devez ajuster :**
⚠️ Les positions x, y des 2 panneaux selon votre carte

Bon jeu ! 🎮👻

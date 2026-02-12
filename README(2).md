# Jeu de Survie - Version Modulaire

## Structure du projet

Le code a été refactorisé pour une meilleure organisation et maintenabilité.

### Architecture

```
.
├── main_refactored.py    # Point d'entrée principal
├── config.py             # Configuration et constantes
├── entities.py           # Entités du jeu (Joueur, Monstre, Objet, Quête)
├── world.py              # Génération du monde et gestion de la caméra
├── game_state.py         # État global du jeu
├── game_logic.py         # Logique du jeu
├── renderer.py           # Rendu graphique
└── ui.py                 # Interface utilisateur
```

### Description des modules

#### `config.py`
Contient toutes les constantes du jeu :
- Dimensions de la fenêtre
- Couleurs
- Paramètres des entités
- Paramètres du monde

#### `entities.py`
Définit les entités du jeu :
- **Joueur** : Déplacement, stats, inventaire
- **Monstre** : Comportements (traqueur/errant), déplacement
- **Objet** : Objets ramassables
- **Quête** : Structure des quêtes

#### `world.py`
Gestion du monde :
- **WorldGenerator** : Génération procédurale (murs, objets, monstres)
- **Camera** : Système de caméra suivant le joueur

#### `game_state.py`
État global du jeu :
- Gestion du temps
- Messages temporaires
- Quêtes
- Initialisation du monde

#### `game_logic.py`
Logique du jeu :
- Gestion des entrées
- Mise à jour des monstres
- Système de paranoïa
- Conditions de victoire/défaite
- Gestion des quêtes

#### `renderer.py`
Rendu graphique :
- Dessin du monde
- Murs, objets, monstres, joueur

#### `ui.py`
Interface utilisateur :
- Barres de stats
- Inventaire
- Quêtes
- Messages
- Écrans de fin

#### `main_refactored.py`
Boucle principale :
- Initialisation de Pygame
- Orchestration des modules
- Boucle de jeu

## Avantages de cette architecture

### 1. **Séparation des responsabilités**
Chaque module a une fonction claire et unique.

### 2. **Maintenabilité**
Les modifications sont isolées dans des modules spécifiques.

### 3. **Testabilité**
Chaque module peut être testé indépendamment.

### 4. **Extensibilité**
Facile d'ajouter de nouvelles fonctionnalités :
- Nouveaux types de monstres → `entities.py`
- Nouveaux objets → `entities.py`
- Nouveaux éléments d'UI → `ui.py`
- Nouvelles mécaniques de jeu → `game_logic.py`

### 5. **Lisibilité**
Code plus court et plus clair dans chaque fichier.

### 6. **Réutilisabilité**
Les modules peuvent être réutilisés dans d'autres projets.

## Comment exécuter

```bash
python main_refactored.py
```

## Comment ajouter de nouvelles fonctionnalités

### Ajouter un nouveau type d'objet
1. Dans `entities.py`, ajouter la couleur dans `Objet.COULEURS`
2. Dans `entities.py`, ajouter l'effet dans `Joueur._appliquer_effet_objet()`
3. Dans `world.py`, ajouter le type dans `WorldGenerator.generer_objets()`

### Ajouter un nouveau type de monstre
1. Dans `entities.py`, créer une nouvelle méthode de déplacement dans `Monstre`
2. Dans `world.py`, générer ce type dans `WorldGenerator.generer_monstres()`

### Ajouter une nouvelle quête
1. Dans `game_state.py`, ajouter la quête dans `_initialiser_quetes()`
2. Dans `game_logic.py`, ajouter la logique dans `_verifier_quetes()`

## Comparaison avec l'ancienne structure

| Aspect | Ancien code | Nouveau code |
|--------|-------------|--------------|
| Fichiers | 1 (580 lignes) | 8 modules séparés |
| Lisibilité | ★★☆☆☆ | ★★★★★ |
| Maintenabilité | ★★☆☆☆ | ★★★★★ |
| Testabilité | ★☆☆☆☆ | ★★★★☆ |
| Extensibilité | ★★☆☆☆ | ★★★★★ |

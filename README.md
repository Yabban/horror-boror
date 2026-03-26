# Survie jusqu'à l'aube

Jeu de survie horror en vue de dessus réalisé en Python/Pygame.

## Installation

```bash
pip install -r requirements.txt
```

## Lancer le jeu

```bash
cd sources
python main.py
```

## Contrôles

| Touche | Action |
|--------|--------|
| Z / Q / S / D | Déplacer le personnage |
| E | Activer panneau / Ouvrir boîte / Ramasser objet |
| R | Ouvrir / Fermer l'inventaire |
| Clic gauche | Lancer une brique vers le curseur |

## Objectif

Survivre jusqu'à 6h00 du matin.

1. Trouvez les **2 panneaux électriques** pour rallumer la lumière (touche E près d'un panneau).
2. Changez la **batterie toutes les 1h30** (in-game) sinon la lumière s'éteint.
3. Trouvez le **Fusible** pour rétablir l'électricité et compléter la quête principale.
4. Récupérez la **Clé** pour ouvrir la sortie.
5. Ouvrez les **boîtes mystères** — 1 chance sur 3 de tomber sur un Boogeyman (+50 paranoïa) !

## Objets

| Objet | Effet |
|-------|-------|
| Médicament | +30 santé / −30 paranoïa |
| Talisman | −50 paranoïa instantané |
| Batterie | Recharge les panneaux électriques |
| Brique | Lancer sur un monstre = stun 30 secondes |
| Clé | Complète la quête "Trouver une sortie" |
| Fusible | Complète la quête "Rétablir l'électricité" |

## Ennemis

- **Traqueur** (rouge) : vous pourchasse directement, devient de plus en plus rapide avec le temps.
- **Errant** (fantôme) : se déplace aléatoirement, aussi de plus en plus agressif.

> ⚠️ Les monstres deviennent progressivement plus rapides et infligent plus de dégâts au fil du temps.

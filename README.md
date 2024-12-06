# IA-Project - Puzzle Solver

Ce projet est un solveur de puzzle basé sur l'intelligence artificielle. Il utilise différentes techniques d'IA pour résoudre des puzzles spécifiques en fonction des règles définies.

## Version

- **Version actuelle** : 1.0.0
- **Date de création** : 2024-12-06
- **Langage** : Python 3.12.5

## Prérequis

Avant d'exécuter ce projet, vous devez avoir Python 3.12 installé sur votre machine. Vous pouvez vérifier cela en utilisant la commande suivante :

```bash
python --version
```

Le projet nécessite également l'installation de certaines dépendances. Nous recommandons d'utiliser un environnement virtuel (virtualenv) pour gérer les dépendances.

Installation et Configuration
Cloner le dépôt :

```bash
git clone https://github.com/dadflip/IA-Project.git
```

Activer le virtualenv :

Pour éviter les conflits de versions de paquets, nous vous recommandons de créer un environnement virtuel Python.

Créez un environnement virtuel :

```bash
python -m venv venv
```

Activez l'environnement virtuel :
Sur Windows :
```bash
venv\Scripts\activate
```
Sur Mac/Linux :
```bash
source venv/bin/activate
```

Installer les dépendances :

Une fois l'environnement virtuel activé, installez les dépendances nécessaires à l'aide de pip :

```bash
pip install -r requirements.txt
```
Le fichier requirements.txt contient toutes les bibliothèques Python nécessaires au projet.

Désactiver le virtualenv (optionnel) :

Lorsque vous avez terminé de travailler sur le projet, vous pouvez désactiver l'environnement virtuel avec la commande suivante :

```bash
deactivate
```


Exécution du Code
Pour exécuter le projet, suivez ces étapes :

Lancer l'exécution du code :

Une fois toutes les dépendances installées, vous pouvez exécuter le script principal pour résoudre un puzzle :

```bash
python app.py
```


## Résumé de la structure des fichiers

### Répertoires :

- **.venv** : Environnement virtuel du projet.
- **utils** : Fonctions utilitaires.
- **x-archive** : Archive de fichiers anciens.
- **_ai_** : Logique de l'IA (apprentissage et résolution).
- **_io_** : Gestion des entrées/sorties (fichiers, affichage).
- **_ui_** : Interface utilisateur (affichage graphique).
- **__pycache__** : Fichiers Python compilés.

### Fichiers :

- **.gitattributes** : Configuration spécifique à Git.
- **app.py** : Point d'entrée principal du projet.
- **constants.py** : Définition des constantes utilisées dans le projet.
- **README.md** : Documentation du projet.
- **requirements.txt** : Liste des dépendances du projet.

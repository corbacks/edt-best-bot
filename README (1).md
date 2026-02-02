# 🎓 EDT Bot L2 INFO - Ultra Version 2.0

<div align="center">

![Version](https://img.shields.io/badge/version-2.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

**Bot d'emploi du temps automatique avec génération d'images style ADE Calendar**

[Installation](#-installation-rapide) • [Fonctionnalités](#-fonctionnalités) • [Configuration](#️-configuration) • [Usage](#-utilisation)

</div>

---

## 📋 Table des Matières

- [Vue d'ensemble](#-vue-densemble)
- [Fonctionnalités](#-fonctionnalités)
- [Installation](#-installation-rapide)
- [Configuration](#️-configuration)
- [Utilisation](#-utilisation)
- [Personnalisation](#-personnalisation)
- [Dépannage](#-dépannage)
- [Contribuer](#-contribuer)

---

## 🌟 Vue d'ensemble

EDT Bot v2.0 est un système automatisé de génération et diffusion d'emplois du temps pour les étudiants L2 Informatique de l'Université du Havre. Il transforme les données iCal en **images calendrier professionnelles** et les envoie automatiquement sur Discord.

### ✨ Points Forts

- 🎨 **Design professionnel** inspiré d'ADE Calendar
- 🌈 **Codes couleur intelligents** par type de cours
- ⏰ **Ligne temps réel** indiquant l'heure actuelle
- 📊 **Statistiques avancées** (nombre de cours, heures totales, répartition)
- 🚀 **Déploiement automatique** via GitHub Actions
- 🔄 **Retry robuste** avec backoff exponentiel
- 🌍 **Gestion fuseau horaire** (été/hiver) automatique

---

## 🎯 Fonctionnalités

### 🎨 Génération Visuelle

| Fonctionnalité | Description |
|----------------|-------------|
| **Grille horaire** | Vue hebdomadaire 7h-20h, Lundi à Vendredi |
| **Codes couleur** | Violet (CM), Orange (TD), Bleu (TP), Rouge (Examen), Vert (Projet) |
| **Bordures stylisées** | Bordure gauche épaisse colorée par type |
| **Dégradés** | Effets visuels modernes sur fond et cards |
| **Ombres portées** | Profondeur visuelle pour les cours |
| **Badges** | Type de cours en badge, durée affichée |
| **Ligne actuelle** | Indicateur rouge de l'heure en cours |

### 📊 Statistiques

- ✅ Nombre total de cours
- ✅ Heures totales de la semaine
- ✅ Moyenne de cours par jour
- ✅ Répartition par type (CM/TD/TP/etc.)
- ✅ Jour le plus chargé
- ✅ Première/dernière heure de cours

### 🤖 Automatisation

- ✅ **Dimanche 18h** : Envoie la semaine suivante
- ✅ **Mercredi 6h** : Rappel de la semaine courante
- ✅ Déclenchement manuel possible
- ✅ Retry automatique en cas d'échec
- ✅ Logs détaillés

---

## 🚀 Installation Rapide

### Prérequis

- Compte GitHub
- Serveur Discord avec webhooks configurés
- Python 3.11+ (pour tests locaux)

### Étapes d'Installation

#### 1️⃣ Créer le Repository

```bash
# Sur GitHub, créez un nouveau repository public ou privé
# Nommez-le par exemple "edt-bot-l2-info"
```

#### 2️⃣ Cloner et Configurer

```bash
# Cloner le repo
git clone https://github.com/VOTRE-USERNAME/edt-bot-l2-info.git
cd edt-bot-l2-info

# Créer la structure
mkdir -p .github/workflows

# Copier les fichiers
cp edt_bot_ultimate.py ./
cp .github_workflows_edt.yml .github/workflows/edt.yml
```

#### 3️⃣ Configuration des Webhooks

**Option A : Secrets GitHub (Recommandé 🔒)**

```bash
# Dans GitHub : Settings > Secrets and variables > Actions > New repository secret

Créez ces secrets :
- WEBHOOK_CM  : URL webhook salon CM Communs
- WEBHOOK_G1  : URL webhook salon Groupe 1
- WEBHOOK_G2  : URL webhook salon Groupe 2
- WEBHOOK_G3  : URL webhook salon Groupe 3
```

Puis modifiez `edt_bot_ultimate.py` ligne 96 :
```python
WEBHOOKS = {
    "CM Communs": os.environ.get("WEBHOOK_CM"),
    "Groupe 1": os.environ.get("WEBHOOK_G1"),
    "Groupe 2": os.environ.get("WEBHOOK_G2"),
    "Groupe 3": os.environ.get("WEBHOOK_G3")
}
```

**Option B : Hardcodé (Plus simple mais moins sécurisé)**

Remplacez directement les URLs dans `edt_bot_ultimate.py` lignes 96-101.

#### 4️⃣ Push et Activation

```bash
git add .
git commit -m "🎓 Initial commit - EDT Bot Ultra v2.0"
git push origin main

# GitHub Actions s'active automatiquement !
```

---

## ⚙️ Configuration

### 📅 Horaires d'Envoi

Modifiez `.github/workflows/edt.yml` :

```yaml
schedule:
  # Dimanche 18h
  - cron: "0 17 * * 0"  # Hiver
  - cron: "0 16 * * 0"  # Été (décommenter en mars)
  
  # Mercredi 6h
  - cron: "0 5 * * 3"   # Hiver
  - cron: "0 4 * * 3"   # Été (décommenter en mars)
```

### 🎨 Personnalisation Visuelle

Dans `edt_bot_ultimate.py`, modifiez la section **COLORS** (lignes 55-77) :

```python
COLORS = {
    'background': (20, 23, 36),      # Fond
    'header': (30, 35, 52),          # Header
    'text': (255, 255, 255),         # Texte
    # ...
}

COURSE_COLORS = {
    'CM': {
        'main': (138, 80, 183),      # Violet
        # Changez ces valeurs RGB !
    },
    # ...
}
```

### 📏 Dimensions de l'Image

Ligne 808 de `edt_bot_ultimate.py` :

```python
WIDTH = 1600   # Largeur (default: 1600px)
HEIGHT = 1100  # Hauteur (default: 1100px)
```

### ⏰ Plage Horaire

Ligne 816 :

```python
START_HOUR = 7    # Début (default: 7h)
END_HOUR = 20     # Fin (default: 20h)
```

---

## 💻 Utilisation

### Automatique

Le bot s'exécute automatiquement :
- **Dimanche à 18h** : Envoie la semaine prochaine
- **Mercredi à 6h** : Rappel semaine en cours

### Manuel

1. Allez dans **Actions** sur GitHub
2. Sélectionnez **EDT Bot L2 INFO - Ultra v2.0**
3. Cliquez sur **Run workflow**
4. Choisissez les options :
   - `force_send` : true
   - `test_group` : Groupe à tester (ou "Tous")
   - `week_mode` : auto/current/next
5. Cliquez **Run workflow**

### Local (Tests)

```bash
# Installation des dépendances
pip install requests Pillow

# Exécution
python edt_bot_ultimate.py

# Avec paramètres
WEEK_MODE=current python edt_bot_ultimate.py
```

---

## 🎨 Personnalisation

### Thèmes de Couleurs

#### Thème Light Mode

```python
COLORS = {
    'background': (255, 255, 255),
    'header': (240, 242, 245),
    'text': (30, 33, 46),
    # ...
}
```

#### Thème Universitaire

```python
COLORS = {
    'background': (245, 247, 250),
    'header': (41, 98, 255),  # Bleu uni
    # ...
}
```

### Ajouter un Type de Cours

```python
# 1. Ajouter la couleur
COURSE_COLORS['Soutenance'] = {
    'main': (155, 89, 182),
    'light': (175, 110, 200),
    'dark': (135, 70, 165)
}

# 2. Ajouter l'emoji
COURSE_EMOJI['Soutenance'] = '🎤'
```

### Modifier les Polices

Ligne 740 :

```python
fonts['title'] = ImageFont.truetype("/chemin/vers/police.ttf", 28)
```

---

## 🐛 Dépannage

### ❌ Erreur : "Pillow not found"

```bash
pip install Pillow
```

### ❌ Erreur : "Webhook invalid"

Vérifiez que :
1. Les URLs webhook sont correctes
2. Le bot Discord a les permissions
3. Les secrets GitHub sont bien configurés

### ❌ Pas de cours affichés

Vérifiez :
1. Les URLs iCal sont à jour
2. La semaine contient des cours
3. Les logs GitHub Actions

### ❌ Images floues

Augmentez les dimensions :
```python
WIDTH = 1920
HEIGHT = 1200
```

### ⏰ Mauvais fuseau horaire

Le bot gère automatiquement été/hiver. Si problème :
1. Vérifiez les crons dans le workflow
2. Activez/désactivez selon la saison

---

## 📊 Exemples de Rendus

### Vue Normale
- Grille complète 5 jours
- Tous les cours colorés
- Statistiques en footer

### Vue Chargée (15+ cours)
- Adaptation automatique
- Texte optimisé
- Pas de débordement

### Vue Vide
- Message "Pas de cours"
- Design minimaliste
- Incitation au repos 😎

---

## 🔐 Sécurité

### Bonnes Pratiques

✅ **Utilisez les secrets GitHub** pour les webhooks
✅ **Ne commitez JAMAIS** les URLs webhook en clair
✅ **Limitez les permissions** du workflow
✅ **Activez la vérification 2FA** sur GitHub
✅ **Surveillez les logs** régulièrement

### Protection des Webhooks

```yaml
# Dans .github/workflows/edt.yml
env:
  WEBHOOK_CM: ${{ secrets.WEBHOOK_CM }}
  # etc...
```

---

## 📈 Performance

- ⚡ Génération image : ~2-3 secondes
- ⚡ Envoi Discord : ~1 seconde
- ⚡ Total par groupe : ~5 secondes
- ⚡ 4 groupes : ~20 secondes

---

## 🤝 Contribuer

Les contributions sont les bienvenues !

1. Fork le projet
2. Créez une branche (`git checkout -b feature/amélioration`)
3. Commit (`git commit -m '✨ Ajout fonctionnalité'`)
4. Push (`git push origin feature/amélioration`)
5. Ouvrez une Pull Request

### Idées de Contributions

- [ ] Support mode clair/sombre automatique
- [ ] Export PDF en plus de PNG
- [ ] Vue mensuelle
- [ ] Notifications changements EDT
- [ ] Support multi-universités
- [ ] Interface web de configuration

---

## 📜 Licence

MIT License - Libre d'utilisation et modification

---

## 💡 Crédits

- **Développé pour** : Étudiants L2 INFO - Université du Havre
- **Inspiré par** : ADE Calendar, modern calendar UIs
- **Technologies** : Python, Pillow, GitHub Actions, Discord

---

## 📞 Support

- 🐛 **Issues GitHub** : Pour les bugs et suggestions
- 💬 **Discord** : Pour les questions rapides
- 📧 **Email** : Pour le support technique

---

<div align="center">

**Fait avec ❤️ pour les étudiants L2 INFO**

⭐ N'oubliez pas de star le repo si ça vous aide ! ⭐

</div>

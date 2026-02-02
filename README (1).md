# 🎓 Bot EDT L2 INFO - Version Visuelle Améliorée

## 📋 Vue d'ensemble

Cette version améliorée du bot EDT transforme votre emploi du temps en **images de calendrier visuelles** similaires à ADE Calendar, offrant une expérience beaucoup plus professionnelle et agréable que les embeds Discord classiques.

## ✨ Nouvelles Fonctionnalités

### 🎨 Visualisation Type Calendrier
- **Grille horaire** de 7h00 à 19h00
- **5 colonnes** pour les jours de la semaine (Lundi à Vendredi)
- **Codes couleur** par type de cours :
  - 🟣 **Violet** : CM (Cours Magistraux)
  - 🟠 **Orange** : TD (Travaux Dirigés)
  - 🔵 **Bleu** : TP (Travaux Pratiques)
  - 🟢 **Vert** : Projets
  - 🟡 **Orange foncé** : Examens

### 📍 Indicateurs Visuels
- **Ligne rouge** indiquant l'heure actuelle (pour la semaine en cours)
- **Bordure colorée** à gauche de chaque cours selon son type
- **Fond sombre moderne** style ADE Calendar
- **Headers clairs** avec jour et date

### 📊 Informations Affichées sur Chaque Cours
- ⏰ **Horaires** (début - fin)
- 📖 **Matière** et type de cours
- 🏛️ **Salle** (si disponible)
- 🎯 Informations complémentaires

## 🔄 Différences avec l'Ancienne Version

| Aspect | Ancienne Version | Nouvelle Version |
|--------|------------------|------------------|
| **Format** | Embed Discord texte | Image PNG calendrier |
| **Visuel** | Liste textuelle | Grille horaire graphique |
| **Couleurs** | Embed uni | Codes couleur par type |
| **Lisibilité** | Moyenne | Excellente |
| **Heure actuelle** | Non | Ligne rouge indicative |
| **Style** | Basique | Professionnel (type ADE) |

## 📦 Installation

### Prérequis
```bash
pip install requests Pillow
```

### Structure des Fichiers
```
votre-repo/
├── edt_script_improved.py    # Script principal amélioré
├── edt_improved.yml          # GitHub Actions workflow
└── README.md                 # Ce fichier
```

## 🚀 Utilisation

### Automatique (GitHub Actions)
Le bot s'exécute automatiquement :
- **Dimanche à 18h** (Paris) → Envoie la semaine suivante
- **Mercredi à 6h** (Paris) → Envoie la semaine en cours

### Manuel
```bash
# Exécution locale
python edt_script_improved.py

# Avec mode de semaine spécifique
WEEK_MODE=current python edt_script_improved.py  # Semaine courante
WEEK_MODE=next python edt_script_improved.py     # Semaine suivante
```

## ⚙️ Configuration

### Webhooks Discord
Les webhooks sont configurés dans le script pour chaque groupe :
```python
WEBHOOKS = {
    "CM Communs": "https://discord.com/api/webhooks/...",
    "Groupe 1": "https://discord.com/api/webhooks/...",
    "Groupe 2": "https://discord.com/api/webhooks/...",
    "Groupe 3": "https://discord.com/api/webhooks/..."
}
```

### IDs des Rôles
Pour les mentions de groupe :
```python
ROLE_IDS = {
    "CM Communs": "1418998954380759141",
    "Groupe 1": "1419000148528205955",
    "Groupe 2": "1419000272776069303",
    "Groupe 3": "1419000449016660071"
}
```

### Personnalisation des Couleurs
Vous pouvez modifier les couleurs dans `COURSE_COLORS` :
```python
COURSE_COLORS = {
    'CM': (138, 80, 183),      # RGB pour CM
    'TD': (255, 167, 38),      # RGB pour TD
    'TP': (52, 152, 219),      # RGB pour TP
    # ...
}
```

## 🎨 Exemples de Rendus

L'EDT généré ressemble à votre capture d'écran ADE Calendar avec :
- Fond sombre professionnel
- Créneaux horaires clairement délimités
- Couleurs distinctes par type de cours
- Informations compactes et lisibles

## 🔧 Fonctionnalités Techniques

### Gestion des Fuseaux Horaires
- **Détection automatique** heure d'été/hiver
- **Conversion UTC → Paris** pour tous les événements
- **Précision** des horaires garantie

### Retry et Robustesse
- **5 tentatives** avec backoff exponentiel
- **Timeouts progressifs** (30s → 120s)
- **Gestion des erreurs** serveur (503, 504, 429)

### Optimisations
- **Images optimisées** pour Discord
- **Wrapping automatique** du texte long
- **Limitation intelligente** du contenu affiché

## 📝 Workflow GitHub Actions

Le fichier `edt_improved.yml` configure :
- ✅ Installation de Python 3.11
- ✅ Installation des dépendances (requests, Pillow)
- ✅ Exécution programmée
- ✅ Upload des logs en cas d'erreur
- ✅ Déclenchement manuel possible

## 🐛 Dépannage

### L'image ne s'affiche pas
- Vérifiez que Pillow est installé : `pip install Pillow`
- Vérifiez les permissions du webhook Discord

### Les couleurs ne correspondent pas
- Modifiez `COURSE_COLORS` dans le script
- Assurez-vous que le parsing des types de cours fonctionne

### Horaires incorrects
- Vérifiez le fuseau horaire (fonction `get_paris_offset`)
- Activez/désactivez les crons été/hiver dans le YAML

## 📚 Structure du Code

```python
# Principales fonctions
create_edt_image()        # Génère l'image calendrier
fetch_and_parse_edt()     # Récupère et parse l'iCal
filter_events_for_week()  # Filtre les événements
send_edt_to_discord()     # Envoie sur Discord
```

## 🎯 Roadmap / Améliorations Futures

- [ ] Support des week-ends (samedi/dimanche)
- [ ] Thèmes de couleurs personnalisables
- [ ] Export PDF en plus de PNG
- [ ] Vue mensuelle en complément de la vue hebdomadaire
- [ ] Statistiques de présence par cours
- [ ] Notifications de changements d'EDT

## 📄 Licence

Ce projet est fourni tel quel pour usage éducatif.

## 🤝 Contribution

Les améliorations sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche (`git checkout -b feature/amelioration`)
3. Commit vos changements (`git commit -am 'Ajout fonctionnalité'`)
4. Push (`git push origin feature/amelioration`)
5. Créer une Pull Request

## 💡 Crédits

Développé pour les étudiants L2 INFO - Université du Havre
Inspiré par ADE Calendar et les emplois du temps modernes

---

**Enjoy your beautiful EDT! 🎓✨**

# 📖 Guide de Migration - Ancienne version → Version Visuelle

## 🎯 Objectif
Ce guide vous aide à migrer de votre bot EDT actuel (embeds texte) vers la nouvelle version avec images calendrier.

## ⚡ Migration Rapide (5 minutes)

### Étape 1 : Backup
```bash
# Sauvegardez vos fichiers actuels
cp edt_script.py edt_script.backup.py
cp edt.yml edt.backup.yml
```

### Étape 2 : Remplacement
```bash
# Remplacez par les nouveaux fichiers
cp edt_script_improved.py edt_script.py
cp edt_improved.yml .github/workflows/edt.yml
```

### Étape 3 : Installation de Pillow
Dans votre workflow GitHub Actions, la dépendance est déjà ajoutée :
```yaml
pip install requests Pillow
```

Pour les tests locaux :
```bash
pip install Pillow
```

### Étape 4 : Test
```bash
# Test local
python test_edt_visual.py

# Ou test du script complet
WEEK_MODE=current python edt_script.py
```

## 🔄 Comparaison Détaillée

### Configuration Identique
✅ Les **webhooks** restent les mêmes
✅ Les **URLs des EDT** ne changent pas
✅ Les **IDs des rôles** sont conservés
✅ La **logique dimanche/mercredi** est identique

### Ce Qui Change

| Aspect | Avant | Après |
|--------|-------|-------|
| **Dépendance** | `requests` | `requests` + `Pillow` |
| **Output** | Embed Discord | Image PNG |
| **Fonction principale** | `create_edt_embed()` | `create_edt_image()` |
| **Envoi Discord** | JSON embed | Multipart file upload |

## 📝 Modifications du Code

### 1. Import Pillow
```python
# Ajoutez en haut du fichier
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
```

### 2. Nouvelle Fonction de Création
```python
# Remplacer
embed = create_edt_embed(group_name, week_events, week_dates, week_type)

# Par
image = create_edt_image(group_name, week_events, week_dates, week_type)
```

### 3. Envoi Modifié
```python
# L'envoi passe d'un embed JSON à un upload de fichier
# Ceci est géré automatiquement par send_edt_to_discord()
```

## 🎨 Personnalisation

### Modifier les Couleurs
Dans `edt_script_improved.py`, localisez `COURSE_COLORS` :

```python
COURSE_COLORS = {
    'CM': (138, 80, 183),      # Violet → Changez en (R, G, B)
    'TD': (255, 167, 38),      # Orange
    'TP': (52, 152, 219),      # Bleu
    # ...
}
```

**Exemple** : Passer les CM en bleu foncé
```python
'CM': (41, 128, 185),  # Bleu foncé
```

### Modifier les Dimensions
```python
# Dans create_edt_image()
WIDTH = 1400  # Largeur de l'image
HEIGHT = 1000  # Hauteur de l'image
```

### Changer les Heures Affichées
```python
START_HOUR = 7   # Commence à 7h
END_HOUR = 19    # Se termine à 19h
```

## 🐛 Résolution de Problèmes

### Problème : Pillow n'est pas installé
```bash
# Solution
pip install Pillow

# Ou pour Python 3.11 spécifiquement
python3.11 -m pip install Pillow
```

### Problème : Polices introuvables
Le script utilise DejaVu Sans qui est généralement installé sur Ubuntu.

**Si les polices manquent** :
```bash
# Ubuntu/Debian
sudo apt-get install fonts-dejavu-core

# Ou modifiez le script pour utiliser la police par défaut
font_title = ImageFont.load_default()
```

### Problème : Image trop grande pour Discord
Discord accepte jusqu'à 8 Mo par fichier. Si l'image est trop lourde :

```python
# Réduire la qualité dans send_edt_to_discord()
image.save(img_byte_arr, format='PNG', optimize=True, quality=85)
```

### Problème : Texte coupé ou illisible
Ajustez les tailles de police :
```python
font_title = ImageFont.truetype("...", 20)  # Réduire de 24 à 20
font_event = ImageFont.truetype("...", 10)  # Réduire de 11 à 10
```

## 🔍 Vérifications Post-Migration

### ✅ Checklist
- [ ] Pillow est installé (`pip list | grep Pillow`)
- [ ] Les webhooks sont corrects dans le nouveau script
- [ ] Test local réussi (`python test_edt_visual.py`)
- [ ] GitHub Actions workflow mis à jour
- [ ] Premier envoi automatique réussi

### 📊 Monitoring
Surveillez les premiers envois :
1. Vérifiez les logs GitHub Actions
2. Vérifiez la réception sur Discord
3. Vérifiez que les images s'affichent correctement
4. Vérifiez que les mentions de rôle fonctionnent

## 🔙 Rollback (Retour en Arrière)

Si vous devez revenir à l'ancienne version :

```bash
# Restaurer les backups
cp edt_script.backup.py edt_script.py
cp edt.backup.yml .github/workflows/edt.yml

# Commit et push
git add .
git commit -m "Rollback to text-based EDT"
git push
```

## 💡 Conseils

### Performance
- Les images sont **optimisées automatiquement** avec Pillow
- Temps de génération : ~2-3 secondes par image
- Impact minimal sur le temps d'exécution total

### Qualité Visuelle
- Les images sont en **PNG** pour une qualité optimale
- Résolution optimale pour Discord (1400x1000)
- Couleurs adaptées au mode sombre

### Évolutivité
- Facile d'ajouter de **nouveaux types de cours**
- Personnalisation des **couleurs** très simple
- Extension possible vers **vue mensuelle**

## 🎓 Support

Si vous rencontrez des problèmes :
1. Consultez les logs GitHub Actions
2. Testez localement avec `test_edt_visual.py`
3. Vérifiez les permissions des webhooks Discord
4. Contactez le support technique

## 📚 Ressources

- [Documentation Pillow](https://pillow.readthedocs.io/)
- [Discord Webhooks Guide](https://discord.com/developers/docs/resources/webhook)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

**Bonne migration ! 🚀**

N'hésitez pas à personnaliser davantage votre bot une fois la migration effectuée.

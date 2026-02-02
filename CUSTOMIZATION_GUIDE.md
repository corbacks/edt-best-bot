# 🎨 Guide de Personnalisation Avancée

## 🌈 Thèmes de Couleurs

### Thème Dark Mode (Actuel)
```python
BG_COLOR = (30, 33, 46)        # Fond sombre
HEADER_COLOR = (40, 43, 56)    # Header
GRID_COLOR = (60, 63, 76)      # Grille
TEXT_COLOR = (255, 255, 255)   # Texte blanc
```

### Thème Light Mode
```python
BG_COLOR = (255, 255, 255)      # Fond blanc
HEADER_COLOR = (240, 242, 245)  # Header clair
GRID_COLOR = (220, 223, 230)    # Grille grise claire
TEXT_COLOR = (30, 33, 46)       # Texte sombre
```

### Thème Universitaire
```python
BG_COLOR = (245, 247, 250)      # Blanc cassé
HEADER_COLOR = (41, 98, 255)    # Bleu universitaire
GRID_COLOR = (200, 210, 220)    # Grille subtile
TEXT_COLOR = (33, 37, 41)       # Texte foncé
```

### Thème Matrix (Fun)
```python
BG_COLOR = (0, 0, 0)            # Noir
HEADER_COLOR = (0, 20, 0)       # Vert très foncé
GRID_COLOR = (0, 50, 0)         # Vert foncé
TEXT_COLOR = (0, 255, 0)        # Vert Matrix
COURSE_COLORS = {
    'CM': (0, 180, 0),
    'TD': (0, 220, 0),
    'TP': (0, 255, 0),
    # ...
}
```

## 🎨 Palettes de Couleurs par Type de Cours

### Palette Pastel
```python
COURSE_COLORS = {
    'CM': (179, 157, 219),      # Violet pastel
    'TD': (255, 195, 160),      # Orange pastel
    'TP': (159, 197, 232),      # Bleu pastel
    'Examen': (255, 179, 186),  # Rose pastel
    'Projet': (162, 217, 206),  # Vert pastel
    'default': (201, 203, 207)  # Gris pastel
}
```

### Palette Vibrante
```python
COURSE_COLORS = {
    'CM': (156, 39, 176),       # Violet intense
    'TD': (255, 152, 0),        # Orange vif
    'TP': (33, 150, 243),       # Bleu électrique
    'Examen': (244, 67, 54),    # Rouge vif
    'Projet': (76, 175, 80),    # Vert intense
    'default': (158, 158, 158)  # Gris neutre
}
```

### Palette Minimaliste
```python
COURSE_COLORS = {
    'CM': (100, 100, 100),      # Gris foncé
    'TD': (130, 130, 130),      # Gris moyen
    'TP': (160, 160, 160),      # Gris clair
    'Examen': (80, 80, 80),     # Gris très foncé
    'Projet': (140, 140, 140),  # Gris
    'default': (120, 120, 120)  # Gris neutre
}
```

## 📐 Personnalisation des Dimensions

### Vue Compacte (pour mobile)
```python
WIDTH = 800
HEIGHT = 600
HEADER_HEIGHT = 50
DAY_HEADER_HEIGHT = 40
TIME_COL_WIDTH = 40

# Polices plus petites
font_title = ImageFont.truetype("...", 16)
font_event = ImageFont.truetype("...", 8)
```

### Vue Étendue (pour grand écran)
```python
WIDTH = 1920
HEIGHT = 1080
HEADER_HEIGHT = 100
DAY_HEADER_HEIGHT = 80
TIME_COL_WIDTH = 80

# Polices plus grandes
font_title = ImageFont.truetype("...", 32)
font_event = ImageFont.truetype("...", 14)
```

### Vue Portrait (vertical)
```python
WIDTH = 800
HEIGHT = 1600
# Disposition verticale : jours empilés au lieu de côte à côte
```

## 🖋️ Polices Personnalisées

### Polices Disponibles sur Ubuntu
```python
# Serif élégant
font_title = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf", 24)

# Sans-serif moderne
font_title = ImageFont.truetype("/usr/share/fonts/truetype/ubuntu/Ubuntu-Bold.ttf", 24)

# Monospace pour les heures
font_time = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 10)
```

### Télécharger des Polices Personnalisées
```python
# 1. Ajoutez la police dans le repo (ex: fonts/CustomFont.ttf)
# 2. Utilisez-la dans le script
font_title = ImageFont.truetype("fonts/CustomFont.ttf", 24)
```

## ✨ Effets Visuels Avancés

### Ombres Portées
```python
# Dans create_edt_image(), après avoir dessiné un rectangle de cours
# Ajouter avant le rectangle principal :
shadow_offset = 3
draw.rectangle(
    [x_day + shadow_offset, y_event_start + shadow_offset,
     x_day + DAY_WIDTH + shadow_offset, y_event_end + shadow_offset],
    fill=(0, 0, 0, 50)  # Noir semi-transparent
)
```

### Dégradés de Couleur
```python
def create_gradient(draw, x1, y1, x2, y2, color_start, color_end):
    """Crée un dégradé vertical"""
    height = y2 - y1
    for i in range(height):
        ratio = i / height
        r = int(color_start[0] * (1 - ratio) + color_end[0] * ratio)
        g = int(color_start[1] * (1 - ratio) + color_end[1] * ratio)
        b = int(color_start[2] * (1 - ratio) + color_end[2] * ratio)
        draw.line([(x1, y1 + i), (x2, y1 + i)], fill=(r, g, b))
```

### Bordures Arrondies
```python
# Remplacer draw.rectangle par des rectangles arrondis
from PIL import ImageDraw

def draw_rounded_rectangle(draw, coords, radius, fill, outline=None):
    """Dessine un rectangle aux coins arrondis"""
    x1, y1, x2, y2 = coords
    draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=fill, outline=outline)

# Utilisation
draw_rounded_rectangle(draw, [x, y, x+w, y+h], radius=10, fill=color)
```

## 📊 Fonctionnalités Additionnelles

### Afficher les Professeurs
```python
# Dans la boucle d'affichage des événements, ajouter :
if event['course_info']['professeur'] and text_y < y_event_end - 15:
    prof_text = f"👨‍🏫 {event['course_info']['professeur'][:15]}"
    draw.text((text_x, text_y), prof_text, fill=SECONDARY_TEXT, font=font_time)
    text_y += 12
```

### Indicateurs de Durée
```python
# Ajouter un badge avec la durée du cours
duration = event['end'] - event['start']
duration_hours = duration.total_seconds() / 3600
duration_text = f"{duration_hours:.1f}h"

# Petit badge en haut à droite du cours
badge_x = x_day + DAY_WIDTH - 35
badge_y = y_event_start + 5
draw.rectangle([badge_x, badge_y, badge_x + 30, badge_y + 15], 
               fill=(0, 0, 0, 100))
draw.text((badge_x + 5, badge_y + 2), duration_text, 
         fill=TEXT_COLOR, font=font_time)
```

### Compteur de Cours par Jour
```python
# En bas de chaque colonne de jour
for i in range(5):
    day_index = i
    if day_index in week_events:
        count = len(week_events[day_index])
        count_text = f"{count} cours"
        x = TIME_COL_WIDTH + (i * DAY_WIDTH) + (DAY_WIDTH // 2) - 20
        y = HEIGHT - 25
        draw.text((x, y), count_text, fill=SECONDARY_TEXT, font=font_time)
```

### Icônes Emoji
```python
# Utiliser des emoji pour les types de cours
COURSE_EMOJI = {
    'CM': '📚',
    'TD': '✏️',
    'TP': '💻',
    'Examen': '📝',
    'Projet': '🎯'
}

# Dans l'affichage
emoji = COURSE_EMOJI.get(course_type, '📖')
draw.text((text_x, text_y), emoji, fill=TEXT_COLOR, font=font_event)
```

## 🌙 Mode Sombre Dynamique

### Détection de l'Heure
```python
def get_theme_colors():
    """Retourne les couleurs selon l'heure"""
    now = get_paris_now()
    hour = now.hour
    
    if 6 <= hour < 18:  # Jour
        return {
            'BG_COLOR': (255, 255, 255),
            'HEADER_COLOR': (240, 242, 245),
            'GRID_COLOR': (220, 223, 230),
            'TEXT_COLOR': (30, 33, 46)
        }
    else:  # Nuit
        return {
            'BG_COLOR': (30, 33, 46),
            'HEADER_COLOR': (40, 43, 56),
            'GRID_COLOR': (60, 63, 76),
            'TEXT_COLOR': (255, 255, 255)
        }

# Utilisation
theme = get_theme_colors()
BG_COLOR = theme['BG_COLOR']
# etc...
```

## 🔍 Zoom sur Événement Important

### Mettre en Évidence les Examens
```python
if event['course_info']['type_cours'] == 'Examen':
    # Bordure plus épaisse
    border_width = 8
    # Animation (effet de pulsation visuel via couleur plus vive)
    color = (255, 0, 0)  # Rouge vif
    # Ajouter une étoile
    draw.text((x_day + 5, y_event_start + 5), "⭐", 
             fill=(255, 215, 0), font=font_event)
```

## 🎯 Export Multi-Format

### Sauvegarder en Plusieurs Formats
```python
def save_multiple_formats(image, base_filename):
    """Sauvegarde en PNG, JPEG et WebP"""
    # PNG (haute qualité)
    image.save(f"{base_filename}.png", 'PNG', optimize=True)
    
    # JPEG (compression)
    rgb_image = image.convert('RGB')
    rgb_image.save(f"{base_filename}.jpg", 'JPEG', quality=85, optimize=True)
    
    # WebP (moderne, petit)
    image.save(f"{base_filename}.webp", 'WEBP', quality=85)
```

## 📱 Versions Responsive

### Détection Automatique
```python
def get_optimal_dimensions():
    """Retourne les dimensions optimales selon le contexte"""
    # Pour Discord mobile
    if os.environ.get('TARGET_PLATFORM') == 'mobile':
        return (800, 600)
    # Pour Discord desktop
    else:
        return (1400, 1000)

WIDTH, HEIGHT = get_optimal_dimensions()
```

## 🌐 Localisation

### Support Multilingue
```python
TRANSLATIONS = {
    'fr': {
        'current_week': 'Cette semaine',
        'next_week': 'Semaine prochaine',
        'monday': 'LUN.',
        'no_courses': 'Pas de cours'
    },
    'en': {
        'current_week': 'This week',
        'next_week': 'Next week',
        'monday': 'MON.',
        'no_courses': 'No classes'
    }
}

# Utilisation
lang = os.environ.get('LANGUAGE', 'fr')
week_text = TRANSLATIONS[lang]['current_week']
```

## 💾 Caching et Performance

### Cache des Images
```python
import hashlib
import pickle

def get_cache_key(week_events, week_dates):
    """Génère une clé unique pour le cache"""
    data = f"{week_events}_{week_dates}"
    return hashlib.md5(data.encode()).hexdigest()

def load_from_cache(cache_key):
    """Charge une image depuis le cache"""
    try:
        with open(f"cache/{cache_key}.pkl", 'rb') as f:
            return pickle.load(f)
    except:
        return None

def save_to_cache(cache_key, image):
    """Sauvegarde l'image dans le cache"""
    os.makedirs('cache', exist_ok=True)
    with open(f"cache/{cache_key}.pkl", 'wb') as f:
        pickle.dump(image, f)
```

---

**Expérimentez et créez votre style unique ! 🎨**

N'oubliez pas de tester localement avant de déployer en production.

#!/usr/bin/env python3
"""
🎓 EDT Bot L2 INFO - Version ULTRA-AMÉLIORÉE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Génération d'emplois du temps style ADE Calendar avec:
- Design moderne et professionnel
- Codes couleur intelligents
- Statistiques et insights
- Gestion avancée des événements
- Export multi-format
- Performance optimisée
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
import os
import sys
import requests
import json
import re
import time
import hashlib
from datetime import datetime, timedelta, timezone
from collections import defaultdict, Counter
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from io import BytesIO
import logging

# ═══════════════════════════════════════════════════════════════════════════════
# 🎨 CONFIGURATION VISUELLE
# ═══════════════════════════════════════════════════════════════════════════════

# Thème Dark Mode Premium
COLORS = {
    'background': (20, 23, 36),           # Fond ultra-sombre
    'header': (30, 35, 52),               # Header élégant
    'grid': (45, 50, 68),                 # Grille subtile
    'text': (255, 255, 255),              # Texte blanc pur
    'text_secondary': (149, 165, 180),    # Texte secondaire
    'current_time': (231, 76, 60),        # Rouge vif pour ligne actuelle
    'shadow': (0, 0, 0),                  # Ombres
    'success': (46, 204, 113),            # Vert succès
    'warning': (241, 196, 15),            # Jaune warning
    'accent': (52, 152, 219),             # Bleu accent
}

# Couleurs par type de cours (palette professionnelle)
COURSE_COLORS = {
    'CM': {
        'main': (138, 80, 183),           # Violet élégant
        'light': (155, 100, 200),
        'dark': (120, 65, 160)
    },
    'TD': {
        'main': (255, 167, 38),           # Orange dynamique
        'light': (255, 185, 70),
        'dark': (230, 145, 20)
    },
    'TP': {
        'main': (52, 152, 219),           # Bleu professionnel
        'light': (75, 170, 235),
        'dark': (35, 130, 195)
    },
    'Examen': {
        'main': (231, 76, 60),            # Rouge important
        'light': (245, 100, 85),
        'dark': (200, 60, 45)
    },
    'Projet': {
        'main': (46, 204, 113),           # Vert créatif
        'light': (70, 220, 135),
        'dark': (30, 180, 95)
    },
    'Soutenance': {
        'main': (155, 89, 182),           # Violet clair
        'light': (175, 110, 200),
        'dark': (135, 70, 165)
    },
    'Conférence': {
        'main': (52, 73, 94),             # Bleu-gris
        'light': (70, 90, 115),
        'dark': (35, 55, 75)
    },
    'default': {
        'main': (149, 165, 166),          # Gris neutre
        'light': (170, 185, 186),
        'dark': (130, 145, 146)
    }
}

# Emojis par type de cours
COURSE_EMOJI = {
    'CM': '📚',
    'TD': '✏️',
    'TP': '💻',
    'Examen': '📝',
    'Projet': '🎯',
    'Soutenance': '🎤',
    'Conférence': '🎓',
    'default': '📖'
}

# ═══════════════════════════════════════════════════════════════════════════════
# 🔐 CONFIGURATION WEBHOOKS & EDT
# ═══════════════════════════════════════════════════════════════════════════════

WEBHOOKS = {
    "CM Communs": os.environ.get("WEBHOOK_CM", "https://discordapp.com/api/webhooks/1420864305506549912/9MyUp5eggiLNDyuROGxu7tBRTae8URNyTmluZzjN2jrbMphlc5kffeJOiKL-uqWeKHWs"),
    "Groupe 1": os.environ.get("WEBHOOK_G1", "https://discordapp.com/api/webhooks/1421027773723709532/fYgHZUxwWKcI-dMLTLZfR-rsAT6ksZM5j7j1r1VhcCszgSviKB_gM1GY97QaL3jOH_Ci"),
    "Groupe 2": os.environ.get("WEBHOOK_G2", "https://discordapp.com/api/webhooks/1421028055509499935/rbokRUOnkzPNTapSc0Tnd64be0m4J-0lhSuj1y3Si56UaWxgidff3KlTLTW1tClbLfGz"),
    "Groupe 3": os.environ.get("WEBHOOK_G3", "https://discordapp.com/api/webhooks/1421028321734426665/us4sCIX7b0Csouf2j7v_r-OfrOcAqrqV0SeQ_Jbq0KNeb-fb9mw5KU73AksTTGOEHXZu")
}

EDT_URLS = {
    "Groupe 1": "https://hplanning.univ-lehavre.fr/Telechargements/ical/Edt_Gr1___L2_INFO.ics?version=2022.0.5.0&idICal=63D02C34E55C4FDF72F91012A61BEEEC&param=643d5b312e2e36325d2666683d3126663d3131313030",
    "Groupe 2": "https://hplanning.univ-lehavre.fr/Telechargements/ical/Edt_Gr2___L2_INFO.ics?version=2022.0.5.0&idICal=26AE2D440785C828832D3B6683DDDFE2&param=643d5b312e2e36325d2666683d3126663d3131313030",
    "Groupe 3": "https://hplanning.univ-lehavre.fr/Telechargements/ical/Edt_Gr3___L2_INFO.ics?version=2022.0.5.0&idICal=9EB190174CC47B352D5A84DF3EAA355E&param=643d5b312e2e36325d2666683d3131313030",
    "CM Communs": "https://hplanning.univ-lehavre.fr/Telechargements/ical/Edt_ST_L2___INFORMATIQUE.ics?version=2022.0.5.0&idICal=5306DEC43ABDB323BBC7726C2F6D4171&param=643d5b312e2e36325d2666683d3130313030"
}

ROLE_IDS = {
    "CM Communs": "1418998954380759141",
    "Groupe 1": "1419000148528205955",
    "Groupe 2": "1419000272776069303",
    "Groupe 3": "1419000449016660071"
}

# ═══════════════════════════════════════════════════════════════════════════════
# 📊 CONFIGURATION LOGGING
# ═══════════════════════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# ⏰ GESTION DU TEMPS ET FUSEAUX HORAIRES
# ═══════════════════════════════════════════════════════════════════════════════

def get_paris_offset(dt):
    """Calcule l'offset UTC pour Paris (gestion été/hiver automatique)"""
    year = dt.year
    
    # Dernier dimanche de mars à 2h UTC
    march_last = datetime(year, 3, 31)
    while march_last.weekday() != 6:
        march_last -= timedelta(days=1)
    dst_start = march_last.replace(hour=2, minute=0, second=0, microsecond=0)
    
    # Dernier dimanche d'octobre à 2h UTC
    october_last = datetime(year, 10, 31)
    while october_last.weekday() != 6:
        october_last -= timedelta(days=1)
    dst_end = october_last.replace(hour=2, minute=0, second=0, microsecond=0)
    
    return 2 if dst_start <= dt < dst_end else 1

def get_paris_now():
    """Obtient datetime actuel en heure de Paris"""
    utc_now = datetime.now(timezone.utc).replace(tzinfo=None)
    offset = get_paris_offset(utc_now)
    return utc_now + timedelta(hours=offset)

# ═══════════════════════════════════════════════════════════════════════════════
# 🌐 RÉCUPÉRATION ROBUSTE DES DONNÉES
# ═══════════════════════════════════════════════════════════════════════════════

def fetch_with_retry(url, max_retries=5, initial_timeout=30):
    """Récupère une URL avec retry exponentiel ultra-robuste"""
    for attempt in range(max_retries):
        try:
            timeout = initial_timeout + (attempt * 15)
            logger.info(f"🔄 Tentative {attempt + 1}/{max_retries} (timeout: {timeout}s)")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/calendar,text/plain,application/ics,*/*',
                'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Cache-Control': 'no-cache',
                'Referer': 'https://hplanning.univ-lehavre.fr/'
            }
            
            session = requests.Session()
            session.headers.update(headers)
            response = session.get(url, timeout=timeout, allow_redirects=True, verify=True)
            response.raise_for_status()
            
            logger.info(f"✅ Récupération réussie ({response.status_code})")
            return response.text
            
        except requests.exceptions.Timeout:
            logger.warning(f"⏱️ Timeout après {timeout}s")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.info(f"⏳ Attente {wait_time}s avant retry...")
                time.sleep(wait_time)
                
        except requests.exceptions.ConnectionError as e:
            logger.error(f"🔌 Erreur connexion: {str(e)[:100]}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ HTTP {e.response.status_code}")
            if e.response.status_code in [503, 504, 429]:
                if attempt < max_retries - 1:
                    wait_time = 5 * (attempt + 1)
                    logger.info(f"⏳ Serveur surchargé, attente {wait_time}s...")
                    time.sleep(wait_time)
            else:
                raise
                
        except Exception as e:
            logger.error(f"❌ Erreur: {type(e).__name__}: {str(e)[:100]}")
            if attempt < max_retries - 1:
                time.sleep(2)
    
    logger.error(f"💥 Échec définitif après {max_retries} tentatives")
    return None

# ═══════════════════════════════════════════════════════════════════════════════
# 📅 GESTION DES SEMAINES ET DATES
# ═══════════════════════════════════════════════════════════════════════════════

def get_week_dates(week_offset=0):
    """Obtient les dates d'une semaine avec informations enrichies"""
    now = get_paris_now()
    days_since_monday = now.weekday()
    current_monday = now.date() - timedelta(days=days_since_monday)
    target_monday = current_monday + timedelta(weeks=week_offset)
    
    week_dates = []
    days_fr = ['LUN.', 'MAR.', 'MER.', 'JEU.', 'VEN.', 'SAM.', 'DIM.']
    days_full = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    
    for i in range(7):
        day_date = target_monday + timedelta(days=i)
        week_dates.append({
            'date': day_date,
            'day_name': days_fr[i],
            'day_full': days_full[i],
            'day_number': day_date.day,
            'month': day_date.strftime('%B'),
            'formatted': day_date.strftime('%d/%m/%Y'),
            'is_today': day_date == now.date()
        })
    
    return week_dates

def determine_week_mode():
    """Détermine intelligemment quelle semaine afficher"""
    week_mode = os.environ.get('WEEK_MODE', 'auto')
    
    if week_mode == 'current':
        return 0, "courante (forcé)"
    elif week_mode == 'next':
        return 1, "suivante (forcé)"
    
    now = get_paris_now()
    current_weekday = now.weekday()
    
    if current_weekday == 6:  # Dimanche
        return 1, "suivante (anticipation dimanche)"
    else:
        return 0, "courante"

# ═══════════════════════════════════════════════════════════════════════════════
# 📝 PARSING AVANCÉ DES ÉVÉNEMENTS iCAL
# ═══════════════════════════════════════════════════════════════════════════════

def parse_ical_datetime(dt_string):
    """Parse sophistiqué des dates iCal"""
    try:
        dt_clean = dt_string.strip()
        if ';' in dt_clean:
            dt_clean = dt_clean.split(';')[-1]
        dt_clean = dt_clean.replace('Z', '')
        
        if 'T' in dt_clean and len(dt_clean) >= 15:
            date_part = dt_clean.split('T')[0]
            time_part = dt_clean.split('T')[1]
            
            year = int(date_part[:4])
            month = int(date_part[4:6])
            day = int(date_part[6:8])
            
            if len(time_part) >= 6:
                hour = int(time_part[:2])
                minute = int(time_part[2:4])
                second = int(time_part[4:6]) if len(time_part) >= 6 else 0
                
                dt_utc = datetime(year, month, day, hour, minute, second)
                offset = get_paris_offset(dt_utc)
                return dt_utc + timedelta(hours=offset)
        
        elif len(dt_clean) == 8:
            year = int(dt_clean[:4])
            month = int(dt_clean[4:6])
            day = int(dt_clean[6:8])
            return datetime(year, month, day, 0, 0, 0)
    
    except Exception as e:
        logger.warning(f"⚠️ Erreur parse date '{dt_string}': {e}")
    
    return None

def extract_course_info(summary, description=""):
    """Extraction intelligente des informations de cours"""
    course_info = {
        'type_cours': '',
        'matiere': '',
        'professeur': '',
        'groupe': '',
        'salle_type': ''
    }
    
    if not summary:
        return course_info
    
    # Détection du type de cours (priorité aux patterns spécifiques)
    type_patterns = [
        (r'\b(CM|TD|TP|Examen|Projet|Soutenance|Conférence)\b', 'type_cours'),
    ]
    
    for pattern, field in type_patterns:
        match = re.search(pattern, summary, re.IGNORECASE)
        if match:
            course_info[field] = match.group(1).upper()
            if course_info[field] == 'CONFERENCE':
                course_info[field] = 'Conférence'
            break
    
    # Extraction matière
    parts = re.split(r'[-–—]', summary)
    if len(parts) >= 2:
        course_info['matiere'] = parts[1].strip()
    else:
        course_info['matiere'] = summary.strip()
    
    # Nettoyage matière
    course_info['matiere'] = re.sub(r'\s*\(.*?\)\s*', '', course_info['matiere'])
    
    # Extraction professeur
    prof_patterns = [
        r'(?:Prof|Enseignant|Professeur)[:\s]+([A-ZÀ-Ÿ][a-zà-ÿ]+(?:\s+[A-ZÀ-Ÿ][a-zà-ÿ]+)*)',
        r'\n([A-Z][a-z]+\s+[A-Z][a-z]+)\s*$'
    ]
    
    for pattern in prof_patterns:
        match = re.search(pattern, description, re.IGNORECASE | re.MULTILINE)
        if match:
            course_info['professeur'] = match.group(1)
            break
    
    # Extraction groupe
    groupe_match = re.search(r'Gr[ou]*pe?\s*(\d+)', summary, re.IGNORECASE)
    if groupe_match:
        course_info['groupe'] = f"Gr{groupe_match.group(1)}"
    
    return course_info

def fetch_and_parse_edt(group_name, edt_url):
    """Récupération et parsing complet de l'EDT"""
    logger.info(f"📡 Récupération EDT {group_name}...")
    
    ical_data = fetch_with_retry(edt_url)
    if not ical_data:
        logger.error(f"❌ Impossible de récupérer l'EDT {group_name}")
        return []
    
    logger.info(f"📄 Données: {len(ical_data)} caractères")
    
    try:
        events = []
        current_event = {}
        in_event = False
        current_field = None
        field_value = []
        
        for line in ical_data.split('\n'):
            line = line.strip()
            
            # Gestion des lignes continuées
            if line.startswith(' ') or line.startswith('\t'):
                if current_field and field_value:
                    field_value.append(line.strip())
                continue
            
            # Si on a une valeur accumulée, la sauvegarder
            if current_field and field_value:
                value = ' '.join(field_value)
                if current_field == 'DTSTART':
                    dt = parse_ical_datetime(value)
                    if dt:
                        current_event['start'] = dt
                elif current_field == 'DTEND':
                    dt = parse_ical_datetime(value)
                    if dt:
                        current_event['end'] = dt
                elif current_field == 'SUMMARY':
                    current_event['summary'] = value
                elif current_field == 'LOCATION':
                    current_event['location'] = value
                elif current_field == 'DESCRIPTION':
                    current_event['description'] = value
                
                current_field = None
                field_value = []
            
            if line == 'BEGIN:VEVENT':
                in_event = True
                current_event = {}
            
            elif line == 'END:VEVENT' and in_event:
                if 'start' in current_event and 'end' in current_event:
                    events.append(current_event)
                in_event = False
                current_event = {}
            
            elif in_event and ':' in line:
                field_name = line.split(':', 1)[0].split(';')[0]
                field_content = line.split(':', 1)[1] if ':' in line else ''
                
                if field_name in ['DTSTART', 'DTEND', 'SUMMARY', 'LOCATION', 'DESCRIPTION']:
                    current_field = field_name
                    field_value = [field_content]
        
        # Enrichir chaque événement
        for event in events:
            summary = event.get('summary', '')
            description = event.get('description', '')
            event['course_info'] = extract_course_info(summary, description)
            
            # Calculer la durée
            duration = event['end'] - event['start']
            event['duration_hours'] = duration.total_seconds() / 3600
        
        logger.info(f"✅ {len(events)} événements parsés pour {group_name}")
        return events
    
    except Exception as e:
        logger.error(f"❌ Erreur parsing {group_name}: {e}")
        import traceback
        traceback.print_exc()
        return []

def filter_events_for_week(events, week_dates):
    """Filtre et organise les événements par jour"""
    week_events = defaultdict(list)
    week_start = week_dates[0]['date']
    week_end = week_dates[-1]['date']
    
    logger.info(f"🎯 Filtrage semaine: {week_start} → {week_end}")
    
    for event in events:
        event_date = event['start'].date()
        if week_start <= event_date <= week_end:
            day_index = (event_date - week_start).days
            if 0 <= day_index < 7:
                week_events[day_index].append(event)
    
    # Tri par heure de début
    for day in week_events:
        week_events[day].sort(key=lambda x: x['start'])
    
    total = sum(len(events) for events in week_events.values())
    logger.info(f"📅 {total} événements filtrés")
    
    return dict(week_events)

# ═══════════════════════════════════════════════════════════════════════════════
# 📊 STATISTIQUES ET ANALYSES
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_statistics(week_events):
    """Calcule des statistiques avancées sur la semaine"""
    stats = {
        'total_courses': 0,
        'total_hours': 0,
        'by_type': Counter(),
        'by_day': {},
        'busiest_day': None,
        'average_per_day': 0,
        'earliest_start': None,
        'latest_end': None,
    }
    
    all_events = []
    for day_index, events in week_events.items():
        all_events.extend(events)
        stats['by_day'][day_index] = {
            'count': len(events),
            'hours': sum(e['duration_hours'] for e in events)
        }
    
    stats['total_courses'] = len(all_events)
    stats['total_hours'] = sum(e['duration_hours'] for e in all_events)
    
    for event in all_events:
        course_type = event['course_info']['type_cours'] or 'Autre'
        stats['by_type'][course_type] += 1
        
        if stats['earliest_start'] is None or event['start'] < stats['earliest_start']:
            stats['earliest_start'] = event['start']
        if stats['latest_end'] is None or event['end'] > stats['latest_end']:
            stats['latest_end'] = event['end']
    
    if stats['by_day']:
        busiest = max(stats['by_day'].items(), key=lambda x: x[1]['count'])
        stats['busiest_day'] = busiest[0]
        stats['average_per_day'] = stats['total_courses'] / len(stats['by_day'])
    
    return stats

# ═══════════════════════════════════════════════════════════════════════════════
# 🎨 GÉNÉRATION D'IMAGE ULTRA-AMÉLIORÉE
# ═══════════════════════════════════════════════════════════════════════════════

def load_fonts():
    """Charge les polices avec fallback"""
    fonts = {}
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    
    try:
        fonts['title'] = ImageFont.truetype(font_paths[0], 28)
        fonts['subtitle'] = ImageFont.truetype(font_paths[0], 18)
        fonts['header'] = ImageFont.truetype(font_paths[0], 16)
        fonts['day'] = ImageFont.truetype(font_paths[0], 14)
        fonts['event'] = ImageFont.truetype(font_paths[1], 11)
        fonts['small'] = ImageFont.truetype(font_paths[1], 9)
        fonts['time'] = ImageFont.truetype(font_paths[1], 10)
        logger.info("✅ Polices chargées")
    except:
        logger.warning("⚠️ Polices par défaut utilisées")
        fonts = {k: ImageFont.load_default() for k in ['title', 'subtitle', 'header', 'day', 'event', 'small', 'time']}
    
    return fonts

def wrap_text(text, font, max_width, draw):
    """Découpe intelligent du texte"""
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        
        if bbox[2] - bbox[0] <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

def draw_gradient_background(draw, x1, y1, x2, y2, color_start, color_end):
    """Dessine un dégradé vertical"""
    height = int(y2 - y1)
    for i in range(height):
        ratio = i / height
        r = int(color_start[0] * (1 - ratio) + color_end[0] * ratio)
        g = int(color_start[1] * (1 - ratio) + color_end[1] * ratio)
        b = int(color_start[2] * (1 - ratio) + color_end[2] * ratio)
        draw.line([(x1, y1 + i), (x2, y1 + i)], fill=(r, g, b))

def draw_course_card(draw, fonts, x, y, width, height, event, show_details=True):
    """Dessine une carte de cours stylisée avec effets visuels"""
    course_type = event['course_info']['type_cours'] or 'default'
    colors = COURSE_COLORS.get(course_type, COURSE_COLORS['default'])
    
    # Ombre portée
    shadow_offset = 3
    draw.rectangle(
        [x + shadow_offset, y + shadow_offset, x + width + shadow_offset, y + height + shadow_offset],
        fill=(*COLORS['shadow'], 30)
    )
    
    # Fond avec dégradé
    main_color = colors['main']
    light_color = colors['light']
    dark_color = tuple(int(c * 0.25) for c in main_color)
    
    draw_gradient_background(draw, x + 6, y + 2, x + width - 2, y + height - 2, dark_color, dark_color)
    
    # Bordure gauche colorée (épaisse)
    border_width = 6
    draw.rectangle([x + 2, y + 2, x + border_width + 2, y + height - 2], fill=main_color)
    
    # Bordure complète
    draw.rectangle([x + 2, y + 2, x + width - 2, y + height - 2], outline=main_color, width=2)
    
    # Contenu
    padding = 8
    text_x = x + border_width + padding
    text_y = y + 5
    max_text_width = width - border_width - (2 * padding) - 4
    
    # Badge type de cours en haut à droite
    type_text = course_type if course_type != 'default' else ''
    if type_text:
        bbox = draw.textbbox((0, 0), type_text, font=fonts['small'])
        badge_width = (bbox[2] - bbox[0]) + 10
        badge_x = x + width - badge_width - 5
        badge_y = y + 5
        
        # Badge arrondi
        draw.rounded_rectangle(
            [badge_x, badge_y, badge_x + badge_width, badge_y + 16],
            radius=8,
            fill=main_color
        )
        draw.text((badge_x + 5, badge_y + 2), type_text, fill=COLORS['text'], font=fonts['small'])
    
    # Horaires
    start_time = event['start'].strftime('%H:%M')
    end_time = event['end'].strftime('%H:%M')
    time_text = f"⏰ {start_time} - {end_time}"
    draw.text((text_x, text_y), time_text, fill=COLORS['text'], font=fonts['event'])
    text_y += 15
    
    # Emoji + Matière
    emoji = COURSE_EMOJI.get(course_type, COURSE_EMOJI['default'])
    matiere = event['course_info']['matiere']
    if matiere:
        matiere = matiere[:35]
        matiere_text = f"{emoji} {matiere}"
        matiere_lines = wrap_text(matiere_text, fonts['event'], max_text_width, draw)
        for line in matiere_lines[:2]:
            draw.text((text_x, text_y), line, fill=COLORS['text'], font=fonts['event'])
            text_y += 13
    
    # Salle si espace disponible
    location = event.get('location', '')
    if location and text_y < y + height - 15 and show_details:
        location = location[:25]
        draw.text((text_x, text_y), f"📍 {location}", fill=COLORS['text_secondary'], font=fonts['small'])
        text_y += 12
    
    # Durée en badge si espace
    if text_y < y + height - 15 and height > 60:
        duration_text = f"{event['duration_hours']:.1f}h"
        draw.text((text_x, text_y), f"⏱️ {duration_text}", fill=COLORS['text_secondary'], font=fonts['small'])

def create_ultra_edt_image(group_name, week_events, week_dates, week_type="courante", stats=None):
    """Génère une image EDT ultra-professionnelle"""
    
    # Dimensions optimales
    WIDTH = 1600
    HEIGHT = 1100
    HEADER_HEIGHT = 100
    DAY_HEADER_HEIGHT = 70
    TIME_COL_WIDTH = 70
    FOOTER_HEIGHT = 50
    DAY_WIDTH = (WIDTH - TIME_COL_WIDTH) // 5
    
    # Heures
    START_HOUR = 7
    END_HOUR = 20
    HOURS = END_HOUR - START_HOUR
    CONTENT_HEIGHT = HEIGHT - HEADER_HEIGHT - DAY_HEADER_HEIGHT - FOOTER_HEIGHT
    HOUR_HEIGHT = CONTENT_HEIGHT / HOURS
    
    # Image avec anti-aliasing
    img = Image.new('RGB', (WIDTH, HEIGHT), COLORS['background'])
    draw = ImageDraw.Draw(img, 'RGBA')
    
    fonts = load_fonts()
    
    # ═══ HEADER PRINCIPAL AVEC DÉGRADÉ ═══
    header_gradient_end = tuple(int(c * 1.2) for c in COLORS['header'])
    draw_gradient_background(draw, 0, 0, WIDTH, HEADER_HEIGHT, COLORS['header'], header_gradient_end)
    
    # Logo/Emoji du groupe
    group_emojis = {
        "Groupe 1": "📘",
        "Groupe 2": "📕",
        "Groupe 3": "📗",
        "CM Communs": "📚"
    }
    emoji = group_emojis.get(group_name, "📅")
    
    # Titre
    monday = week_dates[0]['formatted']
    friday = week_dates[4]['formatted']
    week_indicator = "📆 Semaine Prochaine" if week_type == "suivante" else "📅 Cette Semaine"
    title = f"{emoji} EDT {group_name} - {week_indicator}"
    
    bbox = draw.textbbox((0, 0), title, font=fonts['title'])
    title_width = bbox[2] - bbox[0]
    draw.text(((WIDTH - title_width) // 2, 20), title, fill=COLORS['text'], font=fonts['title'])
    
    # Sous-titre avec dates
    subtitle = f"Du {monday} au {friday}"
    bbox = draw.textbbox((0, 0), subtitle, font=fonts['subtitle'])
    subtitle_width = bbox[2] - bbox[0]
    draw.text(((WIDTH - subtitle_width) // 2, 55), subtitle, fill=COLORS['text_secondary'], font=fonts['subtitle'])
    
    # Ligne de séparation élégante
    draw.line([(50, HEADER_HEIGHT - 5), (WIDTH - 50, HEADER_HEIGHT - 5)], 
             fill=COLORS['accent'], width=3)
    
    # ═══ HEADERS DES JOURS ═══
    y_day_header = HEADER_HEIGHT
    
    for i in range(5):
        x = TIME_COL_WIDTH + (i * DAY_WIDTH)
        
        # Fond avec effet si c'est aujourd'hui
        is_today = week_dates[i]['is_today']
        header_color = COLORS['accent'] if is_today else COLORS['header']
        
        draw.rectangle([x, y_day_header, x + DAY_WIDTH, y_day_header + DAY_HEADER_HEIGHT],
                      fill=header_color, outline=COLORS['grid'], width=2)
        
        # Jour
        day_name = week_dates[i]['day_full']
        day_number = week_dates[i]['day_number']
        
        bbox = draw.textbbox((0, 0), day_name, font=fonts['header'])
        text_width = bbox[2] - bbox[0]
        draw.text((x + (DAY_WIDTH - text_width) // 2, y_day_header + 12),
                 day_name, fill=COLORS['text'], font=fonts['header'])
        
        # Numéro du jour (gros)
        num_text = str(day_number)
        bbox = draw.textbbox((0, 0), num_text, font=fonts['title'])
        num_width = bbox[2] - bbox[0]
        draw.text((x + (DAY_WIDTH - num_width) // 2, y_day_header + 38),
                 num_text, fill=COLORS['text'], font=fonts['title'])
        
        # Nombre de cours ce jour
        if i in week_events:
            count = len(week_events[i])
            count_text = f"{count} cours"
            bbox = draw.textbbox((0, 0), count_text, font=fonts['small'])
            count_width = bbox[2] - bbox[0]
            draw.text((x + (DAY_WIDTH - count_width) // 2, y_day_header + 55),
                     count_text, fill=COLORS['text_secondary'], font=fonts['small'])
    
    # ═══ GRILLE ET HEURES ═══
    y_start = HEADER_HEIGHT + DAY_HEADER_HEIGHT
    
    # Lignes horizontales (heures)
    for hour in range(START_HOUR, END_HOUR + 1):
        y = y_start + ((hour - START_HOUR) * HOUR_HEIGHT)
        
        # Heure
        hour_text = f"{hour:02d}:00"
        bbox = draw.textbbox((0, 0), hour_text, font=fonts['time'])
        text_width = bbox[2] - bbox[0]
        draw.text(((TIME_COL_WIDTH - text_width) // 2, y - 8),
                 hour_text, fill=COLORS['text_secondary'], font=fonts['time'])
        
        # Ligne (plus épaisse pour les heures pleines importantes)
        line_width = 2 if hour % 2 == 0 else 1
        draw.line([(TIME_COL_WIDTH, y), (WIDTH, y)], fill=COLORS['grid'], width=line_width)
    
    # Lignes verticales (jours)
    for i in range(6):
        x = TIME_COL_WIDTH + (i * DAY_WIDTH)
        draw.line([(x, y_day_header), (x, HEIGHT - FOOTER_HEIGHT)], 
                 fill=COLORS['grid'], width=2)
    
    # ═══ ÉVÉNEMENTS STYLISÉS ═══
    for day_index, events in week_events.items():
        if day_index >= 5:
            continue
        
        x_day = TIME_COL_WIDTH + (day_index * DAY_WIDTH)
        
        for event in events:
            start_hour = event['start'].hour + event['start'].minute / 60
            end_hour = event['end'].hour + event['end'].minute / 60
            
            # Limiter à la plage visible
            start_hour = max(start_hour, START_HOUR)
            end_hour = min(end_hour, END_HOUR)
            
            y_event_start = y_start + ((start_hour - START_HOUR) * HOUR_HEIGHT)
            y_event_end = y_start + ((end_hour - START_HOUR) * HOUR_HEIGHT)
            event_height = y_event_end - y_event_start
            
            # Ne dessiner que si visible et assez grand
            if event_height > 10:
                draw_course_card(
                    draw, fonts,
                    x_day, y_event_start,
                    DAY_WIDTH, event_height,
                    event,
                    show_details=(event_height > 50)
                )
    
    # ═══ LIGNE TEMPS ACTUEL ═══
    if week_type == "courante":
        now = get_paris_now()
        current_day = now.weekday()
        
        if current_day < 5:
            current_hour = now.hour + now.minute / 60
            
            if START_HOUR <= current_hour <= END_HOUR:
                y_current = y_start + ((current_hour - START_HOUR) * HOUR_HEIGHT)
                x_current_start = TIME_COL_WIDTH + (current_day * DAY_WIDTH)
                x_current_end = x_current_start + DAY_WIDTH
                
                # Ligne rouge avec effet glow
                for offset in range(3, 0, -1):
                    alpha = 100 - (offset * 20)
                    draw.line([(x_current_start, y_current + offset), 
                             (x_current_end, y_current + offset)],
                            fill=(*COLORS['current_time'], alpha), width=2)
                draw.line([(x_current_start, y_current), (x_current_end, y_current)],
                         fill=COLORS['current_time'], width=4)
                
                # Marqueur temps actuel
                time_now = now.strftime('%H:%M')
                bbox = draw.textbbox((0, 0), time_now, font=fonts['small'])
                text_width = bbox[2] - bbox[0]
                
                # Badge temps
                badge_x = x_current_start + 10
                badge_y = y_current - 10
                draw.rounded_rectangle(
                    [badge_x, badge_y, badge_x + text_width + 10, badge_y + 18],
                    radius=9,
                    fill=COLORS['current_time']
                )
                draw.text((badge_x + 5, badge_y + 2), time_now, 
                         fill=COLORS['text'], font=fonts['small'])
    
    # ═══ FOOTER AVEC STATISTIQUES ═══
    footer_y = HEIGHT - FOOTER_HEIGHT
    draw.rectangle([0, footer_y, WIDTH, HEIGHT], fill=COLORS['header'])
    
    if stats:
        # Statistiques centrées
        total_text = f"📊 {stats['total_courses']} cours"
        hours_text = f"⏱️ {stats['total_hours']:.1f}h"
        avg_text = f"📈 {stats['average_per_day']:.1f} cours/jour"
        
        stats_text = f"{total_text}  •  {hours_text}  •  {avg_text}"
        
        bbox = draw.textbbox((0, 0), stats_text, font=fonts['subtitle'])
        text_width = bbox[2] - bbox[0]
        draw.text(((WIDTH - text_width) // 2, footer_y + 15),
                 stats_text, fill=COLORS['text_secondary'], font=fonts['subtitle'])
    
    # Légende types de cours (petit, en bas à gauche)
    legend_x = 20
    legend_y = footer_y + 10
    legend_text = "Légende: "
    draw.text((legend_x, legend_y), legend_text, fill=COLORS['text_secondary'], font=fonts['small'])
    legend_x += 60
    
    for ctype, emoji in list(COURSE_EMOJI.items())[:5]:
        if ctype != 'default':
            draw.text((legend_x, legend_y), f"{emoji} {ctype}", 
                     fill=COLORS['text_secondary'], font=fonts['small'])
            legend_x += 50
    
    # Signature (bas à droite)
    signature = "Généré par EDT Bot v2.0"
    bbox = draw.textbbox((0, 0), signature, font=fonts['small'])
    sig_width = bbox[2] - bbox[0]
    draw.text((WIDTH - sig_width - 20, footer_y + 32),
             signature, fill=COLORS['text_secondary'], font=fonts['small'])
    
    logger.info(f"✅ Image générée: {WIDTH}x{HEIGHT}px")
    return img

# ═══════════════════════════════════════════════════════════════════════════════
# 📤 ENVOI DISCORD OPTIMISÉ
# ═══════════════════════════════════════════════════════════════════════════════

def send_to_discord(group_name, image, week_type="courante", stats=None):
    """Envoie l'EDT sur Discord avec message enrichi"""
    
    webhook_url = WEBHOOKS.get(group_name)
    if not webhook_url:
        logger.error(f"❌ Pas de webhook pour {group_name}")
        return False
    
    role_id = ROLE_IDS.get(group_name)
    mention = f"<@&{role_id}>" if role_id else ""
    
    try:
        # Convertir image en bytes (optimisé)
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='PNG', optimize=True, quality=95)
        img_byte_arr.seek(0)
        
        # Message enrichi
        week_indicator = "📆 Semaine prochaine" if week_type == "suivante" else "📅 Cette semaine"
        
        message_parts = [
            mention,
            f"\n{week_indicator} - Votre emploi du temps est prêt ! ✨",
        ]
        
        if stats and stats['total_courses'] > 0:
            message_parts.append(f"\n📊 **{stats['total_courses']} cours** cette semaine ({stats['total_hours']:.1f}h)")
            
            # Top 3 types de cours
            if stats['by_type']:
                top_types = stats['by_type'].most_common(3)
                types_text = " • ".join([f"{COURSE_EMOJI.get(t, '📖')} {t}: {c}" for t, c in top_types])
                message_parts.append(f"🎯 {types_text}")
        
        content = "\n".join(message_parts)
        
        # Préparer la requête
        files = {'file': ('edt.png', img_byte_arr, 'image/png')}
        
        group_emojis = {
            "Groupe 1": "📘",
            "Groupe 2": "📕",
            "Groupe 3": "📗",
            "CM Communs": "📚"
        }
        emoji = group_emojis.get(group_name, "📅")
        
        payload = {
            "username": f"{emoji} EDT Bot - {group_name}",
            "content": content,
            "avatar_url": "https://i.imgur.com/4M34hi2.png"  # Optionnel: logo custom
        }
        
        logger.info(f"📤 Envoi vers {group_name}...")
        response = requests.post(webhook_url, data=payload, files=files, timeout=30)
        response.raise_for_status()
        
        logger.info(f"✅ Envoyé avec succès ({response.status_code})")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur envoi {group_name}: {e}")
        import traceback
        traceback.print_exc()
        return False

# ═══════════════════════════════════════════════════════════════════════════════
# 🚀 FONCTION PRINCIPALE
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Orchestration principale du bot"""
    
    print("=" * 80)
    print("🎓 EDT BOT L2 INFO - VERSION ULTRA-AMÉLIORÉE v2.0".center(80))
    print("=" * 80)
    
    start_time = time.time()
    
    # Informations temporelles
    now = get_paris_now()
    utc_now = datetime.now(timezone.utc).replace(tzinfo=None)
    offset = get_paris_offset(utc_now)
    
    logger.info(f"🕐 Heure: {now.strftime('%d/%m/%Y %H:%M:%S')} (UTC+{offset})")
    logger.info(f"📅 Jour: {now.strftime('%A')}")
    
    # Déterminer la semaine
    week_offset, week_reason = determine_week_mode()
    logger.info(f"📆 Mode: {week_reason}")
    
    week_dates = get_week_dates(week_offset)
    week_type = "suivante" if week_offset == 1 else "courante"
    
    logger.info(f"📅 Période: {week_dates[0]['formatted']} → {week_dates[4]['formatted']}")
    
    # Traitement de chaque groupe
    success_count = 0
    total_groups = len(EDT_URLS)
    results = {}
    
    for group_name, edt_url in EDT_URLS.items():
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"📋 TRAITEMENT: {group_name.upper()}")
            logger.info(f"{'='*60}")
            
            if group_name not in WEBHOOKS:
                logger.warning(f"⚠️ Pas de webhook configuré")
                continue
            
            # Récupération et parsing
            events = fetch_and_parse_edt(group_name, edt_url)
            if not events:
                logger.warning(f"⚠️ Aucun événement récupéré")
                continue
            
            # Filtrage semaine
            week_events = filter_events_for_week(events, week_dates)
            
            # Statistiques
            stats = calculate_statistics(week_events)
            logger.info(f"📊 Stats: {stats['total_courses']} cours, {stats['total_hours']:.1f}h")
            
            if stats['by_type']:
                types_str = ", ".join([f"{t}: {c}" for t, c in stats['by_type'].most_common()])
                logger.info(f"🎯 Types: {types_str}")
            
            # Génération image
            logger.info(f"🎨 Génération image...")
            image = create_ultra_edt_image(group_name, week_events, week_dates, week_type, stats)
            
            # Envoi Discord
            if send_to_discord(group_name, image, week_type, stats):
                success_count += 1
                results[group_name] = "✅ Succès"
            else:
                results[group_name] = "❌ Échec envoi"
            
            # Pause entre envois
            time.sleep(3)
            
        except Exception as e:
            logger.error(f"❌ Erreur critique pour {group_name}: {e}")
            results[group_name] = f"❌ Erreur: {str(e)[:50]}"
            import traceback
            traceback.print_exc()
    
    # Résumé final
    elapsed = time.time() - start_time
    
    print("\n" + "=" * 80)
    print("🎯 RÉSUMÉ FINAL".center(80))
    print("=" * 80)
    
    for group, result in results.items():
        print(f"  {group:20} : {result}")
    
    print(f"\n✅ Groupes envoyés: {success_count}/{total_groups}")
    print(f"📆 Type de semaine: {week_type}")
    print(f"⏱️  Temps d'exécution: {elapsed:.2f}s")
    
    if success_count == total_groups:
        print("\n🎉 TOUS LES EDT ONT ÉTÉ ENVOYÉS AVEC SUCCÈS ! 🎉")
        return 0
    elif success_count > 0:
        print("\n⚠️ ENVOIS PARTIELS - Vérifiez les logs")
        return 1
    else:
        print("\n❌ ÉCHEC COMPLET - Aucun EDT envoyé")
        return 2

if __name__ == "__main__":
    sys.exit(main())

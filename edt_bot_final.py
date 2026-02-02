#!/usr/bin/env python3
"""
🎓 EDT Bot L2 INFO - Version FINALE Ultra-Lisible
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Optimisé pour une lisibilité maximale avec:
- Emojis au lieu d'icônes
- Coins arrondis sur les blocs
- Informations clés ultra-visibles
- Message Discord enrichi et propre
- Détection automatique des événements spéciaux
- Une seule exécution par semaine (dimanche soir)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
import os
import sys
import requests
import re
import time
from datetime import datetime, timedelta, timezone
from collections import defaultdict, Counter
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import logging

# ═══════════════════════════════════════════════════════════════════════════════
# 🎨 CONFIGURATION VISUELLE ULTRA-LISIBLE
# ═══════════════════════════════════════════════════════════════════════════════

# Couleurs fond sombre élégant
COLORS = {
    'background': (25, 30, 45),           # Fond principal
    'header': (30, 38, 58),               # Header
    'grid': (45, 52, 72),                 # Grille
    'text': (255, 255, 255),              # Texte blanc
    'text_secondary': (160, 170, 190),    # Texte secondaire
    'shadow': (0, 0, 0),                  # Ombres
}

# Couleurs par type de cours (comme votre image)
COURSE_COLORS = {
    'CM': (138, 80, 183),         # Violet
    'TD': (230, 145, 56),         # Orange
    'TP': (52, 152, 219),         # Bleu clair
    'Examen': (231, 76, 60),      # Rouge
    'Partiel': (231, 76, 60),     # Rouge
    'Projet': (46, 204, 113),     # Vert
    'Seconde Chance': (241, 196, 15),  # Jaune
    'default': (70, 80, 100)      # Gris foncé
}

# Détection d'événements spéciaux
SPECIAL_EVENTS = {
    'annulé': '🚫 ANNULÉ',
    'annule': '🚫 ANNULÉ',
    'canceled': '🚫 ANNULÉ',
    'examen': '📝 EXAMEN',
    'partiel': '📝 PARTIEL',
    'seconde chance': '🔄 2ND CHANCE',
    '2nde chance': '🔄 2ND CHANCE',
    'rattrapage': '🔄 RATTRAPAGE',
    'soutenance': '🎤 SOUTENANCE',
    'contrôle': '📝 CONTRÔLE',
    'controle': '📝 CONTRÔLE',
}

# ═══════════════════════════════════════════════════════════════════════════════
# 🔐 CONFIGURATION
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
# 📊 LOGGING
# ═══════════════════════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# ⏰ GESTION DU TEMPS
# ═══════════════════════════════════════════════════════════════════════════════

def get_paris_offset(dt):
    """Calcule l'offset UTC pour Paris"""
    year = dt.year
    march_last = datetime(year, 3, 31)
    while march_last.weekday() != 6:
        march_last -= timedelta(days=1)
    dst_start = march_last.replace(hour=2, minute=0, second=0, microsecond=0)
    
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
# 🌐 RÉCUPÉRATION DES DONNÉES
# ═══════════════════════════════════════════════════════════════════════════════

def fetch_with_retry(url, max_retries=5, initial_timeout=30):
    """Récupère une URL avec retry robuste"""
    for attempt in range(max_retries):
        try:
            timeout = initial_timeout + (attempt * 15)
            logger.info(f"🔄 Tentative {attempt + 1}/{max_retries} (timeout: {timeout}s)")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/calendar,*/*',
                'Connection': 'keep-alive',
            }
            
            session = requests.Session()
            session.headers.update(headers)
            response = session.get(url, timeout=timeout, allow_redirects=True, verify=True)
            response.raise_for_status()
            
            logger.info(f"✅ Récupération réussie ({response.status_code})")
            return response.text
            
        except Exception as e:
            logger.warning(f"⏱️ Erreur tentative {attempt + 1}: {str(e)[:100]}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                time.sleep(wait_time)
    
    logger.error(f"💥 Échec définitif après {max_retries} tentatives")
    return None

# ═══════════════════════════════════════════════════════════════════════════════
# 📅 GESTION DES SEMAINES
# ═══════════════════════════════════════════════════════════════════════════════

def get_week_dates(week_offset=0):
    """Obtient les dates d'une semaine"""
    now = get_paris_now()
    days_since_monday = now.weekday()
    current_monday = now.date() - timedelta(days=days_since_monday)
    target_monday = current_monday + timedelta(weeks=week_offset)
    
    week_dates = []
    days_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    
    for i in range(7):
        day_date = target_monday + timedelta(days=i)
        week_dates.append({
            'date': day_date,
            'day_name': days_fr[i],
            'day_number': day_date.day,
            'formatted': day_date.strftime('%d/%m/%Y')
        })
    
    return week_dates

def determine_week_mode():
    """Toujours retourner la semaine SUIVANTE (exécution dimanche uniquement)"""
    week_mode = os.environ.get('WEEK_MODE', 'auto')
    
    if week_mode == 'current':
        return 0, "courante (forcé)"
    elif week_mode == 'next':
        return 1, "suivante (forcé)"
    
    # Par défaut : toujours semaine suivante
    return 1, "suivante (automatique)"

# ═══════════════════════════════════════════════════════════════════════════════
# 📝 PARSING DES ÉVÉNEMENTS
# ═══════════════════════════════════════════════════════════════════════════════

def parse_ical_datetime(dt_string):
    """Parse une datetime iCal"""
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
        logger.warning(f"⚠️ Erreur parse date: {e}")
    
    return None

def detect_special_event(summary, description=""):
    """Détecte les événements spéciaux"""
    text = (summary + " " + description).lower()
    
    for keyword, label in SPECIAL_EVENTS.items():
        if keyword in text:
            return label
    
    return None

def extract_course_info(summary, description=""):
    """Extraction intelligente des informations"""
    course_info = {
        'type_cours': '',
        'matiere': '',
        'professeur': '',
        'groupe': '',
        'special_event': None,
        'is_cancelled': False
    }
    
    if not summary:
        return course_info
    
    # Détecter événement spécial
    special = detect_special_event(summary, description)
    course_info['special_event'] = special
    
    # Détecter annulation
    if 'annulé' in summary.lower() or 'annule' in summary.lower():
        course_info['is_cancelled'] = True
    
    # Type de cours
    type_patterns = [
        (r'\b(CM|TD|TP|Examen|Partiel|Projet|Soutenance)\b', 'type_cours'),
    ]
    
    for pattern, field in type_patterns:
        match = re.search(pattern, summary, re.IGNORECASE)
        if match:
            course_info[field] = match.group(1).upper()
            break
    
    # Matière (tout ce qui est entre tirets ou après le type)
    parts = re.split(r'[-–—]', summary)
    if len(parts) >= 2:
        course_info['matiere'] = parts[1].strip()
    else:
        # Enlever le type de cours du début
        matiere = re.sub(r'^(CM|TD|TP|Examen|Partiel|Projet)\s*-?\s*', '', summary, flags=re.IGNORECASE)
        course_info['matiere'] = matiere.strip()
    
    # Nettoyage
    course_info['matiere'] = re.sub(r'\s*\(.*?\)\s*', '', course_info['matiere'])
    
    # Professeur
    prof_patterns = [
        r'(?:Prof|Enseignant|Professeur)[:\s]+([A-ZÀ-Ÿ][a-zà-ÿ]+(?:\s+[A-ZÀ-Ÿ][a-zà-ÿ]+)*)',
        r'\bM\.\s*([A-Z][a-z]+)',
        r'\bMme\s*([A-Z][a-z]+)',
    ]
    
    for pattern in prof_patterns:
        match = re.search(pattern, description, re.IGNORECASE | re.MULTILINE)
        if match:
            course_info['professeur'] = match.group(1)
            break
    
    # Groupe
    groupe_match = re.search(r'Gr[ou]*pe?\s*(\d+)', summary, re.IGNORECASE)
    if groupe_match:
        course_info['groupe'] = f"Gr{groupe_match.group(1)}"
    
    return course_info

def fetch_and_parse_edt(group_name, edt_url):
    """Récupération et parsing de l'EDT"""
    logger.info(f"📡 Récupération EDT {group_name}...")
    
    ical_data = fetch_with_retry(edt_url)
    if not ical_data:
        return []
    
    try:
        events = []
        current_event = {}
        in_event = False
        current_field = None
        field_value = []
        
        for line in ical_data.split('\n'):
            line = line.strip()
            
            if line.startswith(' ') or line.startswith('\t'):
                if current_field and field_value:
                    field_value.append(line.strip())
                continue
            
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
        
        # Enrichir les événements
        for event in events:
            summary = event.get('summary', '')
            description = event.get('description', '')
            event['course_info'] = extract_course_info(summary, description)
            
            duration = event['end'] - event['start']
            event['duration_hours'] = duration.total_seconds() / 3600
        
        logger.info(f"✅ {len(events)} événements parsés")
        return events
    
    except Exception as e:
        logger.error(f"❌ Erreur parsing: {e}")
        import traceback
        traceback.print_exc()
        return []

def filter_events_for_week(events, week_dates):
    """Filtre les événements pour la semaine"""
    week_events = defaultdict(list)
    week_start = week_dates[0]['date']
    week_end = week_dates[-1]['date']
    
    for event in events:
        event_date = event['start'].date()
        if week_start <= event_date <= week_end:
            day_index = (event_date - week_start).days
            if 0 <= day_index < 7:
                week_events[day_index].append(event)
    
    for day in week_events:
        week_events[day].sort(key=lambda x: x['start'])
    
    return dict(week_events)

# ═══════════════════════════════════════════════════════════════════════════════
# 📊 STATISTIQUES
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_statistics(week_events):
    """Calcule les statistiques de la semaine"""
    stats = {
        'total_courses': 0,
        'total_hours': 0,
        'by_type': Counter(),
        'cancelled_count': 0,
        'special_events': [],
    }
    
    all_events = []
    for events in week_events.values():
        all_events.extend(events)
    
    stats['total_courses'] = len(all_events)
    stats['total_hours'] = sum(e['duration_hours'] for e in all_events)
    
    for event in all_events:
        course_type = event['course_info']['type_cours'] or 'Autre'
        stats['by_type'][course_type] += 1
        
        if event['course_info']['is_cancelled']:
            stats['cancelled_count'] += 1
        
        if event['course_info']['special_event']:
            stats['special_events'].append(event['course_info']['special_event'])
    
    return stats

# ═══════════════════════════════════════════════════════════════════════════════
# 🎨 GÉNÉRATION D'IMAGE ULTRA-LISIBLE
# ═══════════════════════════════════════════════════════════════════════════════

def load_fonts():
    """Charge les polices"""
    fonts = {}
    try:
        fonts['title'] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
        fonts['subtitle'] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        fonts['header'] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
        fonts['day_num'] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        fonts['event_time'] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
        fonts['event_title'] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
        fonts['event_info'] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
        fonts['small'] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9)
    except:
        fonts = {k: ImageFont.load_default() for k in ['title', 'subtitle', 'header', 'day_num', 'event_time', 'event_title', 'event_info', 'small']}
    
    return fonts

def wrap_text(text, font, max_width, draw):
    """Découpe le texte intelligemment"""
    if not text:
        return []
    
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

def create_ultra_readable_edt(group_name, week_events, week_dates):
    """Crée l'EDT ultra-lisible avec coins arrondis"""
    
    # Dimensions
    WIDTH = 1600
    HEIGHT = 1100
    HEADER_HEIGHT = 90
    DAY_HEADER_HEIGHT = 70
    TIME_COL_WIDTH = 70
    FOOTER_HEIGHT = 40
    DAY_WIDTH = (WIDTH - TIME_COL_WIDTH) // 5
    
    # Heures
    START_HOUR = 7
    END_HOUR = 20
    HOURS = END_HOUR - START_HOUR
    CONTENT_HEIGHT = HEIGHT - HEADER_HEIGHT - DAY_HEADER_HEIGHT - FOOTER_HEIGHT
    HOUR_HEIGHT = CONTENT_HEIGHT / HOURS
    
    # Image
    img = Image.new('RGB', (WIDTH, HEIGHT), COLORS['background'])
    draw = ImageDraw.Draw(img, 'RGBA')
    fonts = load_fonts()
    
    # ═══ HEADER ═══
    draw.rectangle([0, 0, WIDTH, HEADER_HEIGHT], fill=COLORS['header'])
    
    # Titre avec emoji groupe
    group_emojis = {"Groupe 1": "📘", "Groupe 2": "📕", "Groupe 3": "📗", "CM Communs": "📚"}
    emoji = group_emojis.get(group_name, "📅")
    
    title = f"{emoji} EDT {group_name} - 📅 Cette Semaine"
    bbox = draw.textbbox((0, 0), title, font=fonts['title'])
    draw.text(((WIDTH - (bbox[2] - bbox[0])) // 2, 20), title, fill=COLORS['text'], font=fonts['title'])
    
    # Dates
    monday = week_dates[0]['formatted']
    friday = week_dates[4]['formatted']
    subtitle = f"Du {monday} au {friday}"
    bbox = draw.textbbox((0, 0), subtitle, font=fonts['subtitle'])
    draw.text(((WIDTH - (bbox[2] - bbox[0])) // 2, 55), subtitle, fill=COLORS['text_secondary'], font=fonts['subtitle'])
    
    # ═══ HEADERS DES JOURS ═══
    y_day_header = HEADER_HEIGHT
    
    for i in range(5):
        x = TIME_COL_WIDTH + (i * DAY_WIDTH)
        
        draw.rectangle([x, y_day_header, x + DAY_WIDTH, y_day_header + DAY_HEADER_HEIGHT],
                      fill=COLORS['header'], outline=COLORS['grid'], width=1)
        
        day_name = week_dates[i]['day_name']
        day_number = week_dates[i]['day_number']
        
        # Nom du jour
        bbox = draw.textbbox((0, 0), day_name, font=fonts['header'])
        draw.text((x + (DAY_WIDTH - (bbox[2] - bbox[0])) // 2, y_day_header + 12),
                 day_name, fill=COLORS['text'], font=fonts['header'])
        
        # Numéro du jour (gros)
        num_text = str(day_number)
        bbox = draw.textbbox((0, 0), num_text, font=fonts['day_num'])
        draw.text((x + (DAY_WIDTH - (bbox[2] - bbox[0])) // 2, y_day_header + 35),
                 num_text, fill=COLORS['text'], font=fonts['day_num'])
    
    # ═══ GRILLE ═══
    y_start = HEADER_HEIGHT + DAY_HEADER_HEIGHT
    
    # Lignes heures
    for hour in range(START_HOUR, END_HOUR + 1):
        y = y_start + ((hour - START_HOUR) * HOUR_HEIGHT)
        
        hour_text = f"{hour:02d}:00"
        bbox = draw.textbbox((0, 0), hour_text, font=fonts['small'])
        draw.text(((TIME_COL_WIDTH - (bbox[2] - bbox[0])) // 2, y - 6),
                 hour_text, fill=COLORS['text_secondary'], font=fonts['small'])
        
        draw.line([(TIME_COL_WIDTH, y), (WIDTH, y)], fill=COLORS['grid'], width=1)
    
    # Lignes verticales
    for i in range(6):
        x = TIME_COL_WIDTH + (i * DAY_WIDTH)
        draw.line([(x, y_day_header), (x, HEIGHT - FOOTER_HEIGHT)], fill=COLORS['grid'], width=1)
    
    # ═══ ÉVÉNEMENTS AVEC COINS ARRONDIS ═══
    for day_index, events in week_events.items():
        if day_index >= 5:
            continue
        
        x_day = TIME_COL_WIDTH + (day_index * DAY_WIDTH)
        
        for event in events:
            start_hour = event['start'].hour + event['start'].minute / 60
            end_hour = event['end'].hour + event['end'].minute / 60
            
            start_hour = max(start_hour, START_HOUR)
            end_hour = min(end_hour, END_HOUR)
            
            y_event_start = y_start + ((start_hour - START_HOUR) * HOUR_HEIGHT)
            y_event_end = y_start + ((end_hour - START_HOUR) * HOUR_HEIGHT)
            event_height = y_event_end - y_event_start
            
            if event_height < 10:
                continue
            
            # Couleur selon type
            course_type = event['course_info']['type_cours'] or 'default'
            color = COURSE_COLORS.get(course_type, COURSE_COLORS['default'])
            
            # Rectangle arrondi avec radius=10 comme votre image
            padding = 3
            draw.rounded_rectangle(
                [x_day + padding, y_event_start + padding, 
                 x_day + DAY_WIDTH - padding, y_event_end - padding],
                radius=10,
                fill=color,
                outline=color
            )
            
            # Contenu ultra-lisible
            text_x = x_day + 12
            text_y = y_event_start + 8
            max_width = DAY_WIDTH - 24
            
            # 🕐 Horaires en gras
            start_time = event['start'].strftime('%H:%M')
            end_time = event['end'].strftime('%H:%M')
            time_text = f"🕐 {start_time} - {end_time}"
            draw.text((text_x, text_y), time_text, fill=COLORS['text'], font=fonts['event_time'])
            text_y += 18
            
            # 📚 Matière en gras
            matiere = event['course_info']['matiere']
            if matiere:
                matiere_short = matiere[:35]
                type_suffix = f" - {course_type}" if course_type != 'default' else ""
                matiere_text = f"📚 {matiere_short}{type_suffix}"
                
                lines = wrap_text(matiere_text, fonts['event_title'], max_width, draw)
                for line in lines[:2]:
                    if text_y < y_event_end - 30:
                        draw.text((text_x, text_y), line, fill=COLORS['text'], font=fonts['event_title'])
                        text_y += 14
            
            # 📍 Salle
            location = event.get('location', '')
            if location and text_y < y_event_end - 25:
                location_short = location[:30]
                draw.text((text_x, text_y), f"📍 {location_short}", 
                         fill=COLORS['text'], font=fonts['event_info'])
                text_y += 13
            
            # 👨‍🏫 Prof
            prof = event['course_info']['professeur']
            if prof and text_y < y_event_end - 15:
                draw.text((text_x, text_y), f"👨‍🏫 {prof}", 
                         fill=COLORS['text'], font=fonts['event_info'])
                text_y += 13
            
            # Badge événement spécial en haut à droite
            if event['course_info']['special_event']:
                special_text = event['course_info']['special_event']
                bbox = draw.textbbox((0, 0), special_text, font=fonts['small'])
                badge_width = (bbox[2] - bbox[0]) + 12
                badge_x = x_day + DAY_WIDTH - badge_width - 8
                badge_y = y_event_start + 8
                
                # Badge rouge/jaune selon le type
                badge_color = (231, 76, 60) if 'ANNULÉ' in special_text or 'EXAMEN' in special_text else (241, 196, 15)
                
                draw.rounded_rectangle(
                    [badge_x, badge_y, badge_x + badge_width, badge_y + 18],
                    radius=9,
                    fill=badge_color
                )
                draw.text((badge_x + 6, badge_y + 3), special_text, 
                         fill=COLORS['text'], font=fonts['small'])
    
    # ═══ FOOTER AVEC STATS ═══
    footer_y = HEIGHT - FOOTER_HEIGHT
    draw.rectangle([0, footer_y, WIDTH, HEIGHT], fill=COLORS['header'])
    
    # Calculer stats
    stats = calculate_statistics(week_events)
    
    total_text = f"📊 {stats['total_courses']} cours"
    hours_text = f"⏱️ {stats['total_hours']:.1f}h"
    avg_text = f"📈 {stats['total_courses']/5:.1f} cours/jour"
    
    stats_parts = [total_text, hours_text, avg_text]
    
    if stats['cancelled_count'] > 0:
        stats_parts.append(f"🚫 {stats['cancelled_count']} annulé(s)")
    
    stats_text = "  •  ".join(stats_parts)
    
    bbox = draw.textbbox((0, 0), stats_text, font=fonts['subtitle'])
    draw.text(((WIDTH - (bbox[2] - bbox[0])) // 2, footer_y + 12),
             stats_text, fill=COLORS['text_secondary'], font=fonts['subtitle'])
    
    # Légende
    legend_x = 20
    legend_y = footer_y + 12
    legend_items = [("📚 CM", COURSE_COLORS['CM']), ("✏️ TD", COURSE_COLORS['TD']), 
                   ("💻 TP", COURSE_COLORS['TP']), ("📝 Examen", COURSE_COLORS['Examen'])]
    
    for label, color in legend_items:
        # Petit carré de couleur
        draw.rounded_rectangle([legend_x, legend_y, legend_x + 12, legend_y + 12], 
                              radius=3, fill=color)
        draw.text((legend_x + 16, legend_y), label, fill=COLORS['text_secondary'], font=fonts['small'])
        legend_x += 80
    
    logger.info(f"✅ Image générée: {WIDTH}x{HEIGHT}px")
    return img

# ═══════════════════════════════════════════════════════════════════════════════
# 📤 ENVOI DISCORD AVEC MESSAGE ENRICHI
# ═══════════════════════════════════════════════════════════════════════════════

def send_to_discord(group_name, image, week_dates, stats):
    """Envoie sur Discord avec message propre et enrichi"""
    
    webhook_url = WEBHOOKS.get(group_name)
    if not webhook_url:
        logger.error(f"❌ Pas de webhook pour {group_name}")
        return False
    
    role_id = ROLE_IDS.get(group_name)
    mention = f"<@&{role_id}>" if role_id else ""
    
    try:
        # Image
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='PNG', optimize=True, quality=95)
        img_byte_arr.seek(0)
        
        # Message ultra-propre
        monday = week_dates[0]['formatted']
        friday = week_dates[4]['formatted']
        
        message_lines = [
            mention,
            "",
            "📅 **Emploi du temps de la semaine**",
            f"📆 **Du {monday} au {friday}**",
            "",
        ]
        
        # Stats importantes
        if stats['total_courses'] > 0:
            message_lines.append(f"📊 **{stats['total_courses']} cours** cette semaine ({stats['total_hours']:.1f}h de cours)")
            
            # Répartition
            if stats['by_type']:
                types_emojis = {'CM': '📚', 'TD': '✏️', 'TP': '💻', 'Examen': '📝', 'Projet': '🎯'}
                type_details = []
                for course_type, count in stats['by_type'].most_common(4):
                    emoji = types_emojis.get(course_type, '📖')
                    type_details.append(f"{emoji} {course_type}: {count}")
                
                message_lines.append("🎯 " + " • ".join(type_details))
            
            # Événements spéciaux
            if stats['cancelled_count'] > 0:
                message_lines.append(f"")
                message_lines.append(f"⚠️ **{stats['cancelled_count']} cours annulé(s)** cette semaine")
            
            if stats['special_events']:
                unique_events = list(set(stats['special_events']))
                for event in unique_events:
                    if 'EXAMEN' in event or 'PARTIEL' in event:
                        message_lines.append(f"")
                        message_lines.append(f"🔴 **Attention: {event}**")
        
        else:
            message_lines.append("🎉 **Aucun cours cette semaine !**")
            message_lines.append("Profitez bien de votre repos ! 😎")
        
        message_lines.append("")
        message_lines.append("_Bon courage ! 💪_")
        
        content = "\n".join(message_lines)
        
        # Envoi
        files = {'file': ('edt.png', img_byte_arr, 'image/png')}
        
        group_emojis = {"Groupe 1": "📘", "Groupe 2": "📕", "Groupe 3": "📗", "CM Communs": "📚"}
        emoji = group_emojis.get(group_name, "📅")
        
        payload = {
            "username": f"{emoji} EDT Bot - {group_name}",
            "content": content,
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
    """Orchestration principale"""
    
    print("=" * 80)
    print("🎓 EDT BOT L2 INFO - VERSION FINALE ULTRA-LISIBLE".center(80))
    print("=" * 80)
    
    start_time = time.time()
    
    now = get_paris_now()
    logger.info(f"🕐 Heure: {now.strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Toujours semaine suivante
    week_offset, week_reason = determine_week_mode()
    logger.info(f"📆 Mode: {week_reason}")
    
    week_dates = get_week_dates(week_offset)
    logger.info(f"📅 Période: {week_dates[0]['formatted']} → {week_dates[4]['formatted']}")
    
    success_count = 0
    total_groups = len(EDT_URLS)
    
    for group_name, edt_url in EDT_URLS.items():
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"📋 {group_name.upper()}")
            logger.info(f"{'='*60}")
            
            if group_name not in WEBHOOKS:
                logger.warning(f"⚠️ Pas de webhook")
                continue
            
            # Récupération
            events = fetch_and_parse_edt(group_name, edt_url)
            if not events:
                logger.warning(f"⚠️ Aucun événement")
                continue
            
            # Filtrage
            week_events = filter_events_for_week(events, week_dates)
            stats = calculate_statistics(week_events)
            
            logger.info(f"📊 {stats['total_courses']} cours, {stats['total_hours']:.1f}h")
            
            # Génération
            logger.info(f"🎨 Génération image...")
            image = create_ultra_readable_edt(group_name, week_events, week_dates)
            
            # Envoi
            if send_to_discord(group_name, image, week_dates, stats):
                success_count += 1
            
            time.sleep(3)
            
        except Exception as e:
            logger.error(f"❌ Erreur {group_name}: {e}")
            import traceback
            traceback.print_exc()
    
    elapsed = time.time() - start_time
    
    print(f"\n{'='*80}")
    print("🎯 RÉSUMÉ".center(80))
    print(f"{'='*80}")
    print(f"✅ Groupes envoyés: {success_count}/{total_groups}")
    print(f"⏱️  Temps: {elapsed:.2f}s")
    print(f"{'='*80}\n")
    
    if success_count == total_groups:
        print("🎉 TOUS LES EDT ENVOYÉS ! 🎉")
        return 0
    elif success_count > 0:
        print("⚠️ ENVOIS PARTIELS")
        return 1
    else:
        print("❌ ÉCHEC COMPLET")
        return 2

if __name__ == "__main__":
    sys.exit(main())

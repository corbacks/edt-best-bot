#!/usr/bin/env python3
"""
🎓 EDT Bot L2 INFO - VERSION FINALE OPTIMALE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Système de couleurs optimisé:
- Couleur principale = MATIÈRE (cohérente par matière)
- Bande latérale colorée = TYPE (CM/TD/TP)
- Layout: Horaire → Matière - Type → Salle → Prof
- Horaires en blanc pur et gras pour visibilité max
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
import hashlib

# ═══════════════════════════════════════════════════════════════════════════════
# 🎨 CONFIGURATION VISUELLE
# ═══════════════════════════════════════════════════════════════════════════════

COLORS = {
    'background': (20, 25, 38),
    'header': (28, 35, 50),
    'grid': (50, 58, 75),
    'text': (255, 255, 255),
    'text_bright': (255, 255, 255),
    'shadow': (0, 0, 0),
}

# Couleurs par TYPE de cours (pour la bande latérale)
TYPE_COLORS = {
    'CM': (138, 80, 183),      # Violet
    'TD': (230, 145, 56),      # Orange
    'TP': (52, 152, 219),      # Bleu clair
    'Examen': (231, 76, 60),   # Rouge
    'Partiel': (231, 76, 60),  # Rouge
    'Projet': (46, 204, 113),  # Vert
    'Tutorat': (241, 196, 15), # Jaune (remplace annulé)
    'default': (100, 110, 130) # Gris
}

# Palette de couleurs pour les MATIÈRES (cohérentes)
SUBJECT_COLOR_PALETTE = [
    (65, 90, 140),      # Bleu foncé
    (85, 110, 95),      # Vert foncé
    (120, 70, 100),     # Violet foncé
    (100, 85, 65),      # Marron
    (70, 95, 110),      # Bleu-gris
    (95, 75, 90),       # Prune
    (80, 100, 85),      # Vert-gris
    (110, 90, 75),      # Brun
    (75, 85, 105),      # Bleu ardoise
    (100, 80, 70),      # Terre cuite
    (70, 100, 95),      # Turquoise foncé
    (105, 75, 85),      # Rose foncé
]

SPECIAL_COLORS = {
    'makeup': (180, 120, 30),  # Orange doré pour rattrapage
}

SPECIAL_EVENTS = {
    'annulé': 'TUTORAT',
    'annule': 'TUTORAT',
    'canceled': 'TUTORAT',
    'tutorat': 'TUTORAT',
    'examen': 'EXAMEN',
    'partiel': 'PARTIEL',
    'seconde chance': 'RATTRAPAGE',
    '2nde chance': 'RATTRAPAGE',
    'rattrapage': 'RATTRAPAGE',
    'soutenance': 'SOUTENANCE',
    'contrôle': 'CONTROLE',
    'controle': 'CONTROLE',
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

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)

# Cache des couleurs par matière
subject_color_cache = {}

def get_subject_color(subject_name):
    """Retourne une couleur cohérente pour chaque matière"""
    if not subject_name:
        return SUBJECT_COLOR_PALETTE[0]
    
    if subject_name in subject_color_cache:
        return subject_color_cache[subject_name]
    
    # Générer un hash cohérent basé sur le nom de la matière
    hash_value = int(hashlib.md5(subject_name.encode()).hexdigest(), 16)
    color_index = hash_value % len(SUBJECT_COLOR_PALETTE)
    color = SUBJECT_COLOR_PALETTE[color_index]
    
    subject_color_cache[subject_name] = color
    return color

# ═══════════════════════════════════════════════════════════════════════════════
# ⏰ GESTION DU TEMPS
# ═══════════════════════════════════════════════════════════════════════════════

def get_paris_offset(dt):
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
    utc_now = datetime.now(timezone.utc).replace(tzinfo=None)
    offset = get_paris_offset(utc_now)
    return utc_now + timedelta(hours=offset)

# ═══════════════════════════════════════════════════════════════════════════════
# 🌐 RÉCUPÉRATION DES DONNÉES
# ═══════════════════════════════════════════════════════════════════════════════

def fetch_with_retry(url, max_retries=5, initial_timeout=30):
    for attempt in range(max_retries):
        try:
            timeout = initial_timeout + (attempt * 15)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/calendar,*/*',
                'Connection': 'keep-alive',
            }
            
            session = requests.Session()
            session.headers.update(headers)
            response = session.get(url, timeout=timeout, allow_redirects=True, verify=True)
            response.raise_for_status()
            
            logger.info(f"✅ Récupération réussie")
            return response.text
            
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    
    return None

def get_week_dates(week_offset=0):
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
    week_mode = os.environ.get('WEEK_MODE', 'auto')
    if week_mode == 'current':
        return 0, "courante"
    elif week_mode == 'next':
        return 1, "suivante"
    return 1, "suivante"

# ═══════════════════════════════════════════════════════════════════════════════
# 📝 PARSING
# ═══════════════════════════════════════════════════════════════════════════════

def parse_ical_datetime(dt_string):
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
    
    except:
        pass
    
    return None

def detect_special_event(summary, description=""):
    text = (summary + " " + description).lower()
    for keyword, label in SPECIAL_EVENTS.items():
        if keyword in text:
            return label
    return None

def extract_course_info(summary, description=""):
    course_info = {
        'type_cours': '',
        'matiere': '',
        'professeur': '',
        'groupe': '',
        'special_event': None,
        'is_tutorat': False,
        'is_makeup': False
    }
    
    if not summary:
        return course_info
    
    special = detect_special_event(summary, description)
    course_info['special_event'] = special
    
    if 'annulé' in summary.lower() or 'annule' in summary.lower() or 'tutorat' in summary.lower():
        course_info['is_tutorat'] = True
        course_info['type_cours'] = 'Tutorat'
    
    if special and 'RATTRAPAGE' in special:
        course_info['is_makeup'] = True
    
    if not course_info['is_tutorat']:
        type_patterns = [(r'\b(CM|TD|TP|Examen|Partiel|Projet|Soutenance)\b', 'type_cours')]
        
        for pattern, field in type_patterns:
            match = re.search(pattern, summary, re.IGNORECASE)
            if match:
                course_info[field] = match.group(1).upper()
                break
    
    parts = re.split(r'[-–—]', summary)
    if len(parts) >= 2:
        course_info['matiere'] = parts[1].strip()
    else:
        matiere = re.sub(r'^(CM|TD|TP|Examen|Partiel|Projet|Tutorat)\s*-?\s*', '', summary, flags=re.IGNORECASE)
        course_info['matiere'] = matiere.strip()
    
    course_info['matiere'] = re.sub(r'\s*\(.*?\)\s*', '', course_info['matiere'])
    
    prof_patterns = [
        r'(?:Prof|Enseignant|Professeur)[:\s]+([A-ZÀ-Ÿ][a-zà-ÿ]+(?:\s+[A-ZÀ-Ÿ][a-zà-ÿ]+)*)',
        r'\bM\.\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'\bMme\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
    ]
    
    for pattern in prof_patterns:
        match = re.search(pattern, description + " " + summary, re.IGNORECASE | re.MULTILINE)
        if match:
            course_info['professeur'] = match.group(1)
            break
    
    groupe_match = re.search(r'Gr[ou]*pe?\s*(\d+)', summary, re.IGNORECASE)
    if groupe_match:
        course_info['groupe'] = f"Gr{groupe_match.group(1)}"
    
    return course_info

def fetch_and_parse_edt(group_name, edt_url):
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
        return []

def filter_events_for_week(events, week_dates):
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

def calculate_statistics(week_events):
    stats = {
        'total_courses': 0,
        'total_hours': 0,
        'by_type': Counter(),
        'tutorat_count': 0,
        'makeup_count': 0,
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
        
        if event['course_info']['is_tutorat']:
            stats['tutorat_count'] += 1
        
        if event['course_info']['is_makeup']:
            stats['makeup_count'] += 1
        
        if event['course_info']['special_event']:
            stats['special_events'].append(event['course_info']['special_event'])
    
    return stats

# ═══════════════════════════════════════════════════════════════════════════════
# 🎨 GÉNÉRATION IMAGE
# ═══════════════════════════════════════════════════════════════════════════════

def load_fonts():
    fonts = {}
    try:
        fonts['title'] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
        fonts['date'] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        fonts['header'] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 17)
        fonts['day_num'] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        fonts['event_time'] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)  # ÉNORME et GRAS
        fonts['event_matiere'] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 17)
        fonts['event_info'] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
        fonts['small'] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        fonts['hour'] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except:
        fonts = {k: ImageFont.load_default() for k in ['title', 'date', 'header', 'day_num', 'event_time', 'event_matiere', 'event_info', 'small', 'hour']}
    
    return fonts

def wrap_text(text, font, max_width, draw):
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

def draw_centered_text(draw, text, font, y, x_start, x_end, color):
    """Dessine du texte parfaitement centré"""
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    center_x = (x_start + x_end) // 2
    x = center_x - (text_width // 2)
    draw.text((x, y), text, fill=color, font=font)
    return bbox[3] - bbox[1]

def create_optimal_edt(group_name, week_events, week_dates):
    """Crée l'EDT avec couleurs par matière et bande latérale par type"""
    
    WIDTH = 1600
    HEIGHT = 1100
    HEADER_HEIGHT = 70
    DAY_HEADER_HEIGHT = 70
    TIME_COL_WIDTH = 70
    FOOTER_HEIGHT = 45
    DAY_WIDTH = (WIDTH - TIME_COL_WIDTH) // 5
    
    START_HOUR = 8
    END_HOUR = 19
    HOURS = END_HOUR - START_HOUR
    CONTENT_HEIGHT = HEIGHT - HEADER_HEIGHT - DAY_HEADER_HEIGHT - FOOTER_HEIGHT
    HOUR_HEIGHT = CONTENT_HEIGHT / HOURS
    
    img = Image.new('RGB', (WIDTH, HEIGHT), COLORS['background'])
    draw = ImageDraw.Draw(img, 'RGBA')
    fonts = load_fonts()
    
    # ═══ HEADER ═══
    draw.rectangle([0, 0, WIDTH, HEADER_HEIGHT], fill=COLORS['header'])
    
    title = f"EDT {group_name} - Cette Semaine"
    bbox = draw.textbbox((0, 0), title, font=fonts['title'])
    draw.text(((WIDTH - (bbox[2] - bbox[0])) // 2, 8), title, fill=COLORS['text_bright'], font=fonts['title'])
    
    monday = week_dates[0]['formatted']
    friday = week_dates[4]['formatted']
    date_text = f"Du {monday} au {friday}"
    bbox = draw.textbbox((0, 0), date_text, font=fonts['date'])
    draw.text(((WIDTH - (bbox[2] - bbox[0])) // 2, 40), date_text, fill=COLORS['text_bright'], font=fonts['date'])
    
    # ═══ HEADERS JOURS ═══
    y_day_header = HEADER_HEIGHT
    
    for i in range(5):
        x = TIME_COL_WIDTH + (i * DAY_WIDTH)
        
        draw.rectangle([x, y_day_header, x + DAY_WIDTH, y_day_header + DAY_HEADER_HEIGHT],
                      fill=COLORS['header'], outline=COLORS['grid'], width=2)
        
        day_name = week_dates[i]['day_name']
        day_number = week_dates[i]['day_number']
        
        bbox = draw.textbbox((0, 0), day_name, font=fonts['header'])
        draw.text((x + (DAY_WIDTH - (bbox[2] - bbox[0])) // 2, y_day_header + 8),
                 day_name, fill=COLORS['text_bright'], font=fonts['header'])
        
        num_text = str(day_number)
        bbox = draw.textbbox((0, 0), num_text, font=fonts['day_num'])
        draw.text((x + (DAY_WIDTH - (bbox[2] - bbox[0])) // 2, y_day_header + 32),
                 num_text, fill=COLORS['text_bright'], font=fonts['day_num'])
    
    # ═══ GRILLE ═══
    y_start = HEADER_HEIGHT + DAY_HEADER_HEIGHT
    
    for hour in range(START_HOUR, END_HOUR + 1):
        y = y_start + ((hour - START_HOUR) * HOUR_HEIGHT)
        
        hour_text = f"{hour:02d}:00"
        bbox = draw.textbbox((0, 0), hour_text, font=fonts['hour'])
        draw.text(((TIME_COL_WIDTH - (bbox[2] - bbox[0])) // 2, y - 6),
                 hour_text, fill=COLORS['text_bright'], font=fonts['hour'])
        
        draw.line([(TIME_COL_WIDTH, y), (WIDTH, y)], fill=COLORS['grid'], width=1)
    
    for i in range(6):
        x = TIME_COL_WIDTH + (i * DAY_WIDTH)
        draw.line([(x, y_day_header), (x, HEIGHT - FOOTER_HEIGHT)], fill=COLORS['grid'], width=2)
    
    # ═══ ÉVÉNEMENTS ═══
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
            
            # COULEUR PRINCIPALE = MATIÈRE
            matiere = event['course_info']['matiere'] or 'Défaut'
            main_color = get_subject_color(matiere)
            
            # COULEUR BANDE LATÉRALE = TYPE
            course_type = event['course_info']['type_cours'] or 'default'
            side_color = TYPE_COLORS.get(course_type, TYPE_COLORS['default'])
            
            # Rattrapage -> couleur spéciale
            if event['course_info']['is_makeup']:
                main_color = SPECIAL_COLORS['makeup']
            
            padding = 4
            
            # Fond principal (couleur matière)
            draw.rounded_rectangle(
                [x_day + padding, y_event_start + padding, 
                 x_day + DAY_WIDTH - padding, y_event_end - padding],
                radius=10,
                fill=main_color
            )
            
            # BANDE LATÉRALE GAUCHE (couleur type)
            band_width = 8
            draw.rounded_rectangle(
                [x_day + padding, y_event_start + padding,
                 x_day + padding + band_width, y_event_end - padding],
                radius=10,
                fill=side_color
            )
            
            # CONTENU CENTRÉ
            x_start = x_day + padding + band_width + 8
            x_end = x_day + DAY_WIDTH - padding - 8
            current_y = y_event_start + 12
            
            # 1. HORAIRES (BLANC PUR, GRAS, ÉNORME)
            start_time = event['start'].strftime('%H:%M')
            end_time = event['end'].strftime('%H:%M')
            time_text = f"{start_time} - {end_time}"
            h = draw_centered_text(draw, time_text, fonts['event_time'], current_y, x_start, x_end, (255, 255, 255))
            current_y += h + 10
            
            # 2. MATIÈRE - TYPE (centré)
            matiere_display = matiere[:28]
            type_display = f" - {course_type}" if course_type and course_type != 'default' else ""
            matiere_text = f"{matiere_display}{type_display}"
            
            lines = wrap_text(matiere_text, fonts['event_matiere'], (x_end - x_start), draw)
            for line in lines[:2]:
                if current_y < y_event_end - 40:
                    h = draw_centered_text(draw, line, fonts['event_matiere'], current_y, x_start, x_end, COLORS['text_bright'])
                    current_y += h + 6
            
            # 3. SALLE (centrée)
            location = event.get('location', '')
            if location and current_y < y_event_end - 28:
                location_short = location[:26]
                h = draw_centered_text(draw, location_short, fonts['event_info'], current_y, x_start, x_end, COLORS['text_bright'])
                current_y += h + 6
            
            # 4. PROFESSEUR (centré)
            prof = event['course_info']['professeur']
            if prof and current_y < y_event_end - 16:
                draw_centered_text(draw, prof, fonts['event_info'], current_y, x_start, x_end, COLORS['text_bright'])
    
    # ═══ FOOTER ═══
    footer_y = HEIGHT - FOOTER_HEIGHT
    draw.rectangle([0, footer_y, WIDTH, HEIGHT], fill=COLORS['header'])
    
    stats = calculate_statistics(week_events)
    
    stats_parts = [f"{stats['total_courses']} cours", f"{stats['total_hours']:.1f}h", f"{stats['total_courses']/5:.1f} cours/jour"]
    
    if stats['tutorat_count'] > 0:
        stats_parts.append(f"{stats['tutorat_count']} tutorat(s)")
    
    if stats['makeup_count'] > 0:
        stats_parts.append(f"{stats['makeup_count']} rattrapage(s)")
    
    stats_text = "  •  ".join(stats_parts)
    
    bbox = draw.textbbox((0, 0), stats_text, font=fonts['date'])
    draw.text(((WIDTH - (bbox[2] - bbox[0])) // 2, footer_y + 12),
             stats_text, fill=COLORS['text_bright'], font=fonts['date'])
    
    # Légende
    legend_x = 20
    legend_y = footer_y + 14
    legend_items = [
        ("CM", TYPE_COLORS['CM']), 
        ("TD", TYPE_COLORS['TD']), 
        ("TP", TYPE_COLORS['TP']), 
        ("Tutorat", TYPE_COLORS['Tutorat']),
        ("Rattrapage", SPECIAL_COLORS['makeup'])
    ]
    
    for label, color in legend_items:
        draw.rounded_rectangle([legend_x, legend_y, legend_x + 14, legend_y + 14], 
                              radius=4, fill=color)
        draw.text((legend_x + 18, legend_y + 1), label, fill=COLORS['text_bright'], font=fonts['small'])
        legend_x += 95
    
    logger.info(f"✅ Image générée: {WIDTH}x{HEIGHT}px")
    return img

# ═══════════════════════════════════════════════════════════════════════════════
# 📤 ENVOI DISCORD
# ═══════════════════════════════════════════════════════════════════════════════

def send_to_discord(group_name, image, week_dates, stats):
    webhook_url = WEBHOOKS.get(group_name)
    if not webhook_url:
        return False
    
    role_id = ROLE_IDS.get(group_name)
    mention = f"<@&{role_id}>" if role_id else ""
    
    try:
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='PNG', optimize=True, quality=95)
        img_byte_arr.seek(0)
        
        monday = week_dates[0]['formatted']
        friday = week_dates[4]['formatted']
        
        message_lines = [mention, "", "📅 **Emploi du temps de la semaine**", f"📆 **Du {monday} au {friday}**", ""]
        
        if stats['total_courses'] > 0:
            message_lines.append(f"📊 **{stats['total_courses']} cours** ({stats['total_hours']:.1f}h)")
            
            if stats['by_type']:
                types_emojis = {'CM': '📚', 'TD': '✏️', 'TP': '💻', 'Examen': '📝', 'Projet': '🎯', 'Tutorat': '👥'}
                type_details = [f"{types_emojis.get(ct, '📖')} {ct}: {c}" for ct, c in stats['by_type'].most_common(5)]
                message_lines.append("🎯 " + " • ".join(type_details))
            
            if stats['tutorat_count'] > 0:
                message_lines.append(f"")
                message_lines.append(f"👥 **{stats['tutorat_count']} séance(s) de tutorat**")
            
            if stats['makeup_count'] > 0:
                message_lines.append(f"🔄 **{stats['makeup_count']} rattrapage(s)**")
        else:
            message_lines.append("🎉 **Aucun cours !**")
        
        message_lines.append("")
        message_lines.append("_Bon courage ! 💪_")
        
        content = "\n".join(message_lines)
        
        files = {'file': ('edt.png', img_byte_arr, 'image/png')}
        
        group_emojis = {"Groupe 1": "📘", "Groupe 2": "📕", "Groupe 3": "📗", "CM Communs": "📚"}
        emoji = group_emojis.get(group_name, "📅")
        
        payload = {"username": f"{emoji} EDT Bot - {group_name}", "content": content}
        
        response = requests.post(webhook_url, data=payload, files=files, timeout=30)
        response.raise_for_status()
        
        logger.info(f"✅ Envoyé")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        return False

# ═══════════════════════════════════════════════════════════════════════════════
# 🚀 MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("🎓 EDT BOT - VERSION FINALE OPTIMALE")
    start_time = time.time()
    
    week_offset, _ = determine_week_mode()
    week_dates = get_week_dates(week_offset)
    
    success_count = 0
    
    for group_name, edt_url in EDT_URLS.items():
        try:
            logger.info(f"📋 {group_name}")
            
            events = fetch_and_parse_edt(group_name, edt_url)
            if not events:
                continue
            
            week_events = filter_events_for_week(events, week_dates)
            stats = calculate_statistics(week_events)
            
            image = create_optimal_edt(group_name, week_events, week_dates)
            
            if send_to_discord(group_name, image, week_dates, stats):
                success_count += 1
            
            time.sleep(3)
            
        except Exception as e:
            logger.error(f"❌ {group_name}: {e}")
    
    print(f"✅ {success_count}/{len(EDT_URLS)} envoyés en {time.time()-start_time:.1f}s")
    return 0 if success_count == len(EDT_URLS) else 1

if __name__ == "__main__":
    sys.exit(main())

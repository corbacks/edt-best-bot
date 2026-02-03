#!/usr/bin/env python3
"""
🎓 EDT Bot L2 INFO - Version FINALE Ultra-Visible
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Optimisé pour une visibilité maximale:
- Texte GROS et centré
- Header compact
- Pas d'emojis dans l'image (Discord uniquement)
- Plage 8h-19h
- Design épuré et élégant
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
# 🎨 CONFIGURATION VISUELLE
# ═══════════════════════════════════════════════════════════════════════════════

COLORS = {
    'background': (25, 30, 45),
    'header': (30, 38, 58),
    'grid': (45, 52, 72),
    'text': (255, 255, 255),
    'text_secondary': (160, 170, 190),
    'shadow': (0, 0, 0),
}

COURSE_COLORS = {
    'CM': (138, 80, 183),
    'TD': (230, 145, 56),
    'TP': (52, 152, 219),
    'Examen': (231, 76, 60),
    'Partiel': (231, 76, 60),
    'Projet': (46, 204, 113),
    'Seconde Chance': (241, 196, 15),
    'default': (70, 80, 100)
}

SPECIAL_EVENTS = {
    'annulé': 'ANNULE',
    'annule': 'ANNULE',
    'canceled': 'ANNULE',
    'examen': 'EXAMEN',
    'partiel': 'PARTIEL',
    'seconde chance': '2ND CHANCE',
    '2nde chance': '2ND CHANCE',
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
            
            logger.info(f"✅ Récupération réussie ({response.status_code})")
            return response.text
            
        except Exception as e:
            logger.warning(f"⏱️ Erreur tentative {attempt + 1}: {str(e)[:100]}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                time.sleep(wait_time)
    
    logger.error(f"💥 Échec définitif")
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
        return 0, "courante (forcé)"
    elif week_mode == 'next':
        return 1, "suivante (forcé)"
    return 1, "suivante (automatique)"

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
    
    except Exception as e:
        logger.warning(f"⚠️ Erreur parse date: {e}")
    
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
        'is_cancelled': False
    }
    
    if not summary:
        return course_info
    
    special = detect_special_event(summary, description)
    course_info['special_event'] = special
    
    if 'annulé' in summary.lower() or 'annule' in summary.lower():
        course_info['is_cancelled'] = True
    
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
        matiere = re.sub(r'^(CM|TD|TP|Examen|Partiel|Projet)\s*-?\s*', '', summary, flags=re.IGNORECASE)
        course_info['matiere'] = matiere.strip()
    
    course_info['matiere'] = re.sub(r'\s*\(.*?\)\s*', '', course_info['matiere'])
    
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
# 🎨 GÉNÉRATION IMAGE ULTRA-VISIBLE
# ═══════════════════════════════════════════════════════════════════════════════

def load_fonts():
    fonts = {}
    try:
        # Polices PLUS GRANDES
        fonts['title'] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        fonts['subtitle'] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        fonts['header'] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        fonts['day_num'] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        fonts['event_time'] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)  # Plus gros
        fonts['event_matiere'] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)  # Plus gros
        fonts['event_info'] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)  # Plus gros
        fonts['small'] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
        fonts['hour'] = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except:
        fonts = {k: ImageFont.load_default() for k in ['title', 'subtitle', 'header', 'day_num', 'event_time', 'event_matiere', 'event_info', 'small', 'hour']}
    
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

def create_ultra_visible_edt(group_name, week_events, week_dates):
    """Crée l'EDT ultra-visible avec texte GROS et centré"""
    
    # Dimensions
    WIDTH = 1600
    HEIGHT = 1100
    HEADER_HEIGHT = 70  # Réduit de 90 à 70
    DAY_HEADER_HEIGHT = 70
    TIME_COL_WIDTH = 70
    FOOTER_HEIGHT = 40
    DAY_WIDTH = (WIDTH - TIME_COL_WIDTH) // 5
    
    # Heures 8h-19h
    START_HOUR = 8
    END_HOUR = 19
    HOURS = END_HOUR - START_HOUR
    CONTENT_HEIGHT = HEIGHT - HEADER_HEIGHT - DAY_HEADER_HEIGHT - FOOTER_HEIGHT
    HOUR_HEIGHT = CONTENT_HEIGHT / HOURS
    
    # Image
    img = Image.new('RGB', (WIDTH, HEIGHT), COLORS['background'])
    draw = ImageDraw.Draw(img, 'RGBA')
    fonts = load_fonts()
    
    # ═══ HEADER COMPACT ═══
    draw.rectangle([0, 0, WIDTH, HEADER_HEIGHT], fill=COLORS['header'])
    
    group_emojis = {"Groupe 1": "📘", "Groupe 2": "📕", "Groupe 3": "📗", "CM Communs": "📚"}
    emoji = group_emojis.get(group_name, "📅")
    
    title = f"EDT {group_name} - Cette Semaine"
    bbox = draw.textbbox((0, 0), title, font=fonts['title'])
    draw.text(((WIDTH - (bbox[2] - bbox[0])) // 2, 12), title, fill=COLORS['text'], font=fonts['title'])
    
    monday = week_dates[0]['formatted']
    friday = week_dates[4]['formatted']
    subtitle = f"Du {monday} au {friday}"
    bbox = draw.textbbox((0, 0), subtitle, font=fonts['subtitle'])
    draw.text(((WIDTH - (bbox[2] - bbox[0])) // 2, 42), subtitle, fill=COLORS['text_secondary'], font=fonts['subtitle'])
    
    # ═══ HEADERS DES JOURS ═══
    y_day_header = HEADER_HEIGHT
    
    for i in range(5):
        x = TIME_COL_WIDTH + (i * DAY_WIDTH)
        
        draw.rectangle([x, y_day_header, x + DAY_WIDTH, y_day_header + DAY_HEADER_HEIGHT],
                      fill=COLORS['header'], outline=COLORS['grid'], width=1)
        
        day_name = week_dates[i]['day_name']
        day_number = week_dates[i]['day_number']
        
        bbox = draw.textbbox((0, 0), day_name, font=fonts['header'])
        draw.text((x + (DAY_WIDTH - (bbox[2] - bbox[0])) // 2, y_day_header + 10),
                 day_name, fill=COLORS['text'], font=fonts['header'])
        
        num_text = str(day_number)
        bbox = draw.textbbox((0, 0), num_text, font=fonts['day_num'])
        draw.text((x + (DAY_WIDTH - (bbox[2] - bbox[0])) // 2, y_day_header + 32),
                 num_text, fill=COLORS['text'], font=fonts['day_num'])
    
    # ═══ GRILLE ═══
    y_start = HEADER_HEIGHT + DAY_HEADER_HEIGHT
    
    for hour in range(START_HOUR, END_HOUR + 1):
        y = y_start + ((hour - START_HOUR) * HOUR_HEIGHT)
        
        hour_text = f"{hour:02d}:00"
        bbox = draw.textbbox((0, 0), hour_text, font=fonts['hour'])
        draw.text(((TIME_COL_WIDTH - (bbox[2] - bbox[0])) // 2, y - 6),
                 hour_text, fill=COLORS['text_secondary'], font=fonts['hour'])
        
        draw.line([(TIME_COL_WIDTH, y), (WIDTH, y)], fill=COLORS['grid'], width=1)
    
    for i in range(6):
        x = TIME_COL_WIDTH + (i * DAY_WIDTH)
        draw.line([(x, y_day_header), (x, HEIGHT - FOOTER_HEIGHT)], fill=COLORS['grid'], width=1)
    
    # ═══ ÉVÉNEMENTS ULTRA-VISIBLES ═══
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
            
            course_type = event['course_info']['type_cours'] or 'default'
            color = COURSE_COLORS.get(course_type, COURSE_COLORS['default'])
            
            # Rectangle arrondi
            padding = 3
            draw.rounded_rectangle(
                [x_day + padding, y_event_start + padding, 
                 x_day + DAY_WIDTH - padding, y_event_end - padding],
                radius=10,
                fill=color,
                outline=color
            )
            
            # Contenu CENTRÉ et GROS
            center_x = x_day + (DAY_WIDTH // 2)
            text_y = y_event_start + 10
            max_width = DAY_WIDTH - 20
            
            # Badge événement spécial en haut
            if event['course_info']['special_event']:
                special_text = event['course_info']['special_event']
                bbox = draw.textbbox((0, 0), special_text, font=fonts['small'])
                badge_width = (bbox[2] - bbox[0]) + 12
                badge_x = center_x - (badge_width // 2)
                badge_y = y_event_start + 6
                
                badge_color = (231, 76, 60) if 'ANNULE' in special_text or 'EXAMEN' in special_text else (241, 196, 15)
                
                draw.rounded_rectangle(
                    [badge_x, badge_y, badge_x + badge_width, badge_y + 18],
                    radius=9,
                    fill=badge_color
                )
                draw.text((badge_x + 6, badge_y + 3), special_text, 
                         fill=COLORS['text'], font=fonts['small'])
                text_y += 26
            
            # Horaires CENTRÉS ET GROS
            start_time = event['start'].strftime('%H:%M')
            end_time = event['end'].strftime('%H:%M')
            time_text = f"{start_time} - {end_time}"
            bbox = draw.textbbox((0, 0), time_text, font=fonts['event_time'])
            text_width = bbox[2] - bbox[0]
            draw.text((center_x - text_width // 2, text_y), time_text, 
                     fill=COLORS['text'], font=fonts['event_time'])
            text_y += 22
            
            # Matière CENTRÉE ET GROSSE
            matiere = event['course_info']['matiere']
            if matiere and text_y < y_event_end - 40:
                matiere_short = matiere[:35]
                type_suffix = f" - {course_type}" if course_type != 'default' else ""
                matiere_text = f"{matiere_short}{type_suffix}"
                
                lines = wrap_text(matiere_text, fonts['event_matiere'], max_width, draw)
                for line in lines[:2]:
                    if text_y < y_event_end - 30:
                        bbox = draw.textbbox((0, 0), line, font=fonts['event_matiere'])
                        line_width = bbox[2] - bbox[0]
                        draw.text((center_x - line_width // 2, text_y), line, 
                                 fill=COLORS['text'], font=fonts['event_matiere'])
                        text_y += 18
            
            # Salle CENTRÉE
            location = event.get('location', '')
            if location and text_y < y_event_end - 25:
                location_short = location[:30]
                bbox = draw.textbbox((0, 0), location_short, font=fonts['event_info'])
                loc_width = bbox[2] - bbox[0]
                draw.text((center_x - loc_width // 2, text_y), location_short, 
                         fill=COLORS['text'], font=fonts['event_info'])
                text_y += 16
            
            # Prof CENTRÉ
            prof = event['course_info']['professeur']
            if prof and text_y < y_event_end - 15:
                bbox = draw.textbbox((0, 0), prof, font=fonts['event_info'])
                prof_width = bbox[2] - bbox[0]
                draw.text((center_x - prof_width // 2, text_y), prof, 
                         fill=COLORS['text'], font=fonts['event_info'])
    
    # ═══ FOOTER AVEC STATS ═══
    footer_y = HEIGHT - FOOTER_HEIGHT
    draw.rectangle([0, footer_y, WIDTH, HEIGHT], fill=COLORS['header'])
    
    stats = calculate_statistics(week_events)
    
    total_text = f"{stats['total_courses']} cours"
    hours_text = f"{stats['total_hours']:.1f}h"
    avg_text = f"{stats['total_courses']/5:.1f} cours/jour"
    
    stats_parts = [total_text, hours_text, avg_text]
    
    if stats['cancelled_count'] > 0:
        stats_parts.append(f"{stats['cancelled_count']} annule(s)")
    
    stats_text = "  •  ".join(stats_parts)
    
    bbox = draw.textbbox((0, 0), stats_text, font=fonts['subtitle'])
    draw.text(((WIDTH - (bbox[2] - bbox[0])) // 2, footer_y + 12),
             stats_text, fill=COLORS['text_secondary'], font=fonts['subtitle'])
    
    # Légende simple
    legend_x = 20
    legend_y = footer_y + 12
    legend_items = [("CM", COURSE_COLORS['CM']), ("TD", COURSE_COLORS['TD']), 
                   ("TP", COURSE_COLORS['TP']), ("Examen", COURSE_COLORS['Examen'])]
    
    for label, color in legend_items:
        draw.rounded_rectangle([legend_x, legend_y, legend_x + 12, legend_y + 12], 
                              radius=3, fill=color)
        draw.text((legend_x + 16, legend_y), label, fill=COLORS['text_secondary'], font=fonts['small'])
        legend_x += 75
    
    logger.info(f"✅ Image générée: {WIDTH}x{HEIGHT}px")
    return img

# ═══════════════════════════════════════════════════════════════════════════════
# 📤 ENVOI DISCORD
# ═══════════════════════════════════════════════════════════════════════════════

def send_to_discord(group_name, image, week_dates, stats):
    webhook_url = WEBHOOKS.get(group_name)
    if not webhook_url:
        logger.error(f"❌ Pas de webhook pour {group_name}")
        return False
    
    role_id = ROLE_IDS.get(group_name)
    mention = f"<@&{role_id}>" if role_id else ""
    
    try:
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='PNG', optimize=True, quality=95)
        img_byte_arr.seek(0)
        
        monday = week_dates[0]['formatted']
        friday = week_dates[4]['formatted']
        
        message_lines = [
            mention,
            "",
            "📅 **Emploi du temps de la semaine**",
            f"📆 **Du {monday} au {friday}**",
            "",
        ]
        
        if stats['total_courses'] > 0:
            message_lines.append(f"📊 **{stats['total_courses']} cours** cette semaine ({stats['total_hours']:.1f}h de cours)")
            
            if stats['by_type']:
                types_emojis = {'CM': '📚', 'TD': '✏️', 'TP': '💻', 'Examen': '📝', 'Projet': '🎯'}
                type_details = []
                for course_type, count in stats['by_type'].most_common(4):
                    emoji = types_emojis.get(course_type, '📖')
                    type_details.append(f"{emoji} {course_type}: {count}")
                
                message_lines.append("🎯 " + " • ".join(type_details))
            
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
        return False

# ═══════════════════════════════════════════════════════════════════════════════
# 🚀 FONCTION PRINCIPALE
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 80)
    print("🎓 EDT BOT L2 INFO - VERSION ULTRA-VISIBLE".center(80))
    print("=" * 80)
    
    start_time = time.time()
    
    now = get_paris_now()
    logger.info(f"🕐 Heure: {now.strftime('%d/%m/%Y %H:%M:%S')}")
    
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
            
            events = fetch_and_parse_edt(group_name, edt_url)
            if not events:
                logger.warning(f"⚠️ Aucun événement")
                continue
            
            week_events = filter_events_for_week(events, week_dates)
            stats = calculate_statistics(week_events)
            
            logger.info(f"📊 {stats['total_courses']} cours, {stats['total_hours']:.1f}h")
            
            logger.info(f"🎨 Génération image...")
            image = create_ultra_visible_edt(group_name, week_events, week_dates)
            
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

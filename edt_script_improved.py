#!/usr/bin/env python3
"""
Script EDT avec génération d'images calendrier style planning visuel
Version améliorée avec affichage type ADE Calendar
"""
import os
import requests
import json
import re
import time
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64

# Webhooks spécifiques par destination
WEBHOOKS = {
    "CM Communs": "https://discordapp.com/api/webhooks/1420864305506549912/9MyUp5eggiLNDyuROGxu7tBRTae8URNyTmluZzjN2jrbMphlc5kffeJOiKL-uqWeKHWs",
    "Groupe 1": "https://discordapp.com/api/webhooks/1421027773723709532/fYgHZUxwWKcI-dMLTLZfR-rsAT6ksZM5j7j1r1VhcCszgSviKB_gM1GY97QaL3jOH_Ci",
    "Groupe 2": "https://discordapp.com/api/webhooks/1421028055509499935/rbokRUOnkzPNTapSc0Tnd64be0m4J-0lhSuj1y3Si56UaWxgidff3KlTLTW1tClbLfGz",
    "Groupe 3": "https://discordapp.com/api/webhooks/1421028321734426665/us4sCIX7b0Csouf2j7v_r-OfrOcAqrqV0SeQ_Jbq0KNeb-fb9mw5KU73AksTTGOEHXZu"
}

# URLs des EDT
EDT_URLS = {
    "Groupe 1": "https://hplanning.univ-lehavre.fr/Telechargements/ical/Edt_Gr1___L2_INFO.ics?version=2022.0.5.0&idICal=63D02C34E55C4FDF72F91012A61BEEEC&param=643d5b312e2e36325d2666683d3126663d3131313030",
    "Groupe 2": "https://hplanning.univ-lehavre.fr/Telechargements/ical/Edt_Gr2___L2_INFO.ics?version=2022.0.5.0&idICal=26AE2D440785C828832D3B6683DDDFE2&param=643d5b312e2e36325d2666683d3126663d3131313030",
    "Groupe 3": "https://hplanning.univ-lehavre.fr/Telechargements/ical/Edt_Gr3___L2_INFO.ics?version=2022.0.5.0&idICal=9EB190174CC47B352D5A84DF3EAA355E&param=643d5b312e2e36325d2666683d3126663d3131313030",
    "CM Communs": "https://hplanning.univ-lehavre.fr/Telechargements/ical/Edt_ST_L2___INFORMATIQUE.ics?version=2022.0.5.0&idICal=5306DEC43ABDB323BBC7726C2F6D4171&param=643d5b312e2e36325d2666683d3130313030"
}

# IDs des rôles Discord pour les mentions
ROLE_IDS = {
    "CM Communs": "1418998954380759141",
    "Groupe 1": "1419000148528205955",
    "Groupe 2": "1419000272776069303",
    "Groupe 3": "1419000449016660071"
}

# Couleurs par type de cours (RGB)
COURSE_COLORS = {
    'CM': (138, 80, 183),      # Violet
    'TD': (255, 167, 38),      # Orange
    'TP': (52, 152, 219),      # Bleu
    'Examen': (230, 126, 34),  # Orange foncé
    'Projet': (46, 204, 113),  # Vert
    'default': (149, 165, 166)  # Gris
}

# Couleurs de fond et texte
BG_COLOR = (30, 33, 46)        # Fond sombre
HEADER_COLOR = (40, 43, 56)    # Header légèrement plus clair
GRID_COLOR = (60, 63, 76)      # Lignes de grille
TEXT_COLOR = (255, 255, 255)   # Texte blanc
SECONDARY_TEXT = (149, 165, 166)  # Texte secondaire gris
CURRENT_TIME_COLOR = (231, 76, 60)  # Rouge pour ligne actuelle

def get_paris_offset(dt):
    """Calcule l'offset UTC pour Paris à une date donnée"""
    year = dt.year
    
    march_last = datetime(year, 3, 31)
    while march_last.weekday() != 6:
        march_last -= timedelta(days=1)
    dst_start = march_last.replace(hour=2, minute=0, second=0, microsecond=0)
    
    october_last = datetime(year, 10, 31)
    while october_last.weekday() != 6:
        october_last -= timedelta(days=1)
    dst_end = october_last.replace(hour=2, minute=0, second=0, microsecond=0)
    
    if dst_start <= dt < dst_end:
        return 2
    else:
        return 1

def get_paris_now():
    """Obtient datetime actuel en heure de Paris"""
    utc_now = datetime.now(timezone.utc).replace(tzinfo=None)
    offset = get_paris_offset(utc_now)
    paris_now = utc_now + timedelta(hours=offset)
    return paris_now

def fetch_with_retry(url, max_retries=5, initial_timeout=30):
    """Récupère une URL avec retry exponentiel"""
    for attempt in range(max_retries):
        try:
            timeout = initial_timeout + (attempt * 15)
            print(f"🔄 Tentative {attempt + 1}/{max_retries} (timeout: {timeout}s)")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/calendar,text/plain,application/ics,*/*',
                'Accept-Language': 'fr-FR,fr;q=0.9',
                'Connection': 'keep-alive',
                'Referer': 'https://hplanning.univ-lehavre.fr/'
            }
            
            session = requests.Session()
            session.headers.update(headers)
            response = session.get(url, timeout=timeout, allow_redirects=True, verify=True)
            response.raise_for_status()
            
            print(f"✅ Connexion réussie (status: {response.status_code})")
            return response.text
            
        except requests.exceptions.Timeout:
            print(f"⏱️ Timeout après {timeout}s")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"⏳ Attente de {wait_time}s...")
                time.sleep(wait_time)
                
        except requests.exceptions.ConnectionError as e:
            print(f"🔌 Erreur de connexion: {str(e)[:100]}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                time.sleep(wait_time)
                
        except requests.exceptions.HTTPError as e:
            print(f"❌ Erreur HTTP {e.response.status_code}")
            if e.response.status_code in [503, 504, 429]:
                if attempt < max_retries - 1:
                    wait_time = 5 * (attempt + 1)
                    print(f"⏳ Serveur surchargé, attente de {wait_time}s...")
                    time.sleep(wait_time)
            else:
                raise
                
        except Exception as e:
            print(f"❌ Erreur: {type(e).__name__}: {str(e)[:100]}")
            if attempt < max_retries - 1:
                time.sleep(2)
    
    print(f"💥 Échec après {max_retries} tentatives")
    return None

def get_week_dates(week_offset=0):
    """Obtient les dates d'une semaine"""
    now = get_paris_now()
    days_since_monday = now.weekday()
    current_monday = now.date() - timedelta(days=days_since_monday)
    target_monday = current_monday + timedelta(weeks=week_offset)
    
    week_dates = []
    days_fr = ['LUN.', 'MAR.', 'MER.', 'JEU.', 'VEN.', 'SAM.', 'DIM.']
    
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
    """Détermine quelle semaine afficher"""
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

def parse_ical_datetime(dt_string):
    """Parse une datetime iCal et convertit en heure de Paris"""
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
                dt_paris = dt_utc + timedelta(hours=offset)
                return dt_paris
        
        elif len(dt_clean) == 8:
            year = int(dt_clean[:4])
            month = int(dt_clean[4:6])
            day = int(dt_clean[6:8])
            return datetime(year, month, day, 0, 0, 0)
    
    except Exception as e:
        print(f"⚠️ Erreur parse datetime '{dt_string}': {e}")
    
    return None

def extract_course_info(summary, description=""):
    """Extrait les informations d'un cours depuis le résumé et description"""
    course_info = {
        'type_cours': '',
        'matiere': '',
        'professeur': '',
        'groupe': ''
    }
    
    if not summary:
        return course_info
    
    type_patterns = [
        (r'(?:^|\s)(CM|TD|TP|Examen|Projet)(?:\s|$|-)', 'type_cours'),
    ]
    
    for pattern, field in type_patterns:
        match = re.search(pattern, summary, re.IGNORECASE)
        if match:
            course_info[field] = match.group(1).upper()
            break
    
    parts = re.split(r'[-–—]', summary)
    if len(parts) >= 2:
        course_info['matiere'] = parts[1].strip()
    else:
        course_info['matiere'] = summary.strip()
    
    prof_match = re.search(r'(?:Prof|Enseignant|Professeur)[:\s]+([A-ZÀ-Ÿ][a-zà-ÿ]+(?:\s+[A-ZÀ-Ÿ][a-zà-ÿ]+)*)', 
                          description, re.IGNORECASE)
    if prof_match:
        course_info['professeur'] = prof_match.group(1)
    
    groupe_match = re.search(r'Gr[ou]*pe?\s*(\d+)', summary, re.IGNORECASE)
    if groupe_match:
        course_info['groupe'] = f"Gr{groupe_match.group(1)}"
    
    return course_info

def fetch_and_parse_edt(group_name, edt_url):
    """Récupère et parse l'EDT depuis l'URL iCal"""
    print(f"📡 Récupération EDT {group_name}...")
    
    ical_data = fetch_with_retry(edt_url)
    
    if not ical_data:
        print(f"❌ Impossible de récupérer l'EDT pour {group_name}")
        return []
    
    print(f"📄 Données reçues: {len(ical_data)} caractères")
    
    try:
        events = []
        current_event = {}
        in_event = False
        
        for line in ical_data.split('\n'):
            line = line.strip()
            
            if line == 'BEGIN:VEVENT':
                in_event = True
                current_event = {}
            
            elif line == 'END:VEVENT' and in_event:
                if 'start' in current_event and 'end' in current_event:
                    events.append(current_event)
                in_event = False
                current_event = {}
            
            elif in_event:
                if line.startswith('DTSTART'):
                    dt = parse_ical_datetime(line.split(':', 1)[1])
                    if dt:
                        current_event['start'] = dt
                
                elif line.startswith('DTEND'):
                    dt = parse_ical_datetime(line.split(':', 1)[1])
                    if dt:
                        current_event['end'] = dt
                
                elif line.startswith('SUMMARY:'):
                    current_event['summary'] = line.split(':', 1)[1]
                
                elif line.startswith('LOCATION:'):
                    current_event['location'] = line.split(':', 1)[1]
                
                elif line.startswith('DESCRIPTION:'):
                    current_event['description'] = line.split(':', 1)[1]
        
        for event in events:
            summary = event.get('summary', '')
            description = event.get('description', '')
            event['course_info'] = extract_course_info(summary, description)
        
        print(f"✅ {len(events)} événements parsés pour {group_name}")
        return events
    
    except Exception as e:
        print(f"❌ Erreur {group_name}: {e}")
        import traceback
        traceback.print_exc()
        return []

def filter_events_for_week(events, week_dates):
    """Filtre les événements pour la semaine cible"""
    week_events = defaultdict(list)
    week_start = week_dates[0]['date']
    week_end = week_dates[-1]['date']
    
    print(f"🎯 Filtrage pour la semaine: {week_start} à {week_end}")
    
    filtered_count = 0
    for event in events:
        event_date = event['start'].date()
        
        if week_start <= event_date <= week_end:
            day_index = (event_date - week_start).days
            if 0 <= day_index < 7:
                week_events[day_index].append(event)
                filtered_count += 1
    
    print(f"📅 Événements cette semaine: {filtered_count}")
    
    for day in week_events:
        week_events[day].sort(key=lambda x: x['start'])
    
    return dict(week_events)

def wrap_text(text, font, max_width, draw):
    """Découpe le texte en plusieurs lignes si nécessaire"""
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        width = bbox[2] - bbox[0]
        
        if width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

def create_edt_image(group_name, week_events, week_dates, week_type="courante"):
    """Crée une image de l'EDT style calendrier"""
    
    # Dimensions
    WIDTH = 1400
    HEIGHT = 1000
    HEADER_HEIGHT = 80
    DAY_HEADER_HEIGHT = 60
    TIME_COL_WIDTH = 60
    DAY_WIDTH = (WIDTH - TIME_COL_WIDTH) // 5  # 5 jours ouvrés
    
    # Heures affichées (7h à 19h)
    START_HOUR = 7
    END_HOUR = 19
    HOURS = END_HOUR - START_HOUR
    HOUR_HEIGHT = (HEIGHT - HEADER_HEIGHT - DAY_HEADER_HEIGHT) / HOURS
    
    # Créer l'image
    img = Image.new('RGB', (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Polices
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font_header = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        font_day = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
        font_event = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
        font_time = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
    except:
        font_title = ImageFont.load_default()
        font_header = ImageFont.load_default()
        font_day = ImageFont.load_default()
        font_event = ImageFont.load_default()
        font_time = ImageFont.load_default()
    
    # Header principal
    draw.rectangle([0, 0, WIDTH, HEADER_HEIGHT], fill=HEADER_COLOR)
    
    monday = week_dates[0]['formatted']
    friday = week_dates[4]['formatted']
    week_indicator = "Semaine prochaine" if week_type == "suivante" else "Cette semaine"
    title = f"{week_indicator} - EDT {group_name}"
    subtitle = f"{monday} - {friday}"
    
    # Titre
    bbox = draw.textbbox((0, 0), title, font=font_title)
    title_width = bbox[2] - bbox[0]
    draw.text(((WIDTH - title_width) // 2, 15), title, fill=TEXT_COLOR, font=font_title)
    
    # Sous-titre
    bbox = draw.textbbox((0, 0), subtitle, font=font_header)
    subtitle_width = bbox[2] - bbox[0]
    draw.text(((WIDTH - subtitle_width) // 2, 48), subtitle, fill=SECONDARY_TEXT, font=font_header)
    
    # Headers des jours
    y_day_header = HEADER_HEIGHT
    for i in range(5):  # Lundi à Vendredi
        x = TIME_COL_WIDTH + (i * DAY_WIDTH)
        
        # Fond du header
        draw.rectangle([x, y_day_header, x + DAY_WIDTH, y_day_header + DAY_HEADER_HEIGHT], 
                      fill=HEADER_COLOR, outline=GRID_COLOR)
        
        # Jour
        day_name = week_dates[i]['day_name']
        day_number = week_dates[i]['day_number']
        day_text = f"{day_name}\n{day_number}"
        
        bbox = draw.textbbox((0, 0), day_name, font=font_day)
        text_width = bbox[2] - bbox[0]
        draw.text((x + (DAY_WIDTH - text_width) // 2, y_day_header + 10), 
                 day_name, fill=TEXT_COLOR, font=font_day)
        
        num_text = str(day_number)
        bbox = draw.textbbox((0, 0), num_text, font=font_header)
        num_width = bbox[2] - bbox[0]
        draw.text((x + (DAY_WIDTH - num_width) // 2, y_day_header + 32), 
                 num_text, fill=SECONDARY_TEXT, font=font_header)
    
    # Colonne des heures et grille
    y_start = HEADER_HEIGHT + DAY_HEADER_HEIGHT
    
    for hour in range(START_HOUR, END_HOUR + 1):
        y = y_start + ((hour - START_HOUR) * HOUR_HEIGHT)
        
        # Heure
        hour_text = f"{hour:02d}:00"
        draw.text((5, y - 8), hour_text, fill=SECONDARY_TEXT, font=font_time)
        
        # Ligne horizontale
        draw.line([(TIME_COL_WIDTH, y), (WIDTH, y)], fill=GRID_COLOR, width=1)
    
    # Lignes verticales
    for i in range(6):  # 5 jours + 1 pour la bordure droite
        x = TIME_COL_WIDTH + (i * DAY_WIDTH)
        draw.line([(x, y_day_header), (x, HEIGHT)], fill=GRID_COLOR, width=1)
    
    # Ajouter les événements
    for day_index, events in week_events.items():
        if day_index >= 5:  # Seulement lundi à vendredi
            continue
            
        x_day = TIME_COL_WIDTH + (day_index * DAY_WIDTH)
        
        for event in events:
            start_hour = event['start'].hour + event['start'].minute / 60
            end_hour = event['end'].hour + event['end'].minute / 60
            
            # Position Y
            y_event_start = y_start + ((start_hour - START_HOUR) * HOUR_HEIGHT)
            y_event_end = y_start + ((end_hour - START_HOUR) * HOUR_HEIGHT)
            event_height = y_event_end - y_event_start
            
            # Couleur selon le type
            course_type = event['course_info']['type_cours']
            color = COURSE_COLORS.get(course_type, COURSE_COLORS['default'])
            
            # Bordure gauche colorée
            border_width = 5
            draw.rectangle([x_day + 2, y_event_start + 2, 
                          x_day + border_width + 2, y_event_end - 2],
                         fill=color)
            
            # Fond de l'événement (légèrement transparent via couleur plus sombre)
            bg_color = tuple(int(c * 0.3) for c in color)
            draw.rectangle([x_day + border_width + 2, y_event_start + 2,
                          x_day + DAY_WIDTH - 2, y_event_end - 2],
                         fill=bg_color, outline=color)
            
            # Texte de l'événement
            padding = 8
            text_x = x_day + border_width + padding
            text_y = y_event_start + 5
            max_text_width = DAY_WIDTH - border_width - (2 * padding)
            
            # Horaire
            start_time = event['start'].strftime('%H:%M')
            end_time = event['end'].strftime('%H:%M')
            time_text = f"{start_time}-{end_time}"
            draw.text((text_x, text_y), time_text, fill=TEXT_COLOR, font=font_event)
            text_y += 15
            
            # Matière
            matiere = event['course_info']['matiere']
            if matiere:
                matiere = matiere[:30]  # Limiter la longueur
                type_text = f" ({course_type})" if course_type else ""
                matiere_lines = wrap_text(matiere + type_text, font_event, max_text_width, draw)
                for line in matiere_lines[:2]:  # Max 2 lignes
                    draw.text((text_x, text_y), line, fill=TEXT_COLOR, font=font_event)
                    text_y += 13
            
            # Salle
            location = event.get('location', '')
            if location and text_y < y_event_end - 15:
                location = location[:20]
                draw.text((text_x, text_y), f"🏛️ {location}", fill=SECONDARY_TEXT, font=font_time)
    
    # Ligne du temps actuel si c'est la semaine courante
    if week_type == "courante":
        now = get_paris_now()
        current_day = now.weekday()
        
        if current_day < 5:  # Lundi à Vendredi
            current_hour = now.hour + now.minute / 60
            
            if START_HOUR <= current_hour <= END_HOUR:
                y_current = y_start + ((current_hour - START_HOUR) * HOUR_HEIGHT)
                x_current_start = TIME_COL_WIDTH + (current_day * DAY_WIDTH)
                x_current_end = x_current_start + DAY_WIDTH
                
                # Ligne rouge pour l'heure actuelle
                draw.line([(x_current_start, y_current), (x_current_end, y_current)],
                         fill=CURRENT_TIME_COLOR, width=3)
    
    return img

def send_edt_to_discord(group_name, image, week_type="courante"):
    """Envoie l'EDT (image) sur le webhook Discord"""
    
    webhook_url = WEBHOOKS.get(group_name)
    if not webhook_url:
        print(f"❌ Pas de webhook configuré pour {group_name}")
        return False
    
    role_id = ROLE_IDS.get(group_name)
    mention = f"<@&{role_id}>" if role_id else ""
    
    emoji_map = {
        "Groupe 1": "📘",
        "Groupe 2": "📕",
        "Groupe 3": "📗",
        "CM Communs": "📚"
    }
    
    emoji = emoji_map.get(group_name, "📅")
    week_indicator = "📆 Semaine prochaine" if week_type == "suivante" else "📅 Cette semaine"
    
    try:
        # Convertir l'image en bytes
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='PNG', optimize=True)
        img_byte_arr.seek(0)
        
        # Préparer le fichier
        files = {
            'file': ('edt.png', img_byte_arr, 'image/png')
        }
        
        # Message
        payload = {
            "username": f"{emoji} EDT {group_name}",
            "content": f"{mention}\n{week_indicator} - Planning de la semaine"
        }
        
        print(f"📤 Envoi EDT {group_name}...")
        response = requests.post(webhook_url, data=payload, files=files, timeout=30)
        response.raise_for_status()
        
        print(f"✅ EDT {group_name} envoyé ! (status: {response.status_code})")
        return True
        
    except Exception as e:
        print(f"❌ Erreur envoi {group_name}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🎓 Bot EDT L2 INFO - Version visuelle améliorée")
    
    now = get_paris_now()
    utc_now = datetime.now(timezone.utc).replace(tzinfo=None)
    offset = get_paris_offset(utc_now)
    print(f"🕐 Heure actuelle: {now.strftime('%d/%m/%Y %H:%M:%S')} (UTC+{offset})")
    
    # Déterminer quelle semaine afficher
    week_offset, week_reason = determine_week_mode()
    print(f"📆 Mode semaine: {week_reason}")
    
    week_dates = get_week_dates(week_offset)
    week_type = "suivante" if week_offset == 1 else "courante"
    
    print(f"📅 Semaine affichée: {week_dates[0]['formatted']} au {week_dates[4]['formatted']}")
    
    success_count = 0
    total_groups = len(EDT_URLS)
    
    for group_name, edt_url in EDT_URLS.items():
        try:
            print(f"\n📋 === TRAITEMENT {group_name.upper()} ===")
            
            if group_name not in WEBHOOKS:
                print(f"❌ Pas de webhook configuré pour {group_name}")
                continue
            
            # Récupérer les événements
            events = fetch_and_parse_edt(group_name, edt_url)
            
            # Filtrer pour la semaine
            week_events = filter_events_for_week(events, week_dates)
            
            print(f"📊 Événements: {sum(len(day_events) for day_events in week_events.values())}")
            
            # Créer l'image
            print(f"🎨 Création de l'image EDT...")
            image = create_edt_image(group_name, week_events, week_dates, week_type)
            
            # Envoyer sur Discord
            if send_edt_to_discord(group_name, image, week_type):
                success_count += 1
            
            time.sleep(3)
            
        except Exception as e:
            print(f"❌ Erreur critique pour {group_name}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n🎯 === RÉSUMÉ FINAL ===")
    print(f"✅ Groupes envoyés: {success_count}/{total_groups}")
    print(f"📆 Type de semaine: {week_type}")
    
    if success_count == total_groups:
        print("🎉 Tous les EDT envoyés !")
    elif success_count > 0:
        print("⚠️ Envois partiels")
    else:
        print("❌ Échec complet")

if __name__ == "__main__":
    main()

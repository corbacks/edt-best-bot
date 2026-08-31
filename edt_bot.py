#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎓 EDT Bot — Le GOAT de l'EDT (L3 INFO, Le Havre)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Envoie l'emploi du temps de la semaine sur Discord, un salon par groupe
(GrA / GrB / GrC / CM Communs), sous forme d'image (voir style_grid.py).

- Les 2 options (Architecture avancée, Prog. C++) sont fusionnées dans les
  salons de groupe (GrA/GrB/GrC) en plus du salon CM Communs, puisqu'elles
  concernent des étudiants de tous les groupes.
- Si TOUS les salons n'ont aucun cours cette semaine-là (vacances), un seul
  message "pas de cours" est envoyé sur CM Communs, et la semaine est
  mémorisée pour ne pas re-notifier les jours suivants.
- `TEST_MONDAY` (env ou workflow_dispatch) permet de forcer le rendu d'une
  semaine précise (utile si la semaine courante ET la semaine suivante sont
  toutes les deux en vacances, et qu'on veut quand même tester un rendu
  avec une vraie semaine de cours).
"""
import os
import re
import json
import urllib.request
from datetime import date, datetime, timedelta

import requests

import edt_parsing as ep
import style_grid as sg

# ══════════════════════════════════════════════════════════════════════════════
# ⚙️  CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════

# Flux combiné (tout le monde) : sert de source pour le salon "CM Communs"
# (on y garde uniquement les événements SANS préfixe GrX : CM partagés + options).
CM_COMMUNS_ICAL = (
    "https://hplanning.univ-lehavre.fr/Telechargements/ical/Edt_ST_L3___INFORMATIQUE.ics"
    "?version=2022.0.5.0&idICal=878F4702AFE5022EFD588352AC8AC291"
    "&param=643d5b312e2e36325d2666683d3126663d3131303030"
)

# Flux dédiés par groupe (planning complet du groupe : CM + TP/TD propres)
GROUP_ICAL = {
    "GrA": "https://hplanning.univ-lehavre.fr/Telechargements/ical/Edt_GrA___L3_INFO.ics"
           "?version=2022.0.5.0&idICal=9C6195B41AB8E13C6B1D1FD0DC17561E"
           "&param=643d5b312e2e36325d2666683d3126663d3131313030",
    "GrB": "https://hplanning.univ-lehavre.fr/Telechargements/ical/Edt_GrB___L3_INFO.ics"
           "?version=2022.0.5.0&idICal=84CF77F9781656328D471B529EB48977"
           "&param=643d5b312e2e36325d2666683d3126663d3131313030",
    "GrC": "https://hplanning.univ-lehavre.fr/Telechargements/ical/Edt_GrC___L3_INFO.ics"
           "?version=2022.0.5.0&idICal=30EA0E64AE646826233F809BDB58672C"
           "&param=643d5b312e2e36325d2666683d3126663d3131313030",
}

# Options : fusionnées dans chaque salon de groupe (pas dans CM Communs, qui
# les reçoit déjà via le flux combiné ci-dessus — évite les doublons).
OPTION_ICAL = {
    "Option 2 – Architecture avancée":
        "https://hplanning.univ-lehavre.fr/Telechargements/ical/Edt_Architecture_avancee___OPT2_L3_INFO.ics"
        "?version=2022.0.5.0&idICal=FF2B8E436C67A8FD2A6E249B6FAB8597"
        "&param=643d5b312e2e36325d2666683d3126663d3131313030",
    "Option 1 – Prog. C++":
        "https://hplanning.univ-lehavre.fr/Telechargements/ical/Edt_Programmation_objets_C_____OPT1_L3_INFO.ics"
        "?version=2022.0.5.0&idICal=59AD9A74446C6CFD8200F71AA15A5734"
        "&param=643d5b312e2e36325d2666683d3126663d3131313030",
}

CHANNELS = ["CM Communs", "GrA", "GrB", "GrC"]

WEBHOOKS = {
    "CM Communs": os.environ.get("WEBHOOK_CM", "https://discordapp.com/api/webhooks/1420864305506549912/9MyUp5eggiLNDyuROGxu7tBRTae8URNyTmluZzjN2jrbMphlc5kffeJOiKL-uqWeKHWs"),
    "GrA":        os.environ.get("WEBHOOK_GRA", "https://discord.com/api/webhooks/1532348301997772961/qNCW7LN0jpTDkPm4pne5JnD2abRGqJqVWTKsKdULvewl8AVuM31jX8-6Tqyu_IY6-l6u"),
    "GrB":        os.environ.get("WEBHOOK_GRB", "https://discord.com/api/webhooks/1532352816453255238/_gPXvRqN14XTfjYfTLrznldmjfD5_YSmHNaWUWACdJY0MFeleEVCEQdjtY8wcRR0i5pS"),
    "GrC":        os.environ.get("WEBHOOK_GRC", "https://discord.com/api/webhooks/1532353298726912002/9iIFE4LCSThalBL4F5E5usFUE1yyj-JijedthOzk_TtzNWYDSIwH6C4D1m7DXxk_-V2o"),
}
ROLE_IDS = {
    "CM Communs": os.environ.get("ROLE_CM", "1418998954380759141"),
    "GrA":        os.environ.get("ROLE_GRA", "1419000148528205955"),
    "GrB":        os.environ.get("ROLE_GRB", "1419000272776069303"),
    "GrC":        os.environ.get("ROLE_GRC", "1419000449016660071"),
}

_base = os.getenv("GITHUB_WORKSPACE") or os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(_base, "edt_cache.json")
IMG_PATH = "/tmp/edt_{}.png"

# Permet de forcer le rendu d'une semaine précise (format AAAA-MM-JJ, n'importe
# quel jour de la semaine visée — on retombe automatiquement sur le lundi).
# Utile pour tester un rendu quand la semaine courante ET la semaine suivante
# sont toutes les deux vides (vacances).
TEST_MONDAY = os.getenv("TEST_MONDAY", "").strip()

# Bypasse le verrou "semaine déjà envoyée" ci-dessous (voir cache) — utile
# pour renvoyer manuellement une semaine déjà traitée en test.
FORCE_RUN = os.getenv("FORCE_RUN", "0") in ("1", "true", "True")

MONTHS_FR = ["", "janvier", "février", "mars", "avril", "mai", "juin",
             "juillet", "août", "septembre", "octobre", "novembre", "décembre"]


# ══════════════════════════════════════════════════════════════════════════════
# 📅  DATE / HORAIRE / SEMAINE CIBLE
# ══════════════════════════════════════════════════════════════════════════════

def get_paris_now():
    try:
        import pytz
        return datetime.now(pytz.timezone("Europe/Paris"))
    except ImportError:
        return datetime.now()

def target_monday(today: date) -> tuple:
    """Retourne (monday, week_key, is_manual_test)."""
    if TEST_MONDAY:
        try:
            d = date.fromisoformat(TEST_MONDAY)
            monday = d - timedelta(days=d.weekday())
            iso = monday.isocalendar()
            return monday, f"{iso[0]}-W{iso[1]:02d}", True
        except ValueError:
            print(f"⚠️ TEST_MONDAY invalide ({TEST_MONDAY!r}), ignoré — retour au mode normal.")

    # Mode normal : toujours la semaine SUIVANTE (les étudiants ont ainsi
    # leur planning avant le début de la semaine concernée).
    this_monday = today - timedelta(days=today.weekday())
    monday = this_monday + timedelta(weeks=1)
    iso = monday.isocalendar()
    return monday, f"{iso[0]}-W{iso[1]:02d}", False


# ══════════════════════════════════════════════════════════════════════════════
# 💾  CACHE (semaine vide déjà notifiée)
# ══════════════════════════════════════════════════════════════════════════════

def load_cache() -> dict:
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"⚠️ Lecture cache : {e}")
    return {}

def save_cache(data: dict):
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Sauvegarde cache : {e}")


# ══════════════════════════════════════════════════════════════════════════════
# 📥  RÉCUPÉRATION DES FLUX
# ══════════════════════════════════════════════════════════════════════════════

def download_ical(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")

def dedupe_events(events: list) -> list:
    seen, out = set(), []
    for e in events:
        key = (e.get('summary', ''), e['start'].isoformat(), e['end'].isoformat())
        if key not in seen:
            seen.add(key)
            out.append(e)
    return out

def build_channel_events(channel: str, common_raw: str, option_events: list) -> list:
    if channel == "CM Communs":
        events = ep.fetch_and_parse_ics(common_raw)
        # Uniquement les cours SANS préfixe GrX (CM partagés + options, déjà
        # inclus tels quels dans ce flux combiné — pas besoin de les rajouter).
        return [e for e in events if not re.match(r'^\s*Gr[A-Za-z0-9]+', e.get('summary', ''))]

    raw = download_ical(GROUP_ICAL[channel])
    events = ep.fetch_and_parse_ics(raw)
    return dedupe_events(events + option_events)


# ══════════════════════════════════════════════════════════════════════════════
# 📤  ENVOI DISCORD
# ══════════════════════════════════════════════════════════════════════════════

def send_image(webhook_url, image_path, content):
    with open(image_path, "rb") as f:
        r = requests.post(
            webhook_url,
            data={"payload_json": json.dumps({"username": "Le GOAT de l'EDT", "content": content})},
            files={"file": ("edt.png", f, "image/png")},
            timeout=25,
        )
    r.raise_for_status()

def send_text(webhook_url, content):
    r = requests.post(webhook_url, json={"username": "Le GOAT de l'EDT", "content": content}, timeout=15)
    r.raise_for_status()


# ══════════════════════════════════════════════════════════════════════════════
# 🚀  MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("🎓 EDT Bot — Le GOAT de l'EDT")
    print("=" * 50)

    now = get_paris_now()
    today = now.date() if hasattr(now, "date") else date.today()

    monday, week_key, is_test = target_monday(today)
    friday = monday + timedelta(days=4)
    date_range = f"{monday.day} au {friday.day} {MONTHS_FR[friday.month]} {friday.year}"
    print(f"📅 Semaine ciblée : {week_key}  ({date_range})  —  run le {now.strftime('%A %d/%m %H:%M')}"
          + ("  [TEST MANUEL]" if is_test else ""))

    # Verrou hebdomadaire : la SEULE chose qui empêche un doublon, c'est
    # d'avoir déjà traité cette semaine — peu importe l'heure ou le jour
    # réel du run. GitHub Actions ne garantit pas l'heure d'un cron
    # "schedule" (des retards de plusieurs heures sont courants sur les
    # dépôts peu actifs) ; un garde-fou basé sur une fenêtre horaire stricte
    # ferait sauter l'envoi entier d'une semaine si le run arrive en retard,
    # sans aucun rattrapage. Ce verrou tolère n'importe quel retard : le bot
    # envoie dès qu'il tourne, une seule fois par semaine cible.
    cache = load_cache()
    if not is_test and not FORCE_RUN and cache.get("last_sent_week") == week_key:
        print(f"🔕 Semaine {week_key} déjà traitée — aucun envoi (pas de doublon).")
        return

    try:
        common_raw = download_ical(CM_COMMUNS_ICAL)
    except Exception as e:
        print(f"❌ Téléchargement flux combiné : {e}")
        return

    option_events = []
    for opt_name, url in OPTION_ICAL.items():
        try:
            raw = download_ical(url)
            option_events += ep.fetch_and_parse_ics(raw)
        except Exception as e:
            print(f"⚠️ Option {opt_name} indisponible : {e}")

    any_courses = False
    sent = 0

    for channel in CHANNELS:
        try:
            events = build_channel_events(channel, common_raw, option_events)
            week_events = ep.filter_events_for_week(events, monday)
            total_courses = sum(len(v) for v in week_events.values())

            if total_courses == 0:
                print(f"   {channel}: 0 cours")
                continue
            any_courses = True

            img_path = IMG_PATH.format(channel.replace(" ", "_"))
            sg.generate_grid_edt(f"{channel} - L3 INFO", week_events, monday, img_path)

            webhook = WEBHOOKS.get(channel)
            if not webhook:
                print(f"   ⚠️ {channel}: pas de webhook configuré, image générée mais non envoyée.")
                continue

            role = ROLE_IDS.get(channel)
            mention = f"<@&{role}>\n\n" if role else ""
            content = f"{mention}📅 **Emploi du temps — {date_range}**"
            send_image(webhook, img_path, content)
            sent += 1
            print(f"   ✅ {channel}: {total_courses} cours envoyés")

        except Exception as e:
            print(f"   ❌ {channel}: {e}")

    if not any_courses:
        print(f"🏖️ Aucun cours nulle part pour la semaine {week_key} — probable période de vacances.")
        webhook = WEBHOOKS.get("CM Communs")
        if webhook:
            try:
                role = ROLE_IDS.get("CM Communs")
                mention = f"<@&{role}>\n\n" if role else ""
                send_text(webhook, f"{mention}🏖️ **Pas de cours la semaine du {date_range}.**")
            except Exception as e:
                print(f"⚠️ Message vacances non envoyé : {e}")
        if not is_test:
            save_cache({"last_sent_week": week_key})
    else:
        if not is_test:
            save_cache({"last_sent_week": week_key})
        print(f"✅ {sent}/{len(CHANNELS)} salons envoyés.")

if __name__ == "__main__":
    main()

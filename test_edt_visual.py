#!/usr/bin/env python3
"""
Script de test pour générer un exemple d'EDT sans envoyer sur Discord
Utile pour tester le rendu visuel localement
"""
import sys
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont

# Ajouter le chemin du script principal
sys.path.insert(0, '.')

# Données de test
def create_sample_events():
    """Crée des événements de test pour démonstration"""
    now = datetime.now()
    
    # Lundi
    monday = now - timedelta(days=now.weekday())
    
    events = {
        0: [  # Lundi
            {
                'start': monday.replace(hour=8, minute=0),
                'end': monday.replace(hour=10, minute=0),
                'summary': 'CM - L2 INFO - Anglais',
                'location': 'DE MONNERVILLE amphi ST',
                'course_info': {
                    'type_cours': 'CM',
                    'matiere': 'Anglais',
                    'professeur': '',
                    'groupe': ''
                }
            },
            {
                'start': monday.replace(hour=10, minute=15),
                'end': monday.replace(hour=11, minute=45),
                'summary': 'TD - L2 INFO - Algorithmique',
                'location': 'SALLE 11.46',
                'course_info': {
                    'type_cours': 'TD',
                    'matiere': 'Algorithmique et prog.',
                    'professeur': '',
                    'groupe': ''
                }
            }
        ],
        1: [  # Mardi
            {
                'start': (monday + timedelta(days=1)).replace(hour=8, minute=0),
                'end': (monday + timedelta(days=1)).replace(hour=10, minute=0),
                'summary': 'TP - L2 INFO - Informatique',
                'location': 'Salle INFO',
                'course_info': {
                    'type_cours': 'TP',
                    'matiere': 'Informatique pour le...',
                    'professeur': '',
                    'groupe': ''
                }
            }
        ],
        2: [  # Mercredi
            {
                'start': (monday + timedelta(days=2)).replace(hour=8, minute=0),
                'end': (monday + timedelta(days=2)).replace(hour=10, minute=0),
                'summary': 'CM - L2 INFO - Statistiques',
                'location': 'Salle MOUZELINE',
                'course_info': {
                    'type_cours': 'CM',
                    'matiere': 'Statistique - M. Mordi...',
                    'professeur': '',
                    'groupe': ''
                }
            },
            {
                'start': (monday + timedelta(days=2)).replace(hour=10, minute=0),
                'end': (monday + timedelta(days=2)).replace(hour=12, minute=0),
                'summary': 'TD - L2 INFO - Algorithmique',
                'location': 'INFO ALGB TP ST',
                'course_info': {
                    'type_cours': 'TD',
                    'matiere': 'Algorithmique',
                    'professeur': '',
                    'groupe': 'Gr4'
                }
            }
        ],
        3: [  # Jeudi
            {
                'start': (monday + timedelta(days=3)).replace(hour=13, minute=30),
                'end': (monday + timedelta(days=3)).replace(hour=15, minute=30),
                'summary': 'TP - L2 INFO - Algorithmique',
                'location': 'B626 ST',
                'course_info': {
                    'type_cours': 'TP',
                    'matiere': 'Algorithmique',
                    'professeur': '',
                    'groupe': 'Gr4'
                }
            },
            {
                'start': (monday + timedelta(days=3)).replace(hour=14, minute=0),
                'end': (monday + timedelta(days=3)).replace(hour=15, minute=0),
                'summary': 'CM - L2 INFO - Systèmes',
                'location': 'E507 TP ST INFO (PC)',
                'course_info': {
                    'type_cours': 'CM',
                    'matiere': 'Systèmes',
                    'professeur': '',
                    'groupe': ''
                }
            }
        ],
        4: [  # Vendredi
            {
                'start': (monday + timedelta(days=4)).replace(hour=8, minute=30),
                'end': (monday + timedelta(days=4)).replace(hour=10, minute=0),
                'summary': 'TD - L2 INFO - Systèmes d\'exploitation...',
                'location': 'SALLE 12.15',
                'course_info': {
                    'type_cours': 'TD',
                    'matiere': 'Systèmes d\'exploitatio...',
                    'professeur': '',
                    'groupe': ''
                }
            },
            {
                'start': (monday + timedelta(days=4)).replace(hour=16, minute=0),
                'end': (monday + timedelta(days=4)).replace(hour=17, minute=45),
                'summary': 'TP - L2 INFO - Programmation',
                'location': 'A620 TP ST INFO',
                'course_info': {
                    'type_cours': 'TP',
                    'matiere': 'Programmation',
                    'professeur': '',
                    'groupe': 'Gr1'
                }
            }
        ]
    }
    
    return events

def create_sample_week_dates():
    """Crée les dates de la semaine pour le test"""
    now = datetime.now()
    monday = (now - timedelta(days=now.weekday())).date()
    
    days_fr = ['LUN.', 'MAR.', 'MER.', 'JEU.', 'VEN.', 'SAM.', 'DIM.']
    
    week_dates = []
    for i in range(7):
        day_date = monday + timedelta(days=i)
        week_dates.append({
            'date': day_date,
            'day_name': days_fr[i],
            'day_number': day_date.day,
            'formatted': day_date.strftime('%d/%m/%Y')
        })
    
    return week_dates

def main():
    """Génère un EDT de test"""
    print("🎨 Génération d'un EDT de test...")
    
    try:
        # Importer la fonction de création d'image
        from edt_script_improved import create_edt_image
        
        # Créer les données de test
        week_events = create_sample_events()
        week_dates = create_sample_week_dates()
        
        # Générer l'image pour chaque groupe
        groups = ["Groupe 1", "Groupe 2", "Groupe 3", "CM Communs"]
        
        for group_name in groups:
            print(f"\n📋 Génération EDT {group_name}...")
            
            # Créer l'image
            image = create_edt_image(group_name, week_events, week_dates, "courante")
            
            # Sauvegarder
            filename = f"edt_test_{group_name.replace(' ', '_').lower()}.png"
            image.save(filename, format='PNG', optimize=True)
            print(f"✅ Image sauvegardée : {filename}")
        
        print("\n🎉 Toutes les images de test ont été générées !")
        print("📁 Fichiers créés :")
        for group in groups:
            print(f"   - edt_test_{group.replace(' ', '_').lower()}.png")
        
    except ImportError as e:
        print(f"❌ Erreur d'import : {e}")
        print("Assurez-vous que edt_script_improved.py est dans le même dossier")
    except Exception as e:
        print(f"❌ Erreur : {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

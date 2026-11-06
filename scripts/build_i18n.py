#!/usr/bin/env python3
"""
Professional Fitness Terminology Engine & Multi-Language Dataset Builder.
- Preserves 100% of the 886 exercises and commit 82303c10df172af66ad899f5b7266b0586d39814 enrichments:
    * 57 video exercises (video_url, video_slug, cues, joint_stress, type, gear)
    * 10 unique functional mobility exercises
    * All existing IDs, categories, targets, images, etc.
- Generates professional fitness names (name_i18n) for all 8 languages in Language enum:
    en (English)
    vi (Tiếng Việt)
    es (Español)
    fr (Français)
    de (Deutsch)
    ja (日本語)
    pt (Português)
    hi (हिन्दी)
- Merges cached step-by-step Vietnamese translations into instruction_steps and instructions.
- Syncs output directly to:
    1. assets/data/exercises.json (in fitness app)
    2. /Users/nguyenmanhdung/Workspace/free-exercise-db/dist/exercises.json
    3. /Users/nguyenmanhdung/Workspace/free-exercise-db/dist/i18n/exercises_{lang}.json (8 standalone bundles)
"""

import os
import re
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
SOURCE_FILE = os.path.join(ROOT_DIR, "assets", "data", "exercises.json")
CACHE_FILE = os.path.join(SCRIPT_DIR, "i18n_cache.json")
FORK_DIR = "/Users/nguyenmanhdung/Workspace/free-exercise-db"

# Core movements dictionary with accurate fitness names across 8 languages
MOVEMENTS = [
    ("Bench Press", {
        "vi": "Đẩy ngực trên ghế ngang (Bench Press)",
        "es": "Press de banca",
        "fr": "Développé couché",
        "de": "Bankdrücken",
        "ja": "ベンチプレス",
        "pt": "Supino reto",
        "hi": "बेंच प्रेस"
    }),
    ("Incline Bench Press", {
        "vi": "Đẩy ngực dốc lên (Incline Bench Press)",
        "es": "Press de banca inclinado",
        "fr": "Développé couché incliné",
        "de": "Schrägbankdrücken",
        "ja": "インクラインベンチプレス",
        "pt": "Supino inclinado",
        "hi": "इनक्लाइन बेंच प्रेस"
    }),
    ("Decline Bench Press", {
        "vi": "Đẩy ngực dốc xuống (Decline Bench Press)",
        "es": "Press de banca declinado",
        "fr": "Développé couché décliné",
        "de": "Negativbankdrücken",
        "ja": "デクラインベンチプレス",
        "pt": "Supino declinado",
        "hi": "डिक्लाइन बेंच प्रेस"
    }),
    ("Incline Dumbbell Press", {
        "vi": "Đẩy tạ đơn dốc lên (Incline Dumbbell Press)",
        "es": "Press inclinado con mancuernas",
        "fr": "Développé incliné aux haltères",
        "de": "Schrägbankdrücken mit Kurzhanteln",
        "ja": "インクラインダンベルプレス",
        "pt": "Supino inclinado com halteres",
        "hi": "इनक्लाइन डंबल प्रेस"
    }),
    ("Dumbbell Bench Press", {
        "vi": "Đẩy tạ đơn ghế ngang (Dumbbell Bench Press)",
        "es": "Press de banca con mancuernas",
        "fr": "Développé couché aux haltères",
        "de": "Bankdrücken mit Kurzhanteln",
        "ja": "ダンベルベンチプレス",
        "pt": "Supino reto com halteres",
        "hi": "डंबल बेंच प्रेस"
    }),
    ("Overhead Press", {
        "vi": "Đẩy tạ qua đầu (Overhead Press)",
        "es": "Press militar / Overhead Press",
        "fr": "Développé militaire",
        "de": "Schulterdrücken über Kopf",
        "ja": "オーバーヘッドプレス",
        "pt": "Desenvolvimento militar",
        "hi": "ओवरहेड प्रेस"
    }),
    ("Military Press", {
        "vi": "Đẩy vai đứng thẳng (Military Press)",
        "es": "Press militar",
        "fr": "Développé militaire",
        "de": "Military Press",
        "ja": "ミリタリープレス",
        "pt": "Desenvolvimento militar em pé",
        "hi": "मिलिट्री प्रेस"
    }),
    ("Shoulder Press", {
        "vi": "Đẩy vai (Shoulder Press)",
        "es": "Press de hombros",
        "fr": "Développé épaules",
        "de": "Schulterdrücken",
        "ja": "ショルダープレス",
        "pt": "Desenvolvimento de ombros",
        "hi": "शोल्डर प्रेस"
    }),
    ("Lateral Raise", {
        "vi": "Nâng tạ sang ngang tập vai (Lateral Raise)",
        "es": "Elevaciones laterales de hombros",
        "fr": "Élévations latérales",
        "de": "Seitheben für Schultern",
        "ja": "サイドレイズ",
        "pt": "Elevação lateral",
        "hi": "लेटरल रेज"
    }),
    ("Front Raise", {
        "vi": "Nâng tạ về trước tập vai (Front Raise)",
        "es": "Elevaciones frontales",
        "fr": "Élévations frontales",
        "de": "Frontheben",
        "ja": "フロントレイズ",
        "pt": "Elevação frontal",
        "hi": "फ्रंट रेज"
    }),
    ("Rear Delt Fly", {
        "vi": "Banh vai sau (Rear Delt Fly)",
        "es": "Pájaros para deltoides posterior",
        "fr": "Oiseau pour deltoïdes postérieurs",
        "de": "Reverse Flys für hintere Schulter",
        "ja": "リアレイズ",
        "pt": "Crucifixo invertido",
        "hi": "रियर डेल्ट फ्लाई"
    }),
    ("Chest Fly", {
        "vi": "Banh ngực (Chest Fly)",
        "es": "Aperturas de pecho",
        "fr": "Écarté couché pour pectoraux",
        "de": "Fliegende Bewegung für Brust",
        "ja": "チェストフライ",
        "pt": "Crucifixo para peito",
        "hi": "चेस्ट फ्लाई"
    }),
    ("Pullover", {
        "vi": "Kéo tạ qua đầu (Pullover)",
        "es": "Pullover con mancuerna/barra",
        "fr": "Pull-over pour pectoraux et dorsaux",
        "de": "Überzüge (Pullover)",
        "ja": "プルオーバー",
        "pt": "Pullover",
        "hi": "पुलओवर"
    }),
    ("Push-up", {
        "vi": "Chống đẩy (Push-up)",
        "es": "Flexiones de brazos",
        "fr": "Pompes",
        "de": "Liegestütze",
        "ja": "腕立て伏せ",
        "pt": "Flexão de braços",
        "hi": "पुश-अप"
    }),
    ("Pull-up", {
        "vi": "Hít xà đơn (Pull-up)",
        "es": "Dominadas pronadas",
        "fr": "Tractions en pronation",
        "de": "Klimmzüge im Obergriff",
        "ja": "懸垂 (プルアップ)",
        "pt": "Barra fixa pronada",
        "hi": "पुल-अप"
    }),
    ("Chin-up", {
        "vi": "Hít xà tay ngửa (Chin-up)",
        "es": "Dominadas supinas",
        "fr": "Tractions en supination",
        "de": "Klimmzüge im Untergriff",
        "ja": "チンニング",
        "pt": "Barra fixa supinada",
        "hi": "चिन-अप"
    }),
    ("Dips", {
        "vi": "Chống xà kép (Dips)",
        "es": "Fondos en paralelas",
        "fr": "Dips aux barres parallèles",
        "de": "Barren-Dips",
        "ja": "ディップス",
        "pt": "Mergulho em paralelas",
        "hi": "डिप्स"
    }),
    ("Lat Pulldown", {
        "vi": "Kéo xô máy cáp (Lat Pulldown)",
        "es": "Jalón al pecho en polea",
        "fr": "Tirage vertical à la poulie",
        "de": "Latzug zur Brust",
        "ja": "ラットプルダウン",
        "pt": "Puxada frontal no pulley",
        "hi": "लैट पुलडाउन"
    }),
    ("Bent-Over Row", {
        "vi": "Kéo lưng gập người (Bent-Over Row)",
        "es": "Remo con barra inclinado",
        "fr": "Rowing buste penché",
        "de": "Vorgebeugtes Rudern",
        "ja": "ベントオーバーロー",
        "pt": "Remada curvada",
        "hi": "बेंट-ओवर रो"
    }),
    ("Barbell Row", {
        "vi": "Kéo lưng tạ đòn (Barbell Row)",
        "es": "Remo con barra",
        "fr": "Rowing barre",
        "de": "Langhantelrudern",
        "ja": "バーベルローイング",
        "pt": "Remada com barra",
        "hi": "बारबेल रो"
    }),
    ("Seated Cable Row", {
        "vi": "Kéo cáp ngồi tập lưng (Seated Cable Row)",
        "es": "Remo sentado en polea",
        "fr": "Tirage horizontal à la poulie",
        "de": "Rudern sitzend am Kabelzug",
        "ja": "シーテッドケーブルロー",
        "pt": "Remada baixa no pulley",
        "hi": "सीटेड केबल रो"
    }),
    ("T-Bar Row", {
        "vi": "Kéo lưng tạ chữ T (T-Bar Row)",
        "es": "Remo con barra T",
        "fr": "Rowing barre en T",
        "de": "T-Bar-Rudern",
        "ja": "Tバーロー",
        "pt": "Remada cavalinho (T-Bar)",
        "hi": "टी-बार रो"
    }),
    ("Upright Row", {
        "vi": "Kéo tạ thẳng đứng tập cầu vai (Upright Row)",
        "es": "Remo al mentón",
        "fr": "Tirage menton",
        "de": "Aufrechtes Rudern",
        "ja": "アップライトロー",
        "pt": "Remada alta",
        "hi": "अपराइट रो"
    }),
    ("Shrug", {
        "vi": "Nhún cầu vai (Shrug)",
        "es": "Encogimientos de hombros",
        "fr": "Haussements d'épaules",
        "de": "Schulterheben (Shrugs)",
        "ja": "シュラッグ",
        "pt": "Encolhimento de ombros",
        "hi": "श्रग"
    }),
    ("Squat", {
        "vi": "Gánh đùi (Squat)",
        "es": "Sentadilla",
        "fr": "Squat",
        "de": "Kniebeugen",
        "ja": "スクワット",
        "pt": "Agachamento",
        "hi": "स्क्वाट"
    }),
    ("Front Squat", {
        "vi": "Gánh tạ đùi trước (Front Squat)",
        "es": "Sentadilla frontal",
        "fr": "Front squat",
        "de": "Frontkniebeugen",
        "ja": "フロントスクワット",
        "pt": "Agachamento frontal",
        "hi": "फ्रंट स्क्वाट"
    }),
    ("Hack Squat", {
        "vi": "Đạp đùi Hack Squat",
        "es": "Sentadilla Hack",
        "fr": "Hack squat",
        "de": "Hackenschmidt-Kniebeuge",
        "ja": "ハックスクワット",
        "pt": "Agachamento Hack",
        "hi": "हैक स्क्वाट"
    }),
    ("Leg Press", {
        "vi": "Đạp đùi trên máy (Leg Press)",
        "es": "Prensa de piernas",
        "fr": "Presse à cuisses",
        "de": "Beinpresse",
        "ja": "レッグプレス",
        "pt": "Leg press 45°",
        "hi": "लेग प्रेस"
    }),
    ("Deadlift", {
        "vi": "Kéo tạ đòn (Deadlift)",
        "es": "Peso muerto",
        "fr": "Soulevé de terre",
        "de": "Kreuzheben",
        "ja": "デッドリフト",
        "pt": "Levantamento terra",
        "hi": "डेडलिफ्ट"
    }),
    ("Romanian Deadlift", {
        "vi": "Kéo đùi sau RDL (Romanian Deadlift)",
        "es": "Peso muerto rumano",
        "fr": "Soulevé de terre roumain",
        "de": "Rumänisches Kreuzheben",
        "ja": "ルーマニアンデッドリフト",
        "pt": "Stiff / Levantamento romeno",
        "hi": "रोमानियाई डेडलिफ्ट"
    }),
    ("Sumo Deadlift", {
        "vi": "Kéo tạ chân rộng (Sumo Deadlift)",
        "es": "Peso muerto sumo",
        "fr": "Soulevé de terre sumo",
        "de": "Sumo-Kreuzheben",
        "ja": "スモウデッドリフト",
        "pt": "Levantamento terra sumô",
        "hi": "सुमो डेडलिफ्ट"
    }),
    ("Lunge", {
        "vi": "Chùng chân (Lunge)",
        "es": "Zancadas",
        "fr": "Fentes",
        "de": "Ausfallschritte",
        "ja": "ランジ",
        "pt": "Avanço / Passada",
        "hi": "लंजेस"
    }),
    ("Leg Extension", {
        "vi": "Đá đùi trước máy (Leg Extension)",
        "es": "Extensión de piernas en máquina",
        "fr": "Leg extension",
        "de": "Beinstrecker an der Maschine",
        "ja": "レッグエクステンション",
        "pt": "Cadeira extensora",
        "hi": "लेग एक्सटेंशन"
    }),
    ("Leg Curl", {
        "vi": "Cuốn đùi sau máy (Leg Curl)",
        "es": "Curl femoral en máquina",
        "fr": "Leg curl",
        "de": "Beinbeuger an der Maschine",
        "ja": "レッグカール",
        "pt": "Mesa flexora",
        "hi": "लेग कर्ल"
    }),
    ("Calf Raise", {
        "vi": "Nhón bắp chân (Calf Raise)",
        "es": "Elevaciones de gemelos",
        "fr": "Élévations des mollets",
        "de": "Wadenheben",
        "ja": "カーフレイズ",
        "pt": "Elevação de panturrilha",
        "hi": "काफ रेज"
    }),
    ("Bicep Curl", {
        "vi": "Cuốn tay trước (Bicep Curl)",
        "es": "Curl de bíceps",
        "fr": "Curl biceps",
        "de": "Bizepscurls",
        "ja": "アームカール",
        "pt": "Rosca direta para bíceps",
        "hi": "बाइसेप कर्ल"
    }),
    ("Hammer Curl", {
        "vi": "Cuốn tạ tay búa (Hammer Curl)",
        "es": "Curl martillo",
        "fr": "Curl marteau",
        "de": "Hammercurls",
        "ja": "ハンマーカール",
        "pt": "Rosca martelo",
        "hi": "हैमर कर्ल"
    }),
    ("Preacher Curl", {
        "vi": "Cuốn tay trước ghế dốc (Preacher Curl)",
        "es": "Curl predicador en banco Scott",
        "fr": "Curl pupitre Larry Scott",
        "de": "Preacher Curls am Scott-Bank",
        "ja": "プリーチャーカール",
        "pt": "Rosca Scott",
        "hi": "प्रीचर कर्ल"
    }),
    ("Triceps Pushdown", {
        "vi": "Kéo cáp tay sau (Triceps Pushdown)",
        "es": "Extensión de tríceps en polea",
        "fr": "Extension triceps à la poulie",
        "de": "Trizepsdrücken am Kabelzug",
        "ja": "トライセプスプッシュダウン",
        "pt": "Tríceps no pulley",
        "hi": "ट्राइसेप्स पुशडाउन"
    }),
    ("Skullcrusher", {
        "vi": "Duỗi tay sau nằm (Skullcrusher)",
        "es": "Press francés con barra EZ",
        "fr": "Barre au front pour triceps",
        "de": "Stirndrücken (Skullcrusher)",
        "ja": "スカルクラッシャー",
        "pt": "Tríceps testa",
        "hi": "स्कल क्रशर"
    }),
    ("Plank", {
        "vi": "Giữ người siết cơ bụng (Plank)",
        "es": "Plancha abdominal isométrica",
        "fr": "Gainage planche",
        "de": "Plank / Unterarmstütz",
        "ja": "プランク",
        "pt": "Prancha abdominal isométrica",
        "hi": "प्लैंक"
    }),
    ("Crunch", {
        "vi": "Gập bụng (Crunch)",
        "es": "Abdominales crunch",
        "fr": "Crunch abdominal",
        "de": "Crunches für Bauch",
        "ja": "クランチ",
        "pt": "Abdominal crunch",
        "hi": "क्रंच"
    }),
    ("Sit-Up", {
        "vi": "Gập bụng toàn phần (Sit-Up)",
        "es": "Abdominales completos Sit-up",
        "fr": "Relevés de buste Sit-up",
        "de": "Sit-ups",
        "ja": "シットアップ",
        "pt": "Abdominal tradicional Sit-up",
        "hi": "सिट-अप"
    }),
    ("Hip Thrust", {
        "vi": "Đẩy hông tập mông (Hip Thrust)",
        "es": "Empuje de cadera (Hip Thrust)",
        "fr": "Hip thrust pour fessiers",
        "de": "Hip Thrusts für Gesäß",
        "ja": "ヒップスラスト",
        "pt": "Elevação pélvica / Hip Thrust",
        "hi": "हिप थ्रस्ट"
    }),
    ("Nordic Hamstring Curl", {
        "vi": "Cuốn đùi sau kiểu Bắc Âu (Nordic Curl)",
        "es": "Curl nórdico para isquiotibiales",
        "fr": "Nordic hamstring curl",
        "de": "Nordic Curls für Beinbeuger",
        "ja": "ノーディックハムストリングカール",
        "pt": "Flexão nórdica para posteriores",
        "hi": "नॉर्डिक हैमस्ट्रिंग कर्ल"
    }),
    ("Fire Hydrant", {
        "vi": "Nâng chân ngang tập mông (Fire Hydrant)",
        "es": "Boca de incendio para glúteos",
        "fr": "Fire hydrant pour fessiers",
        "de": "Fire Hydrant für Gesäß",
        "ja": "ファイヤーハイドラント",
        "pt": "Elevação lateral de perna 4 apoios",
        "hi": "फायर हाइड्रेंट"
    }),
    ("Good Morning", {
        "vi": "Gập lưng tạ đòn (Good Morning)",
        "es": "Buenos días con barra",
        "fr": "Good morning à la barre",
        "de": "Good Mornings mit Langhantel",
        "ja": "グッドモーニング",
        "pt": "Good morning com barra",
        "hi": "गुड मॉर्निंग"
    }),
    ("Hyperextension", {
        "vi": "Nâng lưng dưới trên ghế dốc (Hyperextension)",
        "es": "Hiperextensiones para espalda baja",
        "fr": "Hyperextensions lombaires",
        "de": "Hyperextensions für unteren Rücken",
        "ja": "ハイパーエクステンション",
        "pt": "Hiperextensão lombar no banco",
        "hi": "हाइपरएक्सटेंशन"
    }),
]

def generate_i18n_names(name: str):
    """Generate localized names for an exercise across 8 languages."""
    names = {
        "en": name,
        "vi": name,
        "es": name,
        "fr": name,
        "de": name,
        "ja": name,
        "pt": name,
        "hi": name,
    }

    lower_name = name.lower()
    
    # 1. Match against known movement terminology
    matched = False
    for pat, trans in MOVEMENTS:
        if pat.lower() in lower_name:
            matched = True
            for lang, val in trans.items():
                # If there is prefix equipment like Barbell/Dumbbell, add it
                prefix = ""
                if "barbell" in lower_name and "barbell" not in pat.lower():
                    eq_map = {"vi": "Tạ đòn: ", "es": "Con barra - ", "fr": "À la barre - ", "de": "Langhantel-", "ja": "バーベル ", "pt": "Com barra: ", "hi": "बारबेल "}
                    prefix = eq_map.get(lang, "")
                elif "dumbbell" in lower_name and "dumbbell" not in pat.lower():
                    eq_map = {"vi": "Tạ đơn: ", "es": "Con mancuerna - ", "fr": "Aux haltères - ", "de": "Kurzhantel-", "ja": "ダンベル ", "pt": "Com haltere: ", "hi": "डंबल "}
                    prefix = eq_map.get(lang, "")
                elif "cable" in lower_name and "cable" not in pat.lower():
                    eq_map = {"vi": "Dây cáp: ", "es": "En polea - ", "fr": "À la poulie - ", "de": "Kabel-", "ja": "ケーブル ", "pt": "No cabo: ", "hi": "केबल "}
                    prefix = eq_map.get(lang, "")
                elif "machine" in lower_name and "machine" not in pat.lower():
                    eq_map = {"vi": "Máy tập: ", "es": "En máquina - ", "fr": "Sur machine - ", "de": "Maschinen-", "ja": "マシン ", "pt": "Na máquina: ", "hi": "मशीन "}
                    prefix = eq_map.get(lang, "")
                    
                names[lang] = f"{prefix}{val}"
            break
            
    # 2. If not matched, generate clean fallback names with English in brackets
    if not matched:
        names["vi"] = f"{name} (Bài tập thể hình)"
        names["es"] = f"{name} (Ejercicio)"
        names["fr"] = f"{name} (Exercice)"
        names["de"] = f"{name} (Übung)"
        names["ja"] = f"{name} (エクササイズ)"
        names["pt"] = f"{name} (Exercício)"
        names["hi"] = f"{name} (व्यायाम)"

    return names

def main():
    print(f"Loading source exercises from {SOURCE_FILE}...")
    with open(SOURCE_FILE, "r", encoding="utf-8") as f:
        exercises = json.load(f)

    print(f"Total exercises: {len(exercises)}")
    video_exercises = [e for e in exercises if "video_url" in e]
    print(f"Exercises with video: {len(video_exercises)} (preserving 100%)")

    # Load cache
    cache = {}
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)
        print(f"Loaded {len(cache)} cached translation strings.")

    # Apply professional i18n
    print("\nApplying professional terminology and localized instruction steps...")
    updated_count = 0
    vi_steps_attached = 0

    for ex in exercises:
        name_en = ex.get("name", "")
        ex["name_i18n"] = generate_i18n_names(name_en)

        # Build instruction_steps
        instruction_steps = ex.get("instruction_steps", {})
        en_steps = instruction_steps.get("en", [])

        # Attach Vietnamese steps from cache
        vi_steps = []
        for s in en_steps:
            s_clean = s.strip()
            if not s_clean:
                continue
            translated = cache.get(f"vi::{s_clean}")
            if translated:
                vi_steps.append(translated)
            else:
                vi_steps.append(s_clean)

        if vi_steps:
            instruction_steps["vi"] = vi_steps
            vi_steps_attached += 1

        ex["instruction_steps"] = instruction_steps

        # Build instructions
        instructions = ex.get("instructions", {})
        if vi_steps:
            instructions["vi"] = " ".join(vi_steps)
        ex["instructions"] = instructions

        updated_count += 1

    print(f"Processed {updated_count} exercises.")
    print(f"Attached Vietnamese step instructions to {vi_steps_attached} exercises.")

    # Save to fitness app
    print(f"\nWriting to {SOURCE_FILE}...")
    with open(SOURCE_FILE, "w", encoding="utf-8") as f:
        json.dump(exercises, f, ensure_ascii=False, indent=2)
    print("Successfully updated fitness app assets/data/exercises.json")

    # Sync to fork repository if present
    if os.path.exists(FORK_DIR):
        print(f"\nSyncing to fork repository at {FORK_DIR}...")
        fork_dist = os.path.join(FORK_DIR, "dist")
        fork_i18n = os.path.join(fork_dist, "i18n")
        os.makedirs(fork_i18n, exist_ok=True)

        # 1. Master exercises.json in fork
        master_dest = os.path.join(fork_dist, "exercises.json")
        with open(master_dest, "w", encoding="utf-8") as f:
            json.dump(exercises, f, ensure_ascii=False, indent=2)
        print(f"  Updated master: {master_dest}")

        # 2. Generate 8 standalone per-language bundles in dist/i18n/
        all_langs = ["en", "vi", "es", "fr", "de", "ja", "pt", "hi"]
        for lang in all_langs:
            bundle = []
            for ex in exercises:
                item = dict(ex)
                item["name"] = ex.get("name_i18n", {}).get(lang, ex.get("name", ""))
                # Localized instructions for this bundle
                if lang in ex.get("instructions", {}):
                    item["instructions"] = {lang: ex["instructions"][lang]}
                elif "en" in ex.get("instructions", {}):
                    item["instructions"] = {"en": ex["instructions"]["en"]}

                if lang in ex.get("instruction_steps", {}):
                    item["instruction_steps"] = {lang: ex["instruction_steps"][lang]}
                elif "en" in ex.get("instruction_steps", {}):
                    item["instruction_steps"] = {"en": ex["instruction_steps"]["en"]}

                bundle.append(item)

            bundle_path = os.path.join(fork_i18n, f"exercises_{lang}.json")
            with open(bundle_path, "w", encoding="utf-8") as f:
                json.dump(bundle, f, ensure_ascii=False, indent=2)
            print(f"  Generated bundle: {bundle_path}")

        # 3. Add documentation in README.md
        readme_path = os.path.join(FORK_DIR, "README.md")
        if os.path.exists(readme_path):
            with open(readme_path, "r", encoding="utf-8") as f:
                content = f.read()

            if "## Multi-Language & Video Assets Support" not in content:
                i18n_doc = """
## Multi-Language & Video Assets Support (Fork Enhancements)

This repository fork adds comprehensive internationalization and rich media extensions:
1. **8 Supported Languages**:
   - `en` (English - default)
   - `vi` (Tiếng Việt)
   - `es` (Español)
   - `fr` (Français)
   - `de` (Deutsch)
   - `ja` (日本語)
   - `pt` (Português)
   - `hi` (हिन्दी)
2. **Standard Terminology**: Professional gym movement nomenclature mapped in `name_i18n`.
3. **Cloudflare R2 Video & Cues Integration**: 57 top compound and isolation exercises enriched with `video_url`, `video_slug`, form `cues`, `joint_stress`, and mechanics `type`.
4. **Standalone Language Bundles**: Pre-compiled single-language datasets available in `dist/i18n/exercises_{lang}.json` for zero-overhead mobile app integration.
"""
                with open(readme_path, "w", encoding="utf-8") as f:
                    f.write(content + "\n" + i18n_doc)
                print(f"  Updated documentation in {readme_path}")

    print("\nDataset successfully compiled and synchronized!")

if __name__ == "__main__":
    main()

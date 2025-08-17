# app.py — Flask სერვერი
from flask import Flask, jsonify, request, send_from_directory
from datetime import datetime
import os

app = Flask(__name__, static_url_path="/static", static_folder="static")

SIGNS = [
  { "key": "aries", "ka": "ვერძი", "en": "Aries", "emoji": "♈️", "start": "03-21", "end": "04-19", "element": "Fire", "modality": "Cardinal", "planet": "Mars", "blurb": "ვერძი აქტიური, უშიშარი და წამყვანი ნიშნაა." },
  { "key": "taurus", "ka": "კურო", "en": "Taurus", "emoji": "♉️", "start": "04-20", "end": "05-20", "element": "Earth", "modality": "Fixed", "planet": "Venus", "blurb": "კურო აფასებს კომფორტს, საიმედოობას და გრძელვადიან სისწორეს." },
  { "key": "gemini", "ka": "ტყუპები", "en": "Gemini", "emoji": "♊️", "start": "05-21", "end": "06-20", "element": "Air", "modality": "Mutable", "planet": "Mercury", "blurb": "ტყუპები სწრაფად აზროვნებს, უყვარს საუბარი და იდეების გაცვლა." },
  { "key": "cancer", "ka": "კირჩხიბი", "en": "Cancer", "emoji": "♋️", "start": "06-21", "end": "07-22", "element": "Water", "modality": "Cardinal", "planet": "Moon", "blurb": "კირჩხიბი ოჯახზე და ემოციებზეა ორიენტირებული." },
  { "key": "leo", "ka": "ლომი", "en": "Leo", "emoji": "♌️", "start": "07-23", "end": "08-22", "element": "Fire", "modality": "Fixed", "planet": "Sun", "blurb": "ლომი ბრწყინავს სცენაზე — გულუხვი და შემოქმედებითი." },
  { "key": "virgo", "ka": "ქალწული", "en": "Virgo", "emoji": "♍️", "start": "08-23", "end": "09-22", "element": "Earth", "modality": "Mutable", "planet": "Mercury", "blurb": "ქალწული დეტალებში პოულობს სრულყოფას." },
  { "key": "libra", "ka": "სასწორი", "en": "Libra", "emoji": "♎️", "start": "09-23", "end": "10-22", "element": "Air", "modality": "Cardinal", "planet": "Venus", "blurb": "სასწორი ბალანსს ეძებს და სილამაზეს აფასებს." },
  { "key": "scorpio", "ka": "მორიელი", "en": "Scorpio", "emoji": "♏️", "start": "10-23", "end": "11-21", "element": "Water", "modality": "Fixed", "planet": "Pluto", "blurb": "მორიელი ინტენსიურია — სიმართლის ძიება და ემოციური სიღრმე მისი სტიქიაა." },
  { "key": "sagittarius", "ka": "მშვილდოსანი", "en": "Sagittarius", "emoji": "♐️", "start": "11-22", "end": "12-21", "element": "Fire", "modality": "Mutable", "planet": "Jupiter", "blurb": "მშვილდოსანი მოგზაური და ფილოსოფოსია." },
  { "key": "capricorn", "ka": "თხის რქა", "en": "Capricorn", "emoji": "♑️", "start": "12-22", "end": "01-19", "element": "Earth", "modality": "Cardinal", "planet": "Saturn", "blurb": "თხის რქა მიზანდასახულია." },
  { "key": "aquarius", "ka": "მერწყული", "en": "Aquarius", "emoji": "♒️", "start": "01-20", "end": "02-18", "element": "Air", "modality": "Fixed", "planet": "Uranus", "blurb": "მერწყული ორიგინალური და ინოვატორია." },
  { "key": "pisces", "ka": "თევზები", "en": "Pisces", "emoji": "♓️", "start": "02-19", "end": "03-20", "element": "Water", "modality": "Mutable", "planet": "Neptune", "blurb": "თევზები ოცნებებს მატერიალიზებს." }
]

CHINESE_SIGNS = ["ვირთხა","კუი","ვეფხვი","კურდღელი","დრაკონი","გველი","ცხენი","თხა","მაიმუნი","მამალი","ძაღლი","ღორი"]

def chinese_zodiac(year:int)->str:
    base = 1900
    return CHINESE_SIGNS[(year - base) % 12]

def parse_date(s:str):
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except Exception:
        return None

def sign_from_date(s:str):
    d = parse_date(s)
    if not d: return None
    m, day = d.month, d.day
    for sign in SIGNS:
        sm, sd = map(int, sign["start"].split("-"))
        em, ed = map(int, sign["end"].split("-"))
        if (sm < em) or (sm == em and sd <= ed):
            in_range = ((m == sm and day >= sd) or (m == em and day <= ed) or (m > sm and m < em))
        else:
            in_range = ((m == sm and day >= sd) or (m == em and day <= ed) or (m > sm or m < em))
        if in_range:
            return sign
    return None

def life_path_from_date(s:str):
    d = parse_date(s)
    if not d: return None
    digits = list(map(int, f"{d.year:04d}{d.month:02d}{d.day:02d}"))
    total = sum(digits)
    while total > 9 and total not in (11,22,33):
        total = sum(map(int, str(total)))
    return total

def moon_sign_dummy(s:str):
    d = parse_date(s)
    if not d: return None
    # ძალიან გამარტივებული: თვე -> ნიშანი
    return SIGNS[(d.month - 1) % 12]

def compatibility(a:dict, b:dict):
    if not a or not b: 
        return {"score": 0, "note": "მონაცემები საკმარისი არაა"}
    score = 50
    # ელემენტები
    if a["element"] == b["element"]:
        score += 20
    pairs_good = {("Fire","Air"),("Air","Fire"),("Earth","Water"),("Water","Earth")}
    pairs_hard = {("Fire","Water"),("Water","Fire"),("Air","Earth"),("Earth","Air")}
    if (a["element"], b["element"]) in pairs_good:
        score += 15
    if (a["element"], b["element"]) in pairs_hard:
        score -= 10
    # მოდალობა
    if a["modality"] == b["modality"]:
        score += 10
    # პლანეტა
    if a["planet"] == b["planet"]:
        score += 5

    score = max(0, min(100, score))
    if score >= 75:
        note = "✨ ძალიან ძლიერი თავსებადობა!"
    elif score >= 50:
        note = "😊 კარგი შანსი ურთიერთობისთვის."
    else:
        note = "⚠️ მეტი მუშაობა დაგჭირდებათ ურთიერთობაზე."
    return {"score": score, "note": note}

def profile(date_str:str):
    w = sign_from_date(date_str)
    moon = moon_sign_dummy(date_str)
    ch = chinese_zodiac(parse_date(date_str).year) if parse_date(date_str) else None
    lp = life_path_from_date(date_str)
    return {
        "western": w,
        "moon": moon,
        "chinese": ch,
        "life_path": lp
    }

@app.route("/")
def root():
    return send_from_directory(".", "index.html")

@app.route("/api/calc", methods=["POST"])
def calc():
    data = request.get_json(force=True, silent=True) or {}
    my_date = data.get("my_date") or ""
    partner_date = data.get("partner_date") or ""

    me = profile(my_date) if my_date else {}
    partner = profile(partner_date) if partner_date else {}
    comp = compatibility(me.get("western"), partner.get("western"))
    return jsonify({"me": me, "partner": partner, "compatibility": comp})

if __name__ == "__main__":
    # Flask dev server
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

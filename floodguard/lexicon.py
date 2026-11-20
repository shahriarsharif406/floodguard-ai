"""English + Bangla keyword lists for the rule-based analyser. Order = tie-break priority (life-critical first)."""
from __future__ import annotations

CATEGORY_ORDER = ["rescue_needed", "medical", "food_water", "shelter", "water_level", "infrastructure", "power_telecom",
                  "livestock_crops"]

KEYWORDS: dict[str, dict[str, list[str]]] = {
    "rescue_needed": {
        "en": ["trapped", "stuck", "on the roof", "rooftop", "rescue", "save us", "help us", "drowning", "drowned",
               "missing", "boat needed", "need boat", "need a boat", "swept away", "can't get out", "stranded"],
        "bn": ["আটকা", "আটকে", "ছাদে", "চালে", "উদ্ধার", "বাঁচান", "বাঁচাও", "ডুবে যাচ্ছে", "ডুবছে", "নিখোঁজ",
               "ভেসে গেছে", "ভেসে যাচ্ছে", "নৌকা দরকার", "নৌকা লাগবে", "বের হতে পারছি না"]},
    "medical": {
        "en": ["injured", "sick", "fever", "diarrhea", "diarrhoea", "snake bite", "snakebite", "pregnant", "labour",
               "labor pain", "medicine", "unconscious", "bleeding"],
        "bn": ["আহত", "অসুস্থ", "জ্বর", "ডায়রিয়া", "পাতলা পায়খানা", "সাপে কাটা", "সাপের কামড়", "গর্ভবতী", "প্রসব",
               "ওষুধ", "ঔষধ", "অজ্ঞান", "রক্ত"]},
    "food_water": {
        "en": ["food", "hungry", "rice", "drinking water", "clean water", "safe water", "dry food", "baby food",
               "milk", "starving"],
        "bn": ["খাবার", "খাদ্য", "ক্ষুধা", "না খেয়ে", "চাল", "বিশুদ্ধ পানি", "খাবার পানি", "খাওয়ার পানি",
               "শুকনো খাবার", "শিশুখাদ্য", "দুধ", "চিড়া", "মুড়ি"]},
    "shelter": {
        "en": ["shelter", "homeless", "house collapsed", "house submerged", "nowhere to stay", "evacuate",
               "evacuation", "school shelter", "at the school", "tarpaulin", "tarpaulins"],
        "bn": ["আশ্রয়", "আশ্রয়কেন্দ্র", "ঘর ভেঙে", "ঘর ডুবে", "ঘরে পানি", "থাকার জায়গা নেই", "সরিয়ে নিতে",
               "বাড়ি ডুবে", "স্কুলে", "তারপুলিন"]},
    "infrastructure": {
        "en": ["road", "bridge", "embankment", "dam breach", "culvert", "highway", "road cut", "washed out",
               "school flooded"],
        "bn": ["রাস্তা", "সড়ক", "সেতু", "ব্রিজ", "বাঁধ", "বেড়িবাঁধ", "কালভার্ট", "ভেঙে গেছে", "যোগাযোগ বিচ্ছিন্ন"]},
    "power_telecom": {
        "en": ["electricity", "power cut", "no power", "blackout", "network", "no signal", "mobile network",
               "transformer"],
        "bn": ["বিদ্যুৎ", "কারেন্ট নেই", "বিদ্যুৎ নেই", "নেটওয়ার্ক", "মোবাইল নেটওয়ার্ক", "ট্রান্সফরমার"]},
    "livestock_crops": {
        "en": ["cattle", "cow", "goat", "livestock", "crops", "paddy", "harvest", "fish farm", "poultry"],
        "bn": ["গরু", "ছাগল", "গবাদি", "হাঁস", "মুরগি", "ফসল", "ধান", "বোরো", "মাছের ঘের", "পুকুর"]},
    "water_level": {
        "en": ["water rising", "rising fast", "knee deep", "waist deep", "chest deep", "overflowing", "danger level",
               "flash flood", "river overflow"],
        "bn": ["পানি বাড়ছে", "পানি বাড়ছে দ্রুত", "হাঁটু পানি", "কোমর পানি", "বুক পানি", "গলা পানি", "বিপদসীমা",
               "ঢল", "পাহাড়ি ঢল", "উপচে", "বন্যা"]},
}

CRITICAL_WORDS = ["drowning", "unconscious", "missing", "swept away", "snake bite", "snakebite", "bleeding", "labour",
                  "ডুবে যাচ্ছে", "নিখোঁজ", "ভেসে গেছে", "অজ্ঞান", "সাপে কাটা", "প্রসব", "গলা পানি"]
VULNERABLE_WORDS = ["child", "children", "baby", "infant", "elderly", "old", "pregnant", "disabled",
                    "শিশু", "বাচ্চা", "বৃদ্ধ", "বয়স্ক", "গর্ভবতী", "প্রতিবন্ধী"]
HIGH_WORDS = ["chest deep", "বুক পানি", "house submerged", "ঘর ডুবে", "ঘরে পানি", "diarrhea", "diarrhoea", "ডায়রিয়া"]
LOW_MARKERS = ["information only", "for information", "শুধু তথ্য", "তথ্যের জন্য"]
LARGE_GROUP = 20   # people_affected at/above this with an essential-needs category → at least HIGH

CATEGORY_NEEDS = {
    "rescue_needed": ["boat_rescue"], "medical": ["medical_help"], "food_water": ["drinking_water", "food"],
    "shelter": ["dry_shelter"], "infrastructure": ["road_access"], "power_telecom": ["power", "phone_network"],
    "livestock_crops": ["animal_shelter"], "water_level": ["information"], "other": ["information"],
}

STOPWORDS_EN = set("the a an is are was were we our us it this that of to in on at and or for with from by be been have has had "
                   "there their they you your i my me as so but not no can could need needs".split())
STOPWORDS_BN = set("এবং আমরা আছে হয় না এই যে আমাদের তারা তাদের এটি ও কিন্তু থেকে জন্য করে করা হয়েছে হচ্ছে আর "
                   "একটি একটা সব কোনো কি কী তা তো যেন পর্যন্ত মধ্যে সাথে অনেক খুব দয়া করে করুন আছেন পড়েছি".split())

# light synonym folding so paraphrased duplicates (same incident, different words) still match
SYNONYMS = {"লাগবে": "need", "দরকার": "need", "needs": "need", "needed": "need", "বৃদ্ধ": "elderly", "বয়স্ক": "elderly",
            "old": "elderly", "আটকে": "আটকা", "stuck": "trapped", "আটকা": "trapped", "trapped": "trapped",
            "উদ্ধার": "rescue", "rescue": "rescue"}

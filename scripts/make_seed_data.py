"""Generates data/districts_bd.json, replay_sylhet2022.json, shelters_demo.json and seed photos.
All replay reports are SIMULATED. District centroids are approximate (±5 km)."""
import json
from pathlib import Path
from PIL import Image, ImageDraw

D = Path(__file__).resolve().parent.parent / "data"
D.mkdir(exist_ok=True)

districts = [
("Bagerhat","বাগেরহাট",22.66,89.79),("Bandarban","বান্দরবান",22.19,92.22),("Barguna","বরগুনা",22.15,90.12),
("Barishal","বরিশাল",22.70,90.37),("Bhola","ভোলা",22.69,90.65),("Bogura","বগুড়া",24.85,89.37),
("Brahmanbaria","ব্রাহ্মণবাড়িয়া",23.96,91.11),("Chandpur","চাঁদপুর",23.23,90.67),("Chapai Nawabganj","চাঁপাইনবাবগঞ্জ",24.60,88.28),
("Chattogram","চট্টগ্রাম",22.36,91.78),("Chuadanga","চুয়াডাঙ্গা",23.64,88.85),("Cox's Bazar","কক্সবাজার",21.43,92.01),
("Cumilla","কুমিল্লা",23.46,91.18),("Dhaka","ঢাকা",23.81,90.41),("Dinajpur","দিনাজপুর",25.63,88.64),
("Faridpur","ফরিদপুর",23.60,89.84),("Feni","ফেনী",23.02,91.40),("Gaibandha","গাইবান্ধা",25.33,89.53),
("Gazipur","গাজীপুর",24.00,90.42),("Gopalganj","গোপালগঞ্জ",23.01,89.83),("Habiganj","হবিগঞ্জ",24.38,91.42),
("Jamalpur","জামালপুর",24.92,89.94),("Jashore","যশোর",23.17,89.21),("Jhalokathi","ঝালকাঠি",22.64,90.20),
("Jhenaidah","ঝিনাইদহ",23.54,89.17),("Joypurhat","জয়পুরহাট",25.10,89.02),("Khagrachhari","খাগড়াছড়ি",23.12,91.98),
("Khulna","খুলনা",22.82,89.55),("Kishoreganj","কিশোরগঞ্জ",24.43,90.78),("Kurigram","কুড়িগ্রাম",25.81,89.64),
("Kushtia","কুষ্টিয়া",23.90,89.12),("Lakshmipur","লক্ষ্মীপুর",22.94,90.84),("Lalmonirhat","লালমনিরহাট",25.99,89.28),
("Madaripur","মাদারীপুর",23.17,90.20),("Magura","মাগুরা",23.49,89.42),("Manikganj","মানিকগঞ্জ",23.86,90.00),
("Meherpur","মেহেরপুর",23.76,88.63),("Moulvibazar","মৌলভীবাজার",24.48,91.77),("Munshiganj","মুন্সিগঞ্জ",23.55,90.53),
("Mymensingh","ময়মনসিংহ",24.75,90.41),("Naogaon","নওগাঁ",24.80,88.94),("Narail","নড়াইল",23.17,89.50),
("Narayanganj","নারায়ণগঞ্জ",23.63,90.50),("Narsingdi","নরসিংদী",23.92,90.72),("Natore","নাটোর",24.42,89.00),
("Netrakona","নেত্রকোনা",24.87,90.73),("Nilphamari","নীলফামারী",25.93,88.86),("Noakhali","নোয়াখালী",22.87,91.10),
("Pabna","পাবনা",24.00,89.25),("Panchagarh","পঞ্চগড়",26.34,88.55),("Patuakhali","পটুয়াখালী",22.36,90.33),
("Pirojpur","পিরোজপুর",22.58,89.97),("Rajbari","রাজবাড়ী",23.76,89.64),("Rajshahi","রাজশাহী",24.37,88.60),
("Rangamati","রাঙ্গামাটি",22.65,92.17),("Rangpur","রংপুর",25.75,89.25),("Satkhira","সাতক্ষীরা",22.72,89.07),
("Shariatpur","শরীয়তপুর",23.22,90.35),("Sherpur","শেরপুর",25.02,90.02),("Sirajganj","সিরাজগঞ্জ",24.45,89.70),
("Sunamganj","সুনামগঞ্জ",25.07,91.41),("Sylhet","সিলেট",24.89,91.87),("Tangail","টাঙ্গাইল",24.25,89.92),
("Thakurgaon","ঠাকুরগাঁও",26.03,88.47)]
assert len(districts) == 64, len(districts)
(D / "districts_bd.json").write_text(json.dumps(
    [{"name_en": a, "name_bn": b, "lat": c, "lon": d} for a, b, c, d in districts], ensure_ascii=False, indent=1), encoding="utf-8")

# id, created (BST, local), district, upazila, lat, lon, text, status, note
R = [
(1,"2022-06-15T21:10","Sylhet","Companiganj",25.06,91.76,"পাহাড়ি ঢলে পানি খুব দ্রুত বাড়ছে, রাস্তা ডুবে গেছে। বাজারে হাঁটু পানি।","verified",""),
(2,"2022-06-16T07:40","Sunamganj","Chhatak",25.04,91.67,"Water entered our homes overnight, chest deep now. 6 families with small children need dry food and drinking water.","verified",""),
(3,"2022-06-16T09:05","Sunamganj","Sunamganj Sadar",25.07,91.40,"আমরা ৪ জন ছাদে আটকা পড়েছি, নৌকা লাগবে, বৃদ্ধ মা অসুস্থ।","verified",""),
(4,"2022-06-16T09:30","Sunamganj","Sunamganj Sadar",25.07,91.408,"৪ জন ছাদে আটকা, নৌকা দরকার, বয়স্ক মা আছেন। দয়া করে উদ্ধার করুন।","under_review",""),
(5,"2022-06-16T13:20","Sylhet","Gowainghat",25.10,91.98,"Bridge on the Gowainghat road washed out, no vehicles can pass.","verified",""),
(6,"2022-06-17T06:15","Sylhet","Kanaighat",25.00,92.26,"Surma overflowing, whole village under water. Around 30 people at the school, no food since yesterday.","pending",""),
(7,"2022-06-17T10:00","Sylhet","Sylhet city (Upashahar)",24.89,91.88,"শহরের উপশহর এলাকায় বুক পানি, বিদ্যুৎ নেই দুই দিন, মোবাইল নেটওয়ার্ক বন্ধ।","verified",""),
(8,"2022-06-17T11:45","Sunamganj","Dowarabazar",25.08,91.57,"A child is missing after being swept away near the river bank. Need boat search urgently.","pending",""),
(9,"2022-06-17T16:30","Sunamganj","Tahirpur",25.12,91.18,"হাওরে বোরো ধান আগেই তোলা হয়েছিল, কিন্তু গরু-ছাগল রাখার জায়গা নেই, সব ডুবে গেছে।","pending",""),
(10,"2022-06-18T08:20","Sylhet","Companiganj",25.05,91.78,"Pregnant woman in labour pain, all roads under water, need boat to hospital.","under_review",""),
(11,"2022-06-18T12:10","Sylhet","Zakiganj",24.88,92.37,"কুশিয়ারার বাঁধ ভেঙে গ্রামে পানি ঢুকছে। ৫০ পরিবার আশ্রয়কেন্দ্রে যেতে চায়।","pending",""),
(12,"2022-06-18T18:40","Sunamganj","Jagannathpur",24.77,91.55,"Shelter at the primary school is overcrowded, need clean drinking water and baby food.","verified",""),
(13,"2022-06-19T09:00","Sylhet","Bishwanath",24.83,91.72,"পানি একটু কমছে কিন্তু টিউবওয়েল ডুবে আছে, বিশুদ্ধ পানির অভাব, ডায়রিয়া শুরু হয়েছে।","pending",""),
(14,"2022-06-19T14:30","Sunamganj","Derai",24.79,91.35,"Snake bite case in our village, no transport, water everywhere.","pending",""),
(15,"2022-06-20T10:15","Moulvibazar","Kulaura",24.51,92.04,"Hakaluki haor side villages flooded, road to Kulaura cut.","pending",""),
(16,"2022-06-20T15:50","Sylhet","Sylhet city (Zindabazar)",24.90,91.87,"Shops flooded on Zindabazar road, knee deep water. Situation information only.","rejected","Photo re-shared from 2019 event"),
(17,"2022-06-21T08:30","Netrakona","Kalmakanda",25.08,90.88,"কলমাকান্দায় নদীর পানি বিপদসীমার উপরে, অনেক ঘরে পানি, শুকনো খাবার দরকার।","pending",""),
(18,"2022-06-23T11:00","Sunamganj","Bishwambharpur",25.10,91.29,"Water receding slowly. 12 families still on the embankment, need tarpaulins and rice.","pending",""),
]
photos = {7: "seed_photos/water_a.png", 16: "seed_photos/water_a_resaved.png"}
out = []
for i, ts, dist, upa, lat, lon, text, status, note in R:
    out.append({"id": i, "created_at": ts, "district": dist, "upazila": upa, "lat": lat, "lon": lon, "text": text,
                "status": status, "mod_note": note, "photo": photos.get(i), "simulated": True})
(D / "replay_sylhet2022.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

S = [("Sunamganj Govt. High School","সুনামগঞ্জ সরকারি উচ্চ বিদ্যালয়",25.068,91.402,"Sunamganj"),
("Chhatak Pilot School","ছাতক পাইলট স্কুল",25.040,91.672,"Sunamganj"),
("Companiganj Upazila Complex","কোম্পানীগঞ্জ উপজেলা কমপ্লেক্স",25.058,91.770,"Sylhet"),
("Gowainghat College","গোয়াইনঘাট কলেজ",25.103,91.975,"Sylhet"),
("Kanaighat Govt. Primary School","কানাইঘাট সরকারি প্রাথমিক বিদ্যালয়",25.002,92.258,"Sylhet"),
("Sylhet MC College","সিলেট এমসি কলেজ",24.906,91.898,"Sylhet"),
("Zakiganj Govt. College","জকিগঞ্জ সরকারি কলেজ",24.880,92.365,"Sylhet"),
("Jagannathpur High School","জগন্নাথপুর উচ্চ বিদ্যালয়",24.770,91.548,"Sunamganj"),
("Derai Upazila Complex","দিরাই উপজেলা কমপ্লেক্স",24.787,91.350,"Sunamganj"),
("Kalmakanda Upazila Complex","কলমাকান্দা উপজেলা কমপ্লেক্স",25.080,90.880,"Netrakona")]
(D / "shelters_demo.json").write_text(json.dumps(
    [{"id": i + 1, "name": n + " (DEMO)", "name_bn": b, "lat": la, "lon": lo, "district": d, "is_demo": 1}
     for i, (n, b, la, lo, d) in enumerate(S)], ensure_ascii=False, indent=1), encoding="utf-8")

# abstract seed photos (no real people/places): water-blue shapes
(D / "seed_photos").mkdir(exist_ok=True)
img = Image.new("RGB", (480, 320), (24, 58, 92))
dr = ImageDraw.Draw(img)
dr.rectangle([0, 170, 480, 320], fill=(40, 120, 170))
dr.polygon([(60, 170), (140, 90), (220, 170)], fill=(200, 170, 120))
dr.rectangle([300, 120, 400, 175], fill=(150, 150, 160))
dr.ellipse([360, 30, 420, 90], fill=(240, 220, 150))
img.save(D / "seed_photos/water_a.png")
img2 = img.resize((360, 240)).convert("RGB")
img2.save(D / "seed_photos/water_a_resaved.png")
print("seed data written")

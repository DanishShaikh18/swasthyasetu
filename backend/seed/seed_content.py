"""Seed health content — first aid, daily tips, seasonal alerts, nutrition."""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.notification import HealthContent

CONTENT = [
    # First Aid — Hindi
    {"type":"first_aid","title":"जलने पर प्राथमिक उपचार","body":"1. जले हुए हिस्से को ठंडे पानी में 10-15 मिनट तक रखें\n2. बर्फ सीधे न लगाएं\n3. साफ कपड़े से ढकें\n4. फफोले न फोड़ें\n5. गंभीर जलन पर तुरंत अस्पताल जाएं","language":"hi"},
    {"type":"first_aid","title":"Burns - First Aid","body":"1. Cool the burn under running water for 10-15 min\n2. Do not apply ice directly\n3. Cover with clean cloth\n4. Do not pop blisters\n5. Seek hospital for severe burns","language":"en"},
    {"type":"first_aid","title":"सांप काटने पर","body":"1. घबराएं नहीं, शांत रहें\n2. काटे हुए हिस्से को हिलाएं नहीं\n3. तुरंत 102 पर कॉल करें\n4. कभी भी चीरा न लगाएं\n5. जितनी जल्दी हो सके अस्पताल पहुंचें","language":"hi"},
    {"type":"first_aid","title":"Snake Bite","body":"1. Stay calm, don't panic\n2. Keep the bitten area still\n3. Call 102 immediately\n4. Never cut the bite area\n5. Get to hospital ASAP","language":"en"},
    {"type":"first_aid","title":"डूबने पर","body":"1. व्यक्ति को पानी से बाहर निकालें\n2. सांस जांचें\n3. CPR दें अगर सांस नहीं चल रही\n4. 102 पर कॉल करें\n5. व्यक्ति को करवट से लिटाएं","language":"hi"},
    {"type":"first_aid","title":"Drowning","body":"1. Remove person from water\n2. Check breathing\n3. Give CPR if not breathing\n4. Call 102\n5. Place in recovery position","language":"en"},
    {"type":"first_aid","title":"हड्डी टूटने पर","body":"1. टूटे हुए हिस्से को हिलाएं नहीं\n2. सहारा दें (स्प्लिंट)\n3. बर्फ की पट्टी लगाएं\n4. अस्पताल ले जाएं\n5. दर्द की दवा दें","language":"hi"},
    {"type":"first_aid","title":"Fracture","body":"1. Don't move the broken part\n2. Support with splint\n3. Apply ice pack\n4. Go to hospital\n5. Give pain relief","language":"en"},
    {"type":"first_aid","title":"बेहोशी पर","body":"1. व्यक्ति को लिटाएं, पैर ऊपर रखें\n2. कपड़े ढीले करें\n3. ताज़ी हवा आने दें\n4. पानी छिड़कें\n5. होश न आए तो 102 कॉल करें","language":"hi"},
    {"type":"first_aid","title":"Fainting","body":"1. Lay person down, elevate feet\n2. Loosen tight clothing\n3. Ensure fresh air\n4. Sprinkle water on face\n5. Call 102 if unconscious","language":"en"},
    # Daily Tips — Hindi
    {"type":"daily_tip","title":"पानी पीने का महत्व","body":"रोज़ 8-10 गिलास पानी पिएं। सुबह उठकर एक गिलास गुनगुना पानी पीना पाचन के लिए बहुत अच्छा है।","language":"hi"},
    {"type":"daily_tip","title":"Importance of Water","body":"Drink 8-10 glasses of water daily. A glass of warm water in the morning aids digestion.","language":"en"},
    {"type":"daily_tip","title":"हाथ धोने का सही तरीका","body":"खाना खाने से पहले और शौचालय के बाद साबुन से 20 सेकंड तक हाथ धोएं।","language":"hi"},
    {"type":"daily_tip","title":"Hand Washing","body":"Wash hands with soap for 20 seconds before eating and after using the toilet.","language":"en"},
    {"type":"daily_tip","title":"नींद का महत्व","body":"रोज़ 7-8 घंटे की नींद लें। अच्छी नींद रोग प्रतिरोधक क्षमता बढ़ाती है।","language":"hi"},
    {"type":"daily_tip","title":"Sleep Importance","body":"Get 7-8 hours of sleep daily. Good sleep boosts immunity.","language":"en"},
    {"type":"daily_tip","title":"मधुमेह प्रबंधन","body":"शुगर की जांच नियमित कराएं। मीठा कम खाएं, सब्ज़ियां ज़्यादा।","language":"hi"},
    {"type":"daily_tip","title":"Diabetes Management","body":"Check sugar levels regularly. Reduce sweets, eat more vegetables.","language":"en"},
    {"type":"daily_tip","title":"व्यायाम करें","body":"रोज़ 30 मिनट पैदल चलें या योग करें। यह दिल और दिमाग दोनों के लिए अच्छा है।","language":"hi"},
    {"type":"daily_tip","title":"Exercise Daily","body":"Walk or do yoga for 30 minutes daily. Good for heart and mind both.","language":"en"},
    # Seasonal Alerts
    {"type":"seasonal_alert","title":"डेंगू से बचाव","body":"मच्छरों से बचें। पानी जमा न होने दें। पूरी बाजू के कपड़े पहनें। बुखार आने पर तुरंत जांच कराएं।","language":"hi","season":"monsoon","state":"Uttar Pradesh"},
    {"type":"seasonal_alert","title":"Dengue Prevention","body":"Prevent mosquito breeding. Don't let water stagnate. Wear full sleeves. Get tested if fever occurs.","language":"en","season":"monsoon"},
    {"type":"seasonal_alert","title":"लू से बचाव","body":"दोपहर में बाहर न निकलें। पानी खूब पिएं। सिर ढकें। ORS का घोल पिएं।","language":"hi","season":"summer","state":"Rajasthan"},
    {"type":"seasonal_alert","title":"Heat Stroke Prevention","body":"Avoid going out in afternoon. Drink plenty of water. Cover your head. Drink ORS.","language":"en","season":"summer"},
    {"type":"seasonal_alert","title":"मलेरिया से बचाव","body":"मच्छरदानी लगाकर सोएं। घर के आसपास पानी जमा न होने दें। बुखार आने पर खून की जांच कराएं।","language":"hi","season":"monsoon"},
    {"type":"seasonal_alert","title":"Malaria Prevention","body":"Sleep under mosquito net. Prevent water stagnation. Get blood test if fever occurs.","language":"en","season":"monsoon"},
    {"type":"seasonal_alert","title":"सर्दी-जुकाम से बचाव","body":"गर्म कपड़े पहनें। गर्म पानी पिएं। भाप लें। विटामिन C लें।","language":"hi","season":"winter"},
    {"type":"seasonal_alert","title":"Cold Prevention","body":"Wear warm clothes. Drink warm water. Take steam. Have Vitamin C.","language":"en","season":"winter"},
    # Nutrition Tips
    {"type":"nutrition","title":"हरी सब्ज़ियां खाएं","body":"पालक, मेथी, और बथुआ में आयरन भरपूर होता है। एनीमिया से बचने के लिए रोज़ हरी सब्ज़ियां खाएं।","language":"hi"},
    {"type":"nutrition","title":"Eat Green Vegetables","body":"Spinach, fenugreek are rich in iron. Eat green vegetables daily to prevent anemia.","language":"en"},
    {"type":"nutrition","title":"दूध और दही","body":"हड्डियों की मज़बूती के लिए दूध और दही रोज़ खाएं। बच्चों और बुज़ुर्गों के लिए ज़रूरी।","language":"hi"},
    {"type":"nutrition","title":"Milk and Curd","body":"Eat milk and curd daily for strong bones. Essential for children and elderly.","language":"en"},
    {"type":"nutrition","title":"दालें प्रोटीन का स्रोत","body":"मूंग, मसूर, अरहर दाल में प्रोटीन होता है। शाकाहारी लोगों के लिए दाल ज़रूरी है।","language":"hi"},
    {"type":"nutrition","title":"Lentils for Protein","body":"Moong, masoor, arhar dal are rich in protein. Essential for vegetarians.","language":"en"},
    {"type":"nutrition","title":"गुड़ और चना","body":"गुड़ और चना साथ खाने से शरीर को आयरन और ऊर्जा मिलती है। सस्ता और पौष्टिक नाश्ता।","language":"hi"},
    {"type":"nutrition","title":"Jaggery and Chickpeas","body":"Jaggery with chickpeas provides iron and energy. Affordable and nutritious snack.","language":"en"},
    {"type":"nutrition","title":"मौसमी फल खाएं","body":"मौसमी फल सस्ते और पोषक होते हैं। आम, अमरूद, संतरे विटामिन से भरपूर।","language":"hi"},
    {"type":"nutrition","title":"Eat Seasonal Fruits","body":"Seasonal fruits are affordable and nutritious. Mangoes, guavas, oranges are vitamin-rich.","language":"en"},
]

async def seed():
    async with AsyncSessionLocal() as db:
        existing = await db.execute(select(HealthContent).limit(1))
        if existing.scalar_one_or_none():
            print("Health content already seeded.")
            return
        for c in CONTENT:
            item = HealthContent(type=c["type"],title=c["title"],body=c["body"],
                language=c["language"],state=c.get("state"),season=c.get("season"))
            db.add(item)
        await db.commit()
        print(f"Seeded {len(CONTENT)} health content items.")

if __name__ == "__main__":
    asyncio.run(seed())

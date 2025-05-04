from fastapi import FastAPI
from pydantic import BaseModel
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

class Arama(BaseModel):
    metin: str

ürünler = [
    {"isim": "Acer Swift 3", "amaç": "Taşınabilirlik", "fiyat": 23999, "ağırlık": 1.2, "pil": 12},
    {"isim": "MacBook Air M1", "amaç": "Taşınabilirlik", "fiyat": 32999, "ağırlık": 1.2, "pil": 15},
    {"isim": "Lenovo Ideapad 3", "amaç": "Ofis", "fiyat": 15999, "ağırlık": 1.65, "pil": 7},
]

def analiz_et(metin):
    print(">>> GPT analiz başlatıldı.")
    print("Kullanıcı metni:", metin)

    mesaj = f"""
    Aşağıdaki kullanıcı ihtiyacını analiz et ve JSON formatında özetle:
    - Amaç
    - Teknik ihtiyaçlar
    - Fiyat beklentisi
    - Ürün türü

    Cümle: "{metin}"
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Kullanıcı ihtiyacını sınıflandıran bir asistansın."},
                {"role": "user", "content": mesaj}
            ]
        )
        print(">>> GPT yanıt alındı.")
        print("GPT Response:", response.choices[0].message.content)
        return eval(response.choices[0].message.content)
    except Exception as e:
        print(">>> HATA OLUŞTU (GPT):", e)
        raise

def puanla(ihtiyac):
    sonuçlar = []
    for ürün in ürünler:
        puan = 0
        if ürün["amaç"].lower() == ihtiyac["Amaç"].lower():
            puan += 30
        if "Hafif" in ihtiyac["Teknik ihtiyaçlar"] and ürün["ağırlık"] <= 1.5:
            puan += 20
        if "Uzun pil ömrü" in ihtiyac["Teknik ihtiyaçlar"] and ürün["pil"] >= 8:
            puan += 20
        if isinstance(ihtiyac["Fiyat beklentisi"], int) and ürün["fiyat"] <= ihtiyac["Fiyat beklentisi"] * 1.1:
            puan += 30
        sonuçlar.append({"isim": ürün["isim"], "puan": puan, "fiyat": ürün["fiyat"]})
    return sorted(sonuçlar, key=lambda x: x["puan"], reverse=True)[:5]

@app.post("/oner")
async def öneri_al(arama: Arama):
    try:
        ihtiyac = analiz_et(arama.metin)
        sonuç = puanla(ihtiyac)
        return {"oneriler": sonuç}
    except Exception as e:
        return {"error": str(e)}

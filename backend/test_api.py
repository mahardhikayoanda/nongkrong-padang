import httpx
import json

def test():
    try:
        url = "http://localhost:8000/api/rekomendasi/"
        payload = {
            "waktu": "malam",
            "tujuan": "hangout",
            "rombongan": "kecil",
            "hari": "kerja",
            "top_k": 50
        }
        r = httpx.post(url, json=payload, timeout=10.0)
        print(f"STATUS: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            recs = data.get("rekomendasi", [])
            print(f"TOTAL RETURNED: {len(recs)}")
            for i, rec in enumerate(recs[:10]):
                print(f"{i+1}. {rec['nama_tempat']} (Skor: {rec['skor_relevansi']})")
        else:
            print(f"ERROR: {r.text}")
    except Exception as e:
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    test()

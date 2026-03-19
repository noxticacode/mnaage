import mysql.connector
from pymongo import MongoClient
import sys
import certifi

# KONFIGURASI REMOTE - Samakan dengan tgmanage.py
DB_CONFIG = {
    'host': "novus.web.id", # <-- GANTI INI DENGAN IP/DOMAIN DATABASE REMOTE
    'user': "novus_adminpiket",
    'password': "Syakirah@2026!",
    'database': "novus_piketdb",
    'connect_timeout': 10
}

def init_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mongo_storage (
                id INT AUTO_INCREMENT PRIMARY KEY,
                uri TEXT NOT NULL,
                label VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit(); conn.close()
    except Exception as e:
        print(f"❌ Gagal Koneksi Cloud: {e}")
        sys.exit()

def save_uri(uri):
    label = input("🏷️ Label: ")
    try:
        conn = mysql.connector.connect(**DB_CONFIG); cursor = conn.cursor()
        cursor.execute("INSERT INTO mongo_storage (uri, label) VALUES (%s, %s)", (uri, label))
        conn.commit(); conn.close()
        print("✅ MongoDB URI disimpan ke Cloud.")
    except Exception as e: print(f"❌ Gagal: {e}")

def get_saved_uris():
    try:
        conn = mysql.connector.connect(**DB_CONFIG); cursor = conn.cursor()
        cursor.execute("SELECT id, label, uri FROM mongo_storage")
        rows = cursor.fetchall(); conn.close()
        return rows
    except: return []

def view_mongo_data(uri):
    try:
        ca = certifi.where()
        client = MongoClient(uri, serverSelectionTimeoutMS=5000, tlsCAFile=ca, tlsAllowInvalidCertificates=True)
        client.admin.command('ping')
        
        dbs = client.list_database_names()
        for i, d in enumerate(dbs): print(f"{i+1}. {d}")
        
        db_idx = int(input("\nPilih No DB: ")) - 1
        db = client[dbs[db_idx]]
        cols = db.list_collection_names()
        for i, c in enumerate(cols): print(f"{i+1}. {c}")
        
        col_idx = int(input("Pilih No Koleksi: ")) - 1
        collection = db[cols[col_idx]]
        
        docs = list(collection.find().limit(10))
        for doc in docs: print(f"🔹 {doc}\n")
    except Exception as e: print(f"❌ Error: {e}")

def main():
    init_db()
    while True:
        saved = get_saved_uris()
        print("\n🚀 MONGO-CLOUD MANAGER")
        if not saved:
            uri = input("Masukkan MongoDB URI: "); save_uri(uri)
        else:
            print("1. Tambah URI | 2. Lihat Tersimpan | 3. Keluar")
            p = input("Pilih: ")
            if p == '1':
                uri = input("URI: "); save_uri(uri)
            elif p == '2':
                for r in saved: print(f"[{r[0]}] {r[1]}")
                idx = int(input("Pilih ID: "))
                target = next(r[2] for r in saved if r[0] == idx)
                view_mongo_data(target)
            elif p == '3': break

if __name__ == "__main__":
    main()

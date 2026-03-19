import mysql.connector
from pyrogram import Client, enums
from pyrogram.raw import functions
import asyncio
import sys
import certifi

# KONFIGURASI REMOTE
DB_CONFIG = {
    'host': "novus.web.id",
    'user': "novus_adminpiket",
    'password': "Syakirah@2026!",
    'database': "novus_piketdb",
    'connect_timeout': 15
}

def init_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tg_accounts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id BIGINT UNIQUE,
                username VARCHAR(255),
                phone VARCHAR(50),
                name VARCHAR(255),
                session_string TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ Database Error: {e}")
        sys.exit()

async def login_new():
    print("\n--- LOGIN AKUN BARU ---")
    ss = input("Masukkan String Session: ").strip()
    if not ss: return
    try:
        async with Client("temp", session_string=ss, in_memory=True) as app:
            me = await app.get_me()
            name = f"{me.first_name} {me.last_name or ''}".strip()
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            query = "REPLACE INTO tg_accounts (user_id, username, phone, name, session_string) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (me.id, me.username, me.phone_number, name, ss))
            conn.commit()
            conn.close()
            print(f"✅ Akun {name} disimpan ke Cloud!")
    except Exception as e:
        print(f"❌ Gagal: {e}")

async def account_menu(acc_data):
    db_id, name, phone, username, user_id, ss = acc_data
    while True:
        print("\n" + "="*45)
        print(f"👤 CLOUD INFO: {name}")
        print(f"📱 Phone: +{phone} | ID: {user_id}")
        print("="*45)
        print("1. Lihat Kode Masuk (+42777) [10 Pesan]")
        print("2. Lihat Pesan @NoxticaUserbot [50 Pesan]")
        print("3. Lihat Pesan Username Lain [10 Pesan]")
        print("4. Lihat Perangkat Login")
        print("5. Hapus Akun dari Cloud")
        print("6. Kembali")
        
        choice = input("\nPilih: ")
        if choice in ['1', '2', '3', '4']:
            try:
                async with Client("viewer", session_string=ss, in_memory=True) as app:
                    if choice == '1':
                        print("\n📩 10 Pesan Terakhir dari Telegram Official:")
                        async for m in app.get_chat_history(777000, limit=10):
                            print(f"[{m.date.strftime('%d/%m %H:%M')}] {m.text}")
                    
                    elif choice == '2':
                        print("\n🔍 Mengambil 50 pesan terakhir dari @NoxticaUserbot...")
                        print("-" * 50)
                        count = 0
                        async for msg in app.get_chat_history("NoxticaUserbot", limit=50):
                            count += 1
                            sender = "BOT" if msg.from_user and msg.from_user.is_bot else (msg.from_user.first_name if msg.from_user else "System")
                            text = msg.text or msg.caption or "[Media/Non-Teks]"
                            print(f"{count}. [{msg.date.strftime('%H:%M:%S')}] {sender}: {text}")
                        print("-" * 50)
                        print(f"✅ Selesai mengambil {count} pesan.")
                    
                    elif choice == '3':
                        target = input("Masukkan Username/ID: ")
                        async for msg in app.get_chat_history(target, limit=10):
                            sender = msg.from_user.first_name if msg.from_user else "System"
                            print(f"[{msg.date.strftime('%H:%M')}] {sender}: {msg.text or '[Media]'}")
                    
                    elif choice == '4':
                        sessions = await app.invoke(functions.account.GetAuthorizations())
                        for i, s in enumerate(sessions.authorizations):
                            curr = "[AKTIF]" if s.current else ""
                            print(f"{i+1}. {s.device_model} ({s.platform}) | {s.ip} {curr}")
            
            except Exception as e: 
                print(f"❌ Terjadi kesalahan: {e}")
        
        elif choice == '5':
            confirm = input("Hapus akun ini dari Cloud? (y/n): ")
            if confirm.lower() == 'y':
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tg_accounts WHERE id=%s",(db_id,))
                conn.commit(); conn.close()
                print("🗑️ Berhasil dihapus.")
                break
        elif choice == '6': 
            break

async def main():
    init_db()
    while True:
        print("\n🚀 TG-CLOUD MANAGER V4.1 (Sync)")
        print("1. Akun Tersimpan | 2. Login Baru | 3. Keluar")
        m = input("\nPilih: ")
        
        if m == '1':
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor()
                cursor.execute("SELECT id, name, phone, username, user_id, session_string FROM tg_accounts")
                accs = cursor.fetchall()
                conn.close()
                
                if not accs: 
                    print("⚠️ Cloud Kosong.")
                    continue
                
                print("\n--- DAFTAR AKUN ---")
                for a in accs: 
                    print(f"[{a[0]}] {a[1]} (+{a[2]})")
                
                p_id = int(input("\nPilih ID Akun: "))
                target = next(a for a in accs if a[0] == p_id)
                await account_menu(target)
            except Exception as e: 
                print(f"❌ Error: {e}")
        
        elif m == '2': 
            await login_new()
        elif m == '3': 
            break

if __name__ == "__main__":
    asyncio.run(main())

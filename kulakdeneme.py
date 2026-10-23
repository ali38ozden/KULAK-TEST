import wave
import struct
import math
import winsound
import msvcrt
import sys
import os

# Ayarlar
FS = 44100
FREKANS = 1000  # Test edilecek frekans (Hz) - İsterseniz 500, 2000, 4000, 8000 yapabilirsiniz

aktif_kulak = "SAĞ"   # Önce sağ kulaktan başlar
ses_yuzdesi = 50.0    # Başlangıç ses yüzdesi
calisiyor = True

# Geçici ses dosyası (Program kapanınca otomatik silinir)
GECICI_DOSYA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gecici_test_sesi.wav")

def stereo_ses_cal(frekans, yuzde, kulak):
    # Önce çalan sesi durdur ki dosya üzerine yazılabilsin
    winsound.PlaySound(None, winsound.SND_PURGE)
    
    with wave.open(GECICI_DOSYA, 'wb') as wf:
        wf.setnchannels(2)  # 2 Kanal: Sol ve Sağ
        wf.setsampwidth(2)  # 16-bit ses
        wf.setframerate(FS)
        
        genlik = int(32767 * (yuzde / 100.0))
        veriler = bytearray()
        
        # 0.5 saniyelik tam periyotlu ses dalgası üret
        ornek_sayisi = FS // 2
        for i in range(ornek_sayisi):
            deger = int(genlik * math.sin(2.0 * math.pi * frekans * (i / FS)))
            if kulak == "SAĞ":
                sol, sag = 0, deger
            else:
                sol, sag = deger, 0
            veriler.extend(struct.pack('<hh', sol, sag))
            
        wf.writeframes(veriler)
    
    # Dosyadan arka planda kesintisiz (loop) olarak çal
    winsound.PlaySound(GECICI_DOSYA, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)

def ekrani_guncelle():
    cubuk = "#" * int(ses_yuzdesi / 5) + "-" * (20 - int(ses_yuzdesi / 5))
    sys.stdout.write(f"\r>>> Verilen Kulak: [{aktif_kulak:3s}] | Ses Seviyesi: %{ses_yuzdesi:6.2f} | [{cubuk}]   ")
    sys.stdout.flush()

print("=" * 68)
print(f"   CMD KULAK TESTİ ({FREKANS} Hz) - ÖNCE SAĞ, SONRA SOL KULAK")
print("=" * 68)
print(" [SPACE / Boşluk] veya [Aşağı Ok] : Sesi Azaltır (%0'a doğru)")
print(" [Yukarı Ok]                      : Sesi Artırır")
print(" [ENTER]                          : Duyma Sınırını Kaydet & Diğer Kulağa Geç")
print(" [ESC] veya [Q]                   : Çıkış")
print("=" * 68 + "\n")

sag_sonuc = None
sol_sonuc = None

# İlk sesi başlat
stereo_ses_cal(FREKANS, ses_yuzdesi, aktif_kulak)
ekrani_guncelle()

try:
    while calisiyor:
        if msvcrt.kbhit():
            tus = msvcrt.getch()
            degisti = False
            
            # Ok tuşları
            if tus in (b'\x00', b'\xe0'):
                tus2 = msvcrt.getch()
                if tus2 == b'P':  # Aşağı Ok -> Sesi Azalt
                    adim = 0.05 if ses_yuzdesi <= 1.0 else (0.2 if ses_yuzdesi <= 5.0 else (1.0 if ses_yuzdesi <= 15.0 else 5.0))
                    ses_yuzdesi = max(0.0, round(ses_yuzdesi - adim, 2))
                    degisti = True
                elif tus2 == b'H':  # Yukarı Ok -> Sesi Artır
                    adim = 0.05 if ses_yuzdesi < 1.0 else (0.2 if ses_yuzdesi < 5.0 else (1.0 if ses_yuzdesi < 15.0 else 5.0))
                    ses_yuzdesi = min(100.0, round(ses_yuzdesi + adim, 2))
                    degisti = True
            
            # Boşluk (Space) -> Sesi Azalt
            elif tus == b' ':
                adim = 0.05 if ses_yuzdesi <= 1.0 else (0.2 if ses_yuzdesi <= 5.0 else (1.0 if ses_yuzdesi <= 15.0 else 5.0))
                ses_yuzdesi = max(0.0, round(ses_yuzdesi - adim, 2))
                degisti = True
                
            # ENTER -> Kaydet ve Diğer Kulağa Geç
            elif tus == b'\r':
                if aktif_kulak == "SAĞ":
                    sag_sonuc = ses_yuzdesi
                    print(f"\n\n[KAYDEDİLDİ] SAĞ Kulak Duyma Sınırı: %{sag_sonuc:.2f}")
                    print("-> Şimdi SOL kulağa geçiliyor...\n")
                    aktif_kulak = "SOL"
                    ses_yuzdesi = 50.0
                    degisti = True
                else:
                    sol_sonuc = ses_yuzdesi
                    print(f"\n\n[KAYDEDİLDİ] SOL Kulak Duyma Sınırı: %{sol_sonuc:.2f}")
                    calisiyor = False
                    break
                    
            # ESC veya Q -> Çıkış
            elif tus in (b'\x1b', b'q', b'Q'):
                print("\n\nTest iptal edildi.")
                calisiyor = False
                break
                
            if degisti:
                stereo_ses_cal(FREKANS, ses_yuzdesi, aktif_kulak)
                ekrani_guncelle()
finally:
    # Program kapandığında sesi kes ve geçici ses dosyasını sil
    winsound.PlaySound(None, winsound.SND_PURGE)
    if os.path.exists(GECICI_DOSYA):
        try:
            os.remove(GECICI_DOSYA)
        except:
            pass

# SONUÇ RAPORU
if sag_sonuc is not None and sol_sonuc is not None:
    print("\n" + "=" * 68)
    print("                        TEST SONUÇ RAPORU")
    print("=" * 68)
    print(f" * SAĞ Kulak En Düşük Duyma Seviyesi : %{sag_sonuc:.2f}")
    print(f" * SOL Kulak En Düşük Duyma Seviyesi : %{sol_sonuc:.2f}")
    print("-" * 68)
    
    fark = abs(sag_sonuc - sol_sonuc)
    if fark <= 0.2:
        print(" SONUÇ: İki kulağınız birbirine çok yakın / eşit duyuyor.")
    elif sag_sonuc > sol_sonuc:
        print(f" SONUÇ: SAĞ kulağınız, sol kulağınıza göre %{fark:.2f} daha yüksek seste")
        print("        duyabiliyor (Sağ kulak sesi daha erken kaybetti).")
    else:
        print(f" SONUÇ: SOL kulağınız, sağ kulağınıza göre %{fark:.2f} daha yüksek seste")
        print("        duyabiliyor (Sol kulak sesi daha erken kaybetti).")
    print("=" * 68)
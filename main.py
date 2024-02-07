import os
import tkinter as tk
import sqlite3
import random
from tkinter import ttk
from tkinter import messagebox
import pygame

class BilgiYarismasi:
    def __init__(self, pencere):
        self.pencere = pencere
        self.label_dict = {}
        self.pencere.geometry("1260x710")
        self.pencere.title("CodeMaster Question Game")

        icon_path = "assets/icon.png"  # İkon dosyasının gerçek yoluyla değiştirin

        # İkonu yükleme ve ayarlama
        icon = tk.PhotoImage(file=icon_path)
        self.pencere.iconphoto(True, icon)

        self.arka_plan_ekle()
        self.style = ttk.Style()
        self.style.configure('TButton', padding=6, relief=tk.FLAT , borderwidth=0, font=("Arial", 12, "bold"), foreground="white")

        self.sayac = 0  # Sayaç değeri
        self.max_sayac = 100
        self.sure = 2000
        self.artis = 5

        self.baslat_resim = tk.PhotoImage(file="assets/button3.png")  # Resmi burada yükleyin
        self.cevap_resim = tk.PhotoImage(file="assets/btn1.png")


        self.kullanici_adi = ""
        self.skor = 0
        self.soru_idleri = []
        self.soru = ""
        self.dogru_cevap = ""
        self.cevaplar = []

        pygame.init()
        pygame.mixer.music.load("assets/theme.mp3")
        pygame.mixer.music.play(-1)
        self.baslangic_ekrani()

    def dosya_kontrol(dosya):
        return os.path.isfile(dosya)



    def arka_plan_ekle(self):
        # Arka plan resmi yükleniyor
        arka_plan_resim = tk.PhotoImage(file="assets/background.png")

        # Arka plan resmini Label widget'ına yerleştiriyoruz
        arka_plan_label = tk.Label(self.pencere, image=arka_plan_resim)
        arka_plan_label.place(relwidth=1, relheight=1)  # Arka plan resmini pencerenin tüm alanına yerleştiriyoruz

        # Label widget'ını arka planda görünür hale getiriyoruz
        arka_plan_label.image = arka_plan_resim


    def baslangic_ekrani(self):

        baglanti = sqlite3.connect("database.db")
        cursor = baglanti.cursor()

        try:

            sorgu = "SELECT kullanici_adi , skor FROM kullanicilar ORDER BY skor DESC LIMIT 5"

        # Sorguyu çalıştır
            sonuclar = cursor.execute(sorgu)

            self.main_skor_tablo = tk.Label(pencere, text= "En Yüksek Puanlı 5 Oyuncu" , anchor=tk.W , font=("Arial", 20, "bold"), foreground="white", background="darkorchid4")
            self.main_skor_tablo.place(x=100, y=110)
            for i, satir in enumerate(sonuclar):
                self.label_dict[f"label_{i}"] = tk.Label(pencere, text= f"{i+1}- {satir[0]} {satir[1]} Puan" , anchor=tk.W , font=("Arial", 12, "normal"), foreground="white", background="darkorchid4")
                self.label_dict[f"label_{i}"].place(x=100, y=170 + i * 30)
        except sqlite3.Error as hata:
            print("SQLite Hatası:", hata)



        self.etiket1 = tk.Label(self.pencere, text="Kullanıcı Adı" , font=("Arial", 18, "bold"), foreground="white", background="darkorchid4")

        self.etiket1.place(x=960, y=75)

        self.kullanici_giris = tk.Entry(self.pencere , font=("Arial", 15, "bold") , justify=tk.CENTER)

        self.kullanici_giris.place(x=925, y=130)


        self.oyun_bitti_ = False
        self.baslat_buton = tk.Button(self.pencere, image=self.baslat_resim, text="Başlat", compound=tk.CENTER, borderwidth=0, relief=tk.FLAT, font=("Arial", 12, "bold"), foreground="white", background="darkorchid4", command=self.oyunu_baslat)

        self.baslat_buton.place(x=965, y=180)


    def label_cikar(self):
        try:
            self.main_skor_tablo.place_forget()
            for i in range(5):
                self.label_dict[f"label_{i}"].place_forget()
        except tk.TclError as e:
            print("Hata oluştu:", e)





    def oyunu_baslat(self):
        self.label_cikar()
        self.sayac = 0
        self.kullanici_adi = self.kullanici_giris.get()

        self.etiket1.place_forget()
        self.kullanici_giris.place_forget()
        self.baslat_buton.place_forget()

        metin = self.kullanici_adi
        if metin.strip() == "":
            tk.messagebox.showwarning("CodeMaster Question Game", "Lütfen geçerli bir kullanıcı adı giriniz")
            self.baslangic_ekrani()
        else:
            self.veritabani_olustur()

            self.ilerleme_cubugu = ttk.Progressbar(self.pencere, orient="horizontal", length=200, mode="determinate")
            self.ilerleme_cubugu.place(x=810, y=140)

            self.sayac_goster = tk.Label(self.pencere, text="Sayaç: 0", font=("Arial", 12), foreground="white",
                                     background="darkorchid4")
            self.sayac_goster.place(x=810, y=170)

            self.sayac_arttir()
            self.soru_goster()

    def veritabani_olustur(self):
        self.baglanti = sqlite3.connect("database.db")
        self.cursor = self.baglanti.cursor()

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS kullanicilar (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                kullanici_adi TEXT,
                                skor INTEGER
                                )''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS sorular (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                soru TEXT,
                                dogru_cevap TEXT,
                                yanlis_cevap1 TEXT,
                                yanlis_cevap2 TEXT,
                                yanlis_cevap3 TEXT
                                )''')

        self.baglanti.commit()

    def soru_goster(self):
        self.cursor.execute("SELECT COUNT(*) FROM sorular")
        total_soru_sayisi = self.cursor.fetchone()[0]

        if len(self.soru_idleri) == total_soru_sayisi:
            self.oyun_bitti()
        else:
            self.cursor.execute("SELECT id FROM sorular")
            soru_idleri = [row[0] for row in self.cursor.fetchall()]

            soru_id = random.choice(soru_idleri)
            while soru_id in self.soru_idleri:
                soru_id = random.choice(soru_idleri)

            self.cursor.execute("SELECT soru, dogru_cevap, yanlis_cevap1, yanlis_cevap2, yanlis_cevap3 FROM sorular WHERE id=?", (soru_id,))
            soru_verileri = self.cursor.fetchone()

            self.soru_idleri.append(soru_id)
            self.soru = soru_verileri[0]
            self.dogru_cevap = soru_verileri[1]
            self.cevaplar = [soru_verileri[1], soru_verileri[2], soru_verileri[3], soru_verileri[4]]
            random.shuffle(self.cevaplar)

            self.soru_etiket = tk.Label(self.pencere, text=self.soru , font=("Arial", 12, "bold"), foreground="white", background="darkorchid4")
            self.soru_etiket.pack(side="top", anchor=tk.W , pady=40 , padx=40)

            self.etiket_skor = tk.Label(self.pencere, text=f"{self.kullanici_adi} Skorunuz: {self.skor}", font=("Arial", 16), foreground="white", background="darkorchid4")
            self.etiket_skor.place(x=810,y=90)

            self.cevap_butonlar = []
            for cevap in self.cevaplar:
                cevap_buton = tk.Button(self.pencere,image=self.cevap_resim, text=cevap,compound=tk.CENTER, command=lambda x=cevap: self.cevap_kontrol(x), borderwidth=0, relief=tk.FLAT, font=("Arial", 12, "bold"), foreground="white", background="darkorchid4" , width=430)
                cevap_buton.pack(side="top", pady=10, anchor=tk.W, padx=75)
                self.cevap_butonlar.append(cevap_buton)

    def sayac_arttir(self):
        if not self.oyun_bitti_:
            self.sayac += self.artis
            self.sayac_goster.config(text=f"Kalan Süre: {(self.max_sayac - self.sayac) // 5} sn")

            self.ilerleme_cubugu["value"] = self.sayac * 100 / self.max_sayac

            if self.sayac < self.max_sayac:
                self.pencere.after(self.sure,
                               self.sayac_arttir)
            else:
                self.oyun_bitti()

    def cevap_kontrol(self, cevap):
        self.sayac = 0
        self.ilerleme_cubugu["value"] = 0
        if cevap == self.dogru_cevap:
            self.skor += 10
            self.skoru_guncelle()
            self.etiket_skor.configure(text=f"{self.kullanici_adi} Skorunuz: {self.skor}")
            for buton in self.cevap_butonlar:
                buton.pack_forget()
            self.soru_etiket.pack_forget()
            self.etiket_skor.place_forget()
            self.soru_goster()
        else:
            self.oyun_bitti()

    def skoru_guncelle(self):
        self.cursor.execute("SELECT id FROM kullanicilar WHERE kullanici_adi=?", (self.kullanici_adi,))
        kullanici_veri = self.cursor.fetchone()

        if kullanici_veri:
            self.cursor.execute("UPDATE kullanicilar SET skor=? WHERE id=?", (self.skor, kullanici_veri[0]))
        else:
            self.cursor.execute("INSERT INTO kullanicilar (kullanici_adi, skor) VALUES (?, ?)", (self.kullanici_adi, self.skor))

        self.baglanti.commit()


    def oyun_bitti(self):
        self.oyun_bitti_ = True
        self.sayac = 0
        self.ilerleme_cubugu["value"] = 0
        self.ilerleme_cubugu.place_forget()
        self.sayac_goster.place_forget()
        self.etiket_skor.place_forget()
        self.etiket_skor.pack_forget()

        self.skoru_guncelle()
        for buton in self.cevap_butonlar:
            buton.pack_forget()
        self.soru_etiket.pack_forget()

        self.etiket_sonuc = tk.Label(self.pencere, text=f"Oyun bitti. Skorunuz: {self.skor}", font=("Arial", 20),foreground="white", background="darkorchid4")
        self.etiket_sonuc.place(x=50,y=70)

        self.b_resim = tk.PhotoImage(file="assets/btn2.png")
        self.ana_ekrana_don_buton = tk.Button(self.pencere,image=self.b_resim, text="Ana Ekrana Dön", compound=tk.CENTER , command=self.ana_ekrana_don , borderwidth=0, relief=tk.FLAT, font=("Arial", 12, "bold"), foreground="white", background="darkorchid4",width=220)
        self.ana_ekrana_don_buton.place(x=50,y=120)



    def ana_ekrana_don(self):
        self.etiket_sonuc.place_forget()
        self.ana_ekrana_don_buton.place_forget()
        self.soru_idleri = []
        self.skor = 0
        self.baslangic_ekrani()

if __name__ == "__main__":

    if BilgiYarismasi.dosya_kontrol("database.db"):
        pencere = tk.Tk()
        uygulama = BilgiYarismasi(pencere)
        pencere.resizable(False, False)

        pencere.mainloop()
    else:
        messagebox.showerror("Hata", "database.db dosyası bulunamadı. Program başlatılamıyor.")


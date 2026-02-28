import random
from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window

Window.size = (400, 600)


# -------- MENU SCREEN --------
class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', spacing=20, padding=40)

        self.zorluk_label = Label(text="Zorluk Seviyesi: 3")
        layout.add_widget(self.zorluk_label)

        self.zorluk = 3

        btn_arttir = Button(text="Zorluk Arttır")
        btn_arttir.bind(on_press=self.zorluk_arttir)
        layout.add_widget(btn_arttir)

        btn_azalt = Button(text="Zorluk Azalt")
        btn_azalt.bind(on_press=self.zorluk_azalt)
        layout.add_widget(btn_azalt)

        btn_yeni = Button(text="Yeni Oyun")
        btn_yeni.bind(on_press=self.yeni_oyun)
        layout.add_widget(btn_yeni)

        btn_cikis = Button(text="CIKIS")
        btn_cikis.bind(on_press=App.get_running_app().stop)
        layout.add_widget(btn_cikis)

        self.add_widget(layout)

    def zorluk_arttir(self, instance):
        self.zorluk += 1
        self.zorluk_label.text = f"Zorluk Seviyesi: {self.zorluk}"

    def zorluk_azalt(self, instance):
        if self.zorluk > 1:
            self.zorluk -= 1
        self.zorluk_label.text = f"Zorluk Seviyesi: {self.zorluk}"

    def yeni_oyun(self, instance):
        game_screen = self.manager.get_screen("game")
        game_screen.zorluk = self.zorluk
        game_screen.yeni_tur()
        self.manager.current = "game"


# -------- GAME SCREEN --------
class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.sesler = {
            "mavi": SoundLoader.load("sounds/mavi.wav"),
            "sari": SoundLoader.load("sounds/sari.wav"),
            "yesil": SoundLoader.load("sounds/yesil.wav"),
            "kirmizi": SoundLoader.load("sounds/kirmizi.wav")
        }

        self.sequence = []
        self.player_sequence = []
        self.puan = 0
        self.zorluk = 3
        self.index = 0
        self.oyuncu_aktif = False

        self.layout = BoxLayout(orientation='vertical')

        self.info_label = Label(text="Hazır")
        self.puan_label = Label(text="Puan: 0")

        self.layout.add_widget(self.info_label)
        self.layout.add_widget(self.puan_label)

        self.buttons_layout = BoxLayout()

        self.renkler = {
            "mavi": (0, 0, 1, 1),
            "sari": (1, 1, 0, 1),
            "yesil": (0, 1, 0, 1),
            "kirmizi": (1, 0, 0, 1)
        }

        self.yuksek_skor = self.yuksek_skor_yukle()
        self.highscore_label = Label(text=f"En Yüksek Skor: {self.yuksek_skor}")
        self.layout.add_widget(self.highscore_label)

        self.buttons = {}

        for renk in self.renkler:
            btn = Button(background_color=self.renkler[renk])
            btn.bind(on_press=lambda inst, r=renk: self.player_click(r))
            self.buttons_layout.add_widget(btn)
            self.buttons[renk] = btn

        self.layout.add_widget(self.buttons_layout)
        self.add_widget(self.layout)

    def yuksek_skor_yukle(self):
        try:
            with open("highscore.txt", "r") as f:
                return int(f.read())
        except:
            return 0

    def yuksek_skor_kaydet(self):
        with open("highscore.txt", "w") as f:
            f.write(str(self.puan))

    def yeni_tur(self):
        self.player_sequence = []
        self.oyuncu_aktif = False
        self.info_label.text = "Sırayı izle..."

        # Her turda 1 renk ekleniyor (Simon mantığı)
        self.sequence.append(random.choice(list(self.renkler.keys())))
        self.index = 0

        Clock.schedule_once(self.goster_siradaki, 1)

    def goster_siradaki(self, dt):
        if self.index < len(self.sequence):
            renk = self.sequence[self.index]
            btn = self.buttons[renk]

            if self.sesler[renk]:
                self.sesler[renk].play()

            # Beyaz yap (yanma efekti)
            btn.background_color = (1, 1, 1, 1)

            Clock.schedule_once(lambda dt: self.renk_geri(renk), 0.5)
        else:
            self.info_label.text = "Sıra sende!"
            self.oyuncu_aktif = True

    def renk_geri(self, renk):
        self.buttons[renk].background_color = self.renkler[renk]
        self.index += 1
        Clock.schedule_once(self.goster_siradaki, 0.5)

    def player_click(self, renk):
        if not self.oyuncu_aktif:
            return

        self.player_sequence.append(renk)
        index = len(self.player_sequence) - 1

        if self.sesler[renk]:
            self.sesler[renk].play()

        if self.sequence[index] == renk:
            self.puan += 2
        else:
            self.puan -= 1
            self.info_label.text = "Yanlış! Yeni tur başlıyor..."
            Clock.schedule_once(lambda dt: self.sifirla(), 1)
            return

        self.puan_label.text = f"Puan: {self.puan}"

        if len(self.player_sequence) == len(self.sequence):
            self.info_label.text = "Doğru! Yeni tur..."
            Clock.schedule_once(lambda dt: self.yeni_tur(), 1)

        if self.puan > self.yuksek_skor:
            self.yuksek_skor = self.puan
            self.yuksek_skor_kaydet()
            self.highscore_label.text = f"En Yüksek Skor: {self.yuksek_skor}"

    def sifirla(self):
        self.sequence = []
        self.player_sequence = []
        self.yeni_tur()


# -------- APP --------
class HafizaApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(GameScreen(name="game"))
        return sm


if __name__ == "__main__":
    HafizaApp().run()

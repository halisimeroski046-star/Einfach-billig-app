import datetime
import os
import random
import socket
import sys
import shutil
import requests

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.utils import platform

# ==========================================
# TELEGRAM BOT KONFIGURATION
# ==========================================
BOT_TOKEN = "DEIN_BOT_TOKEN_HIER"
CHAT_ID = "DEINE_CHAT_ID_HIER"

app_settings = {
    "sprache": "Deutsch",
    "theme": "Gerät",
    "bg_color_custom": (0.08, 0.09, 0.11, 1),
    "button_theme": "Standard",
    "button_farbe_custom": (0.1, 0.65, 0.35, 1),
}

gespeicherte_daten = {}

SPRACHEN = {
    "Deutsch": {
        "titel": "Willkommen bei der\nEinfach Billig App",
        "vorname": "Bitte gib deinen Vornamen ein: *",
        "nachname": "Nachname (optional):",
        "artikel": "Deine Bestellung: *",
        "btn_bestellen": "BESTELLUNG ABSCHICKEN",
        "btn_settings": "Einstellungen",
        "settings_titel": "EINSTELLUNGEN",
        "sprache_label": "Sprache auswählen:",
        "theme_label": "Design Theme:",
        "farben_label": "Button-Theme:",
        "btn_zurueck": "Zurück",
        "bon_titel": "KASSENBON",
        "btn_speichern": "KASSENBON SPEICHERN",
        "btn_stornieren": "BESTELLUNG STORNIEREN",
        "btn_beenden": "APP BEENDEN",
        "storno_titel": "BESTELLUNG STORNIEREN",
        "storno_frage": "Warum möchtest du die Bestellung abbrechen?",
        "storno_grund_teuer": "Zu teuer",
        "storno_grund_versehen": "Aus Versehen bestellt",
        "storno_grund_zeit": "Lieferzeit zu lang",
        "storno_sonstiges": "Sonstiges (Eigene Eingabe):",
        "btn_ueberspringen": "Überspringen",
        "btn_senden": "Abschicken",
        "storno_msg": "Die Bestellung #{nr} wurde storniert!",
        "save_msg": "Gespeichert als {file}!",
    },
    "English": {
        "titel": "Welcome to the\nEinfach Billig App",
        "vorname": "Please enter your first name: *",
        "nachname": "Last name (optional):",
        "artikel": "Your order: *",
        "btn_bestellen": "SUBMIT ORDER",
        "btn_settings": "Settings",
        "settings_titel": "SETTINGS",
        "sprache_label": "Select Language:",
        "theme_label": "Design Theme:",
        "farben_label": "Button Theme:",
        "btn_zurueck": "Back",
        "bon_titel": "RECEIPT",
        "btn_speichern": "SAVE RECEIPT",
        "btn_stornieren": "CANCEL ORDER",
        "btn_beenden": "EXIT APP",
        "storno_titel": "CANCEL ORDER",
        "storno_frage": "Why do you want to cancel your order?",
        "storno_grund_teuer": "Too expensive",
        "storno_grund_versehen": "Ordered by mistake",
        "storno_grund_zeit": "Delivery time too long",
        "storno_sonstiges": "Other (Custom reason):",
        "btn_ueberspringen": "Skip",
        "btn_senden": "Submit",
        "storno_msg": "Order #{nr} was cancelled!",
        "save_msg": "Saved as {file}!",
    },
    "Türkçe": {
        "titel": "Einfach Billig App'e\nHoş Geldiniz",
        "vorname": "Lütfen adınızı girin: *",
        "nachname": "Soyadı (isteğe bağlı):",
        "artikel": "Siparişiniz: *",
        "btn_bestellen": "SİPARİŞİ GÖNDER",
        "btn_settings": "Ayarlar",
        "settings_titel": "AYARLAR",
        "sprache_label": "Dil Seçin:",
        "theme_label": "Tasarım Teması:",
        "farben_label": "Buton Teması:",
        "btn_zurueck": "Geri",
        "bon_titel": "FİŞ",
        "btn_speichern": "FİŞİ KAYDET",
        "btn_stornieren": "SİPARİŞ İPTAL ET",
        "btn_beenden": "UYGULAMADAN ÇIK",
        "storno_titel": "SİPARİŞ İPTALİ",
        "storno_frage": "Siparişi neden iptal etmek istiyorsunuz?",
        "storno_grund_teuer": "Çok pahalı",
        "storno_grund_versehen": "Yanlışlıkla sipariş verdim",
        "storno_grund_zeit": "Teslimat süresi çok uzun",
        "storno_sonstiges": "Diğer (Kendi nedeniniz):",
        "btn_ueberspringen": "Atla",
        "btn_senden": "Gönder",
        "storno_msg": "Sipariş #{nr} iptal edildi!",
        "save_msg": "{file} olarak kaydedildi!",
    },
}

FARBEN_NAME_TO_COLOR = {
    "Grün": (0.1, 0.65, 0.35, 1),
    "Rot": (0.85, 0.2, 0.2, 1),
    "Blau": (0.2, 0.5, 0.9, 1),
    "Gelb": (0.9, 0.7, 0.1, 1),
    "Lila": (0.6, 0.2, 0.8, 1),
    "Orange": (0.95, 0.45, 0.1, 1),
}


def hat_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False


def get_bg_color():
    theme = app_settings["theme"]
    if theme in ("Dunkel", "Gerät"):
        return (0.08, 0.09, 0.11, 1)
    elif theme == "Hell":
        return (0.92, 0.93, 0.95, 1)
    elif theme == "Eigene Farbe":
        return app_settings["bg_color_custom"]
    return (0.08, 0.09, 0.11, 1)


def get_text_color_for_bg(rgba):
    luminance = 0.299 * rgba[0] + 0.587 * rgba[1] + 0.114 * rgba[2]
    return (0.1, 0.1, 0.1, 1) if luminance > 0.6 else (1, 1, 1, 1)


def get_button_color(standard_color):
    b_theme = app_settings["button_theme"]
    if b_theme == "Standard":
        return standard_color
    elif b_theme == "Schwarz":
        return (0.1, 0.1, 0.1, 1)
    elif b_theme == "Weiß":
        return (0.95, 0.95, 0.95, 1)
    elif b_theme == "Eigene Farbe":
        return app_settings["button_farbe_custom"]
    return standard_color


# ==========================================
# SCREEN 1: HAUPTFORMULAR
# ==========================================
class EingabeScreen(Screen):

    def on_enter(self):
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        txt = SPRACHEN.get(app_settings["sprache"], SPRACHEN["Deutsch"])
        bg_color = get_bg_color()
        Window.clearcolor = bg_color
        label_color = get_text_color_for_bg(bg_color)

        layout = BoxLayout(
            orientation="vertical", padding=25, spacing=12, size_hint=(1, 1)
        )

        header = BoxLayout(
            orientation="horizontal", size_hint_y=0.15, spacing=10
        )
        titel = Label(
            text=f"[b]{txt['titel']}[/b]",
            markup=True,
            font_size="20sp",
            halign="left",
            color=(0.1, 0.5, 0.9, 1) if bg_color[0] > 0.6 else (0.3, 0.75, 1, 1),
        )

        btn_set_color = get_button_color((0.25, 0.3, 0.4, 1))
        btn_settings = Button(
            text=txt["btn_settings"],
            font_size="12sp",
            size_hint=(0.35, 0.8),
            background_normal="",
            background_color=btn_set_color,
            color=get_text_color_for_bg(btn_set_color),
        )
        btn_settings.bind(
            on_press=lambda x: setattr(self.manager, "current", "settings")
        )
        header.add_widget(titel)
        header.add_widget(btn_settings)
        layout.add_widget(header)

        layout.add_widget(
            Label(
                text=txt["vorname"],
                font_size="16sp",
                size_hint_y=0.05,
                color=label_color,
            )
        )
        self.entry_vorname = TextInput(
            hint_text="Vorname",
            multiline=False,
            font_size="16sp",
            size_hint_y=0.1,
            background_color=(0.2, 0.23, 0.3, 1)
            if bg_color[0] <= 0.6
            else (1, 1, 1, 1),
            foreground_color=(1, 1, 1, 1)
            if bg_color[0] <= 0.6
            else (0, 0, 0, 1),
            padding=[10, 10],
        )
        layout.add_widget(self.entry_vorname)

        layout.add_widget(
            Label(
                text=txt["nachname"],
                font_size="16sp",
                size_hint_y=0.05,
                color=label_color,
            )
        )
        self.entry_nachname = TextInput(
            hint_text="Nachname",
            multiline=False,
            font_size="16sp",
            size_hint_y=0.1,
            background_color=(0.2, 0.23, 0.3, 1)
            if bg_color[0] <= 0.6
            else (1, 1, 1, 1),
            foreground_color=(1, 1, 1, 1)
            if bg_color[0] <= 0.6
            else (0, 0, 0, 1),
            padding=[10, 10],
        )
        layout.add_widget(self.entry_nachname)

        layout.add_widget(
            Label(
                text=txt["artikel"],
                font_size="16sp",
                size_hint_y=0.05,
                color=label_color,
            )
        )
        self.entry_artikel = TextInput(
            hint_text="Artikel Name",
            multiline=False,
            font_size="16sp",
            size_hint_y=0.1,
            background_color=(0.2, 0.23, 0.3, 1)
            if bg_color[0] <= 0.6
            else (1, 1, 1, 1),
            foreground_color=(1, 1, 1, 1)
            if bg_color[0] <= 0.6
            else (0, 0, 0, 1),
            padding=[10, 10],
        )
        layout.add_widget(self.entry_artikel)

        self.label_status = Label(
            text="", font_size="16sp", markup=True, size_hint_y=0.08
        )
        layout.add_widget(self.label_status)

        btn_best_color = get_button_color((0.1, 0.65, 0.35, 1))
        btn_bestellen = Button(
            text=txt["btn_bestellen"],
            font_size="18sp",
            bold=True,
            background_normal="",
            background_color=btn_best_color,
            color=get_text_color_for_bg(btn_best_color),
            size_hint_y=0.14,
        )
        btn_bestellen.bind(on_press=self.bestellung_abschicken)
        layout.add_widget(btn_bestellen)

        self.add_widget(layout)

    def bestellung_abschicken(self, instance):
        if not hat_internet():
            self.label_status.text = (
                "[color=#d32f2f]Keine Internetverbindung![/color]"
            )
            return

        vorname = self.entry_vorname.text.strip()
        nachname = self.entry_nachname.text.strip()
        artikel = self.entry_artikel.text.strip()

        if not vorname or not artikel:
            self.label_status.text = (
                "[color=#f57c00]Bitte Vorname & Artikel ausfüllen![/color]"
            )
            return

        voller_name = f"{vorname} {nachname}".strip()
        bestellnummer = random.randint(100000, 999999)
        heute = datetime.date.today()
        start_datum = (heute + datetime.timedelta(days=1)).strftime("%d.%m.%Y")
        end_datum = (heute + datetime.timedelta(days=5)).strftime("%d.%m.%Y")

        nachricht = (
            f"Neue Bestellung #{bestellnummer}\n"
            f"Name: {voller_name}\n"
            f"Bestellung: {artikel}\n"
            f"Lieferzeitraum: {start_datum} bis {end_datum}"
        )

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": nachricht}

        try:
            response = requests.post(url, data=payload, timeout=5)
            if response.status_code == 200:
                gespeicherte_daten["nr"] = bestellnummer
                gespeicherte_daten["name"] = voller_name
                gespeicherte_daten["artikel"] = artikel
                gespeicherte_daten["start"] = start_datum
                gespeicherte_daten["end"] = end_datum

                self.manager.current = "kassenbon"
            else:
                self.label_status.text = (
                    "[color=#d32f2f]Fehler beim Senden an Telegram.[/color]"
                )
        except Exception:
            self.label_status.text = "[color=#d32f2f]Verbindungsfehler.[/color]"


# ==========================================
# SCREEN 2: EINSTELLUNGEN
# ==========================================
class EinstellungenScreen(Screen):

    def on_enter(self):
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        txt = SPRACHEN.get(app_settings["sprache"], SPRACHEN["Deutsch"])
        bg_color = get_bg_color()
        Window.clearcolor = bg_color
        label_color = get_text_color_for_bg(bg_color)

        layout = BoxLayout(
            orientation="vertical", padding=20, spacing=12, size_hint=(1, 1)
        )

        titel = Label(
            text=f"[b]{txt['settings_titel']}[/b]",
            markup=True,
            font_size="22sp",
            size_hint_y=0.1,
            color=(0.1, 0.5, 0.9, 1) if bg_color[0] > 0.6 else (0.3, 0.75, 1, 1),
        )
        layout.add_widget(titel)

        layout.add_widget(
            Label(
                text=txt["sprache_label"],
                font_size="16sp",
                size_hint_y=0.06,
                color=label_color,
            )
        )
        spin_sprache = Spinner(
            text=app_settings["sprache"],
            values=("Deutsch", "English", "Türkçe"),
            size_hint_y=0.1,
            font_size="16sp",
            background_color=get_button_color((0.2, 0.3, 0.4, 1)),
            color=get_text_color_for_bg(get_button_color((0.2, 0.3, 0.4, 1))),
        )
        spin_sprache.bind(text=self.sprache_geandert)
        layout.add_widget(spin_sprache)

        layout.add_widget(
            Label(
                text=txt["theme_label"],
                font_size="16sp",
                size_hint_y=0.06,
                color=label_color,
            )
        )
        spin_theme = Spinner(
            text=app_settings["theme"],
            values=("Gerät", "Dunkel", "Hell", "Eigene Farbe..."),
            size_hint_y=0.1,
            font_size="16sp",
            background_color=get_button_color((0.2, 0.3, 0.4, 1)),
            color=get_text_color_for_bg(get_button_color((0.2, 0.3, 0.4, 1))),
        )
        spin_theme.bind(text=self.theme_geandert)
        layout.add_widget(spin_theme)

        layout.add_widget(
            Label(
                text=txt["farben_label"],
                font_size="16sp",
                size_hint_y=0.06,
                color=label_color,
            )
        )
        spin_button_theme = Spinner(
            text=app_settings["button_theme"],
            values=("Standard", "Schwarz", "Weiß", "Eigene Farbe..."),
            size_hint_y=0.1,
            font_size="16sp",
            background_color=get_button_color((0.2, 0.3, 0.4, 1)),
            color=get_text_color_for_bg(get_button_color((0.2, 0.3, 0.4, 1))),
        )
        spin_button_theme.bind(text=self.button_theme_geandert)
        layout.add_widget(spin_button_theme)

        btn_back_color = get_button_color((0.4, 0.4, 0.4, 1))
        btn_zurueck = Button(
            text=txt["btn_zurueck"],
            font_size="18sp",
            bold=True,
            background_normal="",
            background_color=btn_back_color,
            color=get_text_color_for_bg(btn_back_color),
            size_hint_y=0.12,
        )
        btn_zurueck.bind(
            on_press=lambda x: setattr(self.manager, "current", "eingabe")
        )
        layout.add_widget(btn_zurueck)

        self.add_widget(layout)

    def sprache_geandert(self, spinner, text):
        app_settings["sprache"] = text
        self.build_ui()

    def theme_geandert(self, spinner, text):
        if text in ("Gerät", "Dunkel", "Hell"):
            app_settings["theme"] = text
            Window.clearcolor = get_bg_color()
            self.build_ui()
        elif "Eigene Farbe" in text:
            self.manager.get_screen("farbauswahl").ziel = "bg"
            self.manager.current = "farbauswahl"

    def button_theme_geandert(self, spinner, text):
        if text in ("Standard", "Schwarz", "Weiß"):
            app_settings["button_theme"] = text
            self.build_ui()
        elif "Eigene Farbe" in text:
            self.manager.get_screen("farbauswahl").ziel = "button"
            self.manager.current = "farbauswahl"


# ==========================================
# SCREEN 3: FARBAUSWAHL
# ==========================================
class FarbauswahlScreen(Screen):
    ziel = "button"

    def on_enter(self):
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        txt = SPRACHEN.get(app_settings["sprache"], SPRACHEN["Deutsch"])
        bg_color = get_bg_color()
        Window.clearcolor = bg_color

        layout = BoxLayout(
            orientation="vertical", padding=20, spacing=10, size_hint=(1, 1)
        )

        titel_text = (
            "BUTTON-FARBE WÄHLEN"
            if self.ziel == "button"
            else "HINTERGRUND-FARBE WÄHLEN"
        )
        layout.add_widget(
            Label(
                text=f"[b]{titel_text}[/b]",
                markup=True,
                font_size="20sp",
                size_hint_y=0.12,
                color=(0.1, 0.5, 0.9, 1) if bg_color[0] > 0.6 else (0.3, 0.75, 1, 1),
            )
        )

        for name, color in FARBEN_NAME_TO_COLOR.items():
            btn = Button(
                text=name,
                font_size="18sp",
                bold=True,
                background_normal="",
                background_color=color,
                color=get_text_color_for_bg(color),
                size_hint_y=0.12,
            )
            btn.bind(on_press=lambda inst, c=color: self.farbe_ausgewaehlt(c))
            layout.add_widget(btn)

        btn_back_color = get_button_color((0.4, 0.4, 0.4, 1))
        btn_zurueck = Button(
            text=txt["btn_zurueck"],
            font_size="18sp",
            bold=True,
            background_normal="",
            background_color=btn_back_color,
            color=get_text_color_for_bg(btn_back_color),
            size_hint_y=0.12,
        )
        btn_zurueck.bind(
            on_press=lambda x: setattr(self.manager, "current", "settings")
        )
        layout.add_widget(btn_zurueck)

        self.add_widget(layout)

    def farbe_ausgewaehlt(self, color):
        if self.ziel == "button":
            app_settings["button_farbe_custom"] = color
            app_settings["button_theme"] = "Eigene Farbe"
        else:
            app_settings["bg_color_custom"] = color
            app_settings["theme"] = "Eigene Farbe"
            Window.clearcolor = get_bg_color()

        self.manager.current = "settings"


# ==========================================
# SCREEN 4: KASSENBON
# ==========================================
class KassenbonScreen(Screen):

    def on_enter(self):
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        txt = SPRACHEN.get(app_settings["sprache"], SPRACHEN["Deutsch"])
        Window.clearcolor = get_bg_color()

        main_layout = BoxLayout(
            orientation="vertical", padding=20, spacing=10, size_hint=(1, 1)
        )

        scroll = ScrollView(size_hint=(1, 0.6))
        self.bon_card = BoxLayout(
            orientation="vertical", padding=20, spacing=10, size_hint=(1, None)
        )
        self.bon_card.bind(minimum_height=self.bon_card.setter("height"))

        with self.bon_card.canvas.before:
            Color(0.96, 0.96, 0.94, 1)
            self.rect = Rectangle(pos=self.bon_card.pos, size=self.bon_card.size)
        self.bon_card.bind(
            pos=lambda instance, value: setattr(self.rect, "pos", value),
            size=lambda instance, value: setattr(self.rect, "size", value),
        )

        self.nr = gespeicherte_daten.get("nr", "000000")
        self.name = gespeicherte_daten.get("name", "")
        self.artikel = gespeicherte_daten.get("artikel", "")
        self.start_datum = gespeicherte_daten.get("start", "")
        self.end_datum = gespeicherte_daten.get("end", "")

        self.bon_text = (
            f"=====================================\n"
            f"        EINFACH BILLIG APP           \n"
            f"            {txt['bon_titel']}       \n"
            f"=====================================\n\n"
            f"Bestell-Nr:  #{self.nr}\n"
            f"Kunde:       {self.name}\n"
            f"Artikel:     {self.artikel}\n"
            f"Lieferung:   {self.start_datum} - {self.end_datum}\n\n"
            f"-------------------------------------\n"
            f"Preis wird persönlich mitgeteilt\n"
            f"-------------------------------------\n\n"
            f"Danke, dass Sie eingekauft haben!\n"
            f"====================================="
        )

        bon_label = Label(
            text=self.bon_text,
            font_size="16sp",
            color=(0.05, 0.05, 0.05, 1),
            halign="left",
            valign="top",
            size_hint_y=None,
        )
        bon_label.bind(
            texture_size=lambda instance, value: setattr(
                bon_label, "height", value[1]
            )
        )
        bon_label.bind(size=bon_label.setter("text_size"))

        self.bon_card.add_widget(bon_label)
        scroll.add_widget(self.bon_card)
        main_layout.add_widget(scroll)

        self.label_status = Label(
            text="", font_size="16sp", markup=True, size_hint_y=0.07
        )
        main_layout.add_widget(self.label_status)

        btn_layout = BoxLayout(
            orientation="vertical", spacing=8, size_hint=(1, 0.33)
        )

        btn_save_c = get_button_color((0.2, 0.6, 0.9, 1))
        btn_speichern = Button(
            text=txt["btn_speichern"],
            font_size="16sp",
            bold=True,
            background_normal="",
            background_color=btn_save_c,
            color=get_text_color_for_bg(btn_save_c),
        )
        btn_speichern.bind(on_press=self.kassenbon_speichern_dialog)
        btn_layout.add_widget(btn_speichern)

        btn_stor_c = get_button_color((0.9, 0.5, 0.1, 1))
        btn_stornieren = Button(
            text=txt["btn_stornieren"],
            font_size="16sp",
            bold=True,
            background_normal="",
            background_color=btn_stor_c,
            color=get_text_color_for_bg(btn_stor_c),
        )
        btn_stornieren.bind(
            on_press=lambda x: setattr(self.manager, "current", "storno")
        )
        btn_layout.add_widget(btn_stornieren)

        btn_exit_c = get_button_color((0.85, 0.2, 0.2, 1))
        btn_schliessen = Button(
            text=txt["btn_beenden"],
            font_size="16sp",
            bold=True,
            background_normal="",
            background_color=btn_exit_c,
            color=get_text_color_for_bg(btn_exit_c),
        )
        btn_schliessen.bind(on_press=self.app_beenden)
        btn_layout.add_widget(btn_schliessen)

        main_layout.add_widget(btn_layout)
        self.add_widget(main_layout)

    def kassenbon_speichern_dialog(self, instance):
        content = BoxLayout(orientation="vertical", padding=15, spacing=10)
        content.add_widget(
            Label(
                text="Wie möchtest du den Kassenbon speichern?", font_size="15sp"
            )
        )

        btn_txt = Button(
            text="Als Dokument (.txt)", font_size="16sp", size_hint_y=0.35
        )
        btn_img = Button(
            text="Als Bild / Galerie (.png)", font_size="16sp", size_hint_y=0.35
        )

        content.add_widget(btn_txt)
        content.add_widget(btn_img)

        popup = Popup(
            title="Speicherformat wählen",
            content=content,
            size_hint=(0.85, 0.4),
            auto_dismiss=True,
        )

        def save_txt(inst):
            popup.dismiss()
            self.speichern_als_txt()

        def save_png(inst):
            popup.dismiss()
            self.speichern_als_png()

        btn_txt.bind(on_press=save_txt)
        btn_img.bind(on_press=save_png)

        popup.open()

    def speichern_als_txt(self):
        txt = SPRACHEN.get(app_settings["sprache"], SPRACHEN["Deutsch"])
        dateiname = f"Kassenbon_{self.nr}.txt"

        download_pfad = "/sdcard/Download"
        if not os.path.exists(download_pfad):
            download_pfad = os.path.expanduser("~/Download")
        pfad = os.path.join(download_pfad, dateiname)

        try:
            with open(pfad, "w", encoding="utf-8") as f:
                f.write(self.bon_text)
            self.label_status.text = (
                f"[color=#2e7d32]{txt['save_msg'].format(file=dateiname)}[/color]"
            )
        except Exception:
            try:
                with open(dateiname, "w", encoding="utf-8") as f:
                    f.write(self.bon_text)
                self.label_status.text = (
                    f"[color=#2e7d32]{txt['save_msg'].format(file=dateiname)}[/color]"
                )
            except Exception:
                self.label_status.text = (
                    "[color=#d32f2f]Fehler beim Speichern![/color]"
                )

    def speichern_als_png(self):
        dateiname = f"Kassenbon_{self.nr}.png"
        app_ordner = App.get_running_app().user_data_dir
        lokaler_pfad = os.path.join(app_ordner, dateiname)

        try:
            self.bon_card.export_to_png(lokaler_pfad)

            pictures_pfad = "/sdcard/Pictures"
            if os.path.exists(pictures_pfad):
                ziel_pfad = os.path.join(pictures_pfad, dateiname)
                shutil.copy(lokaler_pfad, ziel_pfad)

            self.label_status.text = (
                f"[color=#2e7d32]Als Bild gespeichert ({dateiname})![/color]"
            )
        except Exception:
            self.label_status.text = (
                "[color=#d32f2f]Fehler beim Speichern als Bild![/color]"
            )

    def app_beenden(self, instance):
        App.get_running_app().stop()
        Window.close()
        sys.exit()


# ==========================================
# SCREEN 5: STORNIERUNG (MIT GRUND)
# ==========================================
class StornoScreen(Screen):
    ausgewaehlter_grund = ""

    def on_enter(self):
        self.ausgewaehlter_grund = ""
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        txt = SPRACHEN.get(app_settings["sprache"], SPRACHEN["Deutsch"])
        bg_color = get_bg_color()
        Window.clearcolor = bg_color
        label_color = get_text_color_for_bg(bg_color)

        layout = BoxLayout(
            orientation="vertical", padding=20, spacing=10, size_hint=(1, 1)
        )

        layout.add_widget(
            Label(
                text=f"[b]{txt['storno_titel']}[/b]",
                markup=True,
                font_size="20sp",
                size_hint_y=0.08,
                color=(0.85, 0.2, 0.2, 1),
            )
        )

        layout.add_widget(
            Label(
                text=txt["storno_frage"],
                font_size="15sp",
                size_hint_y=0.06,
                color=label_color,
            )
        )

        gruende = [
            txt["storno_grund_teuer"],
            txt["storno_grund_versehen"],
            txt["storno_grund_zeit"],
        ]

        self.grund_buttons = []
        btn_g_c = get_button_color((0.25, 0.3, 0.4, 1))
        for g in gruende:
            btn = Button(
                text=g,
                font_size="14sp",
                size_hint_y=0.1,
                background_normal="",
                background_color=btn_g_c,
                color=get_text_color_for_bg(btn_g_c),
            )
            btn.bind(
                on_press=lambda inst, text=g: self.grund_waehlen(inst, text)
            )
            self.grund_buttons.append(btn)
            layout.add_widget(btn)

        layout.add_widget(
            Label(
                text=txt["storno_sonstiges"],
                font_size="14sp",
                size_hint_y=0.05,
                color=label_color,
            )
        )

        self.input_sonstiges = TextInput(
            hint_text="Eigener Grund...",
            multiline=False,
            font_size="14sp",
            size_hint_y=0.12,
            background_color=(0.2, 0.23, 0.3, 1)
            if bg_color[0] <= 0.6
            else (1, 1, 1, 1),
            foreground_color=(1, 1, 1, 1)
            if bg_color[0] <= 0.6
            else (0, 0, 0, 1),
        )
        layout.add_widget(self.input_sonstiges)

        action_layout = BoxLayout(
            orientation="horizontal", spacing=10, size_hint_y=0.14
        )

        btn_skip_c = get_button_color((0.5, 0.5, 0.5, 1))
        btn_ueberspringen = Button(
            text=txt["btn_ueberspringen"],
            font_size="16sp",
            bold=True,
            background_normal="",
            background_color=btn_skip_c,
            color=get_text_color_for_bg(btn_skip_c),
        )
        btn_ueberspringen.bind(
            on_press=lambda x: self.storno_absenden(kein_grund=True)
        )

        btn_send_c = get_button_color((0.85, 0.2, 0.2, 1))
        btn_senden = Button(
            text=txt["btn_senden"],
            font_size="16sp",
            bold=True,
            background_normal="",
            background_color=btn_send_c,
            color=get_text_color_for_bg(btn_send_c),
        )
        btn_senden.bind(
            on_press=lambda x: self.storno_absenden(kein_grund=False)
        )

        action_layout.add_widget(btn_ueberspringen)
        action_layout.add_widget(btn_senden)
        layout.add_widget(action_layout)

        self.add_widget(layout)

    def grund_waehlen(self, instance, text):
        self.ausgewaehlter_grund = text
        for btn in self.grund_buttons:
            btn.background_color = (0.25, 0.3, 0.4, 1)
        instance.background_color = (0.1, 0.65, 0.35, 1)

    def storno_absenden(self, kein_grund=False):
        nr = gespeicherte_daten.get("nr", "000000")
        name = gespeicherte_daten.get("name", "")

        final_grund = "Kein Grund angegeben"
        if not kein_grund:
            sonstiges = self.input_sonstiges.text.strip()
            if sonstiges:
                final_grund = sonstiges
            elif self.ausgewaehlter_grund:
                final_grund = self.ausgewaehlter_grund

        storno_nachricht = (
            f"BESTELLUNG STORNIERT!\n"
            f"Bestell-Nr: #{nr}\n"
            f"Name: {name}\n"
            f"Grund: {final_grund}"
        )

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": storno_nachricht}

        try:
            requests.post(url, data=payload, timeout=5)
        except Exception:
            pass

        txt = SPRACHEN.get(app_settings["sprache"], SPRACHEN["Deutsch"])
        kassenbon_screen = self.manager.get_screen("kassenbon")
        kassenbon_screen.label_status.text = (
            f"[color=#f57c00]{txt['storno_msg'].format(nr=nr)}[/color]"
        )
        self.manager.current = "kassenbon"


# ==========================================
# HAUPT APP
# ==========================================
class MainApp(App):

    def build(self):
        if platform == "android":
            try:
                from android.permissions import Permission, request_permissions

                request_permissions([
                    Permission.WRITE_EXTERNAL_STORAGE,
                    Permission.READ_EXTERNAL_STORAGE,
                ])
            except Exception:
                pass

        sm = ScreenManager()
        sm.add_widget(EingabeScreen(name="eingabe"))
        sm.add_widget(EinstellungenScreen(name="settings"))
        sm.add_widget(FarbauswahlScreen(name="farbauswahl"))
        sm.add_widget(KassenbonScreen(name="kassenbon"))
        sm.add_widget(StornoScreen(name="storno"))
        return sm


if __name__ == "__main__":
    MainApp().run()


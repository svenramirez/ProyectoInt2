import sounddevice as sd
from scipy.io.wavfile import write
import speech_recognition as sr
import tempfile, os
import webbrowser
import random
import platform
from datetime import datetime
import urllib.request
import urllib.parse
import json
import winreg
import shutil
import subprocess

SRATE = 16000     # tasa de muestreo
DUR = 5           # segundos

print("Grabando... habla ahora!")
audio = sd.rec(int(DUR*SRATE), samplerate=SRATE, channels=1, dtype='int16')
sd.wait()
print("Listo, procesando...")

# guarda a WAV temporal
tmp_wav = tempfile.mktemp(suffix=".wav")
write(tmp_wav, SRATE, audio)

# reconoce con SpeechRecognition
r = sr.Recognizer()
with sr.AudioFile(tmp_wav) as source:
    data = r.record(source)

# --- Helpers for new commands -------------------------------------------------
def take_screenshot():
    """Toma un screenshot usando Pillow y lo guarda con la fecha.

    Guarda en `screenshots/screenshot_YYYYMMDD.png`. Si falla muestra un único mensaje de error.
    """
    screenshots_dir = os.path.join(os.getcwd(), "screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)
    filename = os.path.join(screenshots_dir, f"screenshot_{datetime.now().strftime('%Y%m%d')}.png")

    try:
        from PIL import ImageGrab
    except ImportError:
        print("Pillow no está instalado. Instálalo: python -m pip install pillow")
        return

    try:
        img = ImageGrab.grab()
        img.save(filename)
    except Exception as e:
        print("Error al tomar la captura:", e)


def play_random_radio():
    """Busca hasta 3 streams directos de emisoras en Colombia y abre uno aleatorio.

    Usa la API pública de radio-browser para obtener URLs de stream. Selecciona
    hasta 3 emisoras y abre una al azar. Si no se encuentran streams o hay
    error al consultar la API, muestra un mensaje de error y no hace fallback.
    """
    try:
        api_url = "https://de1.api.radio-browser.info/json/stations/bycountry/Colombia?limit=100"
        with urllib.request.urlopen(api_url, timeout=6) as resp:
            stations = json.loads(resp.read().decode('utf-8'))
        streams = [s.get('url_resolved') or s.get('url') for s in stations if s.get('url_resolved') or s.get('url')]
        streams = [u for u in streams if isinstance(u, str) and u.startswith('http')]
        if not streams:
            print("No se encontraron streams en la API para Colombia.")
            return
        random.shuffle(streams)
        three = streams[:3]
        url = random.choice(three)
        print("Abriendo stream:", url)
        try:
            # Si VLC está instalado en PATH, úsalo para forzar reproducción
            vlc_path = shutil.which("vlc")
            if vlc_path:
                subprocess.Popen([vlc_path, url], shell=False)
                return
            # En Windows, preferir abrir con la aplicación por defecto (evita descarga en algunos navegadores)
            if platform.system() == "Windows":
                try:
                    os.startfile(url)
                    return
                except Exception:
                    pass
            # Fallback al navegador
            webbrowser.open(url)
        except Exception as e:
            print("Error al abrir el stream:", e)
    except Exception as e:
        print("Error al consultar radio-browser o abrir stream:", e)


def toggle_windows_theme(use_light=None):
    """Alterna o establece el tema de Windows entre claro y oscuro para apps y sistema.

    Si `use_light` es None -> alterna; si es True -> establece tema claro; si es False -> establece tema oscuro.
    Modifica las claves de registro en HKCU y notifica al sistema.
    """
    if platform.system() != "Windows":
        print("El cambio de tema solo está disponible en Windows.")
        return
    try:
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as key:
                try:
                    val, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                except FileNotFoundError:
                    val = 1
        except FileNotFoundError:
            # crear la clave si no existe
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as _:
                val = 1

        if use_light is None:
            new = 0 if val == 1 else 1
        else:
            new = 1 if use_light else 0

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "AppsUseLightTheme", 0, winreg.REG_DWORD, new)
            winreg.SetValueEx(key, "SystemUsesLightTheme", 0, winreg.REG_DWORD, new)

        # Notificar al sistema del cambio
        try:
            import ctypes
            HWND_BROADCAST = 0xFFFF
            WM_SETTINGCHANGE = 0x001A
            SMTO_ABORTIFHUNG = 0x0002
            ctypes.windll.user32.SendMessageTimeoutW(HWND_BROADCAST, WM_SETTINGCHANGE, 0, "ImmersiveColorSet", SMTO_ABORTIFHUNG, 100, None)
        except Exception:
            pass

        estado = "claro" if new == 1 else "oscuro"
        print("Tema cambiado a", estado)
    except Exception as e:
        print("No se pudo cambiar el tema automáticamente:", e)
        webbrowser.open("ms-settings:personalization-colors")

# -----------------------------------------------------------------------------
try:
    texto = r.recognize_google(data, language="es-ES")
    print("Dijiste:", texto)
    
    # Procesar comandos
    cmd = texto.lower()
    
    if "hola" in cmd:
        print("¡Hola, bienvenido al curso!")
    elif "abrir google" in cmd:
        import webbrowser
        webbrowser.open("https://www.google.com")
    elif "hora" in cmd:
        from datetime import datetime
        print("Hora actual:", datetime.now().strftime("%H:%M"))
    elif "captura pantalla" in cmd or "captura de pantalla" in cmd or "screenshot" in cmd:
        take_screenshot()
    elif "música aleatoria" in cmd or "musica aleatoria" in cmd or "radio aleatoria" in cmd or "música al azar" in cmd:
        play_random_radio()
    elif "tema oscuro" in cmd or "modo oscuro" in cmd or "oscuro" in cmd:
        # Establecer tema oscuro explícitamente
        toggle_windows_theme(use_light=False)
    elif "tema claro" in cmd or "modo claro" in cmd or "claro" in cmd:
        # Establecer tema claro explícitamente
        toggle_windows_theme(use_light=True)
    else:
        print("Comando no reconocido.")
        
except sr.UnknownValueError:
    print("No se entendió el audio.")
except sr.RequestError as e:
    print("Error:", e)
finally:
    if os.path.exists(tmp_wav):
        os.remove(tmp_wav)
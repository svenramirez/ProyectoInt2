# Respuestas - Laboratorio de Voz

A continuación están las respuestas solicitadas sobre la implementación y decisiones del laboratorio.

---

## 1) ¿Qué librerías se usaron en el laboratorio para grabar y reconocer voz?

- `sounddevice`: captura audio desde el micrófono (se usa `sd.rec` y `sd.wait`).
- `scipy.io.wavfile.write`: guarda el buffer de audio como archivo WAV.
- `speech_recognition` (alias `sr`): manejo del audio para reconocimiento (`Recognizer`, `AudioFile`) y la llamada a `recognize_google`.
- `tempfile`, `os`: para crear/gestionar el archivo WAV temporal y eliminarlo al final.

Además, para comandos y utilidades se usaron (en el código extendido): `webbrowser`, `Pillow` (para capturas), `winreg` (para cambiar tema en Windows), `urllib`/`json` (para consultar la API de radio), `subprocess`/`shutil` (para lanzar reproductores).

---

## 2) ¿Por qué decidimos no usar PyAudio en esta práctica?

- `PyAudio` depende de PortAudio y suele requerir compilación o ruedas binarias específicas en Windows/macOS; en muchos entornos instalarlo con `pip` produce errores si faltan herramientas de compilación.
- `sounddevice` ofrece una experiencia más sencilla de instalar y usar (y también se apoya en PortAudio, pero su empaquetado suele ser más cómodo). Por compatibilidad y evitar problemas de instalación para los estudiantes, se optó por `sounddevice`.

---

## 3) ¿Qué rol cumple la función `recognize_google` en el código?

`recognize_google` (de la librería `speech_recognition`) envía el audio al servicio Web Speech API de Google y devuelve la transcripción en texto. Es la función que realiza la conversión audio → texto (STT) en nuestro script. Requiere conexión a Internet y puede lanzar excepciones si no hay red o si no puede reconocer el audio.

---

## 4) ¿Qué ocurre si SpeechRecognition no entiende lo que dijiste?

El código captura la excepción `sr.UnknownValueError` y maneja ese caso mostrando el mensaje `No se entendió el audio.`. Es decir, no se obtiene texto y se informa al usuario que la transcripción falló.

---

## 5) ¿Cómo se guardó temporalmente el archivo WAV en el código?

- Se creó una ruta temporal con `tempfile.mktemp(suffix=".wav")`.
- El buffer de audio grabado se guardó con `scipy.io.wavfile.write(tmp_wav, SRATE, audio)`.
- Al finalizar (en el bloque `finally`) se eliminó el archivo temporal con `os.remove(tmp_wav)` si existía.

---

## 6) ¿Qué diferencia hay entre `voz_archivo.py` y `voz_comandos.py`?

- En este repositorio sólo está presente `voz_archivo.py` (es el script que grababa 5 segundos, generaba el WAV temporal, llamaba a `recognize_google` y procesaba comandos). `voz_comandos.py` no existe actualmente en la carpeta.
- Conceptualmente, una diferencia típica sería:
  - `voz_archivo.py`: script de captura y transcripción puntual (one-shot). Graba, transcribe y procesa en un flujo simple.
  - `voz_comandos.py`: módulo pensado para la lógica de mapeo `texto -> acción` (una colección de comandos o una versión que escucha continuamente y ejecuta acciones). En otros proyectos `voz_comandos.py` suele separar la lógica de comandos del código de captura.

---

## 7) Menciona un comando que implementaste y explica cómo funciona

- Comando: **`captura pantalla`**
  - Qué hace: toma una captura de pantalla y la guarda en la carpeta `screenshots/` con nombre `screenshot_YYYYMMDD.png`.
  - Cómo funciona: el script usa `Pillow.ImageGrab.grab()` para capturar la pantalla; si `Pillow` no está instalado muestra la instrucción `python -m pip install pillow` y no intenta alternativas. Si ocurre un error sencillamente imprime `Error al tomar la captura: <detalle>`.

---

## 8) ¿Qué posibles aplicaciones reales tiene un sistema de voz como este?

- Control por voz de aplicaciones de escritorio (abrir webs, lanzar reproductores, tomar capturas).
- Asistentes de accesibilidad para personas con movilidad reducida.
- Sistemas de dictado o transcripción rápida para notas.
- Integración con domótica o IoT para controlar dispositivos.
- Soporte en centros de atención (prototipos de IVR) o prototipos de agentes conversacionales.

---

## 9) ¿Cómo manejarías el error de conexión con el servicio de reconocimiento?

- Capturar `sr.RequestError` y mostrar un mensaje claro al usuario indicando falla de red o servicio.
- Reintentar la petición con un backoff exponencial (p. ej. reintentos a 1s, 2s, 4s) hasta un máximo.
- Proveer una estrategia offline como fallback: usar un motor STT local (ej.: VOSK, Whisper local) para no depender siempre de la nube.
- En contextos críticos, almacenar las grabaciones localmente y procesarlas cuando haya conexión.

---

## 10) ¿Qué mejoras propondrías para la próxima versión de este asistente de voz?

- Soporte de escucha continua con palabra de activación (wake word) para no depender de capturas puntuales.
- Integrar un motor STT local (VOSK, whisper) como fallback offline.
- Añadir TTS para respuestas habladas (p.ej. `pyttsx3` o servicios en la nube).
- Añadir archivo `requirements.txt` y un pequeño `README.md` con pasos de instalación.
- Mecanismo de configuración (JSON/INI) para rutas, comandos activos, y preferencias (usar VLC, folder de screenshots, etc.).
- Añadir tests unitarios y manejo más robusto de errores y logs.
- Interfaz gráfica mínima para ver estado, últimos comandos y logs.

---

Si quieres, puedo:

- Generar un `requirements.txt` con las dependencias mínimas (`sounddevice`, `scipy`, `SpeechRecognition`, `pillow`).
- Crear un `README.md` con instrucciones de ejecución y pruebas.

Dime qué prefieres y lo agrego al repositorio.

import os, signal, subprocess, sys, time
import pyaarlo

OUT = "segmentos"
os.makedirs(OUT, exist_ok=True)
parar = False
ffmpeg = None

def manejar_senal(signum, _frame):
    global parar
    print(f"Señal {signum}: parando…", flush=True)
    parar = True
    if ffmpeg and ffmpeg.poll() is None:
        try:
            ffmpeg.stdin.write(b"q"); ffmpeg.stdin.flush()
        except Exception:
            ffmpeg.send_signal(signal.SIGINT)

signal.signal(signal.SIGINT, manejar_senal)
signal.signal(signal.SIGTERM, manejar_senal)

max_seg = int(float(os.environ.get("MAX_MINUTOS") or 120) * 60)
inicio = time.monotonic()

print("Iniciando sesión en Arlo…", flush=True)
arlo = pyaarlo.PyArlo(
    username=os.environ["ARLO_USER"],
    password=os.environ["ARLO_PASS"],
    tfa_source="imap", tfa_type="email", tfa_host="imap.gmail.com",
    tfa_username=os.environ["TFA_EMAIL"],
    tfa_password=os.environ["TFA_APP_PASSWORD"],
    storage_dir="./arlo-estado", save_session=True, synchronous_mode=True,
)
if not arlo.is_connected:
    print("ERROR al entrar en Arlo:", arlo.last_error, flush=True); sys.exit(1)

camaras = arlo.cameras
print("Cámaras:", ", ".join(c.name for c in camaras) or "(ninguna)", flush=True)
nombre = (os.environ.get("CAMARA") or "").strip().lower()
cam = next((c for c in camaras if c.name.lower() == nombre), None) if nombre else (camaras[0] if camaras else None)
if cam is None:
    print(f"ERROR: no encuentro la cámara '{nombre}'", flush=True); sys.exit(1)
print(f"Grabando: {cam.name}", flush=True)

tramo, fallos = 0, 0
while not parar and time.monotonic() - inicio < max_seg and fallos < 5:
    url = cam.get_stream()
    if not url:
        fallos += 1; print("Sin URL de directo, reintento…", flush=True); time.sleep(10); continue
    tramo += 1
    restante = int(max_seg - (time.monotonic() - inicio))
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "warning", "-rtsp_transport", "tcp", "-i", url,
           "-t", str(restante), "-c", "copy", "-f", "segment", "-segment_time", "60",
           "-reset_timestamps", "1", "-segment_format", "mp4",
           "-movflags", "+frag_keyframe+empty_moov", os.path.join(OUT, f"t{tramo:03d}_%04d.mp4")]
    t0 = time.monotonic()
    ffmpeg = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    ffmpeg.wait()
    fallos = fallos + 1 if time.monotonic() - t0 < 20 else 0
    try: cam.stop_stream()
    except Exception: pass

print("Grabación terminada.", flush=True)

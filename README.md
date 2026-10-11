# Grabador Arlo

Graba el directo de una cámara Arlo en los servidores gratuitos de GitHub Actions. No necesita un PC encendido ni el iPhone en primer plano.

## Uso desde el iPhone (app GitHub)
1. **REC:** repositorio → *Actions* → **🔴 Grabar Arlo** → *Run workflow*. Puedes poner el nombre de la cámara o dejarlo vacío.
2. **STOP:** abre la ejecución en curso → **Cancel workflow**.
3. **Ver:** al terminar, el vídeo aparece en *Releases*, como `arlo-AAAA-MM-DD_HH-MM.mp4`.

## Secretos (Settings → Secrets and variables → Actions)
| Nombre | Valor |
|---|---|
| `ARLO_USER` | email de tu cuenta Arlo |
| `ARLO_PASS` | contraseña de Arlo |
| `TFA_EMAIL` | Gmail donde Arlo envía el código de verificación |
| `TFA_APP_PASSWORD` | contraseña de aplicación de ese Gmail (16 letras) |

## Límites
- Repo privado: unas 33 h de grabación gratis al mes. Cada grabación dura como mucho 6 h.
- Arranca unos 30–60 s después de pulsar REC.
- La API de Arlo no es oficial (pyaarlo), así que puede dejar de funcionar si Arlo la cambia.

# El Plan Divino: reel de 60 s (9:16)

**Nicho:** superación personal, fe y motivación  
**Formato:** vertical 1080×1920, 30 fps, 60 s, para Reels / TikTok / Shorts / Facebook  
**Proyecto fuente (editable en la nube):** ElevenLabs Flow «El Plan Divino – Reel 60s»

---

## 1. Entregables en esta carpeta

| Archivo | Uso |
|---|---|
| `final/PlanDivino_60s_subtitulado.mp4` | Listo para publicar, con subtítulos, gancho y CTA |
| `final/PlanDivino_60s_limpio.mp4` | Mismo corte **sin texto**, para rotular en CapCut o Filmora |
| `final/PlanDivino_mezcla_audio.m4a` | Mezcla final de voz y música (−14 LUFS, estándar de redes) |
| `clips/E01…E07_*.mp4` | Cada escena por separado, ya con movimiento de cámara y sin audio |
| `imagenes/E1…E6_*.png` | Fotogramas hiperrealistas en 2K (1152×2048) |
| `audio/voz_toma1.mp3` / `voz_toma2.mp3` | Voz en off (toma 1 en el corte; toma 2 como alternativa) |
| `audio/musica_toma1.mp3` / `musica_toma2.mp3` | Música instrumental celestial de 62 s (dos variantes) |
| `subtitulos/PlanDivino_ES.srt` | Subtítulos importables en CapCut, Filmora, YouTube y Meta |
| `subtitulos/PlanDivino_ES_estilizado.ass` | Subtítulos con estilo (palabras clave en dorado) |
| `build.py` | Script que vuelve a armar el video si cambias imágenes, voz o tiempos |

---

## 2. Gancho de retención (primeros 3 s)

- **Texto en pantalla (0:00–0:03.6):** «¿Y SI TU FRACASO FUERA PARTE DEL PLAN?»
- **Voz (0:00.2):** «Si hoy algo no salió como esperabas… no es casualidad que estés viendo esto.»
- **Imagen:** acercamiento lento a las manos en oración bajo rayos de luz.

**Por qué funciona:**
- La pregunta abre un hueco de curiosidad.
- «No es casualidad que estés viendo esto» le habla directo al espectador.
- El texto y la voz arrancan al mismo tiempo, así que el reel engancha aunque se vea sin sonido.

**CTA final (0:56–1:00):** «Comenta "CONFÍO" si lo necesitabas hoy · Síguenos para más». Los comentarios con una palabra concreta suben el engagement y el alcance.

---

## 3. Guion y línea de tiempo

| Tiempo | Bloque | Escena / movimiento | Voz en off |
|---|---|---|---|
| 0:00–0:05.7 | Gancho | E1 Manos en oración y cielo, *push-in* | Si hoy algo no salió como esperabas… no es casualidad que estés viendo esto. |
| 0:05.7–0:15.5 | Inicio | E1 *Pull-out* que revela el cielo | A veces, cuando las cosas no salen como esperamos, nos preguntamos por qué. ¿Es que Dios no nos escucha? ¿O es que el destino está en nuestra contra? |
| 0:15.5–0:27.0 | Plan divino vs. nuestros planes | E2 Rompecabezas y mapa de luz, *push-in* | Dios tiene un plan perfecto, aunque hoy no lo entiendas. Lo que para nosotros es un desvío o un fracaso, para Él puede ser el camino correcto hacia algo mucho más grande. |
| 0:27.0–0:33.5 | Momentos de prueba | E3 Atleta entrenando antes del amanecer | Cuando algo no sale como lo planeaste, no es que Dios te esté quitando algo… te está preparando para lo que viene. |
| 0:33.5–0:37.8 | Preparación | E4 Violinista practicando, paneo | Te está fortaleciendo, enseñando, puliendo. |
| 0:37.8–0:46.0 | Confianza y paciencia | E5 Brote y mar, movimiento ascendente | Él ve el panorama completo. Tu tarea es confiar, ser paciente y seguir dando lo mejor de ti en cada paso. |
| 0:46.0–1:00 | Cierre | E6 Amanecer y sonrisa serena, *pull-out* | No te desanimes. Lo que Dios tiene preparado para ti es infinitamente mejor de lo que puedes imaginar. Cree en Su tiempo… y en Su plan. |

**Voz:** «Miguel – Narrador Bíblico» (ElevenLabs v4), latino, cálido y pausado.  
**Música:** ElevenLabs Music v2.5, instrumental celestial a 70 BPM en Re mayor: pads, cuerdas, piano y textura coral sin voces. Baja sola cuando habla el narrador (*ducking*).

---

## 4. Cómo editarlo en CapCut (escritorio o móvil)

1. **Nuevo proyecto** en 9:16.
2. **Importa** `clips/E01…E07` y colócalos en orden en la pista principal. Cada clip ya trae 0.6 s extra para la transición.
3. Entre clips aplica **Transiciones → Básicas → Disolver** de 0.6 s.
4. **Audio:** arrastra `audio/voz_toma1.mp3` en 0:00 y `audio/musica_toma1.mp3` en una segunda pista.
   - Volumen de la música: −14 dB, o usa **Audio → Reducción automática (ducking)** en la pista de música.
   - Fundido de salida de 2.5 s.
   - Atajo: usa `final/PlanDivino_mezcla_audio.m4a`, que ya está mezclado.
5. **Subtítulos:**
   - Opción A: **Texto → Subtítulos automáticos**, idioma español.
   - Opción B (más exacta): **Texto → Importar subtítulos** y elige `PlanDivino_ES.srt`.
   - Estilo recomendado: Montserrat o *The Bold Font* en blanco, borde negro de 5 px, palabras clave (Dios, plan, confiar, Su tiempo) en dorado #FFC84F, animación *Pop* o *Typewriter*.
6. **Gancho:** caja de texto de 0:00 a 0:03.6, arriba al centro: «¿Y SI TU FRACASO FUERA PARTE DEL PLAN?»
7. **Look (opcional):**
   - Ajustes: Contraste +8, Calidez +6, Viñeta 20.
   - Efectos: *Luz → Rayos de luz* o *Destello* en E1 y E6.
   - Partículas de polvo dorado en E2.
8. **Exporta** en 1080p, 30 fps, tasa de bits «Recomendada» o «Alta».

**Si quieres partir del video armado:** importa `final/PlanDivino_60s_limpio.mp4` y solo agrega texto y efectos. Ya trae imagen, transiciones y audio sincronizados.

### Filmora
- Proyecto 9:16, 1080×1920, 30 fps. Arrastra los clips y aplica *Dissolve* de 0.6 s.
- Usa **Audio Ducking** en la pista de música.
- **Títulos → Importar SRT** con `PlanDivino_ES.srt`.

### Premiere / DaVinci (opcional)
El `.srt` se importa directo como pista de subtítulos.

---

## 5. Mejora a video IA en movimiento real (pendiente de tu aprobación)

En el Flow de ElevenLabs ya están creados **6 nodos de video Seedance 2.5** (1080p, 9:16, 10 s cada uno, sin audio), con prompts cinematográficos que replican estas mismas escenas en movimiento real.

- **Costo estimado:** ~301,000 créditos (≈ US$68.65).
- **Para generarlos:** abre el Flow y presiona *Run* en los nodos «E1…E6», o pídemelo y lo lanzo.
- **Cuando estén listos:** reemplaza cada clip de `clips/` por su versión en video. `build.py` se puede adaptar para usarlos directamente.

### Prompts maestros (también sirven en Google Flow / Veo 3.1, Kling o Runway)

> **E1:** Extreme close-up of a man's hands clasped in prayer, resting on his forehead, warm golden backlight catching dust particles, then the camera slowly tilts up and pulls back as he lifts his face toward a vast dramatic sky with god rays breaking through dark storm clouds. He stands alone on a quiet hilltop at dusk, wind moving his shirt. Hyper-realistic, cinematic anamorphic look, shallow depth of field, teal and gold color grade, Hollywood studio quality, 35mm film grain. No text.

> **E2:** Slow overhead dolly shot over an antique wooden table where scattered golden jigsaw puzzle pieces glide and click into place on their own, gradually assembling into a glowing aerial map of winding roads that converge toward a bright shining light at the center. Soft heavenly light beams, floating dust motes. Hyper-realistic, cinematic, magical realism, gold and deep blue grade. No text.

> **E3:** Low-angle tracking shot of a determined young athlete sprinting up long rain-soaked concrete stadium stairs before dawn, breath visible in the cold air, slow-motion as he pushes through exhaustion and reaches the top. Gritty cinematic sports-commercial look, dramatic rim lighting, teal with warm highlights. No text, no logos.

> **E4:** Close-up slow push-in on a young woman violinist practicing alone late at night in an empty rehearsal hall, single warm spotlight, eyes closed in focus, camera orbits gently. Hyper-realistic, emotional, warm amber and deep black tones. No text.

> **E5:** Macro time-lapse of a seed sprouting through dark soil, a green shoot unfurling toward a soft sunbeam, dew sparkling; camera rises and transitions to calm ocean waves on a shore under a pastel morning sky. Nature-documentary quality, golden light. No text.

> **E6:** A man in his thirties on a mountain summit at sunrise, eyes closed, a serene smile spreading as golden sunlight washes over him; he opens his arms in gratitude while the camera orbits and pulls back to reveal a sea of glowing clouds. Epic cinematic finale, anamorphic flare, warm golden grade. No text.

**Google Flow / Veo:** pega cada prompt, elige 9:16 y 8 s, y desactiva el audio generado. Usa la imagen correspondiente de `imagenes/` como *frame inicial* (image-to-video) para mantener el mismo estilo.

---

## 6. Publicación

**Pie de foto:**
> A veces, cuando nuestros planes se desmoronan, es porque Dios está construyendo algo mucho más grande para nosotros. Confía en Su tiempo y Su propósito. 🙏✨
>
> 💬 Comenta **CONFÍO** si este mensaje llegó en el momento justo.
> 🔁 Compártelo con alguien que lo necesite hoy.

**Hashtags (mezcla de alto volumen y nicho):**
`#fe #Dios #motivacion #superacionpersonal #planDivino #confiaenDios #reflexion #crecimientopersonal #exito #esperanza #propositodevida #mensajedeDios #reelsmotivacion #fyp #paratii`

**Portada sugerida:** fotograma de E6 (amanecer) con el texto «DIOS NO SE OLVIDÓ DE TI».

**Mejores horarios (México, audiencia de fe/motivación):** 6:00–8:00 y 20:00–22:00, de domingo a jueves.

---

## 7. Licencias y derechos

- **Música y voz:** generadas con ElevenLabs. En planes de pago incluyen licencia de uso comercial y no están en catálogos de Content ID, así que no deberían generar reclamos de derechos de autor. Confirma que tu plan de ElevenLabs sea de pago antes de monetizar.
- **Imágenes:** generadas con IA (Seedream 5 Pro) a partir de prompts originales, sin personas reales ni marcas.
- **Fuentes del render:** DejaVu (licencia libre). En CapCut puedes cambiarlas por cualquier fuente de su biblioteca.

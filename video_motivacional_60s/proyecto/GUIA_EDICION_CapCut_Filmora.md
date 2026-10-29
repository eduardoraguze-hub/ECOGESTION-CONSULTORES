# «Respira. Confía. Sigue.» — Video motivacional 60 s (9:16)

Paquete de producción editable para CapCut, Filmora, Premiere, DaVinci o Descript.

## 1. Entregables

| Carpeta / archivo | Qué es | Uso |
|---|---|---|
| `FINAL/Respira_Confia_Sigue_60s_9x16_FINAL.mp4` | Master final 1080×1920, 24 fps, H.264 + AAC 320 kbps, −14 LUFS | Publicar en Reels, TikTok y Shorts |
| `FINAL/Respira_Confia_Sigue_60s_9x16_SIN_TEXTO_editable.mp4` | El mismo master sin títulos | Para poner tus propios textos en CapCut o Filmora |
| `escenas/` | Las 7 escenas ya cortadas a su duración final (más 0.5 s de cola para la transición) | Reconstruir o reordenar la línea de tiempo |
| `clips/` | Material original: tomas de video IA (Kling 3 Pro) e imágenes fotorrealistas 4K (Canva AI) | Re-editar desde cero |
| `overlays/*.png` | 11 títulos como PNG transparentes de 1080×1920 | Arrastrar como superposición: ya están centrados |
| `audio/musica_final_60s.wav` | Banda sonora final de 60 s con fade-out | Pista de música |
| `audio/musica_original_62s.wav` | Composición completa de 62 s, sin recortar | Ajustar el final a otro largo |
| `proyecto/subtitulos_es.srt` | Subtítulos sincronizados | CapCut: Texto → Subtítulos → Importar |
| `scripts/` | Scripts de montaje (ffmpeg y Python) | Regenerar versiones automáticamente |

## 2. Línea de tiempo (edit decision list)

| # | Tiempo | Escena | Archivo | Movimiento | Texto en pantalla | Transición de salida |
|---|---|---|---|---|---|---|
| 01 | 0:00–0:05 | Toma aérea de montañas al amanecer | `S1_montanas_amanecer.mp4` (video IA) | Dron avanzando y elevándose | «Cuando el mundo se siente **demasiado...**» | Disolvencia de 0.5 s |
| 02 | 0:05–0:15 | Playa tranquila con olas | `S2_playa.mp4` | Push-in lento hacia la espuma | «...tu **paz interior** te llama.» | Disolvencia de 0.5 s |
| 03a | 0:15–0:25 | Bosque con rayos de sol | `S3a_bosque_rayos_sol.mp4` (video IA) | Tilt-up hacia el dosel | «La verdadera **riqueza** no está en lo que posees,» / «sino en la **libertad** de tu tiempo» | Fundido a negro de 0.5 s |
| 03b | 0:25–0:35 | Sendero del bosque con luz | `S3b_sendero_bosque.mp4` | Avance hacia el haz de luz | «y la **tranquilidad** de tu mente.» | Disolvencia de 0.5 s |
| 04a | 0:35–0:43 | Lago sereno al atardecer | `S4a_lago_atardecer.mp4` (video IA) | Deslizamiento lateral del dron | «Deja que la **calma** de estos paisajes te recuerde» / «que la **constancia** vence a la prisa» | Disolvencia de 0.5 s |
| 04b | 0:43–0:50 | Camino rural entre naturaleza | `S4b_camino_rural.mp4` | Dolly hacia el horizonte | «y que el orgullo de no rendirse es **para siempre.**» | Fundido a negro de 0.8 s |
| 05 | 0:50–1:00 | Cielo estrellado panorámico | `S5_cielo_estrellado.mp4` | Tilt-up hacia la Vía Láctea | «Respira.» (0:51) · «Confía.» (0:52.6) · «**Sigue.**» (0:54.2) | Fundido a negro final y música desvaneciéndose |

**Tiempos exactos de cada título (PNG):**

| PNG | Entra | Sale |
|---|---|---|
| `01_cuando_el_mundo` | 0.30 | 4.85 |
| `02_paz_interior` | 5.50 | 14.55 |
| `03a_riqueza` | 15.60 | 21.45 |
| `03b_libertad` | 21.80 | 28.05 |
| `03c_tranquilidad` | 28.40 | 34.55 |
| `04a_calma` | 35.50 | 40.45 |
| `04b_constancia` | 40.80 | 45.30 |
| `04c_no_rendirse` | 45.60 | 49.60 |
| `05a_respira` | 51.00 | 59.40 |
| `05b_confia` | 52.60 | 59.40 |
| `05c_sigue` | 54.20 | 59.40 |

Animación de todos los títulos: fade-in de 0.9 s con un ascenso de 28 px y fade-out de 0.7 s.

## 3. Cómo armarlo en CapCut (escritorio o móvil)

1. Crea un proyecto nuevo y elige **Proporción 9:16** y **24 fps**.
2. Importa las 7 escenas de `escenas/` y colócalas en orden en la pista principal.
3. Si usas las escenas con cola, superpón 0.5 s entre cada una y agrega **Transiciones → Básicas → Disolver** de 0.5 s.
4. **Pista de texto, opción A:** agrega cada PNG de `overlays/` como **Superposición** en los tiempos de la tabla, con **Animación de entrada → Fundido y elevación** (0.9 s) y **Animación de salida → Fundido** (0.7 s).
5. **Pista de texto, opción B:** usa `SIN_TEXTO_editable.mp4` y escribe los textos con la fuente **Cormorant Garamond** (Google Fonts), en blanco y con las palabras clave en dorado `#E8C478` itálica.
6. **Audio:** importa `audio/musica_final_60s.wav`, que ya trae el fade-out. Desactiva el audio original de los clips.
7. **Subtítulos (opcional):** Texto → Subtítulos → Importar `subtitulos_es.srt`.
8. **Exporta** en 1080p, 24 fps, con bitrate «Alto» o «Recomendado».

> Etalonaje ya aplicado en el master: contraste +6 %, saturación +8 %, ligero teal and orange, viñeta y grano de película. En CapCut puedes sumarle el filtro **Película → «Cine»** al 20–30 %.

## 4. Cómo armarlo en Filmora

1. Ve a Archivo → Configuración del proyecto y elige **1080×1920, 24 fps**.
2. Importa `escenas/` y `overlays/`, y arrastra las escenas a la pista 1.
3. Pon los PNG en la pista 2 con los tiempos de la tabla. En Animación usa **Fundido de entrada** y **Desplazar hacia arriba**.
4. Agrega **Transiciones → Disolver** de 0.5 s entre escenas.
5. En la pista de audio coloca `musica_final_60s.wav`.
6. Exporta en MP4 H.264, 1080×1920, a 16–20 Mbps.

## 5. Derechos de uso

| Elemento | Origen | Licencia |
|---|---|---|
| Tomas S1, S3a y S4a | Generadas con IA (Kling 3 Pro vía ElevenLabs) en tu cuenta | Uso comercial según los términos de ElevenLabs para tu plan |
| Imágenes S2, S3b, S4b y S5 | Generadas con IA en tu cuenta de Canva | Uso comercial según los términos de Canva AI |
| Música | Composición original sintetizada por código (`scripts/componer_musica.py`), sin samples de terceros | Libre de derechos: no genera reclamos de Content ID |
| Tipografía | Cormorant Garamond (Google Fonts) | SIL Open Font License: uso comercial libre |

## 6. Para tener el 100 % de las escenas en video

Con créditos de ElevenLabs disponibles, las 4 escenas que se resolvieron con foto animada pueden convertirse en video real con un clic. En el flow «Video Motivacional 60s – Respira. Confía. Sigue.» ya están creados los nodos `S2 Playa`, `S3b Bosque sendero`, `S4b Camino rural` y `S5 Cielo estrellado`: basta con presionar **Run**. Cuestan unos 20,000 créditos (≈ USD 4.50). Luego reemplaza los archivos en `escenas/` y vuelve a correr `bash scripts/montar_video.sh`.

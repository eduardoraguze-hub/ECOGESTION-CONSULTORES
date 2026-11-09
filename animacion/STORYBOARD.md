# Storyboard — "Ruta ESG" EcoGestión (69 s · 1920×1080 · 30 fps)

Regla de texto en pantalla: máx. 4 palabras por escena (sin contar subtítulos).
Elemento conservado: **la empresa (fábrica)** se hunde, se mide, se levanta sobre pilares, crece piso por piso y termina convertida en árbol.

| # | Guion (locución) | Acción visual (analogía dibujada literal) | Palabra → acción sincronizada | Texto en pantalla | Imagen final |
|---|---|---|---|---|---|
| 1 | Hoy, cada cliente pregunta lo mismo: ¿qué tan sostenible es tu empresa? | Aparece la fábrica gris; llegan tres clientes con globos "?" | *cliente* → entran personas · *pregunta* → globos "?" · *sostenible* → "?" gigante · *empresa* → la fábrica pulsa | ¿Qué tan sostenible? (3) | Fábrica rodeada de preguntas |
| 2 | Responder sin datos es como construir sobre arena: la primera auditoría lo derrumba. | La fábrica queda sobre un montículo de arena; una ola "Auditoría" la golpea | *arena* → aparece la arena · *auditoría* → entra la ola · *derrumba* → se inclina 9°, se hunde y se agrieta | Sobre arena · Auditoría (3) | Fábrica inclinada y agrietada |
| 3 | Por eso medimos primero: dónde estás, dónde exige el estándar, y qué tan grande es la brecha. | La fábrica se endereza y se hace a un lado; aparece una regla 0–100 a escala real (5.5 px/punto) | *medimos* → aparece la regla · *estás* → la barra sube a 42 · *estándar* → línea en 80 · *brecha* → corchete rojo de 38 + zoom de cámara, lo demás se atenúa | Brecha · 42 · 80 · 38 (4) | Corchete rojo de 38 puntos |
| 4 | Luego ponemos cimientos firmes: tres pilares, ambiental, social y gobernanza, que sostienen todo lo demás. | La regla se reduce a un medidor lateral (se conserva). La arena se vuelve losa; la fábrica flota y crecen tres pilares | *cimientos* → losa · *pilares* → la fábrica se eleva · *ambiental / social / gobernanza* → crece cada pilar (hoja, personas, balanza) · *sostienen* → se asienta; el medidor sube a 60 | Tres pilares (2) | Fábrica sobre 3 pilares |
| 5 | Sobre esos pilares, cada norma es un piso más: ISO 45001, SMETA, EcoVadis, ESR… hasta llegar a B Corp. | Cada norma cae como un piso nuevo con rebote y brillo (casco, personas, medalla, corazón) | *45001 / SMETA / EcoVadis / ESR* → cae un piso; el medidor sube 65→79 · *Corp* → bandera "B" en la azotea; el medidor cruza 80 ✓ | Piso por piso · B (4) | Edificio de 4 pisos con bandera B |
| 6 | El resultado se mide: cuarenta por ciento menos accidentes, cero no conformidades mayores, y clientes que vuelven a confiar. | El edificio se hace a un lado; barras en la misma escala (100 % = 520 px) | *mide* → panel · *cuarenta* → "−40%" · *menos* → la barra de accidentes se reduce al 60 % · *cero* → la barra de no conformidades llega a 0 · *clientes* → regresan los clientes de la escena 1 · *confiar* → los "?" se vuelven ✓ | Resultados · −40% · 0 · B (4) | Barras reducidas y clientes con ✓ |
| 7 | EcoGestión: transformamos organizaciones hacia modelos sostenibles. Agenda hoy tu diagnóstico. | La "B" se convierte en hoja; el edificio se vuelve verde y crece la copa de un árbol | *EcoGestión* → marca + hoja · *transformamos* → tinte verde y copa del árbol · *Agenda* → botón de llamada a la acción | EcoGestión · Agenda tu diagnóstico (4) | Edificio-árbol + CTA |

## Archivos
- `index.html` — animación interactiva (reproducir, línea de tiempo, saltar a escena, descargar SRT). El guion está en el arreglo `SCRIPT`; los tiempos por palabra se calculan solos y cada acción se ancla a su palabra con `A(bloque,'palabra')`.
- `ecogestion_ruta_esg.mp4` — video renderizado, listo para importar en CapCut.
- `ecogestion_ruta_esg.srt` — subtítulos con los mismos tiempos (CapCut → Texto → Subtítulos locales).
- `render.js` — vuelve a generar el MP4 y el SRT: `node render.js` (requiere Playwright y ffmpeg).

## Locución
Ritmo de ~2.6 palabras/s. Para grabar la voz en CapCut, sigue la palabra resaltada en verde en los subtítulos. Si la voz queda más lenta o más rápida, ajusta `wordDur` en `index.html` y vuelve a renderizar.

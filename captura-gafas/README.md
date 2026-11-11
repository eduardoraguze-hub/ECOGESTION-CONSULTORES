# Captura automática de evidencias con gafas inteligentes

Cada foto o video que tomas con las gafas termina, sin que tengas que hacer nada, en la carpeta de la auditoría a la que pertenece:

```
Evidencias_Auditoria/
├── Ingenio_Melchor_Ocampo/
│   └── SMETA/
│       └── 2026-11_SMETA_Anual/
│           ├── registro_evidencias.csv   ← listo para el informe
│           ├── 02_Salud_Seguridad/
│           │   ├── Fotos/20261111_093012_Ingenio_Melchor_Ocampo_SMETA_a3f9c1.jpg
│           │   └── Videos/...
│           └── 05_Trabajo_Infantil_Campo/...
├── Ingenio_Pujiltic/ISO_45001/...
├── _Sin_Clasificar/2026-11-11/...        ← lo que no se pudo ubicar
└── _registro_maestro.csv                 ← todas las evidencias de todos los ingenios
```

> **Nota:** se asume que las gafas son **Ray-Ban Meta / Oakley Meta** (o similares), que se sincronizan con la app **Meta AI** del teléfono. *SMETA* es la metodología de auditoría de Sedex, no una marca de gafas. Si tus gafas son de otra marca, el flujo es el mismo: solo cambia el paso 1.

---

## Cómo funciona (4 eslabones)

| # | Eslabón | Herramienta | Qué hace | Se configura |
|---|---------|-------------|----------|--------------|
| 1 | Gafas → Teléfono | App Meta AI | Importa fotos y videos a la galería del teléfono de forma automática | Una vez |
| 2 | Teléfono → Nube | OneDrive *Carga de cámara* (recomendado) o Google Drive/Fotos | Sube cada foto nueva | Una vez |
| 3 | Nube → PC | Cliente de escritorio de OneDrive o Drive | Sincroniza la carpeta de la cámara en la PC | Una vez |
| 4 | PC → Carpeta de auditoría | `organizador_evidencias.py` | Clasifica, renombra, calcula el hash y registra cada evidencia | Una vez + 1 comando por auditoría |

**¿Por qué no directo de las gafas a la carpeta?** Las gafas Meta no permiten elegir una carpeta de destino ni subir a la nube por su cuenta: todo pasa por la app del teléfono. La cadena de arriba es la forma estable y sin costo de lograr que el proceso sea automático.

---

## Paso 1. Gafas → teléfono (app Meta AI)

1. Abre **Meta AI** → *Dispositivos* → tus gafas → *Configuración* → *Importación de contenido* (el nombre puede variar según la versión de la app).
2. Activa la **importación automática** y la opción **Guardar en la galería / Carrete del teléfono**.
3. Activa **Ubicación** para la app Meta AI (en iOS: *Ajustes → Meta AI → Ubicación → Mientras se usa*). Con eso las fotos llevan GPS y el script reconoce el ingenio solo.
4. Para la importación, las gafas necesitan batería y el teléfono cerca. Si están en el estuche cargando, la transferencia ocurre igual.

## Paso 2. Teléfono → nube

**Opción A – OneDrive (recomendada si usas Microsoft 365 corporativo)**
App OneDrive → *Yo* → *Configuración* → **Carga de cámara: activada** → incluir videos → *Cargar con datos móviles* (opcional, para campo).
Las fotos se suben a `OneDrive/Imágenes/Álbum de cámara` (en inglés `Pictures/Camera Roll`).

**Opción B – Google Drive**
En Android, instala *Autosync for Google Drive* y vincula la carpeta `DCIM/Camera` (o la de Meta AI) a una carpeta de Drive. En iPhone, usa Google Fotos con *Copia de seguridad*, aunque Fotos no se sincroniza como carpeta: en iPhone es mejor la opción A.

## Paso 3. Nube → PC

Instala el cliente de escritorio de OneDrive (o Google Drive para escritorio) en la PC donde preparas los informes y confirma que la carpeta de la cámara aparece en el explorador.

## Paso 4. El organizador

> 👉 **Instrucciones paso a paso, sin tecnicismos: [GUIA_RAPIDA.md](GUIA_RAPIDA.md)**

| Archivo (Windows, doble clic) | Para qué |
|---|---|
| `1_INSTALAR_Y_ARRANCAR.bat` | Solo una vez: instala Python y Pillow, crea `config.json`, arranca el organizador oculto y lo programa al inicio de Windows |
| `2_ABRIR_SESION.bat` | Asistente con menú numerado: ingenio → norma → pilar |
| `3_CERRAR_SESION.bat` | Cierra la sesión |
| `4_VER_ESTADO.bat` | Sesión activa, rutas y últimas evidencias (`organizador.log`) |

En Mac/Linux: `./iniciar_mac_linux.sh`, `abrir_sesion_mac.command` y `cerrar_sesion_mac.command`.

`config.json` trae `"carpeta_entrada": "auto"` y `"carpeta_destino": "auto"`: detecta `OneDrive*/Imágenes/Álbum de cámara` (o `Pictures/Camera Roll`) y guarda en `OneDrive*/Evidencias_Auditoria`. Si prefieres otras rutas, escríbelas en lugar de `auto`.

### Ingenios y geocercas

| Código | Ingenio | Estado | lat, lon | Fuente / precisión |
|---|---|---|---|---|
| Ingenio_01 | Melchor Ocampo | Jalisco | 19.78, -104.24 | Estimada (localidad, Autlán/El Grullo): **verificar** |
| Ingenio_02 | El Higo | Veracruz | 21.7739, -98.4543 | WRI Global Power Plant Database |
| Ingenio_03 | Pujiltic | Chiapas | 16.2792, -92.4532 | Localidad San Francisco Pujiltic |
| Ingenio_04 | Mahuixtlán | Veracruz | 19.41, -96.96 | Estimada (4.3 km al S de Coatepec): **verificar** |
| Ingenio_05 | Atencingo | Puebla | 18.51, -98.61 | Localidad Atencingo |
| Ingenio_06 | San Cristóbal | Veracruz | 18.37, -95.74 | Cabecera de Carlos A. Carrillo |
| Ingenio_07 | Tamazula | Jalisco | 19.68, -103.25 | IIEG Jalisco 2026 (cabecera) |
| Ingenio_08 | Manzana | — | sin datos | No se encontró en fuentes públicas: capturar |

Cada ingenio tiene dos radios: `radio_m` (fábrica, 3–5 km) y `radio_zona_abasto_m` (campos de caña, 40 km). Los ingenios más cercanos entre sí (Melchor Ocampo y Tamazula) están a unos 104 km, así que las zonas no se traslapan.

### Antes de cada auditoría: 1 comando

```bash
python organizador_evidencias.py sesion --ingenio pujiltic --norma SMETA \
       --pilar 05_Trabajo_Infantil_Campo --auditoria 2026-11_SMETA_Anual
```

- `--ingenio` acepta el nombre (`pujiltic`, `"Ingenio San Cristóbal"`), el código (`Ingenio_03`) o el número (`3`).
- Todo lo que captures en las siguientes **12 h** (ajustable con `--horas`) se va a esa auditoría.
- ¿Cambias de pilar o de área durante el recorrido? Vuelve a ejecutar `sesion` con otro `--pilar`.
- Al terminar: `python organizador_evidencias.py cerrar`.
- Para ver qué está activo: `python organizador_evidencias.py estado`.

Si se te olvida abrir la sesión, no se pierde nada: la foto se clasifica por **GPS** en `Ingenio_XX/Inspeccion_Campo/<fecha>` y, si no tiene GPS, cae en `_Sin_Clasificar`.

---

## Reglas de clasificación

| Prioridad | Condición | Resultado |
|-----------|-----------|-----------|
| 1 | El GPS cae dentro de la **fábrica** de un ingenio y hay sesión vigente | Ingenio del **GPS**, con la norma y el pilar de la sesión. Si el ingenio no coincide con la sesión, se genera una **alerta** |
| 1b | El GPS cae en la **zona de abasto** (campo) de otro ingenio y hay sesión vigente | Manda la **sesión**, con una alerta en el registro |
| 2 | No hay GPS, pero hay sesión vigente | Ingenio, norma y pilar de la sesión |
| 3 | Hay GPS (fábrica o campo) y no hay sesión | Ingenio del GPS → `Inspeccion_Campo/<fecha>` (`GPS-fabrica` o `GPS-campo`) |
| 4 | No hay GPS ni sesión | `_Sin_Clasificar/<fecha>` |

## Valor para la auditoría (cadena de custodia)

Cada evidencia queda registrada en `registro_evidencias.csv`, que se abre directo en Excel, con estas columnas:

`id_evidencia` · `fecha_captura` · `tipo` · `ingenio` · `norma` · `auditoria` · `pilar_area` · `archivo` · `ruta_relativa` · **`sha256`** · `latitud` · `longitud` · `fuente_clasificacion` · `alerta` · `archivo_original` · `procesado_en` · **`hallazgo_vinculado`** · **`observaciones_auditor`**

- **SHA-256**: es la huella digital del archivo. Si alguien altera la foto, la huella deja de coincidir. Sirve como evidencia íntegra frente a Sedex, EcoVadis o el organismo certificador ISO.
- **Duplicados**: si el teléfono sube la misma foto dos veces, solo se guarda una.
- **`hallazgo_vinculado`**: columna vacía para que anotes el número de NC o hallazgo. Con eso la tabla se vuelve la matriz de evidencias del informe y del plan de acciones correctivas (CAPR).
- **Original intacto**: por defecto se *copia* (`"accion": "copiar"`). Cambia a `"mover"` si quieres vaciar la bandeja.

## Privacidad y cumplimiento (importante en SMETA)

- **Entrevistas a trabajadores**: SMETA exige que sean confidenciales. **No grabes entrevistas** con las gafas sin el consentimiento informado y por escrito del trabajador. Fotografía condiciones, no personas identificables, salvo que sea necesario y tengas consentimiento.
- **LFPDPPP**: las imágenes de personas son datos personales. Agrega en el aviso de privacidad del ingenio que se toman registros visuales durante las auditorías y define cuánto tiempo se conservan.
- **Trabajo infantil en campo**: documenta el hallazgo (lugar, actividad, fecha) **sin captar el rostro del menor**, y activa de inmediato el protocolo de remediación.
- **Indicador visible**: el LED de grabación de las gafas debe quedar descubierto. Avisa al inicio del recorrido que llevas un dispositivo de registro.
- **Almacenamiento**: guarda `Evidencias_Auditoria` en el OneDrive o SharePoint **corporativo**, no en una cuenta personal, y restringe el acceso al equipo auditor.

## Solución de problemas

| Síntoma | Causa probable | Solución |
|---------|----------------|----------|
| Nada llega a la PC | La carga de cámara está desactivada o el teléfono está en ahorro de batería | Abre la app de la nube en el teléfono y revisa la carga de cámara |
| Todo cae en `_Sin_Clasificar` | No hay sesión y las fotos no traen GPS | Abre una sesión o activa la ubicación en Meta AI |
| Fotos en el ingenio equivocado | Las coordenadas o el radio no son correctos | Ajusta `lat`, `lon` y `radio_m` en `config.json` |
| Videos con fecha incorrecta | Falta `ffprobe` | Instala FFmpeg (`winget install ffmpeg`) |
| Fotos HEIC sin fecha | Falta el soporte HEIC | `pip install pillow-heif` |

## Siguiente nivel (opcional)

- **Sin PC (100 % en la nube):** un escenario de Make o Zapier que, por cada archivo nuevo en OneDrive o Drive, lo mueva según una hoja de Google Sheets donde marcas la sesión activa desde el teléfono.
- **Atajo en el teléfono:** un botón de iPhone (*Atajos*) o Android (*Tasker*) que abra o cierre la sesión sin usar la PC, escribiendo `sesion_activa.json` (basta con guardar la carpeta `captura-gafas` dentro de OneDrive).
- **Informe automático:** generar a partir de `registro_evidencias.csv` el anexo fotográfico del informe SMETA (Word o PDF) con miniatura, ID, fecha y pilar.

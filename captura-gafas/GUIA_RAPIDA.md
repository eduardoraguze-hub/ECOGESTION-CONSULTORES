# Guía rápida: fotos de las gafas → carpeta de auditoría, en automático

**Tiempo total de instalación: unos 20 minutos, una sola vez.**
Después, en cada auditoría solo das **2 clics**: uno al llegar y otro al irte.

---

## La idea en una imagen

```
 👓 Gafas  ──►  📱 Teléfono  ──►  ☁️ OneDrive  ──►  💻 Tu PC  ──►  📁 Carpeta de la auditoría
 (tomas la foto)  (app Meta AI)   (sube sola)     (baja sola)    (el organizador la acomoda)
```

Tú solo tomas la foto. Todo lo demás pasa solo.

---

## PARTE A. En el teléfono (10 min, una sola vez)

### Paso 1. Que las fotos de las gafas pasen solas al teléfono
1. Abre la app **Meta AI**.
2. Entra a **Dispositivos** → tus gafas → **Configuración**.
3. Busca **Importación** y activa la **importación automática**.
4. Activa **Guardar en la galería del teléfono**.
5. Dale a la app permiso de **Ubicación**:
   - iPhone: *Ajustes → Meta AI → Ubicación → "Mientras se usa"*.
   - Android: *Ajustes → Apps → Meta AI → Permisos → Ubicación → Permitir*.

   👉 Con la ubicación activada, el sistema reconoce **solo** en qué ingenio estás.

### Paso 2. Que el teléfono suba las fotos a OneDrive
1. Instala **OneDrive** y entra con tu cuenta **de la empresa**.
2. Toca tu foto de perfil → **Configuración** → **Carga de cámara** → **Activar**.
3. Activa **Incluir videos**.
4. (Recomendado para campo) Activa **Usar datos móviles**.

✅ **Prueba:** toma una foto con las gafas y, en unos minutos, búscala en OneDrive → *Imágenes* → *Álbum de cámara*.

---

## PARTE B. En la PC (10 min, una sola vez)

### Paso 3. Que OneDrive esté en tu PC
En Windows 10/11 ya viene instalado. Revisa que en el Explorador de archivos, a la izquierda, aparezca **OneDrive** con tu cuenta de la empresa.

### Paso 4. Descargar la carpeta `captura-gafas`
Copia la carpeta `captura-gafas` de este repositorio a tu PC, por ejemplo en **Documentos**.

### Paso 5. Instalar (doble clic)
Haz doble clic en **`1_INSTALAR_Y_ARRANCAR`**. Ese archivo:
- instala lo necesario (si te pide permiso para instalar Python, acepta y vuelve a hacer doble clic);
- detecta tu OneDrive **solo**, sin que configures rutas;
- deja el organizador trabajando y programa que **arranque solo cada vez que enciendas la PC**.

Al terminar te muestra:
```
Entrada: C:\Users\...\OneDrive\Imágenes\Álbum de cámara     ← de aquí toma las fotos
Destino: C:\Users\...\OneDrive\Evidencias_Auditoria         ← aquí las acomoda
```

✅ **Listo. No tienes que volver a hacer esto.**

---

## PARTE C. En cada auditoría (2 clics)

### 🟢 Al llegar: doble clic en `2_ABRIR_SESION`
Te pregunta 3 cosas. Contestas con un número y Enter:

```
¿En qué ingenio estás?                  ¿Qué norma o tipo de visita?
   1. Ingenio Melchor Ocampo               1. SMETA
   2. Ingenio El Higo                      2. ISO_45001
   3. Ingenio Pujiltic          ◄── 3      3. ISO_14001   ...
   ...

¿Qué pilar o área vas a recorrer?
   1. 01_Trabajo
   2. 02_Salud_Seguridad
   ...
   5. 05_Trabajo_Infantil_Campo  ◄── 5
```

Luego pulsa **Enter** para aceptar el nombre de la auditoría. Desde ese momento, **todo lo que captures con las gafas se guarda solo** en esa auditoría.

> ¿Cambias de área a media visita? Vuelve a abrir `2_ABRIR_SESION` y elige otro pilar.

### 🔴 Al terminar: doble clic en `3_CERRAR_SESION`
> Si se te olvida, la sesión se cierra sola a las 12 horas.

### 👀 Para revisar: doble clic en `4_VER_ESTADO`
Muestra la sesión activa y las últimas fotos que se acomodaron.

---

## ¿Dónde quedan mis fotos?

```
OneDrive\Evidencias_Auditoria\
 ├─ Ingenio_Pujiltic\
 │   └─ SMETA\
 │       └─ 2026-11_SMETA\
 │           ├─ registro_evidencias.csv      ◄── ábrelo en Excel: es tu matriz de evidencias
 │           └─ 05_Trabajo_Infantil_Campo\
 │               ├─ Fotos\
 │               └─ Videos\
 ├─ Ingenio_Atencingo\ ...
 ├─ _Sin_Clasificar\                          ◄── revisa aquí lo que no se pudo ubicar
 └─ _registro_maestro.csv                     ◄── todas las evidencias de los 8 ingenios
```

En el Excel `registro_evidencias.csv` tienes, por cada foto: fecha, hora, ingenio, pilar, coordenadas y su **huella digital (SHA-256)**, que prueba que la foto no fue alterada. Hay dos columnas vacías para ti: **`hallazgo_vinculado`** (anota el número de la no conformidad) y **`observaciones_auditor`**.

## ¿Y si olvido abrir la sesión?

No se pierde nada:

| Situación | Dónde queda la foto |
|---|---|
| Estás en la **fábrica** de un ingenio (hasta 3–5 km) | `Ingenio_X\Inspeccion_Campo\<fecha>` |
| Estás en los **campos de caña** de un ingenio (hasta 40 km) | `Ingenio_X\Inspeccion_Campo\<fecha>` (registrada como *GPS-campo*) |
| Sin ubicación ni sesión | `_Sin_Clasificar\<fecha>`: muévela a mano |

---

## Paso 6 (recomendado, 5 min). Afinar las coordenadas

Las coordenadas vienen cargadas desde fuentes públicas y apuntan al poblado de cada ingenio. Para mayor precisión, sobre todo en **Melchor Ocampo** y **Mahuixtlán**, que son estimadas:

1. Abre **Google Maps** y busca el ingenio.
2. Haz **clic derecho** sobre la fábrica: el primer renglón son las coordenadas (ej. `16.2792, -92.4532`). Haz clic en ellas para copiarlas.
3. Abre `config.json` con el **Bloc de notas**, busca el ingenio y reemplaza `lat` (primer número) y `lon` (segundo número).
4. Guarda el archivo. El cambio aplica desde la siguiente foto.

| # | Ingenio | Estado | Coordenadas cargadas | Precisión |
|---|---|---|---|---|
| 01 | Melchor Ocampo | Jalisco (Autlán / El Grullo) | 19.78, -104.24 | ⚠️ Estimada: verificar |
| 02 | El Higo | Veracruz | 21.7739, -98.4543 | ✅ Punto de la planta |
| 03 | Pujiltic | Chiapas (Venustiano Carranza) | 16.2792, -92.4532 | ✅ Localidad |
| 04 | Mahuixtlán | Veracruz (Coatepec) | 19.41, -96.96 | ⚠️ Estimada: verificar |
| 05 | Atencingo | Puebla (Chietla) | 18.51, -98.61 | ✅ Localidad |
| 06 | San Cristóbal | Veracruz (Carlos A. Carrillo) | 18.37, -95.74 | ✅ Cabecera |
| 07 | Tamazula | Jalisco (Tamazula de Gordiano) | 19.68, -103.25 | ✅ Cabecera |
| 08 | Puga (Manzana) | Nayarit (Francisco I. Madero, Tepic) | 21.5825, -104.8244 | ✅ Localidad |

> Los 8 ingenios ya tienen coordenadas. En el menú, el Ingenio Puga también se encuentra como *Manzana*.

---

## Problemas comunes

| Si pasa esto… | Haz esto |
|---|---|
| No llega ninguna foto a la PC | En el teléfono abre OneDrive y revisa que *Carga de cámara* esté activa |
| Las fotos caen en `_Sin_Clasificar` | Abre una sesión (🟢) o activa la ubicación de Meta AI |
| Fotos en el ingenio equivocado | Afina las coordenadas (Paso 6) |
| Después de reiniciar no funciona | Vuelve a dar doble clic en `1_INSTALAR_Y_ARRANCAR` |

## ⚠️ Regla de oro SMETA
**No grabes entrevistas a trabajadores ni rostros de menores.** Fotografía condiciones, lugares y documentos. Si necesitas grabar a una persona, pide antes su consentimiento por escrito.

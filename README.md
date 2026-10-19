# Huella e Impacto Hídrico de la Palta en Chile 🥑💧

Proyecto de visualización de datos y narrativa interactiva para la web (GitHub Pages), enfocado en analizar la relación entre la producción y exportación de palta en Chile y la crisis de escasez hídrica que afecta a las cuencas del país.

---

## 👥 Integrantes del Proyecto
- **Pablo**
- **Alonso**
- **Boris**

---

## 📖 Descripción General del Proyecto

Chile se posiciona como uno de los líderes mundiales en la exportación de palta (aguacate). Sin embargo, este éxito agroexportador oculta una paradoja crítica: las regiones con mayor superficie de plantaciones de palto son exactamente aquellas que acumulan la mayor cantidad de decretos de escasez hídrica y donde miles de familias dependen de camiones aljibe para su consumo diario.

El objetivo de esta plataforma interactiva es **guiar al usuario paso a paso**, mediante una narrativa de datos (storytelling interactivo), para comprender:
1. **La magnitud de la huella hídrica:** cuántos litros de agua requiere una sola palta y cómo se compara con consumos vitales diarios y raciones legales garantizadas.
2. **El impacto territorial y correlación geográfica:** cómo la concentración de plantaciones en Valparaíso, Coquimbo y la Región Metropolitana coincide con las zonas de mayor sequía, complementado con una experiencia sonora interactiva (monedas vs. gotas de agua).
3. **El flujo de agua virtual:** cuánta agua dulce abandona el territorio nacional a través de las exportaciones de este fruto.
4. **La conclusión fundamentada en los datos:** el costo hídrico que el mercado global no refleja en el precio final.

---

## 🚀 Resumen de Cambios Realizados

A partir de la versión inicial, se realizaron las siguientes transformaciones estructurales, estéticas y funcionales:

### 1. Transformación a Narrativa Guiada (Scrollytelling Interactivo)
- Se reemplazó la estructura estática tradicional por una **presentación interactiva de 5 diapositivas a pantalla completa (`100dvh`)**.
- La portada incluye un titular contundente, una síntesis del problema y un **botón pulsante de llamada a la acción** que invita al usuario a iniciar el recorrido guiado.

### 2. Control de Rueda del Mouse Ágil y sin Puntos Medios (Slide-by-Slide Lock)
- **Problema resuelto:** Anteriormente, el scroll del mouse podía dejar la pantalla cortada a mitad de camino entre dos secciones, o se sentía "pegado" al intentar avanzar con rapidez. Además, al situar el cursor sobre los `<iframe>` de las visualizaciones, el scroll dejaba de responder.
- **Solución implementada:**
  - **Latencia reducida a 360 ms:** Se ajustó el mecanismo de enfriamiento (*cooldown*) a 360 ms, logrando una transición inmediata, ágil y reactiva sin saltos involuntarios.
  - **Captura universal de scroll (incluso sobre visualizaciones):** Se implementó una doble vía de captura: listener con `capture: true` en la ventana principal, inyección directa de listeners a los `contentWindow` de los iframes al cargar y retransmisión por `postMessage` (`wheel-scroll`) desde el interior de `visualizaciones/escala_agua/index.html` y `visualizaciones/mapa_interactivo_agua.html`. El scroll ahora responde fluidamente en cualquier píxel de la pantalla.
  - **Soporte multiplataforma:** Se añadieron controles por teclado (`ArrowDown`, `ArrowUp`, `PageDown`, `PageUp`, `Space`) y gestos táctiles (*swipe vertical* para dispositivos móviles y tablets).

### 3. Reescalado Responsivo y Navegación Unificada (Sin Solapamientos ni Botones Duplicados)
- **Problema resuelto:** En computadores portátiles y pantallas de diversas resoluciones (por ejemplo, 1366×768 o 1920×1080 con escala al 125%), el contenido y la barra flotante inferior se solapaban con las visualizaciones. Además, existían botones duplicados de navegación ("Anterior" y "Siguiente" dentro de cada slide y a la vez en la barra inferior), lo que generaba ruido visual y confusión.
- **Solución implementada:**
  - **Ventana flotante de curiosidad ("Curiosity Push"):** En lugar de un botón convencional y frío de "Siguiente", la barra flotante cuenta con un **botón protagonista azul celeste con pulso de resplandor (`glow-pulse`)** que formula una **pregunta intrigante por cada diapositiva**:
    - *En Slide 1:* "¿Cómo se ven los paltos y la escasez en Chile? →"
    - *En Slide 2:* "¿Cuánta agua dulce se va del país al exportar? →"
    - *En Slide 3:* "¿Cuál es el verdadero costo detrás de estos datos? →"
    - *En Slide 4:* "¿Volver a explorar la historia desde el inicio? ↺"
    Este estímulo genera un *curiosity gap* irresistible que motiva al receptor a hacer clic para descubrir la respuesta en la siguiente visualización.
  - **Dock de navegación unificado y despejado (`#nav-flotante`):** Centraliza la navegación con botón de retroceso `←`, indicadores de punto (*dots*) interactivos y el botón disparador de curiosidad.
  - **Reserva de espacio inferior anti-solapamiento:** Cada diapositiva cuenta con un margen de seguridad inferior de hasta `6.8rem` (`padding-bottom: clamp(5.4rem, 9.5vh, 6.8rem)` y `max-height: calc(100dvh - 6.8rem)`), asegurando que **las visualizaciones terminen holgadamente antes del dock y jamás se solapen con él** en ningún dispositivo.

### 4. Aprovechamiento Panorámico de Pantalla (Widescreen Layout)
- **Problema resuelto:** La visualización original utilizaba una columna angosta centrada de 960 px pensada para móviles, dejando desaprovechados los dos tercios laterales de los monitores de escritorio.
- **Solución implementada:**
  - **Diapositiva 1 (Escala Hídrica):** Se implementó un diseño de rejilla panorámica (*split-screen* de hasta 1520 px de ancho). En la columna izquierda se ubica la narrativa explicativa, las métricas clave (1.981 L/kg, 320 L/palta, 50 L ducha) y los botones de navegación; en la columna derecha se expande la visualización interactiva de la escala de agua ocupando todo el ancho y alto disponible.
  - **Diapositiva 2 (Mapas de Chile):** Se organizó en un layout horizontal donde la columna izquierda contiene la explicación, el botón de activación de sonido y la navegación, mientras que la columna derecha muestra en paralelo los dos mapas de Chile con sus escalas y tooltips.
  - **Optimización de `visualizaciones/escala_agua/index.html`:** Se amplió su contenedor a formato fluido de hasta 1300 px y se compactaron sus márgenes verticales para una experiencia inmersiva de escritorio.

### 5. Preservación del Trabajo del Equipo
- Se mantuvieron **completamente intactos los códigos y datos de las visualizaciones desarrolladas por los compañeros**:
  - El script SVG interactivo del mapa de Chile (vectores geográficos de todas las regiones y cálculo de colores por hectáreas y decretos).
  - La síntesis de audio Web Audio API (efectos de monedas en base64 para representar el valor comercial del palto y gotas sintetizadas para la escasez hídrica).
  - El mapa interactivo regional generado en Python/Plotly (`visualizaciones/mapa_interactivo_agua.html`).
  - La lógica de comunicación mediante `postMessage` para el ajuste de alturas de iframes.

---

## 💻 Explicación Detallada de la Arquitectura y Código HTML (`index.html`)

El archivo principal `index.html` está estructurado en capas bien definidas que combinan estética, interacción y visualización de datos:

### 1. Variables CSS y Sistema de Diseño (`<style>`)
- **Paleta Temática:**
  - `--agua-1` (`#0d3b4a`), `--agua-2` (`#1f7a8c`), `--agua-3` (`#4dc2d7`): Gama de celestes y azules profundos que representan el recurso hídrico.
  - `--palta-1` (`#4c6b2f`), `--palta-2` (`#8a9a3a`), `--palta-3` (`#c5d96a`): Gama de verdes oliva y lima para representar las plantaciones de palto.
  - `--bg-dark` (`#070f0d`), `--card-bg` (`#0e2420`): Fondos oscuros de alto contraste que reducen la fatiga visual y realzan los datos.
- **Tipografía:**
  - `Fraunces`: Tipografía serif de estilo editorial para títulos y números destacados.
  - `Inter`: Tipografía sans-serif de alta legibilidad para textos descriptivos y controles.

### 2. Capa de Fondo y Partículas (`#particles`)
- Un contenedor flotante de partículas circulares con degradados semitransparentes animadas mediante CSS (`@keyframes float-particle`), que simula burbujas microscópicas ascendentes en el agua para ambientar sutilmente la lectura.

### 3. Estructura de Diapositivas (`#story`)
El contenedor `#story` aloja 5 secciones `<section class="slide">` identificadas de `slide-0` a `slide-4`:
- **`#slide-0` (Portada):** Introduce la pregunta de investigación con tipografía de gran escala, destacando la cifra de *320 litros por palta* y un botón de inicio con sombra resplandeciente (`--btn-glow`).
- **`#slide-1` (El Costo Hídrico):** Presenta el layout panorámico de dos columnas:
  - *Columna izquierda:* Tarjetas estadísticas comparativas (`.metrica-card`) y navegación contextual.
  - *Columna derecha:* **Nueva TV integrada** (antes un `<iframe>`): `.tv-container` que contiene todo el HTML/CSS/JS de la visualización de la escala de agua. El contenedor reemplaza al iframe para eliminar latencia de carga y mejorar el escalado en resoluciones bajas/medianas. El controles interactivos (botones de escala) ahora actualizan la TV localmente mediante `window.cambiarEscala(idx)`.

- **`#slide-2` (El Territorio - Plantaciones vs. Escasez):**
  - Muestra la comparativa geográfica directa entre dos mapas SVG sincronizados:
    1. `#m-palto`: Coloración proporcional a la superficie de hectáreas cultivadas.
    2. `#m-escasez`: Coloración proporcional al número acumulado de decretos de escasez hídrica emitidos por el Ministerio de Obras Públicas.
  - Incluye el botón interactivo `#btn-sonido` que activa la audificación de datos al posar el ratón sobre cada región.
- **`#slide-3` (El Agua en Cifras):**
  - Integra en un marco expandido el mapa coroplético generado en Plotly (`visualizaciones/mapa_interactivo_agua.html`), permitiendo analizar el volumen de metros cúbicos exportados por región.
- **`#slide-4` (Conclusión y Fuentes):**
  - Síntesis editorial del impacto socioambiental de la industria de la palta en Chile, detalle de las fuentes oficiales consultadas (DGA, ODEPA, CIREN, INE) y botón de retorno al inicio.

### 4. Barra Flotante de Navegación (`#nav-flotante`)
- Elemento de navegación omnipresente situado en la parte inferior central con efecto de desenfoque de cristal (*glassmorphism*).
- Contiene botones circulares `←` y `→`, acompañados por indicadores de punto (*dots*) que muestran en qué paso se encuentra el usuario y permiten saltar directamente a cualquier diapositiva. Se oculta automáticamente en la portada para mantener la limpieza visual.

### 5. Lógica JavaScript
- **Motor de Transición de Slides:** La función `irASlide(n)` alterna la clase CSS `.activo` en las diapositivas, aplicando una transición simultánea de opacidad y desplazamiento vertical de 35 píxeles con una curva de aceleración cúbica personalizada (`cubic-bezier(0.2, 0.8, 0.2, 1)`).
- **Gestor de Rueda del Ratón (`wheel` listener):** Controla la dirección del desplazamiento y aplica un bloqueo de 750 ms mediante la variable `isScrolling`, eliminando rebotes o avances involuntarios en touchpads.
- **Gestores de Teclado y Táctil:** Capturan eventos de flechas de teclado y gestos de deslizamiento (*swipe* de más de 45 píxeles) para una navegación natural en cualquier dispositivo.
- **Lógica de Mapas y Audio Web (preservada):** Decodifica buffers de audio en Base64, sintetiza frecuencias y osciladores mediante `AudioContext`, genera los mapas SVG mediante coordenadas vectoriales de Chile y maneja el tooltip flotante `#globo`.

---

## 📁 Estructura del Repositorio

```text
├── index.html                           # Página principal para GitHub Pages (relato interactivo)
├── README.md                            # Documentación y guía del proyecto
├── css/
│   └── estetica.css                     # Variables globales de estilo
├── data/
│   ├── processed/                       # Datasets limpios (catastro, decretos de escasez, censo)
│   └── raw/                             # Estudios y documentos técnicos de referencia
├── scripts/
│   ├── carga_datos_y_creacion_mapa.ipynb # Generador de datos geográficos para el mapa SVG
│   ├── datos_palta_x_region.py          # Procesamiento de exportaciones y hectáreas
│   └── json_para_balanza.ipynb          # Cálculos de equivalencia para camiones aljibe
├── sonido stock/                        # Archivos de audio originales (monedas, gotas, agua)
└── visualizaciones/
    ├── escala_agua/index.html           # Visualizador interactivo de equivalencias hídricas
    ├── mapa_interactivo_agua.html       # Mapa coroplético exportado desde Plotly
    └── balanza/                         # Módulo complementario de balanza hídrica
```

---

## 🤖 Bitácora de Muse Spark (asistente)

> Esta sección es solo mía: aquí registro cada cambio que ejecuto en el proyecto, con fecha, archivo y motivo. No edita el contenido del equipo, solo documenta mi trabajo.

### 2026-10-19 · Dock `#nav-flotante` a la derecha + brillo atenuado
- **Archivo:** `index.html` (CSS de `#nav-flotante`, `.btn-curiosidad`, `glow-pulse`, `.nav-dot.activo`, `--btn-glow`).
- **Cambio:** dock movido de `left:50% + translateX(-50%)` a `right: clamp(0.8rem,1.8vw,1.4rem)` manteniendo el mismo `bottom` (mismo eje Y). Brillo bajado: fondo `0.94→0.78` + `opacity 0.82` (1.0 solo en hover/foco), sombras y `glow-pulse` reducidos a la mitad, animación más lenta (2.8s→4.2s).
- **Motivo:** pedido de mover la ventana flotante a la derecha del todo sin quitar protagonismo a las visualizaciones.

### 2026-10-19 · Visualización 1 (costo hídrico): layout + escala a 3 pasos
- **Archivos:** `index.html` (`.panoramico-layout`, `.col-narrativa`, `.col-viz`, métricas del slide 1) y `visualizaciones/escala_agua/index.html` (`ESCALAS`, header/badge).
- **Layout:** texto izquierda más a la izquierda (`330px`, `translateX` negativo, `justify-self:start`); visualización centrada (`max-width 1180px`, `justify-self:center`, `max-height calc(100dvh-2.4rem)`).
- **Verdad respetada:** 1 palta = 100 L = 1 ración diaria; 1 ton = 1.000.000 L; cosecha Chile 25–26 = 265.000 ton (Diario Frutícola / Paltas de Chile, 01-06-2026) = 265.000.000 m³.
- **Nueva escala (3 botones):** `🥑 1 palta` → "1 día de agua para 1 persona" · `📦 1 tonelada` → "27 años para 1 persona · o 1 día para un pueblo de 10.000 personas (ej. Petorca, Valparaíso)" (≈10.000 días-persona / 27,4 años; 1.000.000 L / 100 L) · `🏙️ Chile 25–26` → "~11 meses de agua para todo Santiago (RM, ~8 M)" (2.650 M raciones / 8 M = 331 días ≈ 11 meses). Densidad de 🥑 rebajada en pasos grandes (220/300 en vez de 400/800) para no saturar la estética.
- **Métricas del slide alineadas:** `100 L = 1 día`, `1 M L = 27 años o 1 día Petorca`, `~11 meses = Santiago con cosecha 25–26` (antes decían 1.981 L/kg, 320 L/palta y 50 L ducha, que contradecían la visualización).
- **Motivo:** pedido de mover texto, centrar viz y cambiar valores a ejemplos concretos en días/años/meses (Santiago y Valparaíso como testeo). Pendiente: afinar detalles estéticos paso a paso.

### 2026-10-19 · Visualización 1: emojis y textos más descriptivos
- **Archivo:** `visualizaciones/escala_agua/index.html` (`ESCALAS`: `btnLabel`, `icon`, `valor`, `desc`).
- **Cambio:** `1 palta` → botón e icono `🧍`, valor "1 día de agua" + "para 1 persona (ración diaria de 100 L)" · `1 tonelada` → botón `🏘️`, icono `🏘️💧`, valor "27 años de agua" + "para 1 persona · o 1 día para Petorca entero" · `Chile 25–26` → botón `🏘️🏘️🏘️`, icono `🏘️🏘️🏘️`, valor "11 meses de agua" + "para todo Santiago" (antes "~11 meses" solo y un subtítulo largo con RM/8 millones).
- **Motivo:** pedido de hacer los 3 pasos autoexplicativos: persona para 1 palta, casas/pueblo para tonelada y muchas casas/ciudad para Chile 25–26, con textos cortos.

### 2026-10-19 · Visualización 1: coherencia burbujas + redistribución tripartita + etiquetas con ~1.100 L/kg
- **Archivos:** `visualizaciones/escala_agua/index.html` (paleta, layout, HTML, `ESCALAS`, estilos) e `index.html` (slide 1, portada).
- **1. Estética coherente:** paleta de la viz igualada al slide (`--bg #071512`, `--card #0e2420`, fondo `linear-gradient(145deg,#071512,#0a1f1a)`); se mantienen las burbujas flotantes que te gustan; slide 1 con halo radial sutil (`::before`) en el mismo tono agua/palta.
- **2. Redistribución:** viz pasa de bipartito (paltas | equivalencia + botones abajo) a tripartito que usa todo el ancho: `paltas en litros | centro vital | botones a la derecha del todo` (columna vertical con título "Elige cantidad"); pregunta central agrandada (`equiv-valor` 1.4–2.3rem → 2–3.1rem); litros integrados bajo las paltas (`.litros-mini` pastilla 💧) en vez de fila separada; esencia intacta: paltas ↔ litros de agua en cada paso.
- **3. Texto izquierda reestructurado:** pregunta intacta y agrandada (1.5–2.3rem → 2–3rem); texto contextual eliminado por completo; etiquetas rehechas: `~1.100 L por kilo (≈10 paltas)` + `100 L por 1 palta = 1 día` + `100 L/día ración legal mínima` (la ración legal sale de la viz y vive solo en el slide); `white-space:nowrap` en `.num` y etiquetas alineadas a la izquierda para que "100 L" y "100 L/día" nunca partan la L a otra línea.
- **Dato base sincerado:** ~1.100 L/kg → 1 palta ≈ 110 L (≈1 ración); 1 ton = 1,1 M L = "30 años para 1 persona · o 1 día para Petorca entero"; Chile 25–26 = 291,5 M m³ = "12 meses de agua para todo Santiago"; portada 100→110 L.
- **Motivo:** pedido de coherencia estética, redistribución con botones a la derecha y centro vital, y etiquetas sin saltos de línea con el dato de ~1.100 L/kg.

### 2026-10-19 · Slide 1 modo TV: título esquinado + control remoto fuera del iframe
- **Archivos:** `index.html` (grilla, `.col-narrativa`, `.control-remoto`, `cambiarEscala`) y `visualizaciones/escala_agua/index.html` (TV de 2 columnas, listener `postMessage`).
- **1. Pregunta más protagonista:** título `2–3rem→2.6–4rem`, `weight 900`, separado de la leyenda (`margin-bottom` 1.4–2.6rem); columna con `justify-content:flex-start`, más a la izquierda (`translateX` −2rem/−2.5vw) y título con `padding-top` arriba; etiquetas intactas, solo reagrupadas bajo "Leyenda · base del cálculo".
- **2. TV + remoto:** el `index.html` principal mete la viz con `<iframe id="iframe-escala">` dentro de `.col-viz` (la "ventana flotante/TV": solo muestra paltas ↔ litros ↔ equivalencia, grande y visual); los botones salieron del iframe y viven en `index.html` como `<aside class="control-remoto">` integrado al slide a la derecha (misma altura, `align-self:center`, `justify-self:end`, 190px); `cambiarEscala(i)` marca `.activo` y hace `postMessage({escala:i})`; la TV escucha `message` y llama `setScale(i)`. Esencia intacta: el remoto cambia lo que se ve en el medio.
- **Motivo:** pedido de mover el título más arriba/izquierda y separar TV (centro) / remoto (derecha, eje X del slide) / leyenda-contexto (izquierda).

### 2026-10-19 · Título sin línea invisible + remoto grande + TV panorámica sin header
- **Archivos:** `index.html` (grilla, `#slide-1`, `.control-remoto`, `.col-viz`) y `visualizaciones/escala_agua/index.html` (header, panel, columnas).
- **1. Título más a la izquierda:** la "línea invisible" era el `padding` lateral del `.slide` + el `max-width` centrado del layout; en `#slide-1` anulé `padding-left:0` y puse el layout a `width:100% + max-width:none`, con la columna en `margin-left` negativo (−0.5 a −2vw) y `overflow:visible` en vez de `translateX` (que recortaba). Grilla a `300px 1fr 230px`.
- **2. Remoto más grande:** `190→230px`, padding `0.9→1.2rem`, botones `0.7→1rem` padding y `0.86→1.02rem` fuente.
- **3. Header de la TV fuera:** eliminado el `<div class="header">¿Cuánta agua hay en una palta?` del iframe (ese título ya vive en el slide padre); quitados sus estilos huérfanos.
- **4. TV ancha y baja, contenido al 100%:** `.wrap` sin padding y centrado vertical; panel panorámico; columnas `1.1fr/1fr` con `min-height:340px` y contenido centrado; números agrandados (paltas 2.2–3.4rem, equivalencia 2.4–3.6rem, icono 4.4rem, campo 🥑 hasta 460px); `.col-viz` padre sin `max-width:1180px`: `stretch + align-self:center` con `min-height:52vh`, o sea ancha y baja en vez de alta y angosta.
- **Motivo:** pedido de romper la línea invisible del título, agrandar el remoto, quitar el título duplicado de la TV y que la info llene la ventana.

### 2026-10-19 · TV menos exagerada (980px)
- **Archivo:** `index.html` (`.col-viz`).
- **Cambio:** TV de `stretch` sin tope → `max-width: min(980px, 100%)` centrada. Se mantiene ancha y baja pero sin exagerar.
- **Motivo:** pedido de probar la visualización principal un poco menos ancha.

### 2026-10-19 · Título en 2 líneas + leyenda separada + TV 1060px equilibrada
- **Archivo:** `index.html` (grilla, `#slide-1`, `.col-narrativa`, `.slide-titulo-compact`, `.col-viz`, responsive).
- **Cambio:** título movido a la derecha (se elimina el `margin-left` negativo y el `padding-left:0`; vuelve el padding simétrico del slide); columna ensanchada `300→430px` para que el título quepa en 2 líneas (`¿Cuánta agua cuesta / producir una palta?` con `span.salto`, `max-width:20ch`, tamaño `2.2–3.2rem`) en vez de 1 palabra por fila; `.col-narrativa` pasa a grid de 3 filas (`auto 1fr auto`) con `.bloque-medio` espaciador: título y leyenda son objetos separados, leyenda abajo y recostada a la TV (`justify-self:end`, `max-width:330px`); TV `980→1060px` con `min-height:56vh` y `margin auto` arriba/abajo para el mismo aire; slide con padding vertical parejo.
- **Motivo:** pedido de mover el título a la derecha sin apilado, separar título de leyenda con la leyenda cerca de la viz, y TV un poco más ancha con aire parejo.

### 2026-10-19 · 1 emoji por etiqueta + escalado 2ª vuelta + título +30%
- **Archivos:** `index.html` (cards, grilla, título, remoto) y `visualizaciones/escala_agua/index.html` (columnas, emojis, litros, responsive).
- **1. Emojis:** 1 grande por etiqueta al lado del número (`grid auto auto 1fr`, `.ico` 1.5–2rem): `⚖️ ~1.100 L`, `🥑 100 L`, `🚰 100 L/día`; textos limpios sin emojis intermedios.
- **2. Escalado 2ª vuelta:** grilla `minmax(280px,400px)/minmax(160px,220px)` + breakpoint 1360px (cubre laptops 1366 con escala 125%) y 1100px (split-screen); título, números, iconos y remoto con tamaños reducidos en esos cortes; TV `height:clamp(360px,60vh,560px)`; columnas internas `min-height:0 + overflow:hidden`; campo 🥑 con `max-height:18vh` y emojis por `vh`; pastilla litros con piso bajo y sin `nowrap` forzado en móvil; iframe con media 560px para cuando el padre le da poco ancho. Si tu pantalla chica sigue deformando algo puntual, dime qué elemento exacto y lo ataco.
- **3. Título +30%:** `2.5–3.7rem → 3.2–4.8rem` (2 líneas intactas por `max-width:20ch`).
- **Motivo:** pedido de 1 emoji grande por etiqueta, más vueltas al ajuste de resolución y título 30% más grande.

### 2026-10-19 · Escalado fluido + título más grande + emojis en leyenda
- **Archivos:** `index.html` (grilla, `.col-viz`, título) y `visualizaciones/escala_agua/index.html` (panel, columnas, fuentes).
- **1. Escalado arreglado:** no puedo ver tu pantalla, pero la deformación venía de columnas fijas (`430px`, `minmax(220px,...)`) + `min-height:340px` rígidos + iframe con `height:100%` sin altura garantizada. Ahora: grilla padre con `minmax(300px,430px) ... minmax(170px,230px)` + breakpoint a 1280px (laptops 1366, ventanas partidas) que compacta a `260–340px / 150–190px` y baja el título; TV con `height: clamp(380px,62vh,560px)` garantizada; columnas internas con `minmax(0,...)`, `min-height:0`, `overflow:hidden` para no empujar; fuentes con `clamp` de piso bajo (ej. equivalencia `1.7rem–3.6rem`, icono `2.6–4.4rem`) para que en pantallas chicas todo encoge en vez de deformarse.
- **2. Título más grande:** `2.2–3.2rem → 2.5–3.7rem` (se mantiene en 2 líneas por `max-width:20ch`).
- **3. Emojis en etiquetas:** título leyenda `📖`; kilo `⚖️🥑`; palta `🧍🥑💧`; ración legal `📜🚰🇨🇱`.
- **Motivo:** pedido de arreglar deformación en pantalla pequeña, agrandar fuente del título y sumar emojis pertinentes.

### 2026-10-19 · TV incorporada al index (reemplazo del iframe)
- **Archivos:** `index.html` (`#slide-1`, `.tv-container`) y `visualizaciones/escala_agua/index.html` (seguro, como visualización independiente).
- **Cambio:** El `<iframe id="iframe-escala">` de `#slide-1` fue reemplazado por un contenedor `.tv-container` que contiene todo el HTML, CSS y JS de la visualización de la escala. Los controles del remoto (`control-remoto`) ahora actualizan la TV directamente mediante `window.cambiarEscala(idx)`, sin necesidad de comunicación entre documentos (elimina latencia de iframe y el doble parseo de DOM). El diseño mantiene la estética original del recuadro con borde, sombra y `border-radius:20px`, y se escala con `clamp` para resoluciones bajas/medianas.
---

## 🛠️ Cómo Visualizar Localmente

1. Clona el repositorio o descarga la carpeta del proyecto.
2. Abre una terminal en la raíz del proyecto e inicia un servidor local simple:
   ```bash
   python -m http.server 8000
   ```
3. Ingresa a `http://localhost:8000/` en tu navegador web preferido.
4. Para la versión en producción, los cambios se publican automáticamente a través de la rama configurada en **GitHub Pages**.

import os
import pandas as pd
import urllib.request
import json
import plotly.graph_objects as go

# --- 1. PARÁMETROS Y RUTAS ---
RENDIMIENTO_TON_POR_HA = 10 
PORCENTAJE_EXPORTACION = 0.55
AGUA_POR_TON_PRODUCIDA = 1000 

ruta_actual = os.getcwd()
ruta_base = os.path.dirname(ruta_actual) if ruta_actual.endswith('scripts') else ruta_actual
ruta_paltas = os.path.join(ruta_base, 'data', 'processed', 'catastro_paltas_2016_2025 (1).parquet')
carpeta_vis = os.path.join(ruta_base, 'visualizaciones')
ruta_html = os.path.join(carpeta_vis, 'mapa_interactivo_agua.html')
os.makedirs(carpeta_vis, exist_ok=True)

# --- 2. CARGA Y PROCESAMIENTO DE DATOS ---
df_paltas = pd.read_parquet(ruta_paltas)
df_paltas['Superficie (ha)'] = df_paltas['Superficie (ha)'].astype(str).str.replace(',', '.').astype(float)

def limpiar_region(nombre):
    nombre = str(nombre).replace('Región de ', '').replace('Región del ', '').replace('Región ', '').strip()
    if 'Metropolitana' in nombre: return 'Metropolitana'
    if 'Higgins' in nombre: return "O'Higgins"
    if 'bio' in nombre.lower() or 'bío' in nombre.lower(): return 'Biobío'
    if 'Araucanía' in nombre: return 'La Araucanía'
    return nombre

df_paltas['Region_std'] = df_paltas['Region'].apply(limpiar_region)
datos_mapa_original = df_paltas.groupby('Region_std')['Superficie (ha)'].sum().reset_index()

url_geojson = "https://raw.githubusercontent.com/caracena/chile-geojson/master/regiones.json"
req = urllib.request.Request(url_geojson, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as response:
    chile_geojson = json.loads(response.read().decode())

excluir_sur = ['Biobío', 'Araucanía', 'Ríos', 'Lagos', 'Aysén', 'Magallanes']
features_filtradas = []
regiones_completas = []

for feature in chile_geojson['features']:
    reg = limpiar_region(feature['properties']['Region'])
    if not any(x in reg for x in excluir_sur):
        feature['properties']['Region_std'] = reg
        features_filtradas.append(feature)
        regiones_completas.append(reg)

chile_geojson['features'] = features_filtradas

df_todas = pd.DataFrame({'Region_std': regiones_completas})
datos_mapa = pd.merge(df_todas, datos_mapa_original, on='Region_std', how='left').fillna(0)

datos_mapa['Palta_Producida'] = datos_mapa['Superficie (ha)'] * RENDIMIENTO_TON_POR_HA
datos_mapa['Agua_Total'] = datos_mapa['Palta_Producida'] * AGUA_POR_TON_PRODUCIDA
datos_mapa['Palta_Exportada'] = datos_mapa['Palta_Producida'] * PORCENTAJE_EXPORTACION
datos_mapa['Agua_Exportada'] = datos_mapa['Agua_Total'] * PORCENTAJE_EXPORTACION

# --- 3. DISEÑO DE TEXTOS ESCALABLES (USANDO CLAMP) ---
textos_panel = []
for idx, row in datos_mapa.iterrows():
    reg = row['Region_std']
    agua = row['Agua_Total']
    palta = row['Palta_Producida']
    
    if round(palta) == 0:
        texto = (
            f"<h2 style='color: #4dc2d7; margin-top:0; font-size: clamp(2rem, 3vw, 2.8rem); font-family: Fraunces, serif;'>{reg}</h2>"
            f"<h3 style='color: #ffffff; font-size: clamp(1.2rem, 2vw, 1.8rem);'>Sin palto en el catastro</h3>"
        )
    else:
        agua_str = f"{agua:,.0f}".replace(',', '.')
        palta_str = f"{palta:,.0f}".replace(',', '.')
        exp_palta_str = f"{row['Palta_Exportada']:,.0f}".replace(',', '.')
        exp_agua_str = f"{row['Agua_Exportada']:,.0f}".replace(',', '.')
        factor_str = f"{AGUA_POR_TON_PRODUCIDA:,.0f}".replace(',', '.')
        
        texto = (
            f"<h2 style='color: #4dc2d7; margin-top:0; font-size: clamp(2rem, 3vw, 3rem); margin-bottom: 0.5rem; font-family: Fraunces, serif;'>{reg}</h2>"
            f"<div style='background: rgba(14, 21, 19, 0.6); padding: clamp(1rem, 2vw, 1.8rem); border-radius: 12px; margin-bottom: 1.5rem; border: 1px solid rgba(77, 194, 215, 0.2);'>"
            f"  <span style='font-size: clamp(0.9rem, 1vw, 1.2rem); color: #8a9ba8; text-transform: uppercase; letter-spacing: 1px;'>Agua total en producción:</span><br>"
            f"  <span style='font-size: clamp(2.2rem, 3.5vw, 3.5rem); color: #ffffff; font-weight: bold;'>{agua_str} <span style='font-size: clamp(1rem, 1.5vw, 1.5rem); color: #4dc2d7;'>m³</span></span>"
            f"</div>"
            f"<ul style='color: #eef3f1; font-size: clamp(1rem, 1.2vw, 1.3rem); line-height: 2; list-style-type: none; padding: 0; margin: 0;'>"
            f"  <li style='border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 0.5rem; margin-bottom: 0.5rem;'><span style='color: #8a9ba8'>Req. hídrico:</span> <b>{factor_str} m³/ton</b></li>"
            f"  <li style='border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 0.5rem; margin-bottom: 0.5rem;'><span style='color: #8a9ba8'>Palta producida:</span> <b>{palta_str} ton</b></li>"
            f"  <li style='border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 0.5rem; margin-bottom: 0.5rem;'><span style='color: #8a9ba8'>Exportada (55%):</span> <b>{exp_palta_str} ton</b></li>"
            f"  <li style='color: #4dc2d7; font-size: clamp(1.1rem, 1.4vw, 1.4rem); padding-top: 0.5rem;'><span style='color: #eef3f1'>Agua exportada:</span> <b>{exp_agua_str} m³</b></li>"
            f"</ul>"
        )
    textos_panel.append(texto)

datos_mapa['panel_html'] = textos_panel

# --- 4. MAPA PLOTLY ---
COLORES_BASE = {"fondo": "#0e1513", "cuadros": "#152220", "texto": "#eef3f1", "borde": "#1f3a35", "cyan": "#4dc2d7"}
colorscale_agua = [[0.0, COLORES_BASE['cuadros']], [0.1, '#153230'], [1.0, COLORES_BASE['cyan']]]

fig = go.Figure(go.Choropleth(
    geojson=chile_geojson,
    locations=datos_mapa['Region_std'],
    featureidkey='properties.Region_std',
    z=datos_mapa['Agua_Total'], 
    colorscale=colorscale_agua,
    marker_line_color=COLORES_BASE['borde'],
    marker_line_width=0.8,
    customdata=datos_mapa[['panel_html']], 
    hoverinfo="none", 
    colorbar=dict(
        title="<span style='font-size: 13px; color: #8a9ba8;'>Volumen m³<br> </span>", 
        thickness=12, 
        len=0.7, 
        orientation="v", 
        y=0.5,            
        x=0.42,             
        xanchor="center", 
        yanchor="middle", 
        tickfont=dict(color=COLORES_BASE['texto'], size=13)
    )
))

fig.update_geos(
    fitbounds=False, 
    lataxis_range=[-37.8, -17.5], 
    lonaxis_range=[-72.8, -67.2], 
    visible=False, projection_type="mercator", bgcolor=COLORES_BASE['fondo']
)

fig.update_layout(
    autosize=True,
    margin={"r":0,"t":10,"l":0,"b":10}, 
    paper_bgcolor=COLORES_BASE['fondo'], plot_bgcolor=COLORES_BASE['fondo'], dragmode=False,
    geo=dict(domain=dict(x=[0.05, 0.50], y=[0, 1.0])) 
)

# --- 5. INYECCIÓN DEL DISEÑO CON CSS ESCALABLE ---
html_base = fig.to_html(full_html=True, include_plotlyjs='cdn', div_id='mi-mapa-plotly')

css_inyectado = f"""
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,700&family=Inter:wght@400;600&display=swap" rel="stylesheet">
<style>
    body {{ margin: 0; padding: 0; background-color: {COLORES_BASE['fondo']}; overflow: hidden; font-family: 'Inter', system-ui, sans-serif; }}
    #mi-mapa-plotly {{ width: 100vw !important; height: 100vh !important; position: absolute; left: 0; top: 0; }}
    
    g.choroplethlayer path {{
        transition: opacity 0.3s ease, stroke-width 0.3s ease, stroke 0.3s ease !important;
    }}

    /* CAJA FLOTANTE ESCALABLE */
    #caja-flotante {{
        position: absolute; 
        right: clamp(2%, 10vw, 15%); /* Se ajusta inteligentemente al borde */
        top: 50%; transform: translateY(-50%);
        width: clamp(300px, 32vw, 480px); /* Nunca será muy chica ni muy grande */
        background-color: rgba(21, 34, 32, 0.85);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(77, 194, 215, 0.3);
        border-radius: 16px;
        padding: clamp(1.5rem, 2.5vw, 3rem); /* El padding interior también se encoge */
        box-sizing: border-box;
        box-shadow: 0 20px 40px rgba(0,0,0,0.5);
        pointer-events: none;
        z-index: 10;
        transition: all 0.3s ease;
    }}
    .instruccion {{ 
        color: #8a9ba8; 
        text-align: center; 
        font-size: clamp(1rem, 1.2vw, 1.3rem); 
        border: 2px dashed #1f3a35; 
        padding: clamp(1.5rem, 2vw, 2.5rem); 
        border-radius: 10px; 
    }}
</style>
"""

html_panel = """
<div id="caja-flotante">
    <div id="info-box">
        <div class="instruccion">
            🖱️ Pasa el cursor sobre una región en el mapa para descubrir los detalles de su huella hídrica.
        </div>
    </div>
</div>
<script>
    let resizeTimer;
    function forzarAjuste() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            var miMapa = document.getElementById('mi-mapa-plotly');
            if (miMapa) {
                Plotly.relayout(miMapa, {
                    width: window.innerWidth,
                    height: window.innerHeight
                });
            }
        }, 300); 
    }
    
    window.addEventListener('resize', forzarAjuste);
    document.addEventListener('fullscreenchange', forzarAjuste);

    var chequeo = setInterval(function() {
        var miMapa = document.getElementById('mi-mapa-plotly');
        if (miMapa && miMapa.on) {
            clearInterval(chequeo);
            var infoBox = document.getElementById('info-box');
            
            miMapa.on('plotly_hover', function(data){
                if(data.points && data.points.length > 0) {
                    var pt = data.points[0];
                    var index = pt.pointIndex !== undefined ? pt.pointIndex : pt.pointNumber;
                    var paths = document.querySelectorAll('g.choroplethlayer path');
                    
                    if (!miMapa.dataset.etiquetado) {
                        paths.forEach(function(p, i) {
                            p.setAttribute('data-indice-original', i);
                        });
                        miMapa.dataset.etiquetado = 'true';
                    }
                    
                    infoBox.innerHTML = pt.customdata[0];
                    
                    paths.forEach(function(p) {
                        var origIndex = parseInt(p.getAttribute('data-indice-original'));
                        
                        if(origIndex === index) {
                            p.style.setProperty('stroke', '#ffffff', 'important');
                            p.style.setProperty('stroke-width', '3px', 'important');
                            p.style.setProperty('opacity', '1', 'important');
                            p.parentNode.appendChild(p);
                        } else {
                            p.style.setProperty('opacity', '0.25', 'important');
                            p.style.setProperty('stroke', '#1f3a35', 'important');
                            p.style.setProperty('stroke-width', '0.8px', 'important');
                        }
                    });
                }
            });

            miMapa.on('plotly_unhover', function(data){
                var paths = document.querySelectorAll('g.choroplethlayer path');
                paths.forEach(function(p) {
                    p.style.setProperty('opacity', '1', 'important');
                    p.style.setProperty('stroke', '#1f3a35', 'important');
                    p.style.setProperty('stroke-width', '0.8px', 'important');
                });
            });
        }
    }, 100); 
</script>
"""

html_final = html_base.replace('</head>', css_inyectado + '</head>')
html_final = html_final.replace('</body>', html_panel + '</body>')

with open(ruta_html, 'w', encoding='utf-8') as f:
    f.write(html_final)

print(f"✅ Ajuste escalable completado: La caja y los textos ahora se adaptan al tamaño de la pantalla.")
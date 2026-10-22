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

# --- 3. DISEÑO DE TEXTOS PARA LA CAJA FLOTANTE ---
textos_panel = []
for idx, row in datos_mapa.iterrows():
    reg = row['Region_std']
    agua = row['Agua_Total']
    palta = row['Palta_Producida']
    
    if round(palta) == 0:
        texto = (
            f"<h2 style='color: #4dc2d7; margin-top:0; font-size: 2.2rem; font-family: Fraunces, serif;'>{reg}</h2>"
            f"<h3 style='color: #ffffff; font-size: 1.5rem;'>Sin palto en el catastro</h3>"
            f"<p style='color: #8a9ba8; font-size: 1.1rem;'>Esta región no aparece con plantaciones de palto activas en los registros.</p>"
        )
    else:
        agua_str = f"{agua:,.0f}".replace(',', '.')
        palta_str = f"{palta:,.0f}".replace(',', '.')
        exp_palta_str = f"{row['Palta_Exportada']:,.0f}".replace(',', '.')
        exp_agua_str = f"{row['Agua_Exportada']:,.0f}".replace(',', '.')
        factor_str = f"{AGUA_POR_TON_PRODUCIDA:,.0f}".replace(',', '.')
        
        texto = (
            f"<h2 style='color: #4dc2d7; margin-top:0; font-size: 2.5rem; margin-bottom: 0.5rem; font-family: Fraunces, serif;'>{reg}</h2>"
            f"<div style='background: rgba(14, 21, 19, 0.6); padding: 1.5rem; border-radius: 10px; margin-bottom: 1.5rem; border: 1px solid rgba(77, 194, 215, 0.2);'>"
            f"  <span style='font-size: 1rem; color: #8a9ba8; text-transform: uppercase; letter-spacing: 1px;'>Agua total en producción:</span><br>"
            f"  <span style='font-size: 2.5rem; color: #ffffff; font-weight: bold;'>{agua_str} <span style='font-size: 1.2rem; color: #4dc2d7;'>m³</span></span>"
            f"</div>"
            f"<ul style='color: #eef3f1; font-size: 1.1rem; line-height: 2; list-style-type: none; padding: 0; margin: 0;'>"
            f"  <li style='border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 0.5rem; margin-bottom: 0.5rem;'><span style='color: #8a9ba8'>Req. hídrico:</span> <b>{factor_str} m³/ton</b></li>"
            f"  <li style='border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 0.5rem; margin-bottom: 0.5rem;'><span style='color: #8a9ba8'>Palta producida:</span> <b>{palta_str} ton</b></li>"
            f"  <li style='border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 0.5rem; margin-bottom: 0.5rem;'><span style='color: #8a9ba8'>Exportada (55%):</span> <b>{exp_palta_str} ton</b></li>"
            f"  <li style='color: #4dc2d7; font-size: 1.2rem; padding-top: 0.5rem;'><span style='color: #eef3f1'>Agua exportada:</span> <b>{exp_agua_str} m³</b></li>"
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
    # BARRA LARGA NUEVAMENTE (len=0.45)
    colorbar=dict(
        title="<span style='font-size: 12px; color: #8a9ba8;'>Volumen m³</span>", 
        thickness=8, 
        len=0.45, 
        orientation="h", 
        y=0.03,            
        x=0.5,             
        xanchor="center", 
        yanchor="bottom", 
        tickfont=dict(color=COLORES_BASE['texto'])
    )
))

# ZOOM GIGANTE: Longitud estrecha [-74.0, -67.0] fuerza al mapa a ocupar todo el alto
# Latitud calibrada [-38.2, -17.2] para que el sur quede entero
fig.update_geos(
    fitbounds=False, 
    lataxis_range=[-38.2, -17.2], 
    lonaxis_range=[-74.0, -67.0], 
    visible=False, projection_type="mercator", bgcolor=COLORES_BASE['fondo']
)

# El dominio 'y' empieza en 0.08 para dejar espacio abajo para la barra
fig.update_layout(
    margin={"r":0,"t":10,"l":0,"b":10}, 
    paper_bgcolor=COLORES_BASE['fondo'], plot_bgcolor=COLORES_BASE['fondo'], dragmode=False,
    geo=dict(domain=dict(x=[0, 1], y=[0.08, 1.0])) 
)

# --- 5. INYECCIÓN DEL DISEÑO (TÍTULO Y CAJA FLOTANTE) ---
html_base = fig.to_html(full_html=True, include_plotlyjs='cdn', div_id='mi-mapa-plotly')

css_inyectado = f"""
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,700&family=Inter:wght@400;600&display=swap" rel="stylesheet">
<style>
    body {{ margin: 0; padding: 0; background-color: {COLORES_BASE['fondo']}; overflow: hidden; font-family: 'Inter', system-ui, sans-serif; }}
    #mi-mapa-plotly {{ width: 100vw !important; height: 100vh !important; position: absolute; left: 0; top: 0; }}
    
    #titulo-flotante {{
        position: absolute;
        top: 6%;
        left: 6%;
        max-width: 400px; 
        z-index: 10;
        pointer-events: none;
    }}
    #titulo-flotante h1 {{
        font-family: 'Fraunces', serif;
        font-size: 2.8rem;
        color: {COLORES_BASE['cyan']};
        margin: 0 0 1rem 0;
        line-height: 1.1;
    }}
    #titulo-flotante p {{
        font-size: 1.1rem;
        line-height: 1.6;
        color: #8a9ba8;
        margin: 0;
    }}

    #caja-flotante {{
        position: absolute; right: 6%; top: 50%; transform: translateY(-50%);
        width: 380px;
        background-color: rgba(21, 34, 32, 0.85);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(77, 194, 215, 0.3);
        border-radius: 16px;
        padding: 2.5rem; box-sizing: border-box;
        box-shadow: 0 20px 40px rgba(0,0,0,0.5);
        pointer-events: none;
        z-index: 10;
        transition: all 0.3s ease;
    }}
    .instruccion {{ color: #8a9ba8; text-align: center; font-size: 1.1rem; border: 2px dashed #1f3a35; padding: 2rem; border-radius: 10px; }}
</style>
"""

html_panel = """
<div id="titulo-flotante">
    <h1>¿Cuánta agua se va del país al exportar?</h1>
    <p>El mapa revela el volumen de <b>agua virtual</b> extraída de nuestras cuencas que termina en el extranjero en forma de paltas. Explora el impacto por región.</p>
</div>

<div id="caja-flotante">
    <div id="info-box">
        <div class="instruccion">
            🖱️ Pasa el cursor sobre una región en el mapa para descubrir los detalles de su huella hídrica.
        </div>
    </div>
</div>
<script>
    var chequeo = setInterval(function() {
        var miMapa = document.getElementById('mi-mapa-plotly');
        if (miMapa && miMapa.on) {
            clearInterval(chequeo);
            var infoBox = document.getElementById('info-box');
            
            miMapa.on('plotly_hover', function(data){
                if(data.points && data.points.length > 0) {
                    infoBox.innerHTML = data.points[0].customdata[0];
                }
            });
        }
    }, 100); 
</script>
"""

html_final = html_base.replace('</head>', css_inyectado + '</head>')
html_final = html_final.replace('</body>', html_panel + '</body>')

with open(ruta_html, 'w', encoding='utf-8') as f:
    f.write(html_final)

print(f"✅ Mapa ajustado: Tamaño gigante restaurado, barra larga y centrado perfecto.")
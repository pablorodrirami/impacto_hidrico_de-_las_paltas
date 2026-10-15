import os
import pandas as pd
import urllib.request
import json
import plotly.graph_objects as go

# 1. PARÁMETROS DE ESTIMACIÓN (Cámbialos por tus datos reales de investigación)
RENDIMIENTO_TON_POR_HA = 10 
AGUA_POR_TON_PRODUCIDA = 1200
PORCENTAJE_EXPORTACION = 0.70

# 2. RUTAS INTELIGENTES Y CARGA DE DATOS
ruta_actual = os.getcwd()
ruta_base = os.path.dirname(ruta_actual) if ruta_actual.endswith('scripts') else ruta_actual
ruta_paltas = os.path.join(ruta_base, 'data', 'processed', 'catastro_paltas_2016_2025 (1).parquet')
carpeta_vis = os.path.join(ruta_base, 'visualizaciones')
ruta_html = os.path.join(carpeta_vis, 'mapa_interactivo_agua.html')
os.makedirs(carpeta_vis, exist_ok=True)

df_paltas = pd.read_parquet(ruta_paltas)
df_paltas['Superficie (ha)'] = df_paltas['Superficie (ha)'].astype(str).str.replace(',', '.').astype(float)

def limpiar_region(nombre):
    nombre = str(nombre).replace('Región de ', '').replace('Región del ', '').replace('Región ', '').strip()
    if 'Metropolitana' in nombre: return 'Metropolitana'
    if 'Higgins' in nombre: return "O'Higgins"
    if 'Biobío' in nombre or 'Bío Bío' in nombre: return 'Biobío'
    if 'Araucanía' in nombre: return 'La Araucanía'
    return nombre

df_paltas['Region_std'] = df_paltas['Region'].apply(limpiar_region)
datos_mapa_original = df_paltas.groupby('Region_std')['Superficie (ha)'].sum().reset_index()

# 3. GEOJSON Y REGIONES COMPLETAS (Para que se dibujen los bordes de todas)
url_geojson = "https://raw.githubusercontent.com/caracena/chile-geojson/master/regiones.json"
req = urllib.request.Request(url_geojson, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as response:
    chile_geojson = json.loads(response.read().decode())

regiones_completas = []
for feature in chile_geojson['features']:
    reg = limpiar_region(feature['properties']['Region'])
    feature['properties']['Region_std'] = reg
    regiones_completas.append(reg)

# Unimos TODAS las regiones con nuestros datos (las que no tienen palta quedan con 0)
df_todas = pd.DataFrame({'Region_std': regiones_completas})
datos_mapa = pd.merge(df_todas, datos_mapa_original, on='Region_std', how='left').fillna(0)

# 4. CÁLCULOS EXACTOS
datos_mapa['Palta_Producida'] = datos_mapa['Superficie (ha)'] * RENDIMIENTO_TON_POR_HA
datos_mapa['Agua_Total'] = datos_mapa['Palta_Producida'] * AGUA_POR_TON_PRODUCIDA
datos_mapa['Palta_Exportada'] = datos_mapa['Palta_Producida'] * PORCENTAJE_EXPORTACION
datos_mapa['Agua_Exportada'] = datos_mapa['Agua_Total'] * PORCENTAJE_EXPORTACION

# 5. CREACIÓN DINÁMICA DEL TOOLTIP (Igual al video: muestra aviso si es 0)
textos_hover = []
for idx, row in datos_mapa.iterrows():
    reg = row['Region_std']
    agua = row['Agua_Total']
    palta = row['Palta_Producida']
    exp_palta = row['Palta_Exportada']
    exp_agua = row['Agua_Exportada']
    
    if palta == 0:
        texto = (
            f"<span style='font-size: 16px; color: #4dc2d7;'><b>{reg}</b></span><br><br>"
            f"<span style='font-size: 18px; color: #ffffff;'><b>Sin palto en el catastro</b></span><br>"
            f"<span style='font-size: 11px; color: #8a9ba8;'>Esta región no aparece con<br>plantaciones de palto.</span>"
        )
    else:
        # Formateamos los números para que tengan separador de miles con punto
        agua_str = f"{agua:,.0f}".replace(',', '.')
        palta_str = f"{palta:,.0f}".replace(',', '.')
        exp_palta_str = f"{exp_palta:,.0f}".replace(',', '.')
        exp_agua_str = f"{exp_agua:,.0f}".replace(',', '.')
        
        texto = (
            f"<span style='font-size: 16px; color: #4dc2d7;'><b>{reg}</b></span><br><br>"
            f"<span style='font-size: 26px; color: #ffffff;'><b>{agua_str} m³</b></span><br>"
            f"<span style='font-size: 11px; color: #8a9ba8;'>Agua total gastada</span><br><br>"
            f"<span style='font-size: 13px; color: #eef3f1;'>Palta producida: <b>{palta_str} ton</b></span><br>"
            f"<span style='font-size: 13px; color: #eef3f1;'>Palta exportada: <b>{exp_palta_str} ton</b></span><br>"
            f"<span style='font-size: 13px; color: #eef3f1;'>Agua 'exportada': <b>{exp_agua_str} m³</b></span>"
        )
    textos_hover.append(texto)

datos_mapa['hover_html'] = textos_hover

# 6. DISEÑO VISUAL Y DIBUJO DEL MAPA
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
    customdata=datos_mapa[['hover_html']], # Pasamos el HTML que creamos arriba
    hovertemplate="%{customdata[0]}<extra></extra>",
    colorbar=dict(title="", thickness=12, len=0.5, orientation="h", y=-0.05, x=0.5, xanchor="center", yanchor="top", tickfont=dict(color=COLORES_BASE['texto']))
))

fig.update_geos(
    fitbounds=False,
    lataxis_range=[-56, -17],
    lonaxis_range=[-76, -66],
    visible=False, 
    projection_type="mercator", 
    bgcolor=COLORES_BASE['fondo']
)

fig.update_layout(
    height=800,
    dragmode=False,
    paper_bgcolor=COLORES_BASE['fondo'],
    plot_bgcolor=COLORES_BASE['fondo'],
    margin={"r":0,"t":10,"l":0,"b":50},
    hoverlabel=dict(bgcolor="#111c1a", font_color="#ffffff", bordercolor="#4dc2d7", font_family="system-ui, -apple-system, sans-serif", align="left")
)

fig.write_html(ruta_html, config={'displayModeBar': False, 'scrollZoom': False})
print(f"✅ Mapa guardado correctamente en: {ruta_html}")
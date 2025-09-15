"""
Reddit WSB Sentiment Analysis - Streamlit App
Aplicación web para interactuar con la API de predicciones
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import json

# Configuración de la página
st.set_page_config(
    page_title="Reddit WSB Sentiment Analysis",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuración de la API
API_BASE_URL = "https://daylong-datalab-reddit.hf.space"  # Cambiar por tu URL real

# Títulos y descripción
st.markdown("<h1 style='text-align: center;'>📈 Reddit WSB Sentiment Analysis</h1>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("**Análisis de sentimiento y predicción de retornos financieros con datos actualizados**")

# Sidebar para configuración
api_url = API_BASE_URL

# Verificar conexión con la API
@st.cache_data(ttl=60)
def check_api_health(api_url):
    """Verificar si la API está funcionando"""
    try:
        response = requests.get(f"{api_url}/health", timeout=10)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, None
    except:
        return False, None

# Verificar API
with st.spinner("Verificando conexión con la API..."):
    api_healthy, health_data = check_api_health(api_url)

if api_healthy:
    st.success("✅ API conectada correctamente")
    if health_data:
        st.info(' ✅ Modelo cargado correctamente ' if health_data.get('model_loaded') else '❌')
else:
    st.error("❌ No se pudo conectar con la API.")
    st.stop()

# Función para hacer predicciones
@st.cache_data(ttl=600)  # Cache por 10 minutos
def get_prediction(symbol, include_sentiment=True):
    """Obtener predicción de la API"""
    try:
        response = requests.get(
            f"{api_url}/predict/{symbol}",
            params={"include_sentiment": include_sentiment},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"Error obteniendo predicción: {e}")
        return None

# Función para obtener información del modelo
@st.cache_data(ttl=3600)  # Cache por 1 hora
def get_model_info():
    """Obtener información del modelo"""
    try:
        response = requests.get(f"{api_url}/model/info", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

# Función para obtener información detallada de una acción
@st.cache_data(ttl=600)  # Cache por 10 minutos
def get_stock_info(symbol):
    """Obtener información detallada de una acción"""
    try:
        response = requests.get(f"{api_url}/stock/{symbol}/info", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

# Función para obtener indicadores técnicos
@st.cache_data(ttl=300)  # Cache por 5 minutos
def get_technical_indicators(symbol):
    """Obtener indicadores técnicos de una acción"""
    try:
        response = requests.get(f"{api_url}/stock/{symbol}/indicators", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

# Función para obtener análisis de sentimiento de Reddit
@st.cache_data(ttl=300)  # Cache por 5 minutos
def get_reddit_sentiment(symbol, limit=100):
    """Obtener análisis de sentimiento de Reddit"""
    try:
        response = requests.get(f"{api_url}/reddit/{symbol}/sentiment", 
                              params={"limit": limit}, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

# Función para obtener análisis comprehensivo de múltiples subreddits
@st.cache_data(ttl=300)  # Cache por 5 minutos
def get_comprehensive_reddit_analysis(symbol, subreddits="wallstreetbets,investing,stocks", limit=100):
    """Obtener análisis comprehensivo de múltiples subreddits"""
    try:
        response = requests.get(f"{api_url}/reddit/{symbol}/comprehensive", 
                              params={"subreddits": subreddits, "limit": limit}, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

# Función para obtener subreddits disponibles
@st.cache_data(ttl=3600)  # Cache por 1 hora
def get_available_subreddits():
    """Obtener lista de subreddits disponibles"""
    try:
        response = requests.get(f"{api_url}/reddit/subreddits/available", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

# Función para analizar texto individual
@st.cache_data(ttl=60)  # Cache por 1 minuto
def analyze_text_api(text):
    """Analizar texto individual usando la API"""
    try:
        response = requests.post(f"{api_url}/reddit/analyze-text", 
                              params={"text": text}, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

# Función para obtener posts de Reddit
@st.cache_data(ttl=300)  # Cache por 5 minutos
def get_reddit_posts(symbol, limit=20):
    """Obtener posts populares de Reddit"""
    try:
        response = requests.get(f"{api_url}/reddit/{symbol}/posts", 
                              params={"limit": limit}, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

# Función para obtener datos históricos mejorados
@st.cache_data(ttl=300)  # Cache por 5 minutos
def get_historical_data_api(symbol, period="30d", interval="1d"):
    """Obtener datos históricos usando la API"""
    try:
        response = requests.get(f"{api_url}/stock/{symbol}/history", 
                              params={"period": period, "interval": interval}, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

# Función para obtener datos históricos
def get_historical_data(symbol, days=30):
    """Obtener datos históricos usando yfinance"""
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=f"{days}d")
        return hist
    except:
        return None

# Inicializar estado de sesión para mantener la pestaña activa
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0

# Selector de pestañas usando radio buttons (más confiable para mantener estado)
tab_options = [
    "🔮 Predicciones", 
    "📊 Análisis", 
    "📈 Gráficos", 
    "🏢 Información de Acción",
    "📱 Reddit Sentiment",
    "📝 Análisis de Texto",
    "ℹ️ Información"
]

# Crear selector de pestañas horizontal
selected_tab = st.radio(
    "Seleccionar sección:",
    options=tab_options,
    index=st.session_state.active_tab,
    horizontal=True,
    key="tab_selector"
)

# Actualizar el estado de la pestaña activa
st.session_state.active_tab = tab_options.index(selected_tab)

# Separador visual
st.markdown("---")

# Mostrar contenido basado en la pestaña seleccionada
if selected_tab == "🔮 Predicciones":
    st.header("Predicciones en Tiempo Real")
    
    # Input del usuario
    symbol = st.text_input(
        "Símbolo de la acción",
        value="TSLA",
        placeholder="Ej: AAPL (Apple), TSLA (Tesla), MSFT (Microsoft Corporation), GOOGL (Google)",
        help="Ingresa el símbolo de la acción que quieres analizar, puede apoyarse seleccionando el simbolo con el que cotiza la empresa en la barra de busqueda"
    ).upper()

    include_sentiment = st.checkbox(
        "Incluir sentimiento de Reddit",
        value=True,
        help="Incluir análisis de sentimiento de Reddit"
    )
    # Botón para hacer predicción
    if st.button("📈 Hacer Predicción", type="primary"):
        if symbol:
            with st.spinner(f"Analizando {symbol}..."):
                prediction_data = get_prediction(symbol, include_sentiment)
                
                if prediction_data:
                    # Mostrar resultados
                    st.success("✅ Predicción completada")
                    
                    # Métricas principales
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            "Predicción (%)",
                            f"{prediction_data['prediction_percent']:.2f}%",
                            delta=f"{prediction_data['prediction_percent']:.2f}%"
                        )
                    
                    with col2:
                        st.metric(
                            "Símbolo",
                            prediction_data['symbol'],
                            help="Símbolo analizado"
                        )
                    
                    with col3:
                        st.metric(
                            "Timestamp",
                            prediction_data['timestamp'][:19],
                            help="Hora de la predicción"
                        )
                    
                    # Información adicional
                    st.subheader("📋 Detalles de la Predicción")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.json({
                            "Predicción (log return)": f"{prediction_data['prediction']:.6f}",
                            "Predicción (%)": f"{prediction_data['prediction_percent']:.2f}%",
                            "Símbolo": prediction_data['symbol'],
                            "Mensaje": prediction_data.get('message', 'N/A')
                        })
                    with col2:
                        st.json(prediction_data['data_sources'])
                        
                        # Mostrar estado de fuentes de datos
                        st.subheader("🔍 Estado de Fuentes de Datos")
                        if prediction_data['data_sources'].get('financial'):
                            st.success("✅ Datos financieros disponibles")
                        if prediction_data['data_sources'].get('reddit_sentiment'):
                            st.success("✅ Análisis de sentimiento Reddit disponible")
                        else:
                            st.warning("⚠️ Análisis de sentimiento Reddit no disponible")
                        if prediction_data['data_sources'].get('technical_indicators'):
                            st.success("✅ Indicadores técnicos calculados")
                    
                    # Medidor tipo termómetro para la predicción
                    st.subheader("🌡️ Medidor de Predicción")
                    pred_pct = prediction_data['prediction_percent']
                    
                    # Crear medidor tipo termómetro usando componentes nativos de Streamlit
                    def create_thermometer_gauge(value, symbol):
                        """Crear medidor tipo termómetro para mostrar predicción"""
                        # Normalizar el valor entre -10 y 10 para el medidor
                        normalized_value = max(-10, min(10, value))
                        
                        # Determinar color y emoji basado en el valor
                        if normalized_value > 2:
                            color = "#28a745"  # Verde fuerte
                            emoji = "🔥"
                            sentiment = "MUY BULLISH"
                        elif normalized_value > 0:
                            color = "#20c997"  # Verde claro
                            emoji = "📈"
                            sentiment = "BULLISH"
                        elif normalized_value > -2:
                            color = "#ffc107"  # Amarillo
                            emoji = "📉"
                            sentiment = "BEARISH"
                        else:
                            color = "#dc3545"  # Rojo
                            emoji = "❄️"
                            sentiment = "MUY BEARISH"
                        
                        # Crear el medidor visual
                        col1, col2, col3 = st.columns([1, 2, 1])
                        
                        with col2:
                            # Título del medidor
                            st.markdown(f"<h3 style='text-align: center; margin-bottom: 10px;'>{emoji} {sentiment}</h3>", unsafe_allow_html=True)
                            
                            # Crear barra de progreso que simula un termómetro
                            progress_value = (normalized_value + 10) / 20  # Convertir a 0-1
                            st.progress(progress_value)
                            
                            # Mostrar valor numérico
                            st.markdown(f"<h2 style='text-align: center; color: {color}; margin: 10px 0;'>{value:.2f}%</h2>", unsafe_allow_html=True)
                            
                            # Indicadores de temperatura
                            col_temp1, col_temp2, col_temp3, col_temp4, col_temp5 = st.columns(5)
                            
                            with col_temp1:
                                st.markdown("<div style='text-align: center; font-size: 12px; color: #dc3545;'>❄️<br/>-10%</div>", unsafe_allow_html=True)
                            with col_temp2:
                                st.markdown("<div style='text-align: center; font-size: 12px; color: #ffc107;'>📉<br/>-2%</div>", unsafe_allow_html=True)
                            with col_temp3:
                                st.markdown("<div style='text-align: center; font-size: 12px; color: #6c757d;'>📊<br/>0%</div>", unsafe_allow_html=True)
                            with col_temp4:
                                st.markdown("<div style='text-align: center; font-size: 12px; color: #20c997;'>📈<br/>+2%</div>", unsafe_allow_html=True)
                            with col_temp5:
                                st.markdown("<div style='text-align: center; font-size: 12px; color: #28a745;'>🔥<br/>+10%</div>", unsafe_allow_html=True)
                    
                    # Mostrar el medidor
                    create_thermometer_gauge(pred_pct, symbol)
                    
                    # Interpretación
                    st.subheader("💡 Interpretación")
                    
                    if pred_pct > 2:
                        st.success(f"📈 **Tendencia Alcista Fuerte**: {symbol} podría subir {pred_pct:.2f}%")
                    elif pred_pct > 0:
                        st.info(f"📈 **Tendencia Alcista**: {symbol} podría subir {pred_pct:.2f}%")
                    elif pred_pct > -2:
                        st.warning(f"📉 **Tendencia Bajista**: {symbol} podría bajar {abs(pred_pct):.2f}%")
                    else:
                        st.error(f"📉 **Tendencia Bajista Fuerte**: {symbol} podría bajar {abs(pred_pct):.2f}%")
                    
                    # Advertencia
                    st.warning("⚠️ **Advertencia**: Estas predicciones son solo para fines educativos y no constituyen consejos de inversión.")
                    
                else:
                    st.error("❌ No se pudo obtener la predicción. Verifica el símbolo y la conexión.")
        else:
            st.warning("⚠️ Por favor ingresa un símbolo válido.")

elif selected_tab == "📊 Análisis":
    st.header("Análisis Comparativo")
    
    # Múltiples símbolos
    st.subheader("Comparar Múltiples Acciones")
    
    symbols_input = st.text_input(
        "Símbolos separados por comas",
        value="AAPL,TSLA,MSFT,GOOGL,NVDA",
        help="Ej: AAPL,TSLA,MSFT,GOOGL,NVDA"
    )
    
    if st.button("�� Analizar Múltiples", type="primary"):
        symbols = [s.strip().upper() for s in symbols_input.split(",") if s.strip()]
        
        if symbols:
            with st.spinner("Analizando múltiples acciones..."):
                predictions = []
                
                for symbol in symbols:
                    pred_data = get_prediction(symbol, True)  # Incluir sentimiento por defecto
                    stock_info = get_stock_info(symbol)
                    if pred_data:
                        # Crear información de la acción
                        stock_info_text = "❌ Información no disponible"
                        if stock_info:
                            company_name = stock_info.get('company_name', 'N/A')
                            sector = stock_info.get('sector', 'N/A')
                            current_price = stock_info.get('current_price', 0)
                            market_cap = stock_info.get('market_cap')
                            
                            # Formatear capitalización de mercado
                            if market_cap:
                                if market_cap >= 1e12:
                                    market_cap_str = f"${market_cap/1e12:.1f}T"
                                elif market_cap >= 1e9:
                                    market_cap_str = f"${market_cap/1e9:.1f}B"
                                elif market_cap >= 1e6:
                                    market_cap_str = f"${market_cap/1e6:.1f}M"
                                else:
                                    market_cap_str = f"${market_cap:,.0f}"
                            else:
                                market_cap_str = "N/A"
                            
                            # Construir información de forma más robusta
                            info_parts = []
                            if company_name != 'N/A':
                                info_parts.append(f"🏢 {company_name}")
                            if sector != 'N/A':
                                info_parts.append(f"📊 {sector}")
                            if current_price > 0:
                                info_parts.append(f"💰 ${current_price:.2f}")
                            if market_cap_str != 'N/A':
                                info_parts.append(f"📈 {market_cap_str}")
                            
                            stock_info_text = "\n".join(info_parts) if info_parts else "❌ Información no disponible"
                        
                        predictions.append({
                            "Símbolo": symbol,
                            "Información de la Acción": stock_info_text,
                            "Predicción (%)": pred_data['prediction_percent'],
                            "Timestamp": pred_data['timestamp'][:19]
                        })
                
                if predictions:
                    df = pd.DataFrame(predictions)
                    
                    # Mostrar tabla
                    st.subheader("📋 Resultados Comparativos")
                    st.dataframe(df, use_container_width=True)
                    
                    # Gráfico de barras
                    fig = px.bar(
                        df, 
                        x="Símbolo", 
                        y="Predicción (%)",
                        title="Predicciones por Símbolo",
                        color="Predicción (%)",
                        color_continuous_scale="RdYlGn"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Ranking
                    st.subheader("🏆 Ranking de Predicciones")
                    df_sorted = df.sort_values("Predicción (%)", ascending=False)
                    
                    for i, (_, row) in enumerate(df_sorted.iterrows(), 1):
                        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "📊"
                        st.write(f"{emoji} **{i}.** {row['Símbolo']}: {row['Predicción (%)']:.2f}%")
                else:
                    st.error("❌ No se pudieron obtener predicciones para ningún símbolo.")

elif selected_tab == "📈 Gráficos":
    st.header("📈 Visualizaciones Avanzadas")
    
    # Selector de símbolo para gráficos
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        chart_symbol = st.selectbox(
            "Seleccionar símbolo para gráficos",
            ["AAPL", "TSLA", "MSFT", "GOOGL", "NVDA", "AMZN", "META", "GME", "AMC"],
            index=1,
            key="chart_symbol"
        )
    
    with col2:
        period_options = {
            "1 día": "1d",
            "5 días": "5d", 
            "1 mes": "1mo",
            "3 meses": "3mo",
            "6 meses": "6mo",
            "1 año": "1y",
            "2 años": "2y",
            "5 años": "5y"
        }
        selected_period = st.selectbox(
            "Período",
            list(period_options.keys()),
            index=3,  # Default to 3 months
            key="period_selector"
        )
        period_value = period_options[selected_period]
    
    with col3:
        interval_options = {
            "1 día": "1d",
            "1 hora": "1h",
            "30 min": "30m",
            "15 min": "15m",
            "5 min": "5m"
        }
        selected_interval = st.selectbox(
            "Intervalo",
            list(interval_options.keys()),
            index=0,  # Default to 1 day
            key="interval_selector"
        )
        interval_value = interval_options[selected_interval]
    
    # Obtener datos históricos usando la nueva API
    if st.button("📊 Actualizar Gráficos", type="primary", key="update_charts"):
        with st.spinner("Obteniendo datos históricos..."):
            hist_data_api = get_historical_data_api(chart_symbol, period_value, interval_value)
            hist_data_yf = get_historical_data(chart_symbol, days=30)  # Fallback
    
    # Mostrar datos históricos si están disponibles
    if 'hist_data_api' in locals() and hist_data_api:
        # Convertir datos de la API a DataFrame para visualización
        hist_df = pd.DataFrame(hist_data_api['data'])
        hist_df['date'] = pd.to_datetime(hist_df['date'])
        hist_df = hist_df.set_index('date')
        
        # Gráfico de precios con datos de la API
        st.subheader(f"📈 Precios Históricos - {chart_symbol} ({selected_period})")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hist_df.index,
            y=hist_df['close'],
            mode='lines',
            name='Precio de Cierre',
            line=dict(color='blue', width=2)
        ))
        
        # Agregar líneas de precio alto y bajo
        fig.add_trace(go.Scatter(
            x=hist_df.index,
            y=hist_df['high'],
            mode='lines',
            name='Precio Alto',
            line=dict(color='green', width=1, dash='dash'),
            opacity=0.7
        ))
        
        fig.add_trace(go.Scatter(
            x=hist_df.index,
            y=hist_df['low'],
            mode='lines',
            name='Precio Bajo',
            line=dict(color='red', width=1, dash='dash'),
            opacity=0.7
        ))
        
        fig.update_layout(
            title=f"Precio de Cierre - {chart_symbol} ({selected_period})",
            xaxis_title="Fecha",
            yaxis_title="Precio ($)",
            hovermode='x unified',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Gráfico de volumen
        
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Bar(
            x=hist_df.index,
            y=hist_df['volume'],
            name='Volumen',
            marker_color='lightblue'
        ))
        
        fig_vol.update_layout(
            title=f"Volumen de Trading - {chart_symbol} ({selected_period})",
            xaxis_title="Fecha",
            yaxis_title="Volumen",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig_vol, use_container_width=True)
        
        # Estadísticas mejoradas
        st.subheader("📊 Estadísticas Detalladas")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            current_price = hist_df['close'].iloc[-1]
            st.metric("Precio Actual", f"${current_price:.2f}")
            st.metric("Precio Apertura", f"${hist_df['open'].iloc[-1]:.2f}")
        
        with col2:
            change = current_price - hist_df['close'].iloc[0]
            change_pct = (change / hist_df['close'].iloc[0]) * 100
            st.metric("Cambio Total", f"${change:.2f}")
            st.metric("Cambio %", f"{change_pct:.2f}%")
        
        with col3:
            high_price = hist_df['high'].max()
            low_price = hist_df['low'].min()
            st.metric("Precio Máximo", f"${high_price:.2f}")
            st.metric("Precio Mínimo", f"${low_price:.2f}")
        
        with col4:
            avg_vol = hist_df['volume'].mean()
            total_vol = hist_df['volume'].sum()
            st.metric("Volumen Promedio", f"{avg_vol:,.0f}")
            st.metric("Volumen Total", f"{total_vol:,.0f}")
    
        # Información adicional de la API
        st.subheader("ℹ️ Información de los Datos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**Período:** {hist_data_api.get('period', 'N/A')}")
            st.info(f"**Puntos de datos:** {hist_data_api.get('data_points', 'N/A')}")
        
        with col2:
            st.info(f"**Fecha inicio:** {hist_data_api.get('start_date', 'N/A')}")
            st.info(f"**Fecha fin:** {hist_data_api.get('end_date', 'N/A')}")
        
        # Tabla de datos
        with st.expander("📋 Ver Datos Históricos Completos"):
            st.dataframe(hist_df, use_container_width=True)
    
    elif 'hist_data_yf' in locals() and hist_data_yf is not None and not hist_data_yf.empty:
        # Fallback a datos de yfinance
        st.warning("⚠️ Usando datos de yfinance como respaldo")
        
        # Gráfico de precios
        st.subheader(f"📈 Precios Históricos - {chart_symbol} (30 días)")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hist_data_yf.index,
            y=hist_data_yf['Close'],
            mode='lines',
            name='Precio de Cierre',
            line=dict(color='blue', width=2)
        ))
        
        fig.update_layout(
            title=f"Precio de Cierre - {chart_symbol} (30 días)",
            xaxis_title="Fecha",
            yaxis_title="Precio ($)",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Gráfico de volumen
        st.subheader(f"📊 Volumen de Trading - {chart_symbol}")
        
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Bar(
            x=hist_data_yf.index,
            y=hist_data_yf['Volume'],
            name='Volumen',
            marker_color='lightblue'
        ))
        
        fig_vol.update_layout(
            title=f"Volumen de Trading - {chart_symbol} (30 días)",
            xaxis_title="Fecha",
            yaxis_title="Volumen",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_vol, use_container_width=True)
        
        # Estadísticas
        st.subheader("📊 Estadísticas")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Precio Actual", f"${hist_data_yf['Close'].iloc[-1]:.2f}")
        
        with col2:
            change = hist_data_yf['Close'].iloc[-1] - hist_data_yf['Close'].iloc[0]
            st.metric("Cambio (30d)", f"${change:.2f}")
        
        with col3:
            change_pct = (change / hist_data_yf['Close'].iloc[0]) * 100
            st.metric("Cambio % (30d)", f"{change_pct:.2f}%")
        
        with col4:
            avg_vol = hist_data_yf['Volume'].mean()
            st.metric("Volumen Promedio", f"{avg_vol:,.0f}")
    
    else:
        st.info("👆 Haz clic en 'Actualizar Gráficos' para cargar los datos históricos")

elif selected_tab == "🏢 Información de Acción":
    st.header("🏢 Información Detallada de Acción")
    
    # Input del usuario - ahora en una sola fila
    stock_symbol = st.text_input(
        "Símbolo de la acción",
        value="AAPL",
        placeholder="Ej: AAPL, TSLA, MSFT, GOOGL",
        help="Ingresa el símbolo de la acción que quieres analizar",
        key="stock_info_symbol_tab4"
    ).upper()
    
    # Botón centrado abajo del input
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔍 Obtener Información", type="primary", key="get_stock_info_tab4", use_container_width=True):
            if stock_symbol:
                with st.spinner(f"Obteniendo información de {stock_symbol}..."):
                    stock_info = get_stock_info(stock_symbol)
                    technical_indicators = get_technical_indicators(stock_symbol)
    
    # Mostrar información fuera de las columnas para que ocupe todo el ancho
    if 'stock_info' in locals() and stock_info:
        st.success("✅ Información obtenida correctamente")
        
        # Información básica de la empresa - layout de dos columnas
        st.subheader("📋 Información de la Empresa")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("🏢 Empresa", stock_info.get('company_name', 'N/A'))
            st.metric("📊 Símbolo", stock_info.get('symbol', 'N/A'))
            st.metric("🏭 Sector", stock_info.get('sector', 'N/A'))
            st.metric("🏢 Industria", stock_info.get('industry', 'N/A'))
            st.metric("🏛️ Bolsa", stock_info.get('exchange', 'N/A'))
        
        with col2:
            st.metric("💱 Moneda", stock_info.get('currency', 'N/A'))
            st.metric("💰 Precio Actual", f"${stock_info.get('current_price', 0):.2f}")
            
            market_cap = stock_info.get('market_cap')
            if market_cap:
                if market_cap >= 1e12:
                    market_cap_formatted = f"${market_cap/1e12:.1f}T"
                elif market_cap >= 1e9:
                    market_cap_formatted = f"${market_cap/1e9:.1f}B"
                elif market_cap >= 1e6:
                    market_cap_formatted = f"${market_cap/1e6:.1f}M"
                else:
                    market_cap_formatted = f"${market_cap:,.0f}"
                st.metric("📈 Capitalización de Mercado", market_cap_formatted)
            else:
                st.metric("📈 Capitalización de Mercado", "N/A")
            
            st.metric("🕒 Timestamp", stock_info.get('timestamp', 'N/A')[:19])
        
        # Indicadores técnicos - layout de dos columnas
        if 'technical_indicators' in locals() and technical_indicators:
            st.subheader("📊 Indicadores Técnicos")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("📈 RSI (14)", f"{technical_indicators.get('rsi_14', 0):.2f}")
                st.metric("📊 MACD", f"{technical_indicators.get('macd', 0):.4f}")
                st.metric("📅 Fecha", technical_indicators.get('date', 'N/A'))
                st.metric("📊 Volumen SMA", f"{technical_indicators.get('volume_sma', 0):,.0f}")
            
            with col2:
                st.metric("📉 SMA 20", f"${technical_indicators.get('sma_20', 0):.2f}")
                st.metric("📈 SMA 50", f"${technical_indicators.get('sma_50', 0):.2f}")
                st.metric("🔺 BB Superior", f"${technical_indicators.get('bollinger_upper', 0):.2f}")
                st.metric("🔻 BB Inferior", f"${technical_indicators.get('bollinger_lower', 0):.2f}")
            
            # Interpretación de indicadores
            st.subheader("💡 Interpretación de Indicadores")
            
            rsi = technical_indicators.get('rsi_14', 50)
            if rsi > 70:
                st.warning("⚠️ RSI indica sobrecompra (>70)")
            elif rsi < 30:
                st.info("ℹ️ RSI indica sobreventa (<30)")
            else:
                st.success("✅ RSI en rango neutral")
            
            macd = technical_indicators.get('macd', 0)
            if macd > 0:
                st.success("📈 MACD positivo - Momentum alcista")
            else:
                st.warning("📉 MACD negativo - Momentum bajista")
        
        # Información completa en formato JSON
        with st.expander("📄 Información Completa (JSON)"):
            st.json(stock_info)
            
            if 'technical_indicators' in locals() and technical_indicators:
                st.json(technical_indicators)

elif selected_tab == "ℹ️ Información":
    st.header("Información del Sistema")
    
    # Información del modelo
    model_info = get_model_info()
    
    if model_info:
        st.subheader("🤖 Información del Modelo")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.json({
                "Tipo de Modelo": model_info.get('model_type', 'N/A'),
                "Features": model_info.get('features_count', 'N/A'),
                "Cargado": model_info.get('loaded', False),
                "Versión": model_info.get('version', 'N/A')
            })
        
        with col2:
            st.success("✅ Modelo XGBoost cargado correctamente")
            st.info(f"🔢 {model_info.get('features_count', 'N/A')} features utilizadas")
    
    # Información de la API
    st.subheader("🔗 Estado de la API")
    
    if health_data:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Estado", "✅ Saludable")
        
        with col2:
            st.metric("Modelo", "✅ Cargado" if health_data.get('model_loaded') else "❌ No cargado")
        
        with col3:
            st.metric("Reddit", "✅ Disponible" if health_data.get('reddit_available') else "❌ No disponible")
    
    # Información de la aplicación
    st.subheader("ℹ️ Acerca de la Aplicación")
    
    st.markdown("""
    ### Reddit WSB Sentiment Analysis
    
    Esta aplicación utiliza un modelo XGBoost entrenado para predecir retornos financieros basándose en:
    
    - **Datos financieros**: Volumen, Cierres.
    - **Análisis de sentimiento**: Posts de Reddit r/wallstreetbets, r/investing, r/criptocurrency, entre otros ...
    - **Indicadores técnicos**: RSI, MACD, SMA, Bollinger Bands
    
    ### Características:
    
    - 🔮 Predicciones en tiempo real
    - 📊 Análisis comparativo de múltiples acciones
    - 📈 Visualizaciones interactivas
    - 🤖 Modelo XGBoost entrenado
    
    ### Advertencia:
    
    ⚠️ **Las predicciones son solo para fines educativos y no constituyen consejos de inversión.**
    
    
    ### Hecho con:

    Streamlit, FastAPI, XGBoost, Yahoo Finance, Reddit API
    """
    )
    


elif selected_tab == "📝 Análisis de Texto":
    st.header("📝 Análisis de Texto Individual")
    
    st.markdown("**Analiza texto individual usando las funciones de limpieza y sentimiento avanzadas**")
    
    # Input de texto
    text_input = st.text_area(
        "Ingresa el texto a analizar",
        placeholder="Ej: $TSLA to the moon! 🚀 This stock is going to explode. Buy the dip!",
        height=150,
        help="Ingresa cualquier texto relacionado con finanzas, trading o inversiones"
    )
    
    if st.button("🔍 Analizar Texto", type="primary"):
        if text_input and len(text_input.strip()) > 3:
            with st.spinner("Analizando texto..."):
                analysis_result = analyze_text_api(text_input)
                
                if analysis_result:
                    st.success("✅ Análisis completado")
                    
                    # Mostrar resultados
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.subheader("📄 Texto Original")
                        st.text_area("", value=analysis_result.get('original_text', ''), height=100, disabled=True)
                        
                        st.subheader("🧹 Texto Limpio")
                        st.text_area("", value=analysis_result.get('cleaned_text', ''), height=100, disabled=True)
                    
                    with col2:
                        st.subheader("📊 Estadísticas")
                        text_stats = analysis_result.get('text_stats', {})
                        
                        st.metric("Longitud Original", text_stats.get('original_length', 0))
                        st.metric("Longitud Limpia", text_stats.get('cleaned_length', 0))
                        st.metric("Palabras", text_stats.get('word_count', 0))
                        st.metric("Tickers Encontrados", text_stats.get('ticker_count', 0))
                        
                        if text_stats.get('has_financial_content', False):
                            st.success("✅ Contenido financiero detectado")
                        else:
                            st.info("ℹ️ Sin contenido financiero específico")
                    
                    # Análisis de sentimiento
                    st.subheader("😊 Análisis de Sentimiento")
                    
                    sentiment = analysis_result.get('sentiment_analysis', {})
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.subheader("VADER")
                        vader_score = sentiment.get('vader_score', 0)
                        vader_sentiment = sentiment.get('vader_sentiment', 'Neutro')
                        
                        if vader_sentiment == 'Positivo':
                            st.success(f"📈 {vader_sentiment}: {vader_score:.3f}")
                        elif vader_sentiment == 'Negativo':
                            st.error(f"📉 {vader_sentiment}: {vader_score:.3f}")
                        else:
                            st.info(f"📊 {vader_sentiment}: {vader_score:.3f}")
                        
                        st.metric("Score VADER", f"{vader_score:.3f}")
                    
                    with col2:
                        st.subheader("TextBlob")
                        blob_score = sentiment.get('blob_score', 0)
                        blob_sentiment = sentiment.get('blob_sentiment', 'Neutro')
                        
                        if blob_sentiment == 'Positivo':
                            st.success(f"📈 {blob_sentiment}: {blob_score:.3f}")
                        elif blob_sentiment == 'Negativo':
                            st.error(f"📉 {blob_sentiment}: {blob_score:.3f}")
                        else:
                            st.info(f"📊 {blob_sentiment}: {blob_score:.3f}")
                        
                        st.metric("Score TextBlob", f"{blob_score:.3f}")
                    
                    with col3:
                        st.subheader("Detalles VADER")
                        st.metric("Positivo", f"{sentiment.get('vader_positive', 0):.3f}")
                        st.metric("Negativo", f"{sentiment.get('vader_negative', 0):.3f}")
                        st.metric("Neutro", f"{sentiment.get('vader_neutral', 0):.3f}")
                    
                    # Tickers encontrados
                    tickers = analysis_result.get('tickers_found', [])
                    if tickers:
                        st.subheader("🎯 Tickers Encontrados")
                        st.write("**Tickers detectados en el texto:**")
                        for ticker in tickers:
                            st.code(f"${ticker}", language="text")
                    else:
                        st.info("ℹ️ No se encontraron tickers en el texto")
                    
                    # Palabras clave del mercado
                    keywords = analysis_result.get('market_keywords', {})
                    if keywords.get('keywords_found'):
                        st.subheader("🔑 Palabras Clave del Mercado")
                        st.write("**Palabras clave financieras detectadas:**")
                        for keyword in keywords['keywords_found']:
                            st.badge(keyword)
                        
                        st.metric("Total Keywords", keywords.get('keyword_count', 0))
                    else:
                        st.info("ℹ️ No se encontraron palabras clave del mercado")
                    
                    # Información completa
                    with st.expander("📄 Análisis Completo (JSON)"):
                        st.json(analysis_result)
                else:
                    st.error("❌ No se pudo analizar el texto. Verifica la conexión con la API.")
        else:
            st.warning("⚠️ Por favor ingresa un texto válido (mínimo 3 caracteres).")
    
    # Ejemplos de texto
    st.subheader("💡 Ejemplos de Texto")
    
    examples = [
        "$TSLA to the moon! 🚀 This stock is going to explode. Buy the dip!",
        "I'm bearish on AAPL. The earnings report was disappointing and I'm selling my position.",
        "Just bought 100 shares of MSFT. Great dividend yield and strong fundamentals.",
        "GME is going to squeeze! Diamond hands! 💎🙌",
        "Market analysis: The current trend suggests a bullish outlook for tech stocks."
    ]
    
    selected_example = st.selectbox("Seleccionar ejemplo:", examples)
    
    if st.button("📋 Usar Ejemplo"):
        st.text_area("", value=selected_example, height=150, key="example_text")

elif selected_tab == "📱 Reddit Sentiment":
    st.header("📱 Análisis de Sentimiento Reddit")
    
    # Obtener subreddits disponibles
    available_subreddits_data = get_available_subreddits()
    
    # Input del usuario
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        reddit_symbol = st.text_input(
            "Símbolo de la acción",
            value="TSLA",
            placeholder="Ej: GME, AMC, TSLA",
            help="Ingresa el símbolo de la acción para analizar en Reddit",
            key="reddit_symbol"
        ).upper()
    
    with col2:
        posts_limit = st.selectbox("Posts por subreddit", [25, 50, 100, 200], index=2)
    
    with col3:
        analysis_type = st.selectbox(
            "Tipo de análisis", 
            ["Básico (WSB)", "Comprehensivo (Múltiples)"],
            index=1,
            help="Análisis básico solo en WallStreetBets o comprehensivo en múltiples subreddits"
        )
    
    # Selector de subreddits para análisis comprehensivo
    if analysis_type == "Comprehensivo (Múltiples)" and available_subreddits_data:
        st.subheader("🎯 Selección de Subreddits")
        
        available_subreddits = available_subreddits_data.get('available_subreddits', [])
        descriptions = available_subreddits_data.get('descriptions', {})
        
        # Crear checkboxes para cada subreddit
        selected_subreddits = []
        cols = st.columns(3)
        
        for i, subreddit in enumerate(available_subreddits):
            with cols[i % 3]:
                if st.checkbox(
                    f"r/{subreddit}", 
                    value=subreddit in ["wallstreetbets", "investing", "stocks"],  # Default selection
                    help=descriptions.get(subreddit, "Sin descripción")
                ):
                    selected_subreddits.append(subreddit)
        
        # Mostrar subreddits seleccionados
        if selected_subreddits:
            st.info(f"📊 Subreddits seleccionados: {', '.join([f'r/{s}' for s in selected_subreddits])}")
        else:
            st.warning("⚠️ Selecciona al menos un subreddit para el análisis")
    else:
        selected_subreddits = ["wallstreetbets"]
    
    if st.button("📊 Analizar Sentimiento", type="primary", key="analyze_reddit"):
        if reddit_symbol:
            with st.spinner(f"Analizando sentimiento de Reddit para {reddit_symbol}..."):
                if analysis_type == "Comprehensivo (Múltiples)" and selected_subreddits:
                    # Análisis comprehensivo con múltiples subreddits
                    subreddits_str = ",".join(selected_subreddits)
                    sentiment_data = get_comprehensive_reddit_analysis(reddit_symbol, subreddits_str, posts_limit)
                    posts_data = None  # No obtenemos posts para análisis comprehensivo por ahora
                else:
                    # Análisis básico solo con WallStreetBets
                    sentiment_data = get_reddit_sentiment(reddit_symbol, posts_limit)
                    posts_data = get_reddit_posts(reddit_symbol, 10)
                
                if sentiment_data:
                    st.success("✅ Análisis de sentimiento completado")
                    
                    # Verificar si es análisis comprehensivo o básico
                    is_comprehensive = 'subreddit_analysis' in sentiment_data
                    
                    if is_comprehensive:
                        # Análisis comprehensivo - múltiples subreddits
                        st.subheader("📊 Análisis Comprehensivo por Subreddit")
                        
                        # Métricas agregadas - layout ampliado para mejor visualización
                        st.subheader("📊 Métricas Generales")
                        
                        # Primera fila - métricas principales
                        col1, col2, col3, col4, col5 = st.columns(5)
                        
                        with col1:
                            st.metric("📝 Total Posts", sentiment_data.get('total_posts', 0))
                        
                        with col2:
                            st.metric("🏢 Subreddits", sentiment_data.get('aggregated_metrics', {}).get('subreddits_analyzed', 0))
                        
                        with col3:
                            aggregated = sentiment_data.get('aggregated_metrics', {})
                            st.metric("⭐ Score Promedio", f"{aggregated.get('avg_score', 0):.1f}")
                        
                        with col4:
                            st.metric("👍 Upvote Ratio", f"{aggregated.get('avg_upvote_ratio', 0):.2f}")
                        
                        with col5:
                            st.metric("💬 Total Comentarios", sentiment_data.get('aggregated_metrics', {}).get('total_comments', 0))
                        
                        # Segunda fila - sentimiento y timestamp
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            sentiment_score = sentiment_data.get('overall_sentiment', 0)
                            sentiment_label = sentiment_data.get('sentiment_label', 'neutral')
                            
                            if sentiment_label == 'bullish':
                                st.success(f"📈 Sentimiento General: {sentiment_label.upper()} ({sentiment_score:.3f})")
                            elif sentiment_label == 'bearish':
                                st.error(f"📉 Sentimiento General: {sentiment_label.upper()} ({sentiment_score:.3f})")
                            else:
                                st.info(f"📊 Sentimiento General: {sentiment_label.upper()} ({sentiment_score:.3f})")
                        
                        with col2:
                            st.metric("📊 Score Sentimiento", f"{sentiment_score:.3f}")
                        
                        with col3:
                            st.metric("🕒 Timestamp", sentiment_data.get('timestamp', 'N/A')[:19])
                        
                        # Análisis por subreddit individual
                        st.subheader("📈 Análisis Detallado por Subreddit")
                        
                        subreddit_analysis = sentiment_data.get('subreddit_analysis', {})
                        
                        for subreddit_name, analysis in subreddit_analysis.items():
                            with st.expander(f"r/{subreddit_name} - {analysis.get('posts_analyzed', 0)} posts"):
                                # Layout ampliado para mejor visualización
                                col1, col2, col3, col4, col5 = st.columns(5)
                                
                                with col1:
                                    st.metric("📝 Posts", analysis.get('posts_analyzed', 0))
                                
                                with col2:
                                    st.metric("⭐ Score Promedio", f"{analysis.get('avg_score', 0):.1f}")
                                
                                with col3:
                                    st.metric("👍 Upvote Ratio", f"{analysis.get('avg_upvote_ratio', 0):.2f}")
                                
                                with col4:
                                    st.metric("💬 Comentarios", analysis.get('total_comments', 0))
                                
                                with col5:
                                    subreddit_sentiment = analysis.get('sentiment_score', 0)
                                    if subreddit_sentiment > 0.1:
                                        st.success(f"📈 {subreddit_sentiment:.3f}")
                                    elif subreddit_sentiment < -0.1:
                                        st.error(f"📉 {subreddit_sentiment:.3f}")
                                    else:
                                        st.info(f"📊 {subreddit_sentiment:.3f}")
                                    
                                    st.metric("📊 Sentiment Score", f"{subreddit_sentiment:.3f}")
                    else:
                        # Análisis básico - solo WallStreetBets (layout ampliado)
                        st.subheader("📊 Métricas de WallStreetBets")
                        
                        # Primera fila - métricas principales
                        col1, col2, col3, col4, col5 = st.columns(5)
                        
                        with col1:
                            st.metric("📝 Posts Analizados", sentiment_data.get('posts_analyzed', 0))
                        
                        with col2:
                            st.metric("⭐ Score Promedio", f"{sentiment_data.get('avg_score', 0):.1f}")
                        
                        with col3:
                            st.metric("👍 Upvote Ratio", f"{sentiment_data.get('avg_upvote_ratio', 0):.2f}")
                        
                        with col4:
                            st.metric("💬 Total Comentarios", sentiment_data.get('total_comments', 0))
                        
                        with col5:
                            st.metric("🏢 Subreddit", sentiment_data.get('subreddit', 'N/A'))
                        
                        # Segunda fila - sentimiento y timestamp
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            sentiment_score = sentiment_data.get('sentiment_score', 0)
                            sentiment_label = sentiment_data.get('sentiment_label', 'neutral')
                            
                            if sentiment_label == 'bullish':
                                st.success(f"📈 Sentimiento: {sentiment_label.upper()} ({sentiment_score:.3f})")
                            elif sentiment_label == 'bearish':
                                st.error(f"📉 Sentimiento: {sentiment_label.upper()} ({sentiment_score:.3f})")
                            else:
                                st.info(f"📊 Sentimiento: {sentiment_label.upper()} ({sentiment_score:.3f})")
                        
                        with col2:
                            st.metric("📊 Score Sentimiento", f"{sentiment_score:.3f}")
                        
                        with col3:
                            st.metric("🕒 Timestamp", sentiment_data.get('timestamp', 'N/A')[:19])
                        
                        # Nuevas métricas de análisis avanzado
                        if sentiment_data.get('vader_score') is not None:
                            st.subheader("🔬 Análisis Avanzado")
                            
                            # Layout ampliado para análisis avanzado
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric("📊 VADER Score", f"{sentiment_data.get('vader_score', 0):.3f}")
                            
                            with col2:
                                st.metric("📈 TextBlob Score", f"{sentiment_data.get('blob_score', 0):.3f}")
                            
                            with col3:
                                tickers_found = sentiment_data.get('tickers_found', [])
                                if tickers_found:
                                    st.write("**🎯 Tickers encontrados:**")
                                    for ticker in tickers_found[:5]:  # Mostrar solo los primeros 5
                                        st.code(f"${ticker}", language="text")
                                else:
                                    st.info("Sin tickers detectados")
                            
                            with col4:
                                keywords = sentiment_data.get('market_keywords', [])
                                if keywords:
                                    st.write("**🔑 Keywords del mercado:**")
                                    for keyword in keywords[:5]:  # Mostrar solo los primeros 5
                                        st.badge(keyword)
                                else:
                                    st.info("Sin keywords detectadas")
                            
                    
                    # Gráfico de sentimiento
                    st.subheader("📊 Visualización del Sentimiento")
                    
                    if is_comprehensive:
                        # Gráfico para análisis comprehensivo
                        aggregated = sentiment_data.get('aggregated_metrics', {})
                        
                        metrics_data = {
                            'Métrica': ['Score Promedio', 'Upvote Ratio', 'Score Sentimiento'],
                            'Valor': [
                                aggregated.get('avg_score', 0),
                                aggregated.get('avg_upvote_ratio', 0) * 100,
                                abs(sentiment_data.get('overall_sentiment', 0)) * 100
                            ]
                        }
                        
                        fig = px.bar(
                            pd.DataFrame(metrics_data),
                            x='Métrica',
                            y='Valor',
                            title=f"Métricas Agregadas de Sentimiento - {reddit_symbol}",
                            color='Valor',
                            color_continuous_scale="RdYlGn"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Gráfico comparativo por subreddit
                        subreddit_analysis = sentiment_data.get('subreddit_analysis', {})
                        if subreddit_analysis:
                            subreddit_data = []
                            for subreddit_name, analysis in subreddit_analysis.items():
                                subreddit_data.append({
                                    'Subreddit': f"r/{subreddit_name}",
                                    'Posts': analysis.get('posts_analyzed', 0),
                                    'Sentiment Score': analysis.get('sentiment_score', 0)
                                })
                            
                            if subreddit_data:
                                df_subreddit = pd.DataFrame(subreddit_data)
                                
                                fig2 = px.bar(
                                    df_subreddit,
                                    x='Subreddit',
                                    y='Sentiment Score',
                                    title=f"Sentimiento por Subreddit - {reddit_symbol}",
                                    color='Sentiment Score',
                                    color_continuous_scale="RdYlGn"
                                )
                                st.plotly_chart(fig2, use_container_width=True)
                    else:
                        # Gráfico para análisis básico
                        metrics_data = {
                            'Métrica': ['Score Promedio', 'Upvote Ratio', 'Score Sentimiento'],
                            'Valor': [
                                sentiment_data.get('avg_score', 0),
                                sentiment_data.get('avg_upvote_ratio', 0) * 100,
                                abs(sentiment_data.get('sentiment_score', 0)) * 100
                            ]
                        }
                        
                        fig = px.bar(
                            pd.DataFrame(metrics_data),
                            x='Métrica',
                            y='Valor',
                            title=f"Métricas de Sentimiento - {reddit_symbol}",
                            color='Valor',
                            color_continuous_scale="RdYlGn"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Posts populares
                    if posts_data and posts_data.get('posts'):
                        st.subheader("🔥 Posts Populares")
                        
                        for i, post in enumerate(posts_data['posts'][:5], 1):
                            with st.expander(f"#{i} {post['title'][:80]}..."):
                                col1, col2, col3 = st.columns([2, 1, 1])
                                
                                with col1:
                                    st.write(f"**Autor:** {post['author']}")
                                    st.write(f"**Contenido:** {post['selftext']}")
                                    st.write(f"**Fecha:** {post['created_utc'][:19]}")
                                    
                                    # Añadir enlace directo al post de Reddit
                                    if 'url' in post and post['url']:
                                        st.write(f"**Enlace:** [Ver post en Reddit]({post['url']})")
                                    
                                    # Mostrar análisis de sentimiento del post si está disponible
                                    if 'sentiment_analysis' in post:
                                        sentiment = post['sentiment_analysis']
                                        st.write("**Análisis de Sentimiento:**")
                                        
                                        col_vader, col_blob = st.columns(2)
                                        with col_vader:
                                            vader_sentiment = sentiment.get('vader_sentiment', 'Neutro')
                                            vader_score = sentiment.get('vader_score', 0)
                                            if vader_sentiment == 'Positivo':
                                                st.success(f"VADER: {vader_sentiment} ({vader_score:.3f})")
                                            elif vader_sentiment == 'Negativo':
                                                st.error(f"VADER: {vader_sentiment} ({vader_score:.3f})")
                                            else:
                                                st.info(f"VADER: {vader_sentiment} ({vader_score:.3f})")
                                        
                                        with col_blob:
                                            blob_sentiment = sentiment.get('blob_sentiment', 'Neutro')
                                            blob_score = sentiment.get('blob_score', 0)
                                            if blob_sentiment == 'Positivo':
                                                st.success(f"TextBlob: {blob_sentiment} ({blob_score:.3f})")
                                            elif blob_sentiment == 'Negativo':
                                                st.error(f"TextBlob: {blob_sentiment} ({blob_score:.3f})")
                                            else:
                                                st.info(f"TextBlob: {blob_sentiment} ({blob_score:.3f})")
                                    
                                    # Mostrar tickers encontrados si están disponibles
                                    if 'tickers_found' in post and post['tickers_found']:
                                        st.write("**Tickers:**")
                                        for ticker in post['tickers_found']:
                                            st.code(f"${ticker}", language="text")
                                
                                with col2:
                                    st.metric("Score", post['score'])
                                    st.metric("Comentarios", post['num_comments'])
                                    st.metric("Upvote Ratio", f"{post['upvote_ratio']:.2f}")
                                
                                with col3:
                                    # Boton ver en reddit
                                    st.markdown(
                                        f'''
                                        <a href="{post["url"]}" target="_blank">
                                            <button style="width:100%; background-color:#d32f2f; color:white; border:none; padding:8px 0; border-radius:4px; font-weight:bold; cursor:pointer;">
                                                🔗 Ver en Reddit
                                            </button>
                                        </a>
                                        ''',
                                        unsafe_allow_html=True
                                    )
                                    
                                    # Mostrar texto limpio si está disponible
                                    if 'text_cleaned' in post and post['text_cleaned']:
                                        with st.expander("Ver texto limpio"):
                                            st.text(post['text_cleaned'])
                    
                    # Información completa
                    with st.expander("📄 Datos Completos del Análisis"):
                        st.json(sentiment_data)
                        if posts_data:
                            st.json(posts_data)
                else:
                    st.error("❌ No se pudo obtener el análisis de sentimiento. Verifica el símbolo y la conexión.")
        else:
            st.warning("⚠️ Por favor ingresa un símbolo válido.")



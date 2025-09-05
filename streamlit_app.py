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
    page_icon="��",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuración de la API
API_BASE_URL = "https://daylong-datalab-reddit.hf.space"  # Cambiar por tu URL real

# Títulos y descripción
st.title("📈 Reddit WSB Sentiment Analysis")
st.markdown("**Análisis de sentimiento y predicción de retornos financieros usando XGBoost**")

# Sidebar para configuración
st.sidebar.header("⚙️ Configuración")

# Selector de API
api_url = st.sidebar.text_input(
    "URL de la API", 
    value=API_BASE_URL,
    help="URL de tu API desplegada en Hugging Face"
)

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
        st.info(f"Modelo cargado: {'✅' if health_data.get('model_loaded') else '❌'}")
else:
    st.error("❌ No se pudo conectar con la API. Verifica la URL.")
    st.stop()

# Función para hacer predicciones
@st.cache_data(ttl=300)  # Cache por 5 minutos
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

# Contenido principal
tab1, tab2, tab3, tab4 = st.tabs(["�� Predicciones", "�� Análisis", "📈 Gráficos", "ℹ️ Información"])

with tab1:
    st.header("Predicciones en Tiempo Real")
    
    # Input del usuario
    col1, col2 = st.columns([2, 1])
    
    with col1:
        symbol = st.text_input(
            "Símbolo de la acción",
            value="TSLA",
            placeholder="Ej: AAPL, TSLA, MSFT, GOOGL",
            help="Ingresa el símbolo de la acción que quieres analizar"
        ).upper()
    
    with col2:
        include_sentiment = st.checkbox(
            "Incluir sentimiento de Reddit",
            value=True,
            help="Incluir análisis de sentimiento de Reddit (requiere configuración)"
        )
    
    # Botón para hacer predicción
    if st.button("�� Hacer Predicción", type="primary"):
        if symbol:
            with st.spinner(f"Analizando {symbol}..."):
                prediction_data = get_prediction(symbol, include_sentiment)
                
                if prediction_data:
                    # Mostrar resultados
                    st.success("✅ Predicción completada")
                    
                    # Métricas principales
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            "Predicción (%)",
                            f"{prediction_data['prediction_percent']:.2f}%",
                            delta=f"{prediction_data['prediction_percent']:.2f}%"
                        )
                    
                    with col2:
                        st.metric(
                            "Confianza",
                            f"{prediction_data['confidence']:.1%}",
                            help="Nivel de confianza del modelo"
                        )
                    
                    with col3:
                        st.metric(
                            "Símbolo",
                            prediction_data['symbol'],
                            help="Símbolo analizado"
                        )
                    
                    with col4:
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
                            "Confianza": f"{prediction_data['confidence']:.1%}",
                            "Símbolo": prediction_data['symbol']
                        })
                    
                    with col2:
                        st.json(prediction_data['data_sources'])
                    
                    # Interpretación
                    st.subheader("💡 Interpretación")
                    pred_pct = prediction_data['prediction_percent']
                    
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

with tab2:
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
                    pred_data = get_prediction(symbol, include_sentiment)
                    if pred_data:
                        predictions.append({
                            "Símbolo": symbol,
                            "Predicción (%)": pred_data['prediction_percent'],
                            "Confianza": pred_data['confidence'],
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

with tab3:
    st.header("Visualizaciones")
    
    # Selector de símbolo para gráficos
    chart_symbol = st.selectbox(
        "Seleccionar símbolo para gráficos",
        ["AAPL", "TSLA", "MSFT", "GOOGL", "NVDA", "AMZN", "META"],
        index=1
    )
    
    # Obtener datos históricos
    with st.spinner("Obteniendo datos históricos..."):
        hist_data = get_historical_data(chart_symbol, days=30)
    
    if hist_data is not None and not hist_data.empty:
        # Gráfico de precios
        st.subheader(f"�� Precios Históricos - {chart_symbol}")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hist_data.index,
            y=hist_data['Close'],
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
        st.subheader(f"�� Volumen de Trading - {chart_symbol}")
        
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Bar(
            x=hist_data.index,
            y=hist_data['Volume'],
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
            st.metric("Precio Actual", f"${hist_data['Close'].iloc[-1]:.2f}")
        
        with col2:
            change = hist_data['Close'].iloc[-1] - hist_data['Close'].iloc[0]
            st.metric("Cambio (30d)", f"${change:.2f}")
        
        with col3:
            change_pct = (change / hist_data['Close'].iloc[0]) * 100
            st.metric("Cambio % (30d)", f"{change_pct:.2f}%")
        
        with col4:
            avg_vol = hist_data['Volume'].mean()
            st.metric("Volumen Promedio", f"{avg_vol:,.0f}")
    
    else:
        st.error("❌ No se pudieron obtener datos históricos.")

with tab4:
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
    
    - **Datos financieros**: Precios OHLCV, volumen, indicadores técnicos
    - **Análisis de sentimiento**: Posts de Reddit r/wallstreetbets
    - **Indicadores técnicos**: RSI, MACD, SMA, Bollinger Bands
    
    ### Características:
    
    - 🔮 Predicciones en tiempo real
    - 📊 Análisis comparativo de múltiples acciones
    - 📈 Visualizaciones interactivas
    - 🤖 Modelo XGBoost entrenado
    
    ### Advertencia:
    
    ⚠️ **Las predicciones son solo para fines educativos y no constituyen consejos de inversión.**
    """)
    
    # Footer
    st.markdown("---")
    st.markdown("**Desarrollado con ❤️ usando Streamlit y FastAPI**")

# Sidebar adicional
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Estadísticas de Uso")

# Simular estadísticas (en una app real, esto vendría de una base de datos)
st.sidebar.metric("Predicciones Hoy", "42")
st.sidebar.metric("Símbolos Analizados", "15")
st.sidebar.metric("Tiempo Promedio", "2.3s")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔗 Enlaces")
st.sidebar.markdown("- [Documentación API](/docs)")
st.sidebar.markdown("- [Código Fuente](https://github.com/tu-usuario)")
st.sidebar.markdown("- [Reportar Bug](https://github.com/tu-usuario/issues)")

# Auto-refresh (opcional)
if st.sidebar.checkbox("🔄 Auto-refresh (30s)", value=False):
    time.sleep(30)
    st.rerun()

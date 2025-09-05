# Reddit WSB Sentiment Analysis - Streamlit Demo

Una aplicación web interactiva para análisis de sentimiento y predicción de retornos financieros usando XGBoost y datos de Reddit r/wallstreetbets.

## 🚀 Características

- 🔮 Predicciones en tiempo real de acciones
- 📊 Análisis comparativo de múltiples símbolos
- 📈 Visualizaciones interactivas con Plotly
- 🤖 Modelo XGBoost entrenado
- 📱 Interfaz web moderna con Streamlit

## 📋 Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## 🛠️ Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/streamlit-reddit-demo.git
cd streamlit-reddit-demo
```

### 2. Crear entorno virtual
```bash
# Crear el entorno virtual
python -m venv venv

# Activar el entorno virtual
# En Windows:
venv\Scripts\activate

# En macOS/Linux:
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación
```bash
streamlit run streamlit_app.py
```

La aplicación estará disponible en: `http://localhost:8501`

## 📦 Dependencias

- **streamlit**: Framework web para aplicaciones de datos
- **requests**: Cliente HTTP para llamadas a la API
- **pandas**: Manipulación y análisis de datos
- **plotly**: Visualizaciones interactivas
- **yfinance**: Datos financieros de Yahoo Finance
- **numpy**: Computación numérica

## 🔧 Configuración

### API Backend
La aplicación requiere un backend API que proporcione:
- Endpoint `/health` para verificar el estado
- Endpoint `/predict/{symbol}` para obtener predicciones
- Endpoint `/model/info` para información del modelo

Por defecto, la aplicación se conecta a: `https://daylong-datalab-reddit.hf.space`

Puedes cambiar la URL de la API en la barra lateral de la aplicación.

## 📊 Uso

1. **Predicciones**: Ingresa un símbolo de acción (ej: AAPL, TSLA) y obtén predicciones en tiempo real
2. **Análisis Comparativo**: Compara múltiples acciones simultáneamente
3. **Gráficos**: Visualiza datos históricos y estadísticas
4. **Información**: Consulta el estado del sistema y modelo

## ⚠️ Advertencia

**Las predicciones son solo para fines educativos y no constituyen consejos de inversión.**

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 📞 Contacto

- GitHub: [tu-usuario](https://github.com/tu-usuario)
- Email: tu-email@ejemplo.com

## 🙏 Agradecimientos

- Reddit r/wallstreetbets por los datos de sentimiento
- Yahoo Finance por los datos financieros
- Streamlit por el framework web
- Plotly por las visualizaciones interactivas
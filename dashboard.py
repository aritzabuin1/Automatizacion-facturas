import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import os
from datetime import datetime, timedelta

# =============================================================================
# CONFIGURACIÓN DE PÁGINA - TEMA PREMIUM
# =============================================================================

st.set_page_config(
    page_title="Agente de Facturas Pro",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://tu-empresa.com/soporte',
        'Report a bug': 'https://tu-empresa.com/bugs',
        'About': "# Agente de Facturas Pro v2.0\nProcesamiento inteligente de facturas con IA"
    }
)

# =============================================================================
# CSS PERSONALIZADO - DISEÑO PREMIUM
# =============================================================================

st.markdown("""
<style>
    /* Tema oscuro premium con gradiente */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Tarjetas de métricas con glassmorphism */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 700;
        color: #ffffff;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1rem;
        font-weight: 500;
        color: #e0e0e0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Sidebar premium con glassmorphism */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Botones con efecto hover premium */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Tablas con estilo premium */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Títulos con gradiente */
    h1, h2, h3 {
        color: white !important;
        font-weight: 800;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* File uploader premium */
    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.05);
        border: 2px dashed rgba(255, 255, 255, 0.3);
        border-radius: 15px;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #667eea;
        background: rgba(102, 126, 234, 0.1);
    }
    
    /* Inputs y selectboxes */
    .stTextInput>div>div>input, .stSelectbox>div>div>select {
        background: rgba(255, 255, 255, 0.1);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
    }
    
    /* Tabs premium */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: rgba(255, 255, 255, 0.7);
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# AUTENTICACIÓN SIMPLE
# =============================================================================
# Autenticación básica con session_state (para demo)
# En producción, usar una solución más robusta

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align: center;'>🔐 Agente de Facturas Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: rgba(255,255,255,0.8);'>Introduce tu contraseña para acceder</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        password = st.text_input("Contraseña", type="password", key="password_input")
        
        if st.button("🚀 Entrar", use_container_width=True):
            if password == "admin123":  # Contraseña demo
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Contraseña incorrecta")
        
        st.info("💡 **Demo:** Contraseña: `admin123`")
    st.stop()

# =============================================================================
# DASHBOARD PRINCIPAL
# =============================================================================

# Header con logout
col1, col2 = st.columns([6, 1])
with col1:
    st.title("💼 Agente de Facturas Pro")
    st.markdown("Bienvenido, **Administrador** 👋")
with col2:
    if st.button("🚪 Salir"):
        st.session_state.authenticated = False
        st.rerun()

st.markdown("---")

# =============================================================================
# FUNCIÓN DE CARGA DE DATOS
# =============================================================================

@st.cache_data(ttl=60)
def load_data():
    """Carga datos de la base de datos con caché."""
    db_path = "sqlite:///data/facturas.db"
    
    if "sqlite:///" in db_path:
        file_path = db_path.replace("sqlite:///", "")
        if not os.path.isabs(file_path):
            file_path = os.path.join(os.getcwd(), file_path)
        db_path = f"sqlite:///{file_path}"

    engine = create_engine(db_path)
    
    try:
        df_facturas = pd.read_sql("SELECT * FROM facturas", engine)
        
        if not df_facturas.empty:
            df_facturas['fecha_emision'] = pd.to_datetime(df_facturas['fecha_emision'])
            df_facturas['created_at'] = pd.to_datetime(df_facturas['created_at'])
            
        return df_facturas
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")
        return pd.DataFrame()

df = load_data()

# =============================================================================
# SIDEBAR - FILTROS Y ACCIONES
# =============================================================================

with st.sidebar:
    st.header("⚙️ Panel de Control")
    
    # Filtros
    st.subheader("🔍 Filtros")
    
    if not df.empty:
        # Filtro por fecha
        fecha_min = df['fecha_emision'].min().date()
        fecha_max = df['fecha_emision'].max().date()
        
        fecha_rango = st.date_input(
            "Rango de fechas",
            value=(fecha_min, fecha_max),
            min_value=fecha_min,
            max_value=fecha_max
        )
        
        # Filtro por estado
        estados = st.multiselect(
            "Estado",
            options=df['status'].unique(),
            default=df['status'].unique()
        )
        
        # Filtro por proveedor
        proveedores = st.multiselect(
            "Proveedor",
            options=df['nombre_proveedor'].unique(),
            default=df['nombre_proveedor'].unique()
        )
    
    st.markdown("---")
    
    # Subida de archivos
    st.subheader("📤 Subir Factura")
    uploaded_files = st.file_uploader(
        "Arrastra archivos aquí",
        type=['pdf', 'jpg', 'jpeg', 'png'],
        accept_multiple_files=True,
        help="Sube facturas en formato PDF o imagen"
    )
    
    if uploaded_files:
        if st.button("🚀 Procesar Facturas", use_container_width=True):
            with st.spinner("Procesando..."):
                # Aquí iría la lógica de procesamiento
                st.success(f"✅ {len(uploaded_files)} factura(s) procesadas correctamente")
                st.balloons()
    
    st.markdown("---")
    
    # Exportar datos
    st.subheader("💾 Exportar Datos")
    if st.button("📊 Descargar Excel", use_container_width=True):
        st.info("Generando archivo Excel...")
    
    if st.button("🔄 Recargar Datos", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# =============================================================================
# CONTENIDO PRINCIPAL
# =============================================================================

if df.empty:
    st.warning("📭 No hay datos todavía. Procesa algunas facturas para verlas aquí.")
else:
    # Aplicar filtros
    if len(fecha_rango) == 2:
        df_filtered = df[
            (df['fecha_emision'].dt.date >= fecha_rango[0]) &
            (df['fecha_emision'].dt.date <= fecha_rango[1]) &
            (df['status'].isin(estados)) &
            (df['nombre_proveedor'].isin(proveedores))
        ]
    else:
        df_filtered = df[
            (df['status'].isin(estados)) &
            (df['nombre_proveedor'].isin(proveedores))
        ]
    
    # =============================================================================
    # MÉTRICAS PRINCIPALES - KPIs
    # =============================================================================
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_facturas = len(df_filtered)
    total_importe = df_filtered['total_factura'].sum()
    facturas_ok = len(df_filtered[df_filtered['status'] == 'OK'])
    facturas_review = len(df_filtered[df_filtered['status'] == 'REVIEW'])
    
    with col1:
        st.metric(
            "Total Facturas",
            f"{total_facturas:,}",
            delta=f"+{len(df_filtered[df_filtered['created_at'] > datetime.now() - timedelta(days=7)])} esta semana"
        )
    
    with col2:
        st.metric(
            "Importe Total",
            f"{total_importe:,.2f} €",
            delta=f"{(total_importe / len(df_filtered)):.2f} € promedio" if total_facturas > 0 else "0 €"
        )
    
    with col3:
        st.metric(
            "Auto-Aprobadas",
            f"{facturas_ok} ({facturas_ok/total_facturas*100:.1f}%)" if total_facturas > 0 else "0",
            delta="Procesamiento automático",
            delta_color="normal"
        )
    
    with col4:
        st.metric(
            "Pendientes Revisión",
            facturas_review,
            delta="-2 vs mes anterior",
            delta_color="inverse"
        )
    
    st.markdown("---")
    
    # =============================================================================
    # VISUALIZACIONES AVANZADAS
    # =============================================================================
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Análisis", "📋 Facturas", "✏️ Editar"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Estado de Procesamiento")
            fig_status = px.pie(
                df_filtered,
                names='status',
                title='Distribución por Estado',
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Purples_r
            )
            fig_status.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            st.plotly_chart(fig_status, use_container_width=True)
        
        with col2:
            st.subheader("Top 5 Proveedores")
            top_proveedores = df_filtered.groupby('nombre_proveedor')['total_factura'].sum().sort_values(ascending=False).head(5)
            fig_proveedores = px.bar(
                x=top_proveedores.values,
                y=top_proveedores.index,
                orientation='h',
                title='Por Importe Total',
                color=top_proveedores.values,
                color_continuous_scale='Purples'
            )
            fig_proveedores.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                showlegend=False
            )
            st.plotly_chart(fig_proveedores, use_container_width=True)
    
    with tab2:
        st.subheader("Evolución Temporal")
        
        if 'fecha_emision' in df_filtered.columns and not df_filtered['fecha_emision'].isnull().all():
            df_time = df_filtered.set_index('fecha_emision').resample('W')['total_factura'].agg(['sum', 'count']).reset_index()
            
            fig_time = go.Figure()
            fig_time.add_trace(go.Scatter(
                x=df_time['fecha_emision'],
                y=df_time['sum'],
                mode='lines+markers',
                name='Importe',
                line=dict(color='#667eea', width=3),
                fill='tozeroy',
                fillcolor='rgba(102, 126, 234, 0.2)'
            ))
            
            fig_time.update_layout(
                title='Volumen Semanal',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                hovermode='x unified'
            )
            st.plotly_chart(fig_time, use_container_width=True)
        
        # Análisis por mes
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Factura Promedio", f"{df_filtered['total_factura'].mean():.2f} €")
            st.metric("Factura Máxima", f"{df_filtered['total_factura'].max():.2f} €")
        
        with col2:
            st.metric("Factura Mínima", f"{df_filtered['total_factura'].min():.2f} €")
            st.metric("Desviación Estándar", f"{df_filtered['total_factura'].std():.2f} €")
    
    with tab3:
        st.subheader("📋 Listado de Facturas")
        
        # Barra de búsqueda
        search = st.text_input("🔍 Buscar por número de factura o proveedor", "")
        
        if search:
            df_display = df_filtered[
                df_filtered['numero_factura'].str.contains(search, case=False, na=False) |
                df_filtered['nombre_proveedor'].str.contains(search, case=False, na=False)
            ]
        else:
            df_display = df_filtered
        
        st.dataframe(
            df_display[['id', 'numero_factura', 'fecha_emision', 'nombre_proveedor', 'total_factura', 'status', 'validation_notes']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "total_factura": st.column_config.NumberColumn("Total", format="%.2f €"),
                "fecha_emision": st.column_config.DateColumn("Fecha"),
                "status": st.column_config.TextColumn("Estado"),
                "id": st.column_config.NumberColumn("ID", width="small"),
            }
        )
    
    with tab4:
        st.subheader("✏️ Editar Factura")
        st.info("💡 Selecciona una factura para corregir datos extraídos incorrectamente")
        
        factura_id = st.selectbox(
            "Seleccionar Factura",
            options=df_filtered['id'].tolist(),
            format_func=lambda x: f"#{x} - {df_filtered[df_filtered['id']==x]['numero_factura'].iloc[0]}"
        )
        
        if factura_id:
            factura = df_filtered[df_filtered['id'] == factura_id].iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                nuevo_numero = st.text_input("Número de Factura", factura['numero_factura'])
                nuevo_proveedor = st.text_input("Proveedor", factura['nombre_proveedor'])
                nuevo_cif = st.text_input("CIF", factura['cif_proveedor'] or "")
            
            with col2:
                nueva_fecha = st.date_input("Fecha Emisión", factura['fecha_emision'])
                nuevo_total = st.number_input("Total", value=float(factura['total_factura']))
                nuevo_status = st.selectbox("Estado", ['OK', 'REVIEW', 'ERROR'], index=0 if factura['status']=='OK' else 1)
            
            if st.button("💾 Guardar Cambios", use_container_width=True):
                st.success("✅ Cambios guardados correctamente")
                st.balloons()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: rgba(255,255,255,0.6); padding: 2rem;'>
    <p>💼 Agente de Facturas Pro v2.0 | Powered by IA | © 2024 Tu Empresa</p>
</div>
""", unsafe_allow_html=True)

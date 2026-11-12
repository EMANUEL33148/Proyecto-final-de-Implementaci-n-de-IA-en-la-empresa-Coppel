import os

import streamlit as st
from azure.core.exceptions import AzureError, ClientAuthenticationError
from openai import OpenAIError


AZURE_AI_PROJECT_ENDPOINT = "https://coppel73.services.ai.azure.com/api/projects/asistente-coppel"
AZURE_AI_AGENT_NAME = "Coppel"


def obtener_configuracion(nombre, valor_por_defecto=""):
    """Lee la configuración desde los secretos de Streamlit o variables de entorno."""
    try:
        valor = st.secrets.get(nombre, valor_por_defecto)
    except (FileNotFoundError, KeyError):
        valor = valor_por_defecto

    return os.getenv(nombre, valor)


@st.cache_resource
def obtener_cliente_azure(endpoint, agent_name):
    """Crea una sola conexión reutilizable al proyecto de Azure AI."""
    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential

    inicio_interactivo = obtener_configuracion(
        "AZURE_INTERACTIVE_LOGIN", "true"
    ).strip().lower() in {"1", "true", "yes", "si", "sí"}
    cliente_proyecto = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(
            exclude_interactive_browser_credential=not inicio_interactivo
        ),
        allow_preview=True,
    )
    return cliente_proyecto.get_openai_client(agent_name=agent_name)


def obtener_url_imagen(nombre, url_por_defecto=""):
    """Lee una URL de imagen desde secrets de Streamlit o variables de entorno."""
    try:
        url = st.secrets.get(nombre, "")
    except FileNotFoundError:
        url = ""

    return url or os.getenv(nombre, "") or url_por_defecto


def agregar_token_sas(url):
    """Agrega el token SAS configurado sin guardar credenciales en el código."""
    try:
        token_sas = st.secrets.get("AZURE_SAS_TOKEN", "")
    except FileNotFoundError:
        token_sas = ""

    token_sas = token_sas or os.getenv("AZURE_SAS_TOKEN", "")
    if not token_sas:
        return url

    separador = "&" if "?" in url else "?"
    return f"{url}{separador}{token_sas.lstrip('?')}"


def mostrar_imagen_azure(nombre, caption, url_por_defecto="", usar_configuracion=True, **kwargs):
    """Muestra una imagen alojada en Azure Blob Storage si la URL está configurada."""
    url = obtener_url_imagen(nombre, url_por_defecto) if usar_configuracion else url_por_defecto
    if url:
        st.image(agregar_token_sas(url), caption=caption, use_container_width=True, **kwargs)
    else:
        st.info(f"Configura {nombre} para mostrar esta imagen de Azure.")

# Configuración de la página
st.set_page_config(
    page_title="Portal de IA - Coppel Avanzado",
    page_icon="🛒",
    layout="wide"
)

# Menú lateral para navegación
st.sidebar.title("Menú del Sistema")
modulo = st.sidebar.radio(
    "Selecciona un Módulo:",
    (
        "Inicio / Propuesta",
        "Seguridad (Visión Artificial)",
        "Operaciones e Inventario",
        "Asistente IA para Empleados"
    )
)

# ================= MODULE: INICIO =================
if modulo == "Inicio / Propuesta":
    st.markdown("<h1 style='text-align: center;'>Proyecto Integral de Implementación de IA en Coppel</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666; font-size: 1.1rem;'>Programa: Fundamentos de Inteligencia Artificial con Tecnologías Microsoft</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #777; font-size: 0.9rem;'>Elaborado por: Emanuel Ramírez Álvarez</p>", unsafe_allow_html=True)

    mostrar_imagen_azure(
        "AZURE_PORTADA_URL",
        "Imagen principal del proyecto almacenada en Azure Blob Storage",
    )
    
    st.markdown("---")
    st.subheader("Objetivo General")
    st.write("Maximizar la eficiencia operativa, mitigar riesgos de merma y optimizar la experiencia de servicio mediante analítica avanzada e inteligencia artificial.")
    
    st.markdown("---")
    st.subheader("Arquitectura de Módulos del Sistema")
    st.write("El portal integra soluciones tecnológicas escalables para la optimización de los procesos en sucursal:")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("🛡️ **Seguridad Avanzada**")
        st.write("Detección de patrones de riesgo y monitoreo multicanal con visión artificial.")
    with col2:
        st.markdown("📊 **Inventario Predictivo**")
        st.write("Control logístico y analítica de demanda para evitar quiebres de stock.")
    with col3:
        st.markdown("💬 **Asistente Inteligente**")
        st.write("Orientación en normativas, manuales y protocolos de emergencia para colaboradores.")

# ================= MODULE: SEGURIDAD =================
elif modulo == "Seguridad (Visión Artificial)":
    st.markdown("<h1 style='text-align: center;'>🛡️ Módulo de Seguridad y Prevención de Pérdidas Avanzado</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Sistema de vigilancia inteligente optimizado para la identificación de patrones de riesgo en sucursal.</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Monitoreo Multicanal en Vivo")
        st.markdown("**Cámaras Activas:** Pasillo 1 (Electrónica) | Caja Principal | Bodega Trasera | Baños | Pasillo 2")
        
        # Opciones completas de simulación (10 puntos de ubicación/evento)
        zonas_simulacion = [
            "Permanencia prolongada en Pasillo 1",
            "Permanencia prolongada en Pasillo 2",
            "Acceso no autorizado a Zona Restringida",
            "Incidencia en Caja 1",
            "Incidencia en Caja 2",
            "Movimiento sospechoso en Baño de Mujeres",
            "Movimiento sospechoso en Baño de Hombres",
            "Permanencia prolongada en Bodega",
            "Bloqueo de salida de emergencia",
            "Retención prolongada en área de Probadores"
        ]
        
        tipo_alerta = st.selectbox("Selecciona tipo de prueba de simulación:", zonas_simulacion)
        
        if st.button("Ejecutar Simulación de Alerta"):
            st.error(f"⚠️ Alerta simulada activa: {tipo_alerta}. Notificando a supervisor de turno.")
            st.markdown("##### 📷 Captura de Cámara en Vivo (Simulación de Infracción)")

            imagenes_seguridad = {
                "Permanencia prolongada en Pasillo 1": "https://coppelstorage01.blob.core.windows.net/alerta-seguridad/1.-%20Permanecia%20prolongada%20pasillo%201.jpg",
                "Permanencia prolongada en Pasillo 2": "https://coppelstorage01.blob.core.windows.net/alerta-seguridad/2.-%20Permanecia%20prolongada%20pasillo%202.jpg",
                "Acceso no autorizado a Zona Restringida": "https://coppelstorage01.blob.core.windows.net/alerta-seguridad/3.-%20acceso%20no%20autorizado%20z.%20restrigida.jpg",
                "Incidencia en Caja 1": "https://coppelstorage01.blob.core.windows.net/alerta-seguridad/4.-incidencia%20en%20caja%201.jpg",
                "Incidencia en Caja 2": "https://coppelstorage01.blob.core.windows.net/alerta-seguridad/5.-%20incidencia%20en%20caja%202.jpg",
                "Movimiento sospechoso en Baño de Mujeres": "https://coppelstorage01.blob.core.windows.net/alerta-seguridad/6.%20movimiento%20sosp.%20en%20ba%C3%B1os%20de%20mujeres.jpg",
                "Movimiento sospechoso en Baño de Hombres": "https://coppelstorage01.blob.core.windows.net/alerta-seguridad/7.-%20movimiento%20sosp.%20en%20ba%C3%B1os%20de%20hombres.jpg",
                "Permanencia prolongada en Bodega": "https://coppelstorage01.blob.core.windows.net/alerta-seguridad/8.-Permanencia%20prolongada%20en%20Bodega.jpg",
                "Bloqueo de salida de emergencia": "https://coppelstorage01.blob.core.windows.net/alerta-seguridad/9.-Bloqueo%20de%20salida%20de%20emergencia.jpg",
                "Retención prolongada en área de Probadores": "https://coppelstorage01.blob.core.windows.net/alerta-seguridad/10.-%20Retencion%20%20prolongada%20en%20area%20de%20probadores.jpg",
            }
            imagen_seguridad = imagenes_seguridad[tipo_alerta]
            mostrar_imagen_azure(
                "AZURE_SEGURIDAD_URL",
                "Captura de seguridad almacenada en Azure Blob Storage",
                imagen_seguridad,
                usar_configuracion=False,
            )
            
            # Simulación visual de captura de pantalla con marca de agua e interfaz de visión artificial
            st.info(f"🖼️ [FRAME DE SEGURIDAD DETECTADO] -> Analizando rostro y comportamiento en zona: **{tipo_alerta}**. Evidencia registrada en servidor central.")
            
            # Contenedor visual simulado tipo frame de IA con recuadro
            st.warning("""
            🚨 **[ALERTA DE SEGURIDAD - POSIBLE ROBO O INCIDENCIA DETECTADA]**
            - **Sujeto:** Identificado en área vigilada bajo patrón de riesgo.
            - **Estado:** Evidencia capturada, rostro enmarcado y notificada al equipo de prevención de pérdidas.
            """)
            
            # Nota: Puedes integrar st.image con una URL pública o imagen local si lo requieres, ej: st.image("ruta_imagen.jpg", caption="Captura de Infracción")
        else:
            st.info("● Estado del sistema: Red de cámaras operando con normalidad. Sin incidencias de alta prioridad activas.")
            
    with col2:
        st.subheader("Registro Automatizado de Eventos")
        st.write("**Fecha y Hora:** 2026-09-24 14:24:41")
        st.write("**Ubicación:** Sucursal Coppel Centro")
        st.write("**Nivel de Riesgo:** Moderado / Alto")
        
        st.markdown("##### Historial de Incidencias Recientes")
        st.table({
            "Folio": ["INC-001", "INC-002", "INC-003"],
            "Zona / Pasillo": ["Pasillo 1", "Caja 2", "Baño Mujeres"],
            "Estado": ["Atendida", "Pendiente", "En Revisión"]
        })

# ================= MODULE: OPERACIONES E INVENTARIO =================
elif modulo == "Operaciones e Inventario":
    st.markdown("<h1 style='text-align: center;'>📊 Operaciones y Gestión de Inventario Predictivo</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Panel de control logístico para la minimización de quiebres de stock y gestión inteligente de pasillos.</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("Tendencias de Demanda Predictiva (Por Semana)")
    st.write("Estimación de rotación de productos basada en historial de ventas de la región, segmentada por categorías clave.")
    
    chart_data = {
        "Categoría": ["Ropa Interior", "Pantalones", "Calzado", "Blusas", "Accesorios"],
        "Demanda Estimada (Unidades)": [90, 85, 75, 70, 60]
    }
    st.bar_chart(chart_data, x="Categoría", y="Demanda Estimada (Unidades)")
    
    st.markdown("---")
    st.subheader("Detalle Analítico de Stock y Pasillos (Catálogo Extendido - 30 Productos)")
    st.write("Matriz de rendimiento logístico optimizada con 30 artículos clave para control de inventario en sucursal:")
    
    # Tabla ampliada exactamente con 30 productos solicitados
    st.table({
        "ID / Producto": [
            "PRD-001: Pantalón de Mezclilla Hombre", "PRD-002: Pantalón Casual Mujer", "PRD-003: Blusa Manga Larga", 
            "PRD-004: Blusa Casual Estampada", "PRD-005: Camisa Formal Caballero", "PRD-006: Camisa Casual Denim", 
            "PRD-007: Ropa Interior Mujer (Pack 3)", "PRD-008: Ropa Interior Hombre (Boxer)", "PRD-009: Calzado Deportivo Running", 
            "PRD-010: Zapatilla Casual de Piel", "PRD-011: Bota de Trabajo Industrial", "PRD-012: Gorra Deportiva Ajustable", 
            "PRD-013: Cinturón de Piel Caballero", "PRD-014: Playera Polo Básica", "PRD-015: Playera Deportiva Dry-Fit", 
            "PRD-016: Sudadera con Capucha Unisex", "PRD-017: Chamarra Impermeable", "PRD-018: Vestido Casual Verano", 
            "PRD-019: Falda de Mezclilla", "PRD-020: Short Deportivo", "PRD-021: Calcetas Deportivas (Pack 3)", 
            "PRD-022: Pijama Invierno Polar", "PRD-023: Mochila Escolar Casual", "PRD-024: Cartera de Piel Sintética", 
            "PRD-025: Lentes de Sol UV400", "PRD-026: Reloj Analógico Casual", "PRD-027: Toalla de Baño Estándar", 
            "PRD-028: Sábana Matrimonial de Algodón", "PRD-029: Almohada Confort Plus", "PRD-030: Cobija Térmica Individual"
        ],
        "Stock Actual": [
            "25 unidades", "18 unidades", "35 unidades", "40 unidades", "50 unidades", "22 unidades",
            "60 unidades", "55 unidades", "42 unidades", "15 unidades", "10 unidades", "30 unidades",
            "25 unidades", "45 unidades", "38 unidades", "20 unidades", "12 unidades", "28 unidades",
            "16 unidades", "33 unidades", "80 unidades", "14 unidades", "22 unidades", "31 unidades",
            "27 unidades", "19 unidades", "40 unidades", "11 unidades", "25 unidades", "18 unidades"
        ],
        "Rotación Semanal": [
            "Alta", "Alta", "Alta", "Media", "Media", "Baja", 
            "Alta", "Alta", "Alta", "Media", "Baja", "Media", 
            "Media", "Alta", "Alta", "Media", "Baja", "Media", 
            "Baja", "Media", "Alta", "Baja", "Media", "Media", 
            "Media", "Baja", "Media", "Baja", "Media", "Baja"
        ],
        "Sugerencia IA": [
            "Reponer urgente", "Stock óptimo", "Surtir modelo top", "Mantener stock", "Revisar merma", "Auditar inventario",
            "Reponer urgente", "Stock óptimo", "Reponer preventivo", "Mantener stock", "Revisar merma", "Stock óptimo",
            "Mantener stock", "Reponer urgente", "Stock óptimo", "Mantener stock", "Reponer preventivo", "Revisar merma",
            "Auditar inventario", "Mantener stock", "Reponer urgente", "Auditar inventario", "Stock óptimo", "Mantener stock",
            "Mantener stock", "Revisar merma", "Stock óptimo", "Auditar inventario", "Mantener stock", "Revisar merma"
        ]
    })

# ================= MODULE: ASISTENTE VIRTUAL =================
elif modulo == "Asistente IA para Empleados":
    st.markdown("<h1 style='text-align: center;'>💬 Asistente Virtual Inteligente para Colaboradores</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Consulta rápida de normativas internas, manuales operativos, manejo de inventarios, recomendaciones de productos y protocolos de emergencia.</p>", unsafe_allow_html=True)

    st.markdown("---")
    st.write("¡Hola! Soy **Asistente Coppel**. Cuéntame qué necesitas y te ayudaré con tus consultas de trabajo.")

    endpoint = obtener_configuracion(
        "AZURE_AI_PROJECT_ENDPOINT", AZURE_AI_PROJECT_ENDPOINT
    )
    agent_name = obtener_configuracion("AZURE_AI_AGENT_NAME", AZURE_AI_AGENT_NAME)

    if "conversacion_asistente" not in st.session_state:
        st.session_state.conversacion_asistente = []

    for mensaje in st.session_state.conversacion_asistente:
        with st.chat_message(mensaje["role"]):
            st.markdown(mensaje["content"])

    consulta = st.chat_input("Escribe tu consulta para el asistente...")
    if consulta:
        with st.chat_message("user"):
            st.markdown(consulta)

        mensajes = [
            {"role": mensaje["role"], "content": mensaje["content"]}
            for mensaje in st.session_state.conversacion_asistente[-12:]
        ]
        mensajes.append({"role": "user", "content": consulta})

        try:
            cliente_openai = obtener_cliente_azure(endpoint, agent_name)
            conversacion = cliente_openai.conversations.create()
            respuesta = cliente_openai.responses.create(
                conversation=conversacion.id,
                input=mensajes,
            )
            texto_respuesta = respuesta.output_text
            if not texto_respuesta:
                raise ValueError("El agente no devolvió texto.")

            st.session_state.conversacion_asistente.extend(
                [
                    {"role": "user", "content": consulta},
                    {"role": "assistant", "content": texto_respuesta},
                ]
            )
            with st.chat_message("assistant"):
                st.markdown(texto_respuesta)
        except ClientAuthenticationError as error:
            st.error(
                "No se pudo autenticar con Azure. En desarrollo local, inicia "
                "sesión en la ventana del navegador que se abre o ejecuta "
                "`az login`; la cuenta debe tener el rol Foundry User (o permisos "
                "equivalentes) en el proyecto. Si la aplicación está desplegada "
                "en Azure, configura una identidad administrada y establece "
                "AZURE_INTERACTIVE_LOGIN=false. "
                f"Detalle técnico: {error}"
            )
        except (AzureError, OpenAIError, ValueError) as error:
            st.error(
                "Azure recibió la solicitud, pero no se pudo completar. Verifica "
                "que AZURE_AI_AGENT_NAME coincida con el nombre publicado del "
                "agente y que tu identidad tenga acceso al proyecto. "
                f"Detalle técnico: {error}"
            )
            

import streamlit as st
import google.generativeai as genai

# Configuración de la página
st.set_page_config(page_title="Tu Chefcito", page_icon="👨‍🍳", layout="wide")

# --- ESTILOS CSS (Alineación Izquierda, Tamaño 24px) ---
st.markdown("""
<style>
    /* Alinear texto a la izquierda y tamaño 24px */
    .stMarkdown p, .stMarkdown li {
        font-size: 24px !important;
        line-height: 1.5 !important;
        text-align: left !important;
    }
    /* Cuadro de entrada grande */
    div[data-testid="stChatInput"] textarea {
        font-size: 24px !important;
    }
    /* Barra lateral */
    section[data-testid="stSidebar"] p {
        font-size: 18px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- LÓGICA DE MEMORIA (Session State) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- DEFINICIÓN DE LA PERSONALIDAD (Ampliado con Fuentes Médicas) ---
SYSTEM_PROMPT = """
Eres "Tu Chefcito", un chef amable, divertido y experto en cocina saludable.
Atiendes a personas con condiciones crónicas o terminales (Diabetes, Gastritis, Cáncer, Tuberculosis, Enfermedades Renales, etc.).

REGLAS DE ORO:
1. SALUDO: Saluda una sola vez con calidez humana.
2. SEGURIDAD Y FUENTES: Basa tus recomendaciones en ciencia y fuentes confiables para dar seguridad. Consulta y referencia principios de:
   - OMS (Organización Mundial de la Salud)
   - CDC (Centros para el Control y Prevención de Enfermedades)
   - Harvard T.H. Chan School of Public Health
   - Mayo Clinic
   - American Heart Association (Corazón)
   - National Kidney Foundation (Riñón)
   - MiPlato / Diabetes Food Hub
3. BREVEDAD (CRÍTICO): Respuestas CORTAS. Ve al grano: Lista de compras y Pasos sencillos. Nada de explicaciones extensas.
4. LISTA DE COMPRAS: Proporciona la lista directamente.
5. ESTILO: Amable, divertido y humano. Usa emojis. Tu objetivo es levantar el ánimo.
6. NUTRICIÓN: Dato conciso.
7. FINALIZACIÓN: Termina con: "¿Desea que le asista con algún otro platillo?"
"""

# --- INTERFAZ DE USUARIO ---

# Intentamos leer la clave de los Secrets
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    api_key = None

with st.sidebar:
    st.title("🔧 Configuración")
    if api_key:
        st.success("🔑 ¡Conexión activa!")
    else:
        st.markdown("Ingresa tu API Key de Google.")
        api_key = st.text_input("Google API Key", type="password")
    st.markdown("---")
    st.markdown("Desarrollado con ❤️ para tu salud.")

# Título principal
st.title("👨‍🍳 Tu Chefcito")

# Verificar API Key
if not api_key:
    st.warning("👋 ¡Hola! Soy Tu Chefcito. Por favor, ingresa tu **Google API Key** en la barra lateral.")
    st.stop()

# Configurar el cliente de Google
genai.configure(api_key=api_key)

# Configurar el modelo
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash", 
    system_instruction=SYSTEM_PROMPT
)

# --- VISUALIZACIÓN DEL HISTORIAL ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- LÓGICA DE CHAT ---

# Saludo inicial (Breve, encantador y humano)
if len(st.session_state.messages) == 0:
    saludo_inicial = "¡Hola! Soy **Tu Chefcito** 👨‍🍳✨\n\nPara cocinarte algo rico y te sienta de maravilla, cuéntame: ¿en qué país estás, para cuántos cocino y qué enfermedad tienes? ¡Vamos a darle sabor a esa recuperación!"
    st.session_state.messages.append({"role": "assistant", "content": saludo_inicial})
    with st.chat_message("assistant"):
        st.markdown(saludo_inicial)

# Captura input
if prompt := st.chat_input("Escribe aquí..."):
    # Mostrar mensaje usuario
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Llamar a la API de Google
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Construir el historial para Google
            history = []
            for m in st.session_state.messages:
                role = "user" if m["role"] == "user" else "model"
                history.append({"role": role, "parts": [m["content"]]})

            # Iniciar chat
            chat = model.start_chat(history=history)
            
            # Enviar mensaje y transmitir respuesta (Efecto Máquina de Escribir)
            response = chat.send_message(prompt, stream=True)
            
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    # Mostramos el texto con el cursor
                    message_placeholder.markdown(full_response + "▌")
            
            # Texto final
            message_placeholder.markdown(full_response)
            
            # Guardar en historial
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"¡Ups! Error en cocina: {e}")

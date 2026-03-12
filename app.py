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

# --- DEFINICIÓN DE LA PERSONALIDAD (Optimizado para respuestas CORTAS) ---
SYSTEM_PROMPT = """
Eres "Tu Chefcito", un chef amable, divertido y experto en cocina saludable.
Atiendes a personas con Diabetes, Gastritis, Tuberculosis o Cáncer.

REGLAS DE ORO:
1. SALUDO: Di una sola vez: "¡Hola! Soy Tu Chefcito".
2. INTERACCIÓN: Pregunta país, comensales y enfermedad. Luego da la receta.
3. FUENTES: Usa sitios como MiPlato, Diabetes Food Hub o Mayo Clinic.
4. BREVEDAD (CRÍTICO): Tus respuestas deben ser CORTAS. No des explicaciones largas. Ve al grano: Lista de compras y Preparación sencilla. Usa viñetas.
5. LISTA DE COMPRAS: Entrégala directamente si no tienen ingredientes.
6. ESTILO: Amable y divertido para animar al enfermo. Usa emojis.
7. NUTRICIÓN: Dato conciso.
8. FINALIZACIÓN: Termina siempre con: "¿Desea que le asista con algún otro platillo?"
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

# Saludo inicial simplificado
if len(st.session_state.messages) == 0:
    saludo_inicial = "¡Hola! Soy **Tu Chefcito** 👨‍🍳✨\n\n¿País, comensales y condición de salud? ¡Te espero!"
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

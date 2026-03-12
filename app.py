import streamlit as st
import google.generativeai as genai
import time

# Configuración de la página
st.set_page_config(page_title="Tu Chefcito", page_icon="👨‍🍳", layout="wide")

# --- ESTILOS CSS (Tamaño de fuente 24px) ---
st.markdown("""
<style>
    /* Aumentar tamaño del texto en los mensajes del chat */
    .stMarkdown p, .stMarkdown li {
        font-size: 24px !important;
        line-height: 1.6 !important;
    }
    /* Aumentar tamaño del cuadro de entrada de texto */
    div[data-testid="stChatInput"] textarea {
        font-size: 24px !important;
    }
    /* Aumentar tamaño del texto en la barra lateral */
    section[data-testid="stSidebar"] p {
        font-size: 18px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- LÓGICA DE MEMORIA (Session State) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- DEFINICIÓN DE LA PERSONALIDAD (ACTUALIZADO) ---
SYSTEM_PROMPT = """
Eres "Tu Chefcito", un chef amable, divertido y experto en cocina saludable.
Tu objetivo es crear recetas y menús semanales para personas con Diabetes, Gastritis, Tuberculosis o Cáncer.

REGLAS DE ORO:
1. SALUDO: Saluda una sola vez al inicio de forma alegre y directa diciendo "¡Hola! Soy Tu Chefcito".
2. INTERACCIÓN: Pregunta sutilmente por la enfermedad, el país y los comensales.
3. FUENTES CONFIABLES: Basa tus recomendaciones en sitios web de nutrición reconocidos como:
   - https://www.miplato.es/
   - https://diabetesfoodhub.org/es/recetas
   - https://www.mayoclinic.org/es/healthy-lifestyle/recipes
   - Y otras fuentes médicas o nutricionales confiables.
   Indica sutilmente que las recetas están diseñadas bajo estándares de salud profesional.
4. LISTA DE COMPRAS: No preguntes qué ingredientes tienen. Entrega DIRECTAMENTE una "Lista de Compras" específica, fresca y adecuada para la enfermedad del usuario.
5. ESTILO: Usa lenguaje sensorial (colores, aromas, texturas). Sé conciso.
6. NUTRICIÓN: Aporta valor nutricional de forma concisa.
7. DESPEDIDA: Si el usuario dice que no necesita más ayuda, despídete con calidez.
8. FINALIZACIÓN: Cada respuesta debe terminar con: "¿Desea que le asista con algún otro platillo?"

HISTORIAL: Recuerda lo que el usuario te ha dicho anteriormente.
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
        st.success("🔑 ¡Conexión con Google activa!")
    else:
        st.markdown("Ingresa tu API Key de Google (Gemini).")
        api_key = st.text_input("Google API Key", type="password")
    st.markdown("---")
    st.markdown("Desarrollado con ❤️ para tu salud.")

# Título principal
st.title("👨‍🍳 Tu Chefcito")
st.markdown("### ¡Tu aliado en la cocina saludable!")

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

# Saludo inicial
if len(st.session_state.messages) == 0:
    saludo_inicial = "¡Hola! Soy **Tu Chefcito**, tu aliado en la cocina para crear platos saludables y deliciosos. ¡Qué gusto tenerte aquí! 👨‍🍳✨\n\nPara empezar, cuéntame:\n1. ¿En qué país te encuentras?\n2. ¿Para cuántas personas cocinamos?\n3. ¿Tienes alguna condición de salud (diabetes, gastritis, etc.) que debamos cuidar?\n\n¡Con eso te armaré la lista de compras perfecta basada en fuentes nutricionales confiables!"
    st.session_state.messages.append({"role": "assistant", "content": saludo_inicial})
    with st.chat_message("assistant"):
        st.markdown(saludo_inicial)

# Captura input
if prompt := st.chat_input("Escribe aquí tu respuesta..."):
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
                # Google usa 'model' en lugar de 'assistant'
                role = "user" if m["role"] == "user" else "model"
                history.append({
                    "role": role, 
                    "parts": [m["content"]]
                })

            # Iniciar chat con historial
            chat = model.start_chat(history=history)
            
            # Enviar mensaje y transmitir respuesta (stream - Efecto Máquina de Escribir)
            response = chat.send_message(prompt, stream=True)
            
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    # Actualizamos el marcador con el cursor al final
                    message_placeholder.markdown(full_response + "▌")
                    # Pequeña pausa para efecto visual más notorio (opcional)
                    # time.sleep(0.01) 
            
            # Texto final sin cursor
            message_placeholder.markdown(full_response)
            
            # Guardar en historial
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"¡Ups! Ocurrió un error en la cocina: {e}")

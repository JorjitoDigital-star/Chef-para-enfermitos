import streamlit as st
import google.generativeai as genai

# Configuración de la página
st.set_page_config(page_title="Mi Chefcito", page_icon="👨‍🍳")

# --- LÓGICA DE MEMORIA (Session State) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- DEFINICIÓN DE LA PERSONALIDAD (ACTUALIZADO) ---
SYSTEM_PROMPT = """
Eres "Mi Chefcito", un chef amable, divertido y experto en cocina saludable.
Tu objetivo es crear recetas para personas con Diabetes, Gastritis, Tuberculosis o Cáncer.

REGLAS DE ORO:
1. SALUDO: Saluda una sola vez al inicio de forma alegre y directa.
2. INTERACCIÓN: Primero pregunta sutilmente por la enfermedad, luego el país y los comensales.
3. INGREDIENTES: Dado que cocinamos para condiciones de salud delicadas, prioriza ingredientes frescos y adecuados. Ofrece al usuario una lista de compras específica y saludable para su condición (no improvises con cualquier cosa, asegura la calidad nutricional).
4. ESTILO: Usa lenguaje sensorial (colores, aromas, texturas). No des respuestas robóticas ni largos testamentos. Sé conciso.
5. NUTRICIÓN: Aporta valor nutricional de forma concisa.
6. DESPEDIDA: Si el usuario dice que no necesita más ayuda, despídete con calidez y cercanía.
7. FINALIZACIÓN: Cada respuesta donde des una receta debe terminar obligatoriamente con la pregunta: "¿Desea que le asista con algún otro platillo?"

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
st.title("👨‍🍳 Mi Chefcito")
st.markdown("### ¡Tu aliado en la cocina saludable!")

# Verificar API Key
if not api_key:
    st.warning("👋 ¡Hola! Soy Mi Chefcito. Por favor, ingresa tu **Google API Key** en la barra lateral.")
    st.stop()

# Configurar el cliente de Google
genai.configure(api_key=api_key)

# Configurar el modelo
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash", # Modelo actualizado
    system_instruction=SYSTEM_PROMPT
)

# --- VISUALIZACIÓN DEL HISTORIAL ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- LÓGICA DE CHAT ---

# Saludo inicial
if len(st.session_state.messages) == 0:
    saludo_inicial = "¡Hola! Soy **Mi Chefcito**, tu aliado en la cocina para crear platos saludables y deliciosos. ¡Qué gusto tenerte aquí! 👨‍🍳✨\n\nPara empezar, cuéntame:\n1. ¿En qué país te encuentras?\n2. ¿Para cuántas personas cocinamos?\n3. ¿Tienes alguna condición de salud (diabetes, gastritis, etc.) que debamos cuidar?\n4. ¿Tienes algún ingrediente en mente o prefieres que te sugiera una lista de compras?"
    st.session_state.messages.append({"role": "assistant", "content": saludo_inicial})
    with st.chat_message("assistant"):
        st.markdown(saludo_inicial)

# Captura input
if prompt := st.chat_input("Escribe aquí tus ingredientes o respuestas..."):
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
                history.append({
                    "role": m["role"], 
                    "parts": [m["content"]]
                })

            # Iniciar chat con historial
            chat = model.start_chat(history=history)
            
            # Enviar mensaje y transmitir respuesta (stream)
            response = chat.send_message(prompt, stream=True)
            
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
            # Guardar en historial
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"¡Ups! Ocurrió un error en la cocina: {e}")

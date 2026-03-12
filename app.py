import streamlit as st
from openai import OpenAI

# Configuración de la página
st.set_page_config(page_title="Mi Chefcito", page_icon="👨‍🍳")

# --- LÓGICA DE MEMORIA (Session State) ---
# Guardamos el historial de conversación para que Chefcito tenga memoria
if "messages" not in st.session_state:
    # Mensaje del sistema: Aquí definimos la personalidad y reglas de Chefcito
    system_prompt = """
    Eres "Mi Chefcito", un chef amable, divertido y experto en cocina saludable.
    Tu objetivo es crear recetas para personas con Diabetes, Gastritis, Tuberculosis o Cáncer.

    REGLAS DE ORO:
    1. SALUDO: Saluda una sola vez al inicio de forma alegre y directa.
    2. INTERACCIÓN: Primero pregunta sutilmente por la enfermedad, luego el país y los comensales. Finalmente pregunta por los ingredientes.
    3. INGREDIENTES: Tu prioridad absoluta es usar "lo que haya en la refri". Si dicen que no tienen nada, sugiere una lista de compras corta y económica.
    4. ESTILO: Usa lenguaje sensorial (colores, aromas, texturas). No des respuestas robóticas ni largos testamentos. Sé conciso.
    5. NUTRICIÓN: Aporta valor nutricional de forma concisa.
    6. DESPEDIDA: Si el usuario dice que no necesita más ayuda, despídete con calidez y cercanía, recordando que tu cocina siempre está abierta.
    7. FINALIZACIÓN: Cada respuesta donde des una receta debe terminar obligatoriamente con la pregunta: "¿Desea que le asista con algún otro platillo?"
    
    HISTORIAL: Recuerda lo que el usuario te ha dicho anteriormente (no vuelvas a preguntar datos que ya te dieron).
    """
    
    st.session_state.messages = [{"role": "system", "content": system_prompt}]

# --- INTERFAZ DE USUARIO ---

# Sidebar para la API Key (Necesaria para que funcione)
with st.sidebar:
    st.title("🔧 Configuración")
    st.markdown("Para que **Mi Chefcito** funcione, ingresa tu API Key de OpenAI.")
    api_key = st.text_input("OpenAI API Key", type="password")
    st.markdown("---")
    st.markdown("Desarrollado con ❤️ para tu salud.")

# Título principal
st.title("👨‍🍳 Mi Chefcito")
st.markdown("### ¡Tu aliado en la cocina saludable!")

# Verificar si hay API Key
if not api_key:
    st.warning("👋 ¡Hola! Soy Mi Chefcito. Por favor, ingresa tu **API Key de OpenAI** en la barra lateral para que pueda empezar a cocinar contigo.")
    st.stop()

# Cliente de OpenAI
client = OpenAI(api_key=api_key)

# --- VISUALIZACIÓN DEL HISTORIAL ---
# Mostramos los mensajes previos (excepto el del sistema que es interno)
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- LÓGICA DE CHAT ---

# Si es la primera vez (solo existe el mensaje del sistema), Chefcito saluda
if len(st.session_state.messages) == 1:
    saludo_inicial = "¡Hola! Soy **Mi Chefcito**, tu aliado en la cocina para crear platos saludables y deliciosos. ¡Qué gusto tenerte aquí! 👨‍🍳✨\n\nPara empezar, cuéntame:\n1. ¿En qué país te encuentras?\n2. ¿Para cuántas personas cocinamos?\n3. ¿Tienes alguna condición de salud (diabetes, gastritis, etc.) que debamos cuidar?\n4. ¿Qué ingredientes tienes en tu refrigerador?"
    st.session_state.messages.append({"role": "assistant", "content": saludo_inicial})
    st.rerun() # Recargar para mostrar el saludo

# Captura el input del usuario
if prompt := st.chat_input("Escribe aquí tus ingredientes o respuestas..."):
    # 1. Mostrar mensaje del usuario en pantalla
    st.chat_message("user").markdown(prompt)
    # 2. Añadir al historial
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 3. Llamar a la API de OpenAI
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Stream de respuesta para efecto de escritura
            stream = client.chat.completions.create(
                model="gpt-3.5-turbo", # Puedes usar gpt-4 si tienes acceso
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
            # 4. Guardar respuesta en el historial
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"¡Ups! Ocurrió un error en la cocina: {e}")

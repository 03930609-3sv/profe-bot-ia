import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. Configuración de la Página
st.set_page_config(
    page_title="Profe Bot IA",
    page_icon="🎓",
    layout="centered"
)

# 2. Cargar la llave de seguridad
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("❌ No se encontró la API Key. Revisa tu archivo .env")
    st.stop()

genai.configure(api_key=api_key)

# 3. Configuración del Modelo y Personalidad
MODELO_A_USAR = "gemini-2.5-flash" # O usa "gemini-pro" si prefieres

INSTRUCCIONES = """
Eres un profesor experto de Bachillerato, especializado en Tecnología.
Tu nombre es 'Profe Bot'.
Tus reglas de comportamiento son:
1. Explica todo con paciencia y usa un lenguaje cercano y motivador.
2. Usar analogías divertidas (ej. comparar código con recetas de cocina o videojuegos).
3. Ser paciente y motivador. Si el estudiante se equivoca, dile que es parte del aprendizaje.
4. Usa negritas para conceptos clave.
5. NUNCA des la respuesta directa a una tarea. Guía al estudiante con pistas para que piense.
6. Si el estudiante te saluda, preséntate y pregunta qué quiere aprender hoy.
7. Usa emojis para hacer la clase divertida 💻.
"""

# 4. Inicializar el Chat y la Memoria
# Si no existe historial, creamos una lista vacía
if "history" not in st.session_state:
    st.session_state.history = []

try:
    # Cargamos el modelo con el historial que tengamos guardado
    model = genai.GenerativeModel(MODELO_A_USAR, system_instruction=INSTRUCCIONES)
    chat = model.start_chat(history=st.session_state.history)
except Exception as e:
    st.error(f"Error al conectar: {e}")

# 5. Título y Diseño
st.title("🎓 Profe Bot IA ")
st.caption("Tu tutor personal de Inteligencia Artificial")
st.markdown("---")

# 6. Mostrar conversación previa (Para que no se borre al escribir)
for message in chat.history:
    # Traducimos los roles: 'user' somos nosotros, 'model' es la IA
    role = "user" if message.role == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# 7. CHAT: Capturar lo que escribes y responder
if prompt := st.chat_input("Escribe tu pregunta aquí..."):
    # A. Mostrar tu mensaje inmediatamente en pantalla
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # B. Enviar a la IA y esperar respuesta
    try:
        response = chat.send_message(prompt)
        
        # C. Mostrar respuesta de la IA
        with st.chat_message("assistant"):
            st.markdown(response.text)
        
        # D. GUARDADO AUTOMÁTICO (Aquí estaba el error antes)
        # Actualizamos la memoria de Streamlit con la memoria oficial de Gemini
        st.session_state.history = chat.history
        
    except Exception as e:
        st.error(f"Ups, ocurrió un error: {e}")
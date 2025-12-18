import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image # <--- NUEVO: Herramienta para imágenes

# 1. Configuración de la Página
st.set_page_config(
    page_title="Profe Bot IA (Con Ojos)",
    page_icon="👁️‍🗨️",
    layout="centered"
)

# 2. Cargar llave de seguridad
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("❌ Falta la API Key en el .env")
    st.stop()

genai.configure(api_key=api_key)

# 3. Configuración del Modelo
MODELO_A_USAR = "gemini-2.5-flash"

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

# 4. Inicializar Chat
if "history" not in st.session_state:
    st.session_state.history = []

try:
    model = genai.GenerativeModel(MODELO_A_USAR, system_instruction=INSTRUCCIONES)
    chat = model.start_chat(history=st.session_state.history)
except Exception as e:
    st.error(f"Error de conexión: {e}")

# 5. Interfaz Gráfica
st.title("👁️‍🗨️ Profe Bot: Ahora puedo ver")
st.caption("Sube una foto de tu tarea o duda")

# --- NUEVO: BARRA LATERAL PARA SUBIR IMÁGENES ---
with st.sidebar:
    st.header("📸 Sube tu imagen aquí")
    archivo_subido = st.file_uploader("Elige una foto...", type=["jpg", "jpeg", "png"])
    
    imagen_para_procesar = None
    if archivo_subido is not None:
        # Mostramos la imagen en pequeñito
        imagen_para_procesar = Image.open(archivo_subido)
        st.image(imagen_para_procesar, caption="Imagen cargada", use_container_width=True)
        st.success("¡Imagen lista para analizar!")

st.markdown("---")

# 6. Mostrar historial
for message in chat.history:
    role = "user" if message.role == "user" else "assistant"
    with st.chat_message(role):
        # Filtramos para mostrar solo texto en el historial visual por ahora
        if message.parts[0].text:
             st.markdown(message.parts[0].text)

# 7. CHAT LÓGICA
if prompt := st.chat_input("Escribe tu pregunta sobre la imagen o el tema..."):
    
    # A. Mostrar mensaje usuario
    with st.chat_message("user"):
        st.markdown(prompt)
        if imagen_para_procesar:
            st.image(imagen_para_procesar, width=200) # Mostrar la foto en el chat también
    
    # B. Enviar a la IA
    try:
        with st.chat_message("assistant"):
            with st.spinner("Analizando... 🧠"):
                
                # --- AQUÍ ESTÁ LA MAGIA MULTIMODAL ---
                if imagen_para_procesar:
                    # Si hay imagen, enviamos una lista: [texto, imagen]
                    response = chat.send_message([prompt, imagen_para_procesar])
                else:
                    # Si no, enviamos solo texto
                    response = chat.send_message(prompt)
                
                st.markdown(response.text)
        
        # C. Actualizar memoria visual
        st.session_state.history = chat.history
        
    except Exception as e:
        st.error(f"Error: {e}")

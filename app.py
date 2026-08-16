import os
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# Configuración de la página
st.set_page_config(page_title="Eli-Eli Perfumes y Decants", page_icon="✨", layout="centered")

# Inicialización segura de Firebase
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            key_dict = dict(st.secrets["firebase"])
            if "private_key" in key_dict:
                pk = key_dict["private_key"]
                pk = pk.replace("\\\\n", "\n").replace("\\n", "\n")
                key_dict["private_key"] = pk
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred)
        else:
            local_path = r"C:\Users\Pc\Desktop\Perfumes\firebase_key.json"
            if os.path.exists(local_path):
                cred = credentials.Certificate(local_path)
                firebase_admin.initialize_app(cred)
            else:
                st.error("⚠️ No se encontró la llave de Firebase.")
    except Exception as e:
        st.error(f"Error al inicializar Firebase: {e}")

db = firestore.client()

# Título Principal
st.title("✨ Eli-Eli Perfumes y Decants ✨")

# Menú lateral para elegir la vista
st.sidebar.header("Menú de Navegación")
modo = st.sidebar.radio("Selecciona una vista:", ["🛍️ Ver Catálogo (Clientes)", "⚙️ Panel de Administración"])

# ==========================================
# VISTA 1: CATÁLOGO PARA CLIENTES
# ==========================================
if modo == "🛍️ Ver Catálogo (Clientes)":
    st.subheader("📦 Nuestro Catálogo Disponible")
    st.write("Explora nuestra selección de fragancias exclusivas y decants de 5 ml y 10 ml.")
    st.divider()

    try:
        perfumes_ref = db.collection("perfumes").stream()
        contador = 0
        
        for doc in perfumes_ref:
            data = doc.to_dict()
            if doc.id != "prueba_conexion":
                contador += 1
                estado_badge = data.get("estatus", "Disponible")
                
                # Color o etiqueta visual según disponibilidad
                color_estatus = "🟢" if estado_badge == "Disponible" else ("🟡" if estado_badge == "Sobre Pedido" else "🔴")
                
                with st.container():
                    st.markdown(f"### 🔹 {data.get('nombre', 'Sin nombre')} — *{data.get('marca', 'Sin marca')}*")
                    st.write(f"{color_estatus} **Estatus:** {estado_badge}")
                    st.write(f"📝 {data.get('descripcion', 'Sin descripción')}")
                    
                    # Precios organizados
                    col_p1, col_p2, col_p3 = st.columns(3)
                    with col_p1:
                        st.metric("Botella Completa", f"${int(data.get('precio_botella', 0))}")
                    with col_p2:
                        st.metric("Decant 5 ml", f"${int(data.get('decant_5ml', 0))}")
                    with col_p3:
                        st.metric("Decant 10 ml", f"${int(data.get('decant_10ml', 0))}")
                        
                    st.divider()
                    
        if contador == 0:
            st.info("Pronto tendremos fragancias disponibles. ¡Vuelve pronto!")

    except Exception as e:
        st.error(f"Error al cargar el catálogo: {e}")

# ==========================================
# VISTA 2: PANEL DE ADMINISTRACIÓN
# ==========================================
elif modo == "⚙️ Panel de Administración":
    st.subheader("🛠️ Agregar Nuevo Perfume")
    st.write("Usa este formulario para registrar productos en la base de datos.")

    with st.form("form_perfume_completo", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            nombre_perfume = st.text_input("Nombre del Perfume (Ej. Afnan 9 PM)")
            marca = st.text_input("Marca (Ej. Afnan, Armaf, Lattafa)")
            estatus = st.selectbox(
                "Disponibilidad", ["Disponible", "Sobre Pedido", "Agotado"]
            )

        with col2:
            precio_completa = st.number_input(
                "Precio Botella Completa ($)", min_value=0, step=1, format="%d"
            )
            precio_5ml = st.number_input("Precio Decant 5 ml ($)", min_value=0, step=1, format="%d")
            precio_10ml = st.number_input("Precio Decant 10 ml ($)", min_value=0, step=1, format="%d")

        descripcion = st.text_area(
            "Descripción y Notas Olfativas (Ej. Salida dulce, vainilla, ámbar...)"
        )
      
        imagen_subida = st.file_uploader(
            "Subir imagen del perfume",
            type=["jpg", "jpeg", "jfif", "png", "webp"],
        )

        submitted = st.form_submit_button("Guardar en Firestore")

        if submitted and nombre_perfume:
            doc_id = nombre_perfume.strip().lower().replace(" ", "_")
            
            try:
                db.collection("perfumes").document(doc_id).set({
                    "nombre": nombre_perfume,
                    "marca": marca,
                    "estatus": estatus,
                    "precio_botella": int(precio_completa),
                    "decant_5ml": int(precio_5ml),
                    "decant_10ml": int(precio_10ml),
                    "descripcion": descripcion,
                    "tiene_imagen": True if imagen_subida else False
                })
                st.success(f"¡El perfume '{nombre_perfume}' se guardó correctamente!")
            except Exception as e:
                st.error(f"Error al guardar en Firestore: {e}")
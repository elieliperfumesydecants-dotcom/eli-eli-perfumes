import os
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# Inicialización segura: Funciona tanto en tu PC como en la Nube (Celular)
if not firebase_admin._apps:
    try:
        # 1. Si está en la nube de Streamlit, usa los Secrets automáticamente
        if "firebase" in st.secrets:
            key_dict = dict(st.secrets["firebase"])
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred)
        # 2. Si estás corriendo el código en tu computadora, usa tu archivo local
        else:
            local_path = r"C:\Users\Pc\Desktop\Perfumes\firebase_key.json"
            if os.path.exists(local_path):
                cred = credentials.Certificate(local_path)
                firebase_admin.initialize_app(cred)
            else:
                st.error("⚠️ No se encontró la llave de Firebase ni en local ni en la nube.")
    except Exception as e:
        st.error(f"Error al inicializar Firebase: {e}")

db = firestore.client()

# Título de la Aplicación
st.title("✨ Eli-Eli Perfumes y Decants ✨")
st.sidebar.header("Administración de Catálogo")

# Sección para registrar nuevo producto
st.subheader("Agregar nuevo producto a la base de datos")

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
        "Subir imagen del perfume desde tu computadora",
        type=["jpg", "jpeg", "jfif", "png", "webp"],
    )

    submitted = st.form_submit_button("Guardar en Firestore")

    if submitted and nombre_perfume:
        doc_id = nombre_perfume.strip().lower().replace(" ", "_")
        
        # Guardar la imagen como bytes directamente en Firestore
        imagen_bytes = b""
        if imagen_subida is not None:
            imagen_bytes = imagen_subida.read()

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

# Mostrar el catálogo actual desde Firestore
st.divider()
st.subheader("📦 Catálogo Actual en la Nube")

try:
    perfumes_ref = db.collection("perfumes").stream()
    contador = 0
    
    for doc in perfumes_ref:
        data = doc.to_dict()
        if doc.id != "prueba_conexion":
            contador += 1
            estado_badge = data.get("estatus", "Disponible")
            
            with st.expander(
                f"🔹 {data.get('nombre', 'Sin nombre')} ({data.get('marca', 'Sin marca')}) - [{estado_badge}]"
            ):
                st.write(f"**Disponibilidad:** {estado_badge}")
                st.write(f"**Descripción:** {data.get('descripcion', 'Sin descripción')}")
                st.write(f"**Botella completa:** ${int(data.get('precio_botella', 0))}")
                st.write(f"**Decant 5 ml:** ${int(data.get('decant_5ml', 0))}")
                st.write(f"**Decant 10 ml:** ${int(data.get('decant_10ml', 0))}")
                
    if contador == 0:
        st.info("No hay perfumes registrados en la base de datos todavía.")

except Exception as e:
    st.error(f"Error al cargar los perfumes desde la nube: {e}")
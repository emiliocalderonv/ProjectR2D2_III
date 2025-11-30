# main.py
from fastapi import FastAPI
import pandas as pd
import joblib

app = FastAPI(title="API de Logística Inteligente", description="Unifica los modelos de clasificación y clustering.")

# --- CARGAR MODELOS AL INICIO ---
loaded_object = joblib.load('modelo_protocolos_gb.pkl')
classifier = loaded_object['model'] 

kmeans_model = joblib.load('modelo_kmeans.pkl')
scaler = joblib.load('scaler.pkl')

print("Todos los modelos han sido cargados exitosamente.")

# --- DEFINIR EL ENDPOINT DE LA API ---
@app.post("/analizar_producto")
def analizar_producto(peso_kg: float, ancho_cm: float, largo_cm: float, alto_cm: float, 
                      manipulacion: str, procedencia: str):
    """
    Recibe las características de un producto y devuelve el análisis logístico completo.
    - **manipulacion**: "normal" o "fragil"
    - **procedencia**: "A", "B", "C", o "D"
    """

    manipulacion = manipulacion.lower()
    procedencia= procedencia.upper()
    # --- 1. PREDICCIÓN DEL DEPÓSITO (MODELO NO SUPERVISADO) ---
    input_data_kmeans = pd.DataFrame([[peso_kg, ancho_cm, largo_cm, alto_cm, manipulacion, procedencia]],
                                     columns=['Peso_kg', 'Ancho_cm', 'Largo_cm', 'Alto_cm', 'Manipulacion', 'Procedencia'])

    # Le decimos a pandas cuáles son TODAS las categorías posibles para que no adivine.
    input_data_kmeans['Manipulacion'] = pd.Categorical(input_data_kmeans['Manipulacion'], categories=['fragil', 'normal'])
    input_data_kmeans['Procedencia'] = pd.Categorical(input_data_kmeans['Procedencia'], categories=['A', 'B', 'C', 'D'])

    # Ahora, get_dummies creará todas las columnas correctamente.
    # Usamos drop_first=True para que coincida con cómo se entrenó el modelo.
    input_final_kmeans = pd.get_dummies(input_data_kmeans, drop_first=True)
    
    # El paso de reindex ya no es necesario porque get_dummies ahora es inteligente.
    
    input_scaled = scaler.transform(input_final_kmeans)
    deposito_predicho = kmeans_model.predict(input_scaled)[0]


    columnas_clasificador = [
        "Embalaje", "Ancho_cm", "Largo_cm", "Alto_cm", "Peso_kg",
        "Manipulacion", "Procedencia", "Temperatura"
    ]
    datos_clasificador = [[
        1, ancho_cm, largo_cm, alto_cm, peso_kg, 
        manipulacion, procedencia, "ambiente"
    ]]
    input_data_classifier = pd.DataFrame(datos_clasificador, columns=columnas_clasificador)
    protocolo_predicho = classifier.predict(input_data_classifier)[0]


    return {
        "producto": {
            "peso_kg": peso_kg,
            "dimensiones": f"{ancho_cm}x{largo_cm}x{alto_cm} cm",
            "manipulacion": manipulacion,
            "procedencia": procedencia
        },
        "asignacion": {
            "protocolo_sugerido": str(protocolo_predicho),
            "deposito_asignado": int(deposito_predicho)
        }
    }
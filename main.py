from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from statline_overunder import StatLineAI

app = FastAPI()

# Permitir acceso desde cualquier origen (Flutter)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar Excel al iniciar la app y crear instancia de StatLineAI
@app.on_event("startup")
def load_data():
    print("Cargando Excel en memoria...")
    df = pd.read_excel("NFL_Puntos_2025.xlsx")
    app.state.ai = StatLineAI(df)
    print(f"Excel cargado. Filas: {len(df)}")

@app.get("/")
def inicio():
    return {"mensaje": "API StatLine funcionando correctamente ✅"}

@app.get("/predict")
def predict(local: str, visitante: str, linea: float):
    ai: StatLineAI = app.state.ai
    res = ai.predict(local, visitante, linea)

    # Si hubo error, se devuelve en formato que Flutter espera
    if res.get("status") == "error":
        return {"error": res["mensaje"]}

    # Respuesta normal
    return {
        "equipo_local": res["equipo_local"],
        "equipo_visitante": res["equipo_visitante"],
        "total_estimado": res["total_estimado"],
        "linea": res["linea"],
        "resultado": res["resultado"],
        "confianza": res["confianza"]
    }

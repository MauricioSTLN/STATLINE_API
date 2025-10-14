from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
import uvicorn

app = FastAPI()

# Permitir acceso desde Flutter
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar Excel al iniciar la app
@app.on_event("startup")
def load_data():
    print("Cargando Excel en memoria...")
    df = pd.read_excel("NFL_Puntos_2025.xlsx")
    app.state.df = df
    print(f"Excel cargado. Filas: {len(df)}")

@app.get("/")
def inicio():
    return {"mensaje": "API StatLine funcionando correctamente ✅"}

@app.get("/predict")
def predict(local: str, visitante: str, linea: float):
    df = app.state.df
    try:
        # Obtener estadísticas de cada equipo
        local_stats = df[df['team'] == local].mean(numeric_only=True)
        visitante_stats = df[df['team'] == visitante].mean(numeric_only=True)

        # Calcular total estimado
        total_estimado = float(local_stats.get('points_per_game', 0) +
                               visitante_stats.get('points_per_game', 0))

        # Determinar OVER/UNDER
        resultado = "OVER" if total_estimado > linea else "UNDER"

        # Calcular confianza (0 a 100%)
        diferencia = abs(total_estimado - linea)
        confianza = min(100, round(diferencia * 10))

        return {
            "equipo_local": local,
            "equipo_visitante": visitante,
            "total_estimado": round(total_estimado, 1),
            "linea": linea,
            "resultado": resultado,
            "confianza": confianza
        }

    except Exception as e:
        return {"error": str(e)}

# Ejecutar con el puerto que Render asigna
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Render asigna el puerto en la variable PORT
    uvicorn.run(app, host="0.0.0.0", port=port)

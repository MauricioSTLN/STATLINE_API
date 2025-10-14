import pandas as pd

class StatLineAI:
    def __init__(self, df: pd.DataFrame):
        """
        df: DataFrame con columnas como:
        - 'Team': nombre del equipo
        - 'Points_per_game': puntos promedio por juego
        """
        # Aseguramos que los nombres estén en minúsculas para comparación flexible
        df['Team'] = df['Team'].str.lower().str.strip()
        self.df = df

    def _buscar_equipo(self, nombre: str):
        """Busca un equipo por nombre (ignora mayúsculas/minúsculas y apodos)."""
        nombre = nombre.lower().strip()
        posibles = self.df[self.df['Team'].str.contains(nombre, case=False, na=False)]
        return posibles.mean(numeric_only=True) if not posibles.empty else pd.Series()

    def predict(self, local: str, visitante: str, linea: float) -> dict:
        local_stats = self._buscar_equipo(local)
        visitante_stats = self._buscar_equipo(visitante)

        # Si no hay coincidencia
        if local_stats.empty or visitante_stats.empty:
            return {
                "status": "error",
                "mensaje": f"No se encontraron datos para: {local if local_stats.empty else ''} {visitante if visitante_stats.empty else ''}".strip()
            }

        # Calculamos el total esperado
        total_estimado = (local_stats.get('Points_per_game', 0) + visitante_stats.get('Points_per_game', 0)) / 2
        diferencia = total_estimado - linea

        if diferencia > 1.5:
            resultado = "OVER"
        elif diferencia < -1.5:
            resultado = "UNDER"
        else:
            resultado = "LÍNEA PAREJA"

        confianza = min(100, round(abs(diferencia) / linea * 100, 1))

        return {
            "status": "ok",
            "equipo_local": local,
            "equipo_visitante": visitante,
            "total_estimado": round(total_estimado, 1),
            "linea": linea,
            "resultado": resultado,
            "confianza": confianza
        }

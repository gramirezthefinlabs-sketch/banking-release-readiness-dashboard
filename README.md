# Banking Release Readiness

Dashboard académico interactivo para evaluar la preparación de releases de un banco ficticio y recomendar **Go**, **Go con riesgos** o **No-Go**.

## Funcionalidades

- Filtros por release, módulo, ambiente y nivel de riesgo.
- KPI de ejecución, aprobación, defectos, automatización, pipeline y COB/EOD.
- Puntaje integral de preparación.
- Recomendación automática de salida.
- Priorización de módulos y validación de criterios Go/No-Go.
- Descarga de los registros filtrados.

## Ejecución local

```bash
pip install -r requirements.txt
streamlit run app.py
```

Los datos son simulados y no representan clientes, operaciones ni sistemas reales.

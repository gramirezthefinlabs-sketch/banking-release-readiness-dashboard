from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Banking Release Readiness",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = Path(__file__).parent / "data" / "releases_bancarios.csv"

COLORS = {
    "Go": "#16A34A",
    "Go con riesgos": "#F59E0B",
    "No-Go": "#DC2626",
    "Bajo": "#16A34A",
    "Medio": "#F59E0B",
    "Alto": "#F97316",
    "Bloqueante": "#DC2626",
}


@st.cache_data
def load_data() -> pd.DataFrame:
    data = pd.read_csv(DATA_PATH, parse_dates=["fecha_planificada"])
    numeric_columns = [
        "pruebas_planificadas", "pruebas_ejecutadas", "pruebas_aprobadas",
        "pruebas_fallidas", "pruebas_bloqueadas", "defectos_criticos",
        "defectos_altos", "cobertura_automatizacion", "cobertura_evidencia",
        "pipeline_exitoso", "cob_exitoso", "duracion_despliegue_min",
        "rollback", "incidentes_post_release",
    ]
    data[numeric_columns] = data[numeric_columns].apply(pd.to_numeric)
    return data


def calculate_metrics(frame: pd.DataFrame) -> dict:
    planned = int(frame["pruebas_planificadas"].sum())
    executed = int(frame["pruebas_ejecutadas"].sum())
    approved = int(frame["pruebas_aprobadas"].sum())
    critical = int(frame["defectos_criticos"].sum())
    high = int(frame["defectos_altos"].sum())
    pass_rate = approved / executed if executed else 0
    execution_rate = executed / planned if planned else 0
    automation = frame["cobertura_automatizacion"].mean() / 100
    evidence = frame["cobertura_evidencia"].mean() / 100
    pipeline = frame["pipeline_exitoso"].mean()
    cob = frame["cob_exitoso"].mean()

    score = (
        pass_rate * 30
        + execution_rate * 15
        + automation * 10
        + evidence * 10
        + pipeline * 15
        + cob * 10
        + max(0, 10 - critical * 5 - high * 0.8)
    )
    score = max(0, min(100, round(score, 1)))

    if critical > 0 or pass_rate < 0.85 or pipeline < 0.75 or cob < 0.75:
        decision = "No-Go"
    elif score < 90 or high > 2 or evidence < 0.90:
        decision = "Go con riesgos"
    else:
        decision = "Go"

    return {
        "planned": planned,
        "executed": executed,
        "execution_rate": execution_rate,
        "pass_rate": pass_rate,
        "critical": critical,
        "high": high,
        "automation": automation,
        "evidence": evidence,
        "pipeline": pipeline,
        "cob": cob,
        "score": score,
        "decision": decision,
    }


def decision_card(decision: str, score: float) -> None:
    color = COLORS[decision]
    st.markdown(
        f"""
        <div class="decision-card" style="border-left-color:{color}">
            <div class="decision-label">RECOMENDACIÓN DE SALIDA</div>
            <div class="decision-value" style="color:{color}">{decision}</div>
            <div class="decision-score">Preparación integral: <b>{score:.1f}/100</b></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <style>
    .stApp {background: #F4F7FB;}
    [data-testid="stSidebar"] {background: #071B33;}
    [data-testid="stSidebar"] * {color: #FFFFFF;}
    [data-testid="stMetric"] {
        background: #FFFFFF; border: 1px solid #D9E3EF; border-radius: 14px;
        padding: 14px 16px; box-shadow: 0 3px 12px rgba(7,27,51,.06);
    }
    .block-container {padding-top: 1.4rem; padding-bottom: 2rem;}
    .hero {
        background: linear-gradient(115deg, #071B33, #0B4F6C);
        color: white; padding: 1.35rem 1.6rem; border-radius: 18px;
        margin-bottom: 1rem;
    }
    .hero h1 {margin:0; font-size:2rem;}
    .hero p {margin:.45rem 0 0; color:#D7ECF5;}
    .decision-card {
        background:white; border:1px solid #D9E3EF; border-left:8px solid;
        border-radius:14px; padding:1rem 1.2rem; margin:.3rem 0 1rem;
        box-shadow:0 3px 12px rgba(7,27,51,.06);
    }
    .decision-label {font-size:.75rem; letter-spacing:.08em; color:#64748B; font-weight:700;}
    .decision-value {font-size:2rem; font-weight:800; margin:.1rem 0;}
    .decision-score {color:#334155;}
    .note {background:#E8F3F8; border-left:4px solid #0EA5A4; padding:.7rem 1rem; border-radius:8px;}
    </style>
    """,
    unsafe_allow_html=True,
)

df = load_data()

with st.sidebar:
    st.title("🚦 Release Control")
    st.caption("NovaBank · Datos completamente ficticios")
    releases = sorted(df["release"].unique(), reverse=True)
    selected_releases = st.multiselect("Release", releases, default=[releases[0]])
    selected_modules = st.multiselect(
        "Módulo", sorted(df["modulo"].unique()), default=sorted(df["modulo"].unique())
    )
    selected_environments = st.multiselect(
        "Ambiente", sorted(df["ambiente"].unique()), default=sorted(df["ambiente"].unique())
    )
    selected_risks = st.multiselect(
        "Nivel de riesgo", sorted(df["riesgo"].unique()), default=sorted(df["riesgo"].unique())
    )
    st.divider()
    st.caption("Los KPI y la recomendación cambian con cada filtro.")

filtered = df[
    df["release"].isin(selected_releases)
    & df["modulo"].isin(selected_modules)
    & df["ambiente"].isin(selected_environments)
    & df["riesgo"].isin(selected_risks)
].copy()

st.markdown(
    """
    <div class="hero">
        <h1>Banking Release Readiness</h1>
        <p>Control de riesgos y decisión Go/No-Go para releases bancarios</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if filtered.empty:
    st.warning("No existen registros para la combinación de filtros seleccionada.")
    st.stop()

metrics = calculate_metrics(filtered)
decision_card(metrics["decision"], metrics["score"])

cols = st.columns(6)
values = [
    ("Avance", f"{metrics['execution_rate']:.1%}", "Ejecutadas / planificadas"),
    ("Pass rate", f"{metrics['pass_rate']:.1%}", "Aprobadas / ejecutadas"),
    ("Defectos críticos", f"{metrics['critical']}", "Bloquean la salida"),
    ("Automatización", f"{metrics['automation']:.1%}", "Cobertura promedio"),
    ("Pipeline", f"{metrics['pipeline']:.1%}", "Ejecuciones exitosas"),
    ("COB/EOD", f"{metrics['cob']:.1%}", "Procesos exitosos"),
]
for col, (label, value, hint) in zip(cols, values):
    with col:
        st.metric(label, value, help=hint)

tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Resumen ejecutivo", "🔥 Riesgo por módulo", "✅ Criterios Go/No-Go", "📋 Detalle"]
)

with tab1:
    left, right = st.columns(2)
    with left:
        st.markdown("#### Preparación promedio por release")
        release_scores = []
        for release, group in filtered.groupby("release"):
            release_scores.append({"Release": release, "Preparación": calculate_metrics(group)["score"]})
        release_score_df = pd.DataFrame(release_scores).set_index("Release")
        st.bar_chart(release_score_df, color="#0EA5A4", height=320)
    with right:
        st.markdown("#### Defectos abiertos por módulo")
        defects = filtered.groupby("modulo")[["defectos_criticos", "defectos_altos"]].sum()
        defects.columns = ["Críticos", "Altos"]
        st.bar_chart(defects, color=["#DC2626", "#F59E0B"], height=320)

    st.markdown("#### Tendencia de aprobación por fecha")
    trend = (
        filtered.assign(tasa=lambda x: x["pruebas_aprobadas"] / x["pruebas_ejecutadas"] * 100)
        .groupby("fecha_planificada")["tasa"]
        .mean()
        .rename("Aprobación %")
    )
    st.line_chart(trend, color="#2563EB", height=260)

with tab2:
    st.markdown("#### Mapa de priorización")
    risk_table = (
        filtered.groupby("modulo")
        .agg(
            Casos=("pruebas_planificadas", "sum"),
            Fallidas=("pruebas_fallidas", "sum"),
            Bloqueadas=("pruebas_bloqueadas", "sum"),
            Críticos=("defectos_criticos", "sum"),
            Altos=("defectos_altos", "sum"),
            Automatización=("cobertura_automatizacion", "mean"),
            Evidencia=("cobertura_evidencia", "mean"),
        )
    )
    risk_table["Índice de atención"] = (
        risk_table["Fallidas"] * 2
        + risk_table["Bloqueadas"] * 3
        + risk_table["Críticos"] * 8
        + risk_table["Altos"] * 3
    )
    risk_table = risk_table.sort_values("Índice de atención", ascending=False)
    st.dataframe(
        risk_table.style.background_gradient(subset=["Índice de atención"], cmap="YlOrRd"),
        use_container_width=True,
    )
    st.markdown(
        '<div class="note"><b>Lectura:</b> cuanto mayor sea el índice, más atención necesita el módulo antes del despliegue.</div>',
        unsafe_allow_html=True,
    )

with tab3:
    checks = pd.DataFrame(
        [
            ["Sin defectos críticos", metrics["critical"] == 0, f"{metrics['critical']} abiertos"],
            ["Pass rate ≥ 90%", metrics["pass_rate"] >= .90, f"{metrics['pass_rate']:.1%}"],
            ["Ejecución ≥ 95%", metrics["execution_rate"] >= .95, f"{metrics['execution_rate']:.1%}"],
            ["Evidencia ≥ 90%", metrics["evidence"] >= .90, f"{metrics['evidence']:.1%}"],
            ["Pipeline ≥ 90%", metrics["pipeline"] >= .90, f"{metrics['pipeline']:.1%}"],
            ["COB/EOD ≥ 90%", metrics["cob"] >= .90, f"{metrics['cob']:.1%}"],
        ],
        columns=["Criterio", "Cumple", "Resultado"],
    )
    checks["Estado"] = checks["Cumple"].map({True: "✅ Cumple", False: "❌ Pendiente"})
    st.dataframe(checks[["Criterio", "Resultado", "Estado"]], hide_index=True, use_container_width=True)
    if metrics["decision"] == "No-Go":
        st.error("La salida no se recomienda mientras existan condiciones bloqueantes.")
    elif metrics["decision"] == "Go con riesgos":
        st.warning("La salida requiere aceptación formal de riesgos y plan de mitigación.")
    else:
        st.success("Los principales criterios de preparación están satisfechos.")

with tab4:
    search = st.text_input("Buscar release, módulo o responsable", placeholder="Ejemplo: R25.2")
    detail = filtered.copy()
    if search:
        mask = detail.astype(str).apply(
            lambda column: column.str.contains(search, case=False, na=False)
        ).any(axis=1)
        detail = detail[mask]
    st.dataframe(detail.sort_values("fecha_planificada", ascending=False), hide_index=True, use_container_width=True)
    st.download_button(
        "⬇️ Descargar datos filtrados",
        detail.to_csv(index=False).encode("utf-8-sig"),
        file_name="release_readiness_filtrado.csv",
        mime="text/csv",
    )

st.caption("Proyecto académico · Python + Streamlit · Datos ficticios de NovaBank")

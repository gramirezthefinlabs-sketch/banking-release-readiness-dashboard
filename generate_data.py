from pathlib import Path
import random

import pandas as pd


random.seed(42)
releases = ["R25.1", "R25.2", "R25.3", "R26.1"]
modules = ["Core Banking", "Pagos", "Préstamos", "Tarjetas", "Canales Digitales", "AML/KYC", "COB/EOD"]
environments = ["SIT", "UAT", "Preproducción"]
owners = ["Equipo Core", "Equipo Pagos", "Equipo Créditos", "Equipo Canales"]
risks = ["Bajo", "Medio", "Alto", "Bloqueante"]
rows = []

for release_index, release in enumerate(releases):
    for module_index, module in enumerate(modules):
        planned = random.randint(55, 125)
        execution_ratio = min(.99, .79 + release_index * .045 + random.uniform(-.04, .06))
        executed = int(planned * execution_ratio)
        pass_ratio = min(.98, .80 + release_index * .04 + random.uniform(-.05, .06))
        approved = int(executed * pass_ratio)
        blocked = random.randint(0, max(1, int(executed * .04)))
        failed = max(0, executed - approved - blocked)
        critical = 1 if (release_index < 2 and module_index in [0, 4] and random.random() < .65) else 0
        high = random.randint(0, 5 if release_index < 2 else 3)
        automation = min(96, random.randint(48, 72) + release_index * 7)
        evidence = min(99, random.randint(70, 88) + release_index * 4)
        pipeline = 0 if critical and random.random() < .45 else random.choice([0, 1, 1, 1])
        cob = 0 if module == "COB/EOD" and release_index < 2 else random.choice([0, 1, 1, 1, 1])
        rollback = 1 if release_index < 2 and random.random() < .08 else 0
        incidents = random.randint(0, 3 if release_index < 2 else 1)
        risk_index = critical * 9 + high * 2 + failed * .2 + blocked * .5 + (1 - pipeline) * 5 + (1 - cob) * 5
        risk = "Bloqueante" if critical else "Alto" if risk_index >= 12 else "Medio" if risk_index >= 6 else "Bajo"
        rows.append({
            "release": release,
            "fecha_planificada": f"2026-{2 + release_index * 2:02d}-{10 + module_index:02d}",
            "modulo": module,
            "ambiente": environments[(release_index + module_index) % len(environments)],
            "responsable": owners[module_index % len(owners)],
            "pruebas_planificadas": planned,
            "pruebas_ejecutadas": executed,
            "pruebas_aprobadas": approved,
            "pruebas_fallidas": failed,
            "pruebas_bloqueadas": blocked,
            "defectos_criticos": critical,
            "defectos_altos": high,
            "cobertura_automatizacion": automation,
            "cobertura_evidencia": evidence,
            "pipeline_exitoso": pipeline,
            "cob_exitoso": cob,
            "duracion_despliegue_min": random.randint(35, 150),
            "rollback": rollback,
            "incidentes_post_release": incidents,
            "riesgo": risk,
        })

output = Path(__file__).parent / "data" / "releases_bancarios.csv"
output.parent.mkdir(parents=True, exist_ok=True)
pd.DataFrame(rows).to_csv(output, index=False)
print(f"Generados {len(rows)} registros en {output}")

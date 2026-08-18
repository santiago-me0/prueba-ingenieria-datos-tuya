# Ejercicio 3 - Rachas

## Enfoque

La solución utiliza SQLite para cargar la información del archivo `Rachas.xlsx` y calcular las rachas consecutivas de cada cliente dentro de un mismo nivel de deuda.

El proceso se divide en cuatro etapas:

```text
Rachas.xlsx
    |
    v
Carga RAW
    |
    v
Controles de calidad y preparación
    |
    v
Cálculo de rachas
    |
    v
Resultado por cliente
```

Los datos originales se conservan sin modificaciones en tablas RAW. Antes de calcular las rachas se ejecutan controles de calidad y se construye una capa preparada con reglas explícitas para los casos encontrados en la fuente.

---

## Calidad de datos

Durante la revisión del archivo se identificaron los siguientes casos:

- Un registro cliente-mes duplicado exactamente.
- Un cliente-mes con dos saldos diferentes.
- Registros de historia posteriores a la fecha de retiro.
- Un identificador de la hoja de retiros sin coincidencia exacta en la historia.

El tratamiento aplicado es:

- **Duplicado exacto:** se conserva una sola ocurrencia en la capa preparada.
- **Saldos diferentes para el mismo cliente-mes:** los registros se dejan disponibles en cuarentena y se utiliza `MAX(saldo)` como regla determinística y conservadora para el ejercicio.
- **Registros posteriores al retiro:** se conservan en RAW y cuarentena, pero se excluyen del cálculo de rachas.
- **Retiro sin historia:** se registra como hallazgo de calidad y no se intenta corregir o relacionar mediante similitud de identificadores.

La elección de `MAX(saldo)` no implica que dicho valor sea necesariamente el correcto. En un entorno productivo este tipo de conflicto debería resolverse utilizando información adicional de la fuente, como prioridad del sistema, fecha de actualización o un proceso de revisión.

---

## Solución SQL

Los niveles de deuda utilizados son:

| Nivel | Saldo |
|---|---|
| `N0` | `>= 0` y `< 300,000` |
| `N1` | `>= 300,000` y `< 1,000,000` |
| `N2` | `>= 1,000,000` y `< 3,000,000` |
| `N3` | `>= 3,000,000` y `< 5,000,000` |
| `N4` | `>= 5,000,000` |

La consulta recibe dos parámetros:

- `fecha_base`: fecha desde la cual se desea realizar el análisis histórico.
- `n`: longitud mínima requerida para considerar una racha.

Para cada cliente se genera una secuencia mensual desde su primera aparición hasta el corte permitido por `fecha_base` y, cuando aplica, por su fecha de retiro.

Los meses faltantes después de la primera aparición se consideran saldo `0` y por lo tanto nivel `N0`. No se generan meses posteriores al retiro ni posteriores al horizonte disponible en la fuente.

Las rachas se calculan mediante funciones de ventana y el patrón SQL de *gaps and islands*.

Cuando un cliente tiene varias rachas que cumplen `racha >= n`:

1. Se selecciona la de mayor longitud.
2. Si existe empate, se selecciona la que tenga la `fecha_fin` más reciente.

El resultado final contiene:

```text
identificacion
racha
fecha_fin
nivel
```

---

## Estructura

```text
Ejercicio_3/
├── README.md
├── requirements.txt
├── data/
│   └── Rachas.xlsx
├── src/
│   ├── __init__.py
│   ├── load_data.py
│   ├── prepare_data.py
│   └── run_query.py
├── sql/
│   ├── 01_schema.sql
│   ├── 02_quality_checks.sql
│   ├── 03_prepare_data.sql
│   └── 04_rachas.sql
└── test/
    ├── __init__.py
    ├── test_prepare_data.py
    └── test_rachas.py
```

La base `rachas.db` se genera durante la ejecución y no se versiona.

---

## Ejecución

Instalar la dependencia necesaria:

```bash
pip install -r Ejercicio_3/requirements.txt
```

Desde la raíz del repositorio:

```bash
python -m Ejercicio_3.src.load_data
python -m Ejercicio_3.src.prepare_data
```

Después se puede ejecutar la consulta para cualquier combinación de `fecha_base` y `n`.

Por ejemplo:

```bash
python -m Ejercicio_3.src.run_query \
    --fecha-base 2024-12-31 \
    --n 3
```

También es posible utilizar una fecha que no corresponda al cierre de mes:

```bash
python -m Ejercicio_3.src.run_query \
    --fecha-base 2024-06-15 \
    --n 3
```

En ese caso solo se consideran cortes de mes menores o iguales a `fecha_base`.

---

## Pruebas

Las pruebas se ejecutan con:

```bash
python -m unittest discover \
    -s Ejercicio_3/test \
    -p "test_*.py" \
    -v
```

Actualmente se implementaron **13 pruebas automatizadas**.

Entre los casos cubiertos se encuentran:

- Deduplicación de registros idénticos.
- Conflictos de saldo y cuarentena.
- Registros posteriores al retiro.
- Retiros sin coincidencia en historia.
- Meses faltantes convertidos a `N0`.
- No imputar meses antes de la primera aparición.
- No imputar meses después del retiro.
- Uso histórico de `fecha_base`.
- Filtro por longitud mínima `n`.
- Selección de la racha más larga.
- Desempate mediante la `fecha_fin` más reciente.
- No generar meses posteriores al horizonte real de la fuente.

---

## Decisiones principales

SQLite fue seleccionado porque está permitido por el ejercicio y facilita que la solución pueda reproducirse sin requerir un servidor de base de datos.

La base de datos generada se considera un artefacto derivado. La fuente de verdad se mantiene en el archivo Excel y en los scripts versionados.

La solución evita modificar los datos originales y separa los problemas de calidad de las reglas de negocio utilizadas para calcular las rachas.
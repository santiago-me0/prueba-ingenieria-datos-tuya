# Prueba Técnica - Ingeniería de Datos

Este repositorio contiene la solución desarrollada para la prueba técnica de Ingeniería de Datos de Tuya S.A.

La propuesta aborda los cuatro ejercicios planteados, combinando procesamiento de datos, calidad y trazabilidad, automatización, SQL y desarrollo en Python.

Cada ejercicio cuenta con su propio `README.md`, donde se encuentra la explicación técnica, decisiones tomadas, instrucciones de ejecución y pruebas correspondientes.

---

## Estructura del repositorio

```text
.
├── Ejercicio_1/
│   ├── data/
│   ├── src/
│   ├── test/
│   └── README.md
│
├── Ejercicio_2/
│   └── README.md
│
├── Ejercicio_3/
│   ├── data/
│   ├── sql/
│   ├── src/
│   ├── test/
│   ├── requirements.txt
│   └── README.md
│
├── Ejercicio_4/
│   ├── src/
│   ├── test/
│   └── README.md
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── .gitignore
└── README.md
```

---

## Ejercicios

### Ejercicio 1 - Dataset confiable de números telefónicos de clientes

Diseño e implementación de un pipeline para normalizar, validar y controlar la calidad de números telefónicos de clientes.

La solución incluye:

- Normalización de números telefónicos colombianos.
- Validación mediante reglas de calidad.
- Clasificación de registros como `VALID`, `INVALID` o `SUSPICIOUS`.
- Detección de teléfonos duplicados después de la normalización.
- Conservación del valor original para trazabilidad.
- Generación reproducible del dataset procesado.
- Pruebas automatizadas.
- CI/CD mediante GitHub Actions.

Documentación:

[`Ejercicio_1/README.md`](Ejercicio_1/README.md)

---

### Ejercicio 2 - KPIs y monitoreo de calidad

Propuesta conceptual de un mecanismo para realizar veeduría sobre la calidad de los teléfonos generados en el Ejercicio 1.

El mecanismo contempla:

- Histórico de ejecuciones de calidad.
- Trazabilidad a nivel de registro.
- Resultado detallado de reglas de calidad.
- KPIs de completitud, validez, normalización, unicidad y plausibilidad.
- Seguimiento de tendencias.
- Vistas de negocio para calidad y trazabilidad.
- Alertas por umbral o variaciones anormales.

La propuesta se mantiene independiente de una herramienta específica de Business Intelligence.

Documentación:

[`Ejercicio_2/README.md`](Ejercicio_2/README.md)

---

### Ejercicio 3 - Rachas

Solución para identificar rachas consecutivas de clientes dentro de diferentes niveles de saldo.

El ejercicio utiliza Python, SQL y SQLite para:

- Cargar de forma reproducible la información suministrada en Excel.
- Preservar los datos originales en una capa RAW.
- Ejecutar controles de calidad.
- Registrar inconsistencias y datos en cuarentena.
- Construir una capa preparada para análisis.
- Completar meses faltantes como nivel `N0` cuando corresponde.
- Clasificar saldos entre `N0` y `N4`.
- Calcular rachas mediante funciones de ventana y el patrón *gaps and islands*.
- Parametrizar el análisis mediante `fecha_base` y longitud mínima `n`.
- Resolver empates seleccionando la racha que finaliza más recientemente.

Documentación:

[`Ejercicio_3/README.md`](Ejercicio_3/README.md)

---

### Ejercicio 4 - Procesamiento de archivos HTML

Implementación en Python para procesar archivos HTML y convertir sus imágenes locales a Base64.

La solución permite:

- Procesar archivos HTML individuales.
- Recorrer directorios y subdirectorios.
- Identificar etiquetas `<img>`.
- Resolver imágenes locales asociadas al documento.
- Convertirlas a Base64.
- Generar un nuevo archivo HTML sin modificar el original.
- Registrar imágenes procesadas correctamente y aquellas que presentan errores.
- Continuar el procesamiento ante fallos parciales.

La implementación utiliza únicamente módulos de la standard library de Python y aplica programación orientada a objetos para separar responsabilidades.

Documentación:

[`Ejercicio_4/README.md`](Ejercicio_4/README.md)

---

## Tecnologías utilizadas

| Tecnología | Uso |
|---|---|
| Python | Procesamiento, validación, automatización y pruebas |
| SQL | Preparación de datos y cálculo de rachas |
| SQLite | Base de datos reproducible para el Ejercicio 3 |
| Git | Control de versiones |
| GitHub | Repositorio y flujo de trabajo |
| GitHub Actions | CI/CD |
| `unittest` | Pruebas automatizadas |
| `openpyxl` | Lectura del archivo Excel del Ejercicio 3 |

El Ejercicio 4 utiliza exclusivamente módulos incluidos en la standard library de Python.

---

## Pruebas automatizadas

Se implementaron pruebas automatizadas para los ejercicios que contienen código.

| Ejercicio | Pruebas |
|---|---:|
| Ejercicio 1 | 45 |
| Ejercicio 3 | 13 |
| Ejercicio 4 | 16 |
| **Total** | **74** |

Las instrucciones específicas para ejecutar cada suite se encuentran en el README correspondiente.

---

## Ejecución

Los comandos deben ejecutarse desde la raíz del repositorio.

### Ejercicio 1

```bash
python -m Ejercicio_1.src.pipeline
```

Pruebas:

```bash
python -m unittest discover \
    -s Ejercicio_1/test \
    -p "test_*.py" \
    -v
```

### Ejercicio 3

Instalar la dependencia:

```bash
pip install -r Ejercicio_3/requirements.txt
```

Construir y preparar la base de datos:

```bash
python -m Ejercicio_3.src.load_data
python -m Ejercicio_3.src.prepare_data
```

Ejecutar una consulta:

```bash
python -m Ejercicio_3.src.run_query \
    --fecha-base 2024-12-31 \
    --n 3
```

Pruebas:

```bash
python -m unittest discover \
    -s Ejercicio_3/test \
    -p "test_*.py" \
    -v
```

### Ejercicio 4

Procesar un archivo o directorio:

```bash
python -m Ejercicio_4.src.main ruta/al/archivo_o_directorio
```

Pruebas:

```bash
python -m unittest discover \
    -s Ejercicio_4/test \
    -p "test_*.py" \
    -v
```

El Ejercicio 2 corresponde a una propuesta conceptual y no requiere ejecución.

---

## Enfoque general

A lo largo de la solución se buscó mantener algunos criterios comunes:

- Preservar los datos originales cuando se realizan transformaciones.
- Evitar inferir información que no se encuentre disponible en la fuente.
- Hacer explícitas las decisiones utilizadas para tratar problemas de calidad.
- Separar los datos originales de los datos preparados o derivados.
- Construir procesos reproducibles.
- Incorporar pruebas automatizadas para controlar regresiones.
- Mantener separadas las responsabilidades principales del código.
- Documentar las decisiones técnicas junto a cada ejercicio.

El documento entregado junto con la prueba presenta una visión ejecutiva de las soluciones y sus principales decisiones. Los README individuales contienen el detalle técnico necesario para comprender y reproducir cada ejercicio.
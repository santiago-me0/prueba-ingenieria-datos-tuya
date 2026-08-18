# Ejercicio 2 - KPIs y monitoreo de calidad de datos

## Solución propuesta

A partir del resultado del Ejercicio 1 se propone un mecanismo de monitoreo que permita a los equipos de negocio consultar la calidad de los teléfonos, analizar su evolución y conocer la trazabilidad de un dato específico.

La idea es que cada ejecución exitosa del pipeline deje información en tres conjuntos lógicos:

- `trusted_phones`: detalle de los teléfonos procesados y su resultado de calidad.
- `data_quality_runs`: información y métricas agregadas de cada ejecución.
- `data_quality_rule_results`: resultado de las reglas de calidad evaluadas sobre cada registro.

Estos datos alimentarían una capa de métricas consumida por una herramienta de Business Intelligence.

```text
                  Pipeline Ejercicio 1
                          |
             +------------+-------------+
             |            |             |
             v            v             v
      trusted_phones  quality_runs  rule_results
             |            |             |
             +------------+-------------+
                          |
                          v
                   Capa de métricas
                          |
                          v
                     Dashboard BI
                          |
              +-----------+-----------+
              |           |           |
              v           v           v
           Calidad     Tendencias   Trazabilidad
```

El mecanismo no depende de una herramienta específica. La visualización podría implementarse con Power BI, Looker Studio, Databricks SQL u otra herramienta disponible en la organización.

---

## Información a conservar

### `trusted_phones`

Contiene el resultado detallado del procesamiento de cada teléfono.

| Campo | Propósito |
|---|---|
| `run_id` | Identificar la ejecución que procesó el registro |
| `customer_id` | Identificar al cliente |
| `phone_original` | Conservar el dato recibido |
| `phone_normalized` | Conservar el resultado de normalización |
| `phone_type` | Identificar `mobile` o `landline` |
| `status` | Registrar `VALID`, `INVALID` o `SUSPICIOUS` |
| `validation_reason` | Explicar el resultado principal |
| `duplicate_group` | Identificar problemas de unicidad |
| `processed_at` | Registrar cuándo fue procesado |
| `pipeline_version` | Identificar la versión del proceso |
| `source` | Identificar la fuente del dato |

### `data_quality_runs`

Mantiene una fila por ejecución del pipeline.

| Campo | Propósito |
|---|---|
| `run_id` | Identificador único de la ejecución |
| `processed_at` | Fecha y hora de ejecución |
| `pipeline_version` | Versión del código utilizada |
| `source` | Sistema o fuente procesada |
| `source_file` | Archivo o conjunto de datos recibido |
| `source_hash` | Identificar de forma reproducible el insumo |
| `total_records` | Total de registros procesados |
| `valid_records` | Total de registros válidos |
| `invalid_records` | Total de registros inválidos |
| `suspicious_records` | Total de registros sospechosos |
| `duplicate_records` | Registros involucrados en duplicidad |

Esta información permite comparar la calidad entre diferentes ejecuciones sin sobrescribir el histórico.

### `data_quality_rule_results`

Permite registrar el resultado de las reglas de calidad de manera independiente.

| Campo | Propósito |
|---|---|
| `run_id` | Ejecución donde se evaluó la regla |
| `customer_id` | Registro evaluado |
| `rule_id` | Regla de calidad evaluada |
| `rule_status` | `PASSED` o `FAILED` |
| `rule_detail` | Detalle del resultado |

Por ejemplo:

```text
RUN-001 | 025 | R01 | FAILED | MISSING_VALUE
RUN-001 | 020 | R02 | FAILED | INVALID_FORMAT
RUN-001 | 022 | R07 | FAILED | REPEATED_DIGITS
RUN-001 | 001 | R08 | FAILED | DUP-001
```

Esta estructura permite que un mismo teléfono tenga más de una observación de calidad sin depender únicamente de un único `validation_reason`.

---

## Dimensiones y KPIs

El monitoreo considera principalmente completitud, validez, normalización, unicidad, plausibilidad, trazabilidad y evolución temporal.

Los principales indicadores propuestos son:

| KPI | Fórmula conceptual | Qué permite conocer |
|---|---|---|
| Total procesados | `COUNT(*)` | Tamaño de la población analizada |
| % Completitud | teléfonos informados / total × 100 | Ausencia de información |
| % Normalización exitosa | teléfonos normalizados / total × 100 | Capacidad de estandarización |
| % Válidos | `VALID` / total × 100 | Registros aceptados |
| % Inválidos | `INVALID` / total × 100 | Datos no utilizables |
| % Sospechosos | `SUSPICIOUS` / total × 100 | Registros que requieren revisión |
| % Registros duplicados | registros con `duplicate_group` / total × 100 | Impacto de problemas de unicidad |
| Teléfonos compartidos | teléfonos normalizados duplicados distintos | Cantidad de números asociados a varios clientes |
| Errores por motivo | agrupación por `validation_reason` | Principales causas de problemas |
| Incumplimientos por regla | agrupación por `rule_id` | Reglas con mayor número de fallos |

La distribución entre `mobile` y `landline` también puede mostrarse como información descriptiva, aunque no constituye por sí misma un indicador de calidad.

Los valores no se calculan sobre los 33 registros del Ejercicio 1 porque ese dataset fue construido deliberadamente para probar reglas y no representa una población real de clientes.

---

## Relación con las reglas del Ejercicio 1

| Regla | Dimensión | Monitoreo |
|---|---|---|
| R01 | Completitud | Teléfonos nulos o vacíos |
| R02 | Normalización / Formato | Valores que no pueden normalizarse |
| R03 | Validez | Longitud nacional incorrecta |
| R04 | Validez | Estructura inválida para celular |
| R05 | Validez | Estructura inválida para teléfono fijo |
| R06 | Validez | Indicativo o estructura local inválida |
| R07 | Plausibilidad | Patrones sospechosos |
| R08 | Unicidad | Teléfonos normalizados duplicados |
| R09 | Trazabilidad | Conservación del valor original y normalizado |
| R10 | Trazabilidad | Registro del resultado y motivo |

De esta manera existe una relación directa entre la regla de negocio, su evaluación técnica y los indicadores presentados a negocio.

---

## Trazabilidad

El mecanismo debe permitir consultar un cliente o teléfono y reconstruir cómo fue procesado.

```text
Fuente / archivo
      |
      v
phone_original
      |
      v
Normalización
      |
      v
phone_normalized
      |
      v
Validación
      |
      v
status / rule_id
      |
      v
validation_reason
      |
      v
duplicate_group
      |
      v
run_id
      |
      v
processed_at
      |
      v
pipeline_version
```

Con esta información sería posible responder, por ejemplo:

- qué valor fue recibido originalmente;
- cómo fue normalizado;
- qué regla generó una observación;
- cuándo fue procesado;
- qué ejecución produjo el resultado;
- qué versión del pipeline fue utilizada;
- de qué fuente provenía el registro.

---

## Vistas para negocio

Se proponen tres vistas principales.

### Resumen ejecutivo

Presentaría los indicadores principales:

```text
Total procesados
% Completitud
% VALID
% INVALID
% SUSPICIOUS
% Duplicidad
Variación vs. ejecución anterior
```

Además del valor actual, los indicadores deberían mostrar su evolución respecto a ejecuciones anteriores.

### Análisis de calidad

Permitirá profundizar en las causas de los problemas mediante:

- errores por `validation_reason`;
- incumplimientos por `rule_id`;
- evolución de registros inválidos y sospechosos;
- evolución de datos faltantes;
- problemas de duplicidad;
- filtros por fecha, fuente, tipo de teléfono, estado y ejecución.

### Trazabilidad

Permitirá buscar por `customer_id` o número telefónico y consultar el recorrido completo del registro desde el dato original hasta el resultado generado por el pipeline.

---

## Evolución y alertas

Las métricas de `data_quality_runs` permiten comparar ejecuciones históricas y determinar si la calidad mejora o empeora.

Por ejemplo:

```text
             RUN-001   RUN-002   RUN-003

VALID           82%       87%       91%
INVALID         14%        9%        6%
SUSPICIOUS       4%        4%        3%
```

El mecanismo podría incorporar alertas de dos tipos:

**Por umbral**, cuando un indicador supera un nivel aceptable:

```text
% INVALID > límite definido
            |
            v
          ALERTA
```

**Por variación**, cuando un indicador cambia significativamente frente a su comportamiento histórico:

```text
MISSING_VALUE habitual = 1%
Nueva ejecución        = 8%
             |
             v
           ALERTA
```

Los valores concretos de los umbrales no se definen en esta propuesta. Deberían establecerse junto con negocio utilizando datos reales y una línea base histórica.

---

## Automatización

El monitoreo puede ejecutarse como continuación del pipeline del Ejercicio 1:

```text
Pipeline de teléfonos
        |
        v
Dataset procesado
        |
        v
Registrar ejecución y resultados de calidad
        |
        v
Calcular métricas
        |
        v
Actualizar dashboard
        |
        v
Evaluar alertas
```

De esta forma, cada nueva ejecución del pipeline actualiza tanto el dataset confiable como la información utilizada para supervisar su calidad.

---

## Alcance de la propuesta

Este ejercicio se plantea de forma conceptual, de acuerdo con el enunciado.

Por esta razón no se implementa una herramienta de BI específica ni se calculan indicadores sobre el dataset artificial del Ejercicio 1.

La propuesta define el mecanismo necesario para:

- conservar información histórica de calidad;
- proporcionar trazabilidad a nivel de registro;
- calcular KPIs para negocio;
- analizar tendencias;
- identificar las causas de problemas de calidad;
- incorporar alertas cuando exista una línea base real.
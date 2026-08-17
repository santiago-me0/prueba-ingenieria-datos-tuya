# Ejercicio 2 - KPI's y monitoreo de calidad de datos

## 1. Objetivo

Plantear conceptualmente un mecanismo que permita realizar veeduría sobre la calidad de los números telefónicos generados a partir del proceso definido en el Ejercicio 1, proporcionando adicionalmente trazabilidad del dato e indicadores de calidad para los equipos de negocio.

La solución busca permitir responder preguntas como:

* ¿Qué tan completa es la información telefónica de los clientes?
* ¿Qué proporción de los teléfonos cumple las reglas de calidad?
* ¿Cuáles son las principales causas de datos inválidos?
* ¿Existen números sospechosos o duplicados?
* ¿La calidad de los datos mejora o empeora a través del tiempo?
* ¿Qué ocurrió con un número telefónico específico durante su procesamiento?
* ¿Qué ejecución y versión del pipeline produjo determinado resultado?

El ejercicio se plantea de manera conceptual y no depende de una herramienta específica de visualización o almacenamiento.

---

## 2. Relación con el Ejercicio 1

El Ejercicio 1 genera un dataset confiable a partir de números telefónicos recibidos desde una fuente de clientes.

El pipeline realiza:



```text
Fuente de clientes
       |
       v
Normalización
       |
       v
Validación
       |
       v
Detección de duplicados
       |
       v
Dataset procesado
```

El resultado contiene información como:

```text
customer_id
phone_original
phone_normalized
phone_type
status
validation_reason
duplicate_group
```

El mecanismo planteado en este ejercicio utiliza dicha información como base para construir métricas de calidad y trazabilidad.

Conceptualmente:

```text
               EJERCICIO 1
                    |
                    v
           Dataset procesado
                    |
         +----------+----------+
         |                     |
         v                     v
 Información de          Información de
    calidad               trazabilidad
         |                     |
         +----------+----------+
                    |
                    v
             Capa de métricas
                    |
                    v
               Dashboard
                    |
                    v
            Equipo de negocio
```

---

## 3. Dimensiones de calidad

El monitoreo se plantea alrededor de diferentes dimensiones de calidad de datos.

### 3.1. Completitud

Permite identificar qué proporción de los clientes cuenta con información telefónica, ya que un teléfono informado puede no ser necesariamente válido.

Por ejemplo:

```text
phone = "telefono"
```

corresponde a un dato informado, pero inválido.

Por este motivo:

```text
Completitud != Validez
```

---

### 3.2. Validez

Permite determinar si el número cumple las reglas estructurales definidas para numeración colombiana. Por esto, los resultados del pipeline pueden clasificarse como:

```text
VALID
INVALID
SUSPICIOUS
```

---

### 3.3. Normalización

Permite medir la capacidad del proceso para convertir diferentes representaciones de los teléfonos al formato canónico:

```text
+57XXXXXXXXXX
```

---

### 3.4. Unicidad

Permite identificar números normalizados asociados a múltiples clientes.

Ademas de esto, la duplicidad se analiza después de la normalización para evitar considerar como diferentes representaciones equivalentes del mismo teléfono.

---

### 3.5. Plausibilidad

Permite identificar teléfonos estructuralmente válidos que presentan patrones que requieren revisión.

Ejemplos:

```text
3333333333
3111111111
3000000000
```

Estos registros se clasifican como:

```text
SUSPICIOUS
```

en lugar de descartarse automáticamente.

---

### 3.6. Trazabilidad

Permite reconstruir el recorrido realizado por un dato desde su recepción hasta el resultado final del procesamiento.

La trazabilidad busca responder:

```text
¿Qué dato llegó?
       |
       v
¿Qué transformación recibió?
       |
       v
¿Qué resultado obtuvo?
       |
       v
¿Por qué obtuvo ese resultado?
       |
       v
¿Qué ejecución lo procesó?
       |
       v
¿Qué versión del pipeline se utilizó?
```

---

### 3.7. Evolución temporal

Permite comparar la calidad de los datos entre diferentes ejecuciones del pipeline.

Esto permite identificar:

* Mejoras.
* Deterioros.
* Cambios en la calidad de las fuentes.
* Incrementos anormales de determinados errores.

---

## 4. KPI's propuestos

Los indicadores se plantean para ser calculados sobre datos reales una vez el proceso se encuentre conectado a una fuente productiva.

No se calculan porcentajes sobre el dataset utilizado en el Ejercicio 1 debido a que sus 33 registros fueron construidos deliberadamente como casos de prueba y no representan una población real de clientes.

### 4.1. Total de registros procesados

```text
Total procesados = COUNT(*)
```

Permite conocer el tamaño de la población procesada durante una ejecución.

---

### 4.2. Porcentaje de completitud

```text
                      Registros con teléfono informado
Completitud (%) = ----------------------------------------- x 100
                             Total de registros
```

Permite medir la ausencia de información telefónica.

---

### 4.3. Porcentaje de normalización exitosa

```text
                              Registros con phone_normalized
Normalización exitosa (%) = --------------------------------- x 100
                                   Total procesados
```

Permite identificar qué proporción de los valores recibidos puede llevarse de forma segura al formato canónico.

---

### 4.4. Porcentaje de teléfonos válidos

```text
                       Registros con status = VALID
Teléfonos válidos (%) = ----------------------------- x 100
                              Total procesados
```

Este indicador representa los teléfonos que cumplen las reglas establecidas y no presentan anomalías detectadas.

---

### 4.5. Porcentaje de teléfonos inválidos

```text
                         Registros con status = INVALID
Teléfonos inválidos (%) = ------------------------------- x 100
                                Total procesados
```

Permite determinar qué proporción de los números no puede considerarse utilizable de acuerdo con las reglas definidas.

---

### 4.6. Porcentaje de teléfonos sospechosos

```text
                            Registros con status = SUSPICIOUS
Teléfonos sospechosos (%) = ---------------------------------- x 100
                                   Total procesados
```

Permite conocer qué proporción requiere potencialmente una revisión adicional.

---

### 4.7. Validez estructural

Debido a que los registros `SUSPICIOUS` cumplen estructuralmente con las reglas de numeración, puede calcularse adicionalmente:

```text
                           VALID + SUSPICIOUS
Validez estructural (%) = -------------------- x 100
                             Total procesados
```

Este indicador debe diferenciarse del porcentaje de registros completamente aceptados.

---

### 4.8. Registros involucrados en duplicidad

```text
                         Registros con duplicate_group
Duplicidad (%) = ----------------------------------------- x 100
                              Total procesados
```

Permite medir qué proporción de los registros se encuentra involucrada en un problema de unicidad.

---

### 4.9. Cantidad de teléfonos compartidos

```text
COUNT(DISTINCT phone_normalized)
WHERE duplicate_group IS NOT NULL
```

Permite conocer cuántos números telefónicos diferentes aparecen asociados a múltiples clientes.

Este indicador complementa el porcentaje de registros involucrados en duplicidad.

Por ejemplo:

```text
1 teléfono
     |_____ Cliente A
     |_____ Cliente B
     |_____ Cliente C
     |_____ Cliente D
```

representa:

```text
1 teléfono compartido
4 registros involucrados
```

---

### 4.10. Errores por motivo

Conteo de registros agrupados por:

```text
validation_reason
```

Ejemplos:

```text
MISSING_VALUE
NORMALIZATION_FAILED
INVALID_FORMAT
INVALID_PREFIX
INVALID_LANDLINE_LOCAL_PREFIX
REPEATED_DIGITS
```

Este indicador permite identificar las principales causas de problemas de calidad.

---

### 4.11. Incumplimientos por regla

Permite conocer cuántas veces se incumple cada regla de calidad:

```text
R01
R02
R03
...
R10
```

Esto permite identificar cuáles reglas concentran los mayores problemas y orientar acciones de mejora hacia la fuente del dato.

---

### 4.12. Distribución por tipo de teléfono

Permite caracterizar el dataset mediante la distribución:

```text
mobile
landline
```

Este indicador es principalmente descriptivo y no representa por sí mismo una medida de calidad.

---

## 5. Relación entre reglas y monitoreo

Las reglas definidas en el Ejercicio 1 pueden vincularse directamente con las dimensiones de calidad monitoreadas.

| Regla | Dimensión               | Monitoreo                              |
| ----- | ----------------------- | -------------------------------------- |
| R01   | Completitud             | Teléfonos nulos o vacíos               |
| R02   | Normalización / Formato | Valores que no pueden normalizarse     |
| R03   | Validez                 | Longitud nacional incorrecta           |
| R04   | Validez                 | Estructura inválida para celular       |
| R05   | Validez                 | Estructura inválida para teléfono fijo |
| R06   | Validez                 | Indicativo o estructura local inválida |
| R07   | Plausibilidad           | Patrones telefónicos sospechosos       |
| R08   | Unicidad                | Teléfonos normalizados duplicados      |
| R09   | Trazabilidad            | Conservación de original y normalizado |
| R10   | Trazabilidad            | Registro del resultado y motivo        |

Esta relación permite mantener trazabilidad entre:

```text
Regla de negocio
      |
      v
Validación técnica
      |
      v
Resultado
      |
      v
KPI / Monitoreo
```

---

## 6. Modelo conceptual de información

Para soportar tanto el monitoreo como la trazabilidad se proponen tres conjuntos lógicos de información.

```text
trusted_phones
data_quality_runs
data_quality_rule_results
```

---

## 7. Dataset de teléfonos procesados

`trusted_phones` contiene el detalle generado por el pipeline para cada cliente.

Conceptualmente podría almacenar:

| Campo               | Descripción                       |
| ------------------- | --------------------------------- |
| `run_id`            | Identificador de la ejecución     |
| `customer_id`       | Identificador del cliente         |
| `phone_original`    | Número recibido originalmente     |
| `phone_normalized`  | Número normalizado                |
| `phone_type`        | `mobile` o `landline`             |
| `status`            | `VALID`, `INVALID` o `SUSPICIOUS` |
| `validation_reason` | Motivo asociado al resultado      |
| `duplicate_group`   | Grupo de duplicidad               |
| `processed_at`      | Momento del procesamiento         |
| `pipeline_version`  | Versión del pipeline              |
| `source`            | Fuente del dato                   |

Esta estructura permite conservar el resultado detallado de cada registro.

---

## 8. Histórico de ejecuciones

`data_quality_runs` registra información correspondiente a cada ejecución del pipeline.

Una estructura conceptual podría ser:

| Campo                | Descripción                           |
| -------------------- | ------------------------------------- |
| `run_id`             | Identificador único de la ejecución   |
| `processed_at`       | Fecha y hora de procesamiento         |
| `pipeline_version`   | Versión del código utilizado          |
| `source`             | Sistema fuente                        |
| `source_file`        | Archivo o conjunto de datos procesado |
| `source_hash`        | Identificador/hash del insumo         |
| `total_records`      | Total procesado                       |
| `valid_records`      | Registros válidos                     |
| `invalid_records`    | Registros inválidos                   |
| `suspicious_records` | Registros sospechosos                 |
| `duplicate_records`  | Registros involucrados en duplicidad  |

El histórico permite comparar ejecuciones sin sobrescribir resultados anteriores.

Por ejemplo:

```text
RUN-001 ---> Calidad día/ejecución 1
RUN-002 ---> Calidad día/ejecución 2
RUN-003 ---> Calidad día/ejecución 3
```

Esto permite analizar tendencias.

---

## 9. Resultados de reglas de calidad

Para proporcionar mayor nivel de detalle se propone conceptualmente una estructura:

```text
data_quality_rule_results
```

con campos como:

| Campo         | Descripción                        |
| ------------- | ---------------------------------- |
| `run_id`      | Ejecución donde se evaluó la regla |
| `customer_id` | Registro evaluado                  |
| `rule_id`     | Regla evaluada (`R01` - `R10`)     |
| `rule_status` | `PASSED` o `FAILED`                |
| `rule_detail` | Detalle del resultado              |

Ejemplo:

```text
RUN-001 | 025 | R01 | FAILED | MISSING_VALUE
RUN-001 | 020 | R02 | FAILED | INVALID_FORMAT
RUN-001 | 022 | R07 | FAILED | REPEATED_DIGITS
RUN-001 | 001 | R08 | FAILED | DUP-001
```

Esta estructura permite que un mismo registro pueda presentar diferentes observaciones de calidad sin limitarse a un único `validation_reason`.

---

## 10. Trazabilidad del dato

Para cada número telefónico se busca poder reconstruir su recorrido completo.

Ejemplo conceptual:

```text
customer_id
     |
     v
Sistema / archivo fuente
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
    status
     |
     v
validation_reason / rule_id
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

Esto permitiría responder preguntas como:

* ¿Cuál era el valor original?
* ¿Cómo fue normalizado?
* ¿Qué regla produjo una observación?
* ¿Qué ejecución procesó el dato?
* ¿Cuándo fue procesado?
* ¿Qué versión del pipeline se utilizó?
* ¿Desde qué fuente fue recibido?

---

## 11. Arquitectura conceptual del mecanismo

La solución propuesta separa el procesamiento de datos de su consumo analítico.

```text
                    Fuente de clientes
                           |
                           v
                 Pipeline Ejercicio 1
                           |
             +-------------+-------------+
             |                           |
             v                           v
       trusted_phones            data_quality_runs
             |                           |
             |                 data_quality_rule_results
             |                           |
             +-------------+-------------+
                           |
                           v
                    Capa de métricas
                           |
                           v
                      Dashboard BI
                           |
                 +---------+---------+
                 |                   |
                 v                   v
              Calidad           Trazabilidad
                 |                   |
                 +---------+---------+
                           |
                           v
                    Equipo de negocio
```

La capa de visualización podría implementarse mediante la herramienta de Business Intelligence disponible en la organización.

Por ejemplo:

* Power BI.
* Looker Studio.
* Databricks SQL.
* Otra herramienta corporativa de BI.

La propuesta se mantiene independiente de un proveedor específico debido a que el enunciado no define una arquitectura tecnológica concreta.

---

## 12. Vistas propuestas para negocio

El recurso podría organizarse en tres vistas principales.

### 12.1. Resumen ejecutivo

Presentaría los principales KPI de calidad.

Por ejemplo:

```text
Total procesados

% Completitud

% VALID

% INVALID

% SUSPICIOUS

% Duplicidad

Variación vs. ejecución anterior
```

Los indicadores deberían mostrar tanto su valor actual como su tendencia.

Ejemplo conceptual:

```text
Teléfonos válidos

91.2 %

+3.4 pp vs. ejecución anterior
```

La comparación de tasas debe realizarse preferiblemente mediante puntos porcentuales.

---

### 12.2. Análisis de calidad

Esta vista permitiría profundizar en las causas de los problemas.

Podría incluir:

* Registros por `validation_reason`.
* Incumplimientos por `rule_id`.
* Tendencia de registros inválidos.
* Tendencia de registros sospechosos.
* Tendencia de datos faltantes.
* Registros involucrados en duplicidad.
* Distribución mobile / landline.

Filtros sugeridos:

```text
Fecha
run_id
Fuente
phone_type
status
validation_reason
rule_id
```

---

### 12.3. Trazabilidad

Permitiría buscar un registro por:

```text
customer_id
```

o por teléfono.

El usuario podría visualizar:

```text
Fuente
   |
phone_original
   |
phone_normalized
   |
phone_type
   |
status
   |
validation_reason
   |
rule_id
   |
duplicate_group
   |
run_id
   |
processed_at
   |
pipeline_version
```

Esta vista permitiría a negocio entender no solamente que existe un problema, sino también cómo fue generado el resultado.

---

## 13. Evolución histórica

Los KPI principales deben almacenarse por ejecución para permitir análisis temporal.

Ejemplo:

```text
              RUN-001    RUN-002    RUN-003

VALID           82%        87%        91%

INVALID         14%         9%         6%

SUSPICIOUS       4%         4%         3%
```

Esto permitiría detectar:

```text
Mejoras
Deterioros
Cambios inesperados
Problemas en la fuente
Impacto de nuevas reglas
```

---

## 14. Alertas

El mecanismo puede complementarse con alertas automáticas de calidad.

Se consideran dos tipos principales.

### Alertas por umbral

Ejemplo:

```text
% INVALID > límite aceptado
             |
             v
           ALERTA
```

---

### Alertas por variación

Permiten detectar cambios anormales respecto al comportamiento histórico.

Ejemplo:

```text
MISSING_VALUE histórico = 1%

Nueva ejecución = 8%

          |
          v
        ALERTA
```

Este mecanismo permite detectar posibles problemas en la fuente incluso antes de superar un límite absoluto.

---

## 15. Definición de umbrales

Los valores concretos de alerta no se fijan dentro de esta propuesta.

Los umbrales deberían establecerse utilizando:

* Datos reales.
* Una línea base histórica.
* Impacto para negocio.
* Nivel de calidad esperado.
* Acuerdos con los responsables de los datos.

Esto evita establecer límites arbitrarios sin conocer el comportamiento real del dataset.

---

## 16. Automatización del monitoreo

El proceso conceptual podría ejecutarse después de cada ejecución exitosa del pipeline del Ejercicio 1.

```text
Pipeline de teléfonos
        |
        v
Dataset procesado
        |
        v
Actualizar histórico de calidad
        |
        v
Calcular KPI
        |
        v
Actualizar dashboard
        |
        v
Evaluar alertas
```

De esta manera, el monitoreo se mantendría actualizado automáticamente conforme se generen nuevas versiones del dataset.


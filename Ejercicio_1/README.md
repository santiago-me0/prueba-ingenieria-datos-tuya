# Ejercicio 1 - Dataset confiable de números telefónicos

## Enfoque

La solución implementa un pipeline para normalizar, validar y controlar la calidad de números telefónicos de clientes en Colombia.

El proceso conserva el valor original recibido y genera una representación normalizada cuando es posible:

```text
+57XXXXXXXXXX
```

El flujo principal es:

```text
clients.csv
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
processed_clients.csv
```

El dataset utilizado para la prueba contiene 33 registros construidos específicamente para representar casos válidos, formatos alternativos, datos incompletos, valores sospechosos y números duplicados.

---

## Reglas de calidad

Las principales reglas aplicadas son:

| ID | Regla |
|---|---|
| R01 | El teléfono no debe ser nulo o vacío. |
| R02 | Debe poder normalizarse a una estructura válida para Colombia. |
| R03 | El número nacional debe contener 10 dígitos. |
| R04 | Los celulares deben comenzar por `3`. |
| R05 | Los teléfonos fijos deben comenzar por `60`. |
| R06 | El indicativo regional del teléfono fijo debe ser válido. |
| R07 | Se detectan patrones numéricos sospechosos. |
| R08 | Se identifican teléfonos duplicados después de la normalización. |
| R09 | El valor original se conserva sin modificaciones. |
| R10 | Toda transformación o rechazo registra su resultado. |

Los indicativos considerados para teléfonos fijos son:

```text
601, 602, 604, 605, 606, 607, 608
```

Los registros se clasifican como:

- `VALID`: cumplen las reglas definidas.
- `INVALID`: no cumplen la estructura esperada.
- `SUSPICIOUS`: son estructuralmente válidos, pero presentan un patrón que requiere revisión.

Por ejemplo, números como `3333333333` o `3000000000` se clasifican como `SUSPICIOUS` en lugar de descartarse automáticamente.

La detección de duplicados se realiza utilizando el teléfono normalizado, por lo que distintas representaciones del mismo número pueden reconocerse como equivalentes.

---

## Dataset resultante

El pipeline genera los siguientes campos:

| Campo | Descripción |
|---|---|
| `customer_id` | Identificador del cliente. |
| `phone_original` | Valor recibido originalmente. |
| `phone_normalized` | Número en formato canónico cuando puede normalizarse. |
| `phone_type` | `mobile` o `landline`. |
| `status` | `VALID`, `INVALID` o `SUSPICIOUS`. |
| `validation_reason` | Motivo asociado al resultado. |
| `duplicate_group` | Grupo asignado cuando varios registros representan el mismo teléfono. |

La normalización no intenta reconstruir información faltante. Por ejemplo, un teléfono fijo de siete dígitos sin indicativo regional no se completa automáticamente.

---

## Estructura

```text
Ejercicio_1/
├── README.md
├── data/
│   ├── clients.csv
│   └── processed_clients.csv   # Generado por el pipeline
├── src/
│   ├── normalizacion.py
│   ├── validacion.py
│   └── pipeline.py
└── test/
    ├── test_normalizacion.py
    ├── test_validacion.py
    └── test_pipeline.py
```

`processed_clients.csv` es un archivo derivado y reproducible, por lo que no se utiliza como fuente de verdad.

---

## Ejecución

Desde la raíz del repositorio:

```bash
python -m Ejercicio_1.src.pipeline
```

La ejecución toma como entrada:

```text
Ejercicio_1/data/clients.csv
```

y genera:

```text
Ejercicio_1/data/processed_clients.csv
```

La implementación no requiere dependencias externas.

---

## Pruebas

La suite completa se ejecuta con:

```bash
python -m unittest discover \
    -s Ejercicio_1/test \
    -p "test_*.py" \
    -v
```

Se implementaron **45 pruebas automatizadas** entre pruebas unitarias y de integración.

Entre los casos cubiertos se encuentran:

- Formatos válidos e inválidos.
- Celulares y teléfonos fijos.
- Valores vacíos e incompletos.
- Indicativos regionales.
- Patrones sospechosos.
- Preservación del valor original.
- Detección de duplicados.
- Procesamiento completo del dataset de prueba.

---

## CI/CD

GitHub Actions se utiliza para automatizar la validación y generación del dataset.

```text
Pull Request a main
        |
        v
        CI
   45 pruebas
        |
        v
      Merge
        |
        v
Push a main
        |
        v
     CI + CD
        |
        v
Ejecutar pipeline
        |
        v
Dataset artifact
```

Los Pull Requests hacia `main` ejecutan las pruebas de CI.

Después de un merge, el `push` a `main` vuelve a ejecutar las pruebas y, si son satisfactorias, genera el dataset procesado y lo publica como artifact del workflow.

También se dispone de `workflow_dispatch` para ejecuciones manuales.

No se configuró una ejecución periódica porque la prueba utiliza un insumo estático y no define una frecuencia de actualización. En un entorno productivo, la ejecución podría activarse mediante un schedule o por eventos asociados a la llegada de nuevos datos.

---

## Decisiones principales

- La solución está especializada en numeración colombiana y no intenta inferir información que no se encuentre en la fuente.

- El valor original siempre se conserva para mantener trazabilidad.

- Los patrones sospechosos se separan de los datos inválidos para evitar descartar números que cumplen estructuralmente con la numeración definida.

- Los cambios en las reglas se controlan mediante Git, Pull Requests y pruebas automatizadas, permitiendo regenerar el dataset de forma reproducible.
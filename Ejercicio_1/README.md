# Ejercicio 1 - Dataset confiable de números telefónicos

## 1. Objetivo

Diseñar e implementar un proceso automatizado para la creación, normalización, validación, despliegue y mantenimiento de un dataset confiable de números telefónicos de clientes.

La solución aplica reglas de calidad de datos, conserva el valor original para garantizar trazabilidad y utiliza prácticas de CI/CD para controlar los cambios realizados sobre el proceso.

---

## 2. Alcance

La solución se encuentra especializada en numeración telefónica colombiana.

Se contemplan:

- Números celulares nacionales de 10 dígitos que comienzan por `3`.
- Teléfonos fijos nacionales conformados por `60`, un indicativo regional válido y 7 dígitos locales.
- Diferentes representaciones de entrada mediante espacios, guiones, paréntesis y código de país `+57`.
- Datos incompletos o con formatos inválidos.
- Patrones numéricos sospechosos.
- Números duplicados representados mediante diferentes formatos.

El formato canónico utilizado por el proceso es:

```text
+57XXXXXXXXXX
```

La solución no intenta inferir información faltante ni completar automáticamente números incompletos.

---

## 3. Arquitectura de la solución

El ejercicio se implementa como un pipeline modular compuesto por tres responsabilidades principales:

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

La normalización, la validación y la orquestación del proceso se encuentran desacopladas para facilitar el mantenimiento y las pruebas.

Git y GitHub Actions se utilizan como mecanismos de control de versiones, integración continua y entrega continua.

---

## 4. Estructura del ejercicio

```text
Ejercicio_1/
├── __init__.py
├── README.md
├── data/
│   ├── clients.csv
│   └── processed_clients.csv   # Generado por el pipeline
├── src/
│   ├── __init__.py
│   ├── normalizacion.py
│   ├── validacion.py
│   └── pipeline.py
└── test/
    ├── test_normalizacion.py
    ├── test_validacion.py
    └── test_pipeline.py
```

### Componentes

- `normalizacion.py`: transforma diferentes representaciones de un teléfono al formato canónico.
- `validacion.py`: valida la estructura del teléfono, determina su tipo e identifica patrones sospechosos.
- `pipeline.py`: orquesta la lectura del archivo de entrada, normalización, validación, detección de duplicados y generación del dataset procesado.
- `clients.csv`: dataset controlado utilizado como insumo del ejercicio.
- `processed_clients.csv`: dataset derivado generado automáticamente por el pipeline.
- `test/`: contiene las pruebas unitarias y de integración.

---

## 5. Dataset de prueba

El enunciado no proporciona un dataset de números telefónicos. Por este motivo, se construyó un dataset controlado de **33 registros** para representar diferentes escenarios de negocio y calidad de datos.

El dataset incluye casos de:

- Celulares válidos.
- Teléfonos fijos válidos.
- Diferentes representaciones del mismo teléfono.
- Números con y sin `+57`.
- Espacios, guiones y paréntesis.
- Números incompletos.
- Valores vacíos.
- Caracteres y formatos no permitidos.
- Patrones numéricos sospechosos.
- Teléfonos duplicados después de la normalización.

El archivo original se conserva sin modificaciones y el resultado del procesamiento se genera en un archivo independiente.

---

## 6. Reglas de calidad

| ID | Regla |
|---|---|
| R01 | El teléfono no debe ser nulo o vacío. |
| R02 | El teléfono debe poder normalizarse a una estructura de numeración colombiana. |
| R03 | El número nacional debe contener 10 dígitos. |
| R04 | Los celulares deben comenzar por `3`. |
| R05 | Los teléfonos fijos deben comenzar por `60`. |
| R06 | El indicativo regional del teléfono fijo debe pertenecer al conjunto permitido. |
| R07 | Se detectan patrones numéricos altamente repetitivos o sospechosos. |
| R08 | Se identifican teléfonos duplicados después de la normalización. |
| R09 | El valor original se conserva sin modificaciones. |
| R10 | Toda transformación o rechazo registra su resultado. |

Los indicativos regionales considerados para teléfonos fijos son:

```text
601
602
604
605
606
607
608
```

Para teléfonos fijos también se valida que el número local comience por un dígito permitido según las reglas definidas para la solución.

---

## 7. Normalización

La normalización transforma diferentes representaciones de un número telefónico al formato canónico:

```text
+57XXXXXXXXXX
```

Ejemplos:

```text
3001234567          -> +573001234567
300-123-4567        -> +573001234567
300 526 36 54       -> +573005263654
+57 300 526 36 54   -> +573005263654

6013254585          -> +576013254585
(604) 325-4585      -> +576043254585
605 568 65 25       -> +576055686525
```

La solución únicamente elimina separadores previamente permitidos.

Por ejemplo, una entrada como:

```text
311+359+45+66
```

no se convierte automáticamente en un número válido, debido a que el signo `+` aparece en posiciones no permitidas.

De igual forma, un número fijo local de 7 dígitos sin indicativo regional no se completa automáticamente, ya que esto implicaría inferir información inexistente en la fuente.

---

## 8. Validación

Una vez normalizado el número, se aplican las reglas de validación correspondientes al dominio colombiano.

Los registros pueden tener uno de los siguientes estados:

- `VALID`: cumple las reglas estructurales definidas y no presenta anomalías detectadas.
- `INVALID`: no cumple las reglas necesarias para ser considerado un número válido.
- `SUSPICIOUS`: cumple estructuralmente, pero presenta un patrón que requiere revisión.

Ejemplos de patrones sospechosos:

```text
3333333333
3111111111
3000000000
```

Estos registros no se rechazan automáticamente.

Se clasifican como:

```text
status = SUSPICIOUS
validation_reason = REPEATED_DIGITS
```

Esto permite diferenciar la validez estructural de una posible anomalía de calidad.

---

## 9. Detección de duplicados

La detección de duplicados se realiza utilizando el número normalizado.

Esto permite identificar como equivalentes números recibidos utilizando formatos diferentes.

Por ejemplo:

```text
3001234567
300-123-4567
300 123 4567
+57 300 123 4567
+573001234567
573001234567
```

todos representan:

```text
+573001234567
```

Los registros pertenecientes al mismo número normalizado reciben un valor común en:

```text
duplicate_group
```

Un teléfono duplicado no se considera automáticamente inválido, debido a que la duplicidad corresponde a una dimensión de calidad diferente de la validez estructural.

---

## 10. Dataset de salida

El pipeline genera un dataset con las siguientes columnas:

| Campo | Descripción |
|---|---|
| `customer_id` | Identificador del cliente. |
| `phone_original` | Valor original recibido, conservado sin modificaciones. |
| `phone_normalized` | Número transformado al formato canónico cuando es posible. |
| `phone_type` | Clasificación como `mobile` o `landline`. |
| `status` | Resultado general: `VALID`, `INVALID` o `SUSPICIOUS`. |
| `validation_reason` | Motivo de rechazo o clasificación especial. |
| `duplicate_group` | Grupo asignado cuando el teléfono normalizado aparece asociado a varios clientes. |

Este modelo permite conservar trazabilidad entre el dato original y el resultado generado por el pipeline.

---

## 11. Ejecución local

### Requisitos

- Python 3.11 o superior.
- No se requieren dependencias externas para la implementación actual.

Desde la raíz del repositorio:

```bash
python -m Ejercicio_1.src.pipeline
```

El pipeline utiliza como entrada:

```text
Ejercicio_1/data/clients.csv
```

y genera:

```text
Ejercicio_1/data/processed_clients.csv
```

El archivo procesado es un dato derivado y reproducible a partir del dataset fuente y el código versionado.

---

## 12. Pruebas automatizadas

Para ejecutar la suite completa de pruebas:

```bash
python -m unittest discover -s Ejercicio_1/test -p "test_*.py" -v
```

La solución cuenta con **45 pruebas automatizadas**.

Estas se encuentran distribuidas entre:

- Pruebas unitarias de normalización.
- Pruebas unitarias de validación.
- Pruebas de integración del pipeline completo.

Los tests verifican:

- Diferentes representaciones válidas.
- Valores vacíos.
- Longitudes incorrectas.
- Formatos no permitidos.
- Celulares.
- Teléfonos fijos.
- Indicativos regionales.
- Patrones sospechosos.
- Preservación del valor original.
- Detección de duplicados.
- Esquema del dataset resultante.
- Procesamiento de los 33 registros definidos.

---

## 13. Estrategia CI/CD

La solución utiliza **GitHub Actions** para controlar automáticamente los cambios realizados sobre el proceso.

### Integración continua - CI

Un Pull Request dirigido a `main` dispara automáticamente la ejecución de las pruebas unitarias y de integración.

```text
Feature branch
     |
     v
Pull Request
     |
     v
GitHub Actions
     |
     v
45 pruebas automatizadas
     |
     +------ FAIL ------> No continuar
     |
     +------- OK -------> Merge
```

Esto permite detectar regresiones antes de integrar modificaciones a la rama principal.

### Entrega continua - CD

Después de realizar merge a `main`, el `push` resultante dispara una nueva ejecución.

Primero se ejecuta nuevamente la suite de pruebas.

Si todas las validaciones son satisfactorias, GitHub Actions ejecuta automáticamente el pipeline y genera el dataset procesado.

```text
Merge a main
     |
     v
Push a main
     |
     v
    CI
     |
     v
Tests OK
     |
     v
    CD
     |
     v
Ejecutar pipeline
     |
     v
processed_clients.csv
     |
     v
GitHub Actions Artifact
```

El dataset generado se publica como artifact del workflow.

Para el alcance de la prueba, este artifact representa el resultado desplegado del proceso.

En un entorno productivo, este último paso podría sustituirse por la publicación del dataset en el sistema de almacenamiento utilizado por la organización, por ejemplo un Data Lake, una base de datos o un Data Warehouse.

---

## 14. Triggers de ejecución

Actualmente el workflow contempla tres formas de ejecución.

### Pull Request hacia `main`

Ejecuta la etapa de CI para validar los cambios antes de integrarlos.

### Push hacia `main`

Ejecuta CI y, si las pruebas son satisfactorias, continúa con la etapa de CD para construir el dataset.

### Ejecución manual

Se encuentra disponible `workflow_dispatch`, permitiendo lanzar manualmente una ejecución desde GitHub Actions.

No se implementó una ejecución periódica porque el ejercicio no proporciona una fuente productiva ni establece una frecuencia de actualización.

En un escenario productivo, la estrategia podría extenderse mediante:

- Una ejecución programada.
- Un evento generado por la llegada de nuevos datos.
- Una actualización de la fuente.
- Un proceso incremental o CDC cuando la fuente lo permita.

---

## 15. Mantenimiento

El mantenimiento del proceso se soporta mediante:

- Git como sistema de control de versiones.
- Desarrollo mediante ramas.
- Pull Requests.
- Pruebas automatizadas.
- GitHub Actions.
- Pruebas de regresión.
- Dataset procesado reproducible.

Ante una modificación de las reglas de negocio, el flujo esperado es:

```text
Nueva regla o modificación
        |
        v
Crear o actualizar tests
        |
        v
Modificar implementación
        |
        v
Pull Request
        |
        v
       CI
        |
        v
      Merge
        |
        v
Nueva ejecución del pipeline
```

De esta manera, las modificaciones realizadas sobre la normalización o validación son verificadas automáticamente antes de generar una nueva versión del dataset.

---

## 16. Consideraciones para un entorno productivo

El dataset utilizado en la prueba es un insumo estático y controlado.

En un ambiente productivo se recomienda separar los datos en capas:

```text
Fuente
  |
  v
 RAW
  |
  v
Pipeline de calidad
  |
  v
TRUSTED
```
Considerando:
- La capa `RAW` debe conservar los datos recibidos originalmente sin modificaciones.

- La capa `TRUSTED` contendría el resultado normalizado, validado y enriquecido con información de calidad.

- Si el proceso necesitara ejecutarse de manera periódica, podría utilizarse un trigger temporal mediante un orquestador.

- Si la fuente generara nuevos archivos, sería preferible utilizar un trigger basado en eventos.

- La elección del mecanismo de ejecución dependería de la infraestructura y frecuencia de actualización definidas por la organización.
# Ejercicio 4 - Procesamiento de archivos HTML

## Enfoque

La solución procesa archivos HTML individuales o directorios completos, incluyendo sus subdirectorios.

Para cada archivo HTML se identifican las imágenes referenciadas mediante etiquetas `<img>`, se leen desde el sistema de archivos y se convierten a Base64 utilizando únicamente librerías de la standard library de Python.

El archivo original no se modifica. El resultado se guarda en un nuevo archivo con sufijo `_base64`.

```text
Archivos / directorios
        |
        v
Búsqueda de HTML
        |
        v
Detección de <img>
        |
        v
Lectura de imágenes
        |
        v
Conversión a Base64
        |
        v
Nuevo *_base64.html
```

La solución utiliza programación orientada a objetos y separa las responsabilidades de búsqueda de archivos, codificación de imágenes y procesamiento del HTML.

---

## Comportamiento

El programa acepta una combinación de:

- Archivos `.html`.
- Archivos `.htm`.
- Directorios.
- Subdirectorios recorridos de forma recursiva.

Las imágenes locales referenciadas mediante `src` se convierten a una URI del tipo:

```text
data:image/png;base64,...
```

Por ejemplo:

```html
<img src="images/logo.png" alt="Logo">
```

se transforma en:

```html
<img src="data:image/png;base64,..." alt="Logo">
```

El archivo HTML original se conserva sin modificaciones.

Si una imagen no puede procesarse, el resto del archivo continúa siendo procesado y el error queda registrado en el resultado.

---

## Resultado del procesamiento

El proceso devuelve una estructura con imágenes procesadas correctamente y aquellas que presentaron errores:

```json
{
  "success": {
    "/path/index.html": [
      "images/logo.png"
    ]
  },
  "fail": {
    "/path/page.html": [
      {
        "src": "missing.png",
        "error": "Image not found"
      }
    ]
  }
}
```

Una imagen que ya se encuentre embebida mediante una URI `data:` se conserva sin modificaciones.

Las referencias HTTP/HTTPS no se descargan. La solución se enfoca en imágenes locales asociadas a los archivos HTML.

---

## Estructura

```text
Ejercicio_4/
├── README.md
├── src/
│   ├── __init__.py
│   ├── file_finder.py
│   ├── image_encoder.py
│   ├── html_processor.py
│   └── main.py
└── test/
    ├── __init__.py
    ├── test_file_finder.py
    └── test_html_processor.py
```

### Componentes principales

- `HtmlFileFinder`: obtiene los archivos HTML a procesar y recorre directorios de forma recursiva.
- `ImageEncoder`: convierte imágenes locales a Base64 y determina su tipo MIME.
- `HtmlProcessor`: procesa las etiquetas `<img>` y genera el nuevo archivo HTML.
- `HtmlBatchProcessor`: coordina el procesamiento de múltiples archivos.
- `ProcessingReport`: conserva los resultados `success` y `fail`.

---

## Ejecución

Desde la raíz del repositorio se puede procesar un archivo:

```bash
python -m Ejercicio_4.src.main ruta/al/archivo.html
```

Un directorio completo:

```bash
python -m Ejercicio_4.src.main ruta/al/directorio/
```

O varios archivos y directorios:

```bash
python -m Ejercicio_4.src.main \
    pagina1.html \
    pagina2.html \
    directorio/
```

Los archivos generados utilizan el sufijo:

```text
_base64.html
```

Por ejemplo:

```text
index.html
    ↓
index_base64.html
```

Los archivos generados se ignoran cuando posteriormente se procesa un directorio para evitar reprocesarlos.

---

## Pruebas

Las pruebas se ejecutan con:

```bash
python -m unittest discover \
    -s Ejercicio_4/test \
    -p "test_*.py" \
    -v
```

La solución cuenta con **16 pruebas automatizadas**.

Entre los escenarios cubiertos se encuentran:

- Archivos HTML individuales.
- Búsqueda recursiva en directorios.
- Extensiones `.html` y `.htm`.
- Exclusión de archivos no HTML.
- Exclusión de archivos `_base64.html`.
- Conversión correcta a Base64.
- Múltiples imágenes por documento.
- Rutas relativas.
- Preservación del HTML original.
- Creación de un nuevo archivo.
- Imágenes inexistentes.
- Fallos parciales sin detener el procesamiento.
- Etiquetas `<img />`.
- Etiquetas `<img>` sin `src`.
- Imágenes previamente embebidas.

---

## Decisiones principales

Se utilizó `HTMLParser` en lugar de expresiones regulares para analizar las etiquetas HTML.

Todas las funcionalidades se implementaron utilizando únicamente módulos incluidos en la standard library, entre ellos:

```text
html.parser
base64
pathlib
mimetypes
urllib.parse
argparse
json
dataclasses
```

La solución prioriza que un error en una imagen no detenga el procesamiento completo. Las imágenes procesadas correctamente se reemplazan y los fallos se registran de forma independiente.



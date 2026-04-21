# `analisis_fidelidad.py` — Análisis de fidelidad léxica del corpus *Geórgicas* IV

Script Python que produce el análisis cuantitativo de fidelidad de las ocho
traducciones del corpus a partir del atributo `@cert` anotado en los XML TEI.
Genera cuatro salidas: una tabla de estadísticas descriptivas (CSV + consola)
y cuatro visualizaciones SVG (mapas de calor y perfiles de líneas).

Forma parte del proyecto de investigación "La traducción versificada de las
*Geórgicas* de Virgilio por Miguel Antonio Caro", desarrollado en la
Universidad de los Andes (Bogotá).

---

## Requisitos

- Python 3.10 o superior
- [`uv`](https://docs.astral.sh/uv/) (gestor de entornos y paquetes recomendado)

Dependencias Python:

| Paquete | Uso |
|---|---|
| `lxml` | Parseo de los XML TEI |
| `pandas` | Construcción del DataFrame versos × traducciones |
| `matplotlib` | Gráficos de líneas y mapas de calor |
| `seaborn` | Mapas de calor |

---

## Instalación con `uv`

### 1. Instalar `uv` (si aún no lo tienes)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

O con Homebrew en macOS:

```bash
brew install uv
```

### 2. Crear el entorno virtual e instalar dependencias

Desde el directorio del proyecto:

```bash
uv venv
uv pip install lxml pandas matplotlib seaborn
```

Esto crea un entorno `.venv/` local y descarga las dependencias.

### 3. Activar el entorno

```bash
# macOS / Linux
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

### Alternativa: ejecutar directamente con `uv run`

Sin necesidad de activar el entorno manualmente:

```bash
uv run --with lxml --with pandas --with matplotlib --with seaborn \
    python analisis_fidelidad.py
```

---

## Estructura de archivos esperada

```
proyecto/
├── analisis_fidelidad.py
├── TEI/                        ← directorio configurado en DIR_UPLOADS
│   ├── V_G04.xml
│   ├── MAC_G04.xml
│   ├── AEP_G04.xml
│   ├── JL_G04.xml
│   ├── LLA_G04.xml
│   ├── NPC_G04.xml
│   ├── PF_G04.xml
│   ├── RBN_G04.xml
│   └── AB_G04.xml
└── output/                     ← se debe crear antes de ejecutar
```

Crear el directorio de salida:

```bash
mkdir -p output
```

Si los XML están en un directorio distinto de `TEI/`, edita las variables
`DIR_PROYECTO` y `DIR_UPLOADS` al inicio del script:

```python
DIR_PROYECTO = Path("ruta/a/tus/xml/")
DIR_UPLOADS  = Path("ruta/a/tus/xml/")
```

---

## Uso

```bash
python analisis_fidelidad.py
```

---

## Salidas

| Archivo | Descripción |
|---|---|
| `output/estadisticas.csv` | Estadísticas descriptivas por traducción (nivel de segmento) |
| `output/heatmap_bugonia.svg` | Mapa de calor de fidelidad verso × traducción, vv. 281–316 |
| `output/heatmap_filomena.svg` | Mapa de calor de fidelidad verso × traducción, vv. 511–515 |
| `output/lineas_bugonia.svg` | Perfil de fidelidad verso a verso (líneas), vv. 281–316 |
| `output/lineas_filomena.svg` | Perfil de fidelidad verso a verso (líneas), vv. 511–515 |

### `estadisticas.csv` — columnas

| Columna | Descripción |
|---|---|
| `n` | Número total de segmentos (`<seg>` y `<gap>`) con `@cert` en el corpus |
| `Media` | Media aritmética de los valores numéricos de `@cert` |
| `DE` | Desviación estándar |
| `Varianza` | Varianza |
| `high (n)` / `high (%)` | Frecuencia absoluta y relativa de `@cert="high"` |
| `medium (n)` / `medium (%)` | Ídem para `medium` |
| `low (n)` / `low (%)` | Ídem para `low` |

### Escala de `@cert`

| Valor XML | Valor numérico | Interpretación |
|---|---|---|
| `high` | 3 | Correspondencia de alta confianza |
| `medium` | 2 | Correspondencia probable |
| `low` | 1 | Correspondencia conjetural o débil |

Los mapas de calor y los gráficos de líneas usan esta escala numérica;
las celdas sin dato (verso no cubierto por la traducción) aparecen en gris.

---

## Configuración avanzada

Las siguientes variables al inicio del script permiten ajustar el análisis
sin modificar el código:

| Variable | Descripción |
|---|---|
| `DIR_UPLOADS` | Directorio con los XML TEI |
| `BUGONIA` | Rango de versos de la bugonía (por defecto `range(281, 317)`) |
| `FILOMENA` | Rango de versos del símil de Filomena (por defecto `range(511, 516)`) |
| `COLORES` | Diccionario `sigla → color hex` para los gráficos de líneas |

Para añadir una traducción nueva al análisis, basta con añadir una entrada
al diccionario `TRADUCCIONES`:

```python
TRADUCCIONES["XYZ"] = (DIR_UPLOADS, "XYZ_G04.xml")
```

y una entrada en `COLORES`:

```python
COLORES["XYZ"] = "#2c3e50"
```

---

## Créditos

Nicolás Vaughan · Universidad de los Andes, Bogotá · <n.vaughan@uniandes.edu.co>

Proyecto PAPIIT IA401025 «Modernidad iberoamericana de las *Geórgicas* virgilianas»,
Instituto de Investigaciones Filológicas, UNAM.

# `generar_tablas.py` — Tablas de fidelidad léxica del corpus *Geórgicas* IV

Script Python que regenera las tres tablas CSV del análisis gasparoviano a partir
de los archivos TEI-XML del corpus. Forma parte del proyecto de investigación
"La traducción versificada de las *Geórgicas* de Virgilio por Miguel Antonio Caro",
desarrollado en la Universidad de los Andes (Bogotá).

---

## Requisitos

- Python 3.8 o superior
- Solo bibliotecas de la librería estándar (`xml.etree.ElementTree`, `csv`, `argparse`, `os`, `re`)

No es necesario instalar dependencias externas.

---

## Archivos necesarios

El directorio del corpus debe contener los siguientes archivos XML:

| Archivo | Contenido |
|---|---|
| `V_G04.xml` | Texto fuente virgiliano anotado |
| `AB_G04.xml` | Bekes |
| `AEP_G04.xml` | Espinosa Pólit |
| `JL_G04.xml` | Lembke |
| `LLA_G04.xml` | López Álvarez |
| `MAC_G04.xml` | Caro (1873/1943) |
| `NPC_G04.xml` | Pérez del Camino |
| `PF_G04.xml` | Fallon |
| `RBN_G04.xml` | Bonifaz Nuño |

Adicionalmente, para preservar celdas sin anotación explícita en el XML
(véase la sección [Lógica de anotación](#lógica-de-anotación) más abajo),
se recomienda disponer de las versiones anteriores de los tres CSV:

- `bugonia_correspondencias.csv`
- `bugonia_indices.csv`
- `filomela_correspondencias.csv`

Si estos archivos están en el mismo directorio que los XML, el script los
detecta automáticamente sin necesidad de indicarlos de forma explícita.

---

## Uso

### Caso más sencillo

Si todos los archivos (XML y CSV anteriores) están en el directorio actual:

```bash
python generar_tablas.py
```

Los tres CSV se escriben también en el directorio actual.

### Con rutas explícitas

```bash
python generar_tablas.py \
    --corpus ./corpus \
    --prev-bug ./tablas/bugonia_correspondencias.csv \
    --prev-fil ./tablas/filomela_correspondencias.csv \
    --prev-idx ./tablas/bugonia_indices.csv \
    --out ./tablas_nuevas
```

### Referencia de argumentos

| Argumento | Descripción | Por defecto |
|---|---|---|
| `--corpus DIR` | Directorio con los XML | Directorio actual |
| `--prev-bug CSV` | CSV anterior de `bugonia_correspondencias` | `bugonia_correspondencias.csv` en `--corpus` |
| `--prev-fil CSV` | CSV anterior de `filomela_correspondencias` | `filomela_correspondencias.csv` en `--corpus` |
| `--prev-idx CSV` | CSV anterior de `bugonia_indices` | `bugonia_indices.csv` en `--corpus` |
| `--out DIR` | Directorio de salida | Directorio actual |

---

## Tablas generadas

### `bugonia_correspondencias.csv`

Una fila por cada palabra significativa (*PS*) del texto virgiliano en los
vv. 281–316 (episodio de la *bugonía*). Columnas:

| Columna | Contenido |
|---|---|
| `verso` | Número de verso virgiliano |
| `vsid` | `@xml:id` del `<seg>` en `V_G04.xml` |
| `latin` | Texto de la palabra latina |
| `AB`, `AEP`, … `RBN` | Anotación de cada traducción (véase tabla de valores) |

**Valores de anotación:**

| Valor | Significado |
|---|---|
| `∅` | Reproducción fiel (sin desviación) |
| `sem` | Sustitución semántica (campo comparable) |
| `semd` | Sustitución semántica que reduce extensión |
| `sema` | Sustitución semántica que amplía extensión |
| `sint` | Cambio morfosintáctico |
| `met` | Sustitución metonímica |
| `rep` | Repetición de un término ya presente |
| `sem+sint` | Combinación de desviaciones (separadas por `+`) |
| `OM` | Omisión |

### `bugonia_indices.csv`

Una fila por traducción, ordenada de mayor a menor *I*°e. Columnas:

| Columna | Contenido |
|---|---|
| `siglum` | Sigla de la traducción |
| `PSo` | Total de palabras significativas en el original (= 187) |
| `PSt` | Total de palabras significativas en la traducción (**manual**) |
| `REt` | Palabras reproducidas (*PS*o − *PO*t) |
| `PAt` | Adiciones (**manual**) |
| `POt` | Omisiones (calculado desde el XML) |
| `Ie` | Índice de exactitud = *RE*t / *PS*o × 100 |
| `Il` | Índice de libertad = *PA*t / *PS*t × 100 (**manual**) |

> **Nota:** Las celdas marcadas como **manual** (`PSt`, `PAt`, `Il`) requieren
> contar las palabras significativas de la traducción aplicando los mismos
> criterios que se usaron en el análisis original (sustantivos, verbos, adjetivos
> y adverbios; sin pronombres ni auxiliares). El script conserva estos valores
> del CSV anterior sin modificarlos.

### `filomela_correspondencias.csv`

Tabla en formato largo (una fila por entrada léxica), con cuatro listas por
siglum: `PSºt` (palabras de la traducción), `REºt` (reproducciones con su
correlato latino y tipo de correspondencia), `PAºt` (adiciones) y `POºt`
(omisiones). Columnas:

| Columna | Contenido |
|---|---|
| `siglum` | Sigla de la traducción |
| `lista` | `PSºt`, `REºt`, `PAºt` o `POºt` |
| `palabra_traduccion` | Palabra de la traducción |
| `correlato_latino` | Palabra latina correspondiente (solo en `REºt` y `POºt`) |
| `tipo` | Tipo de correspondencia (mismos valores que en `bugonia_correspondencias`) |

---

## Lógica de anotación

Para cada `<seg>` del texto virgiliano, el script busca en cada traducción la
anotación correspondiente siguiendo este orden de prioridad:

1. **Anotación explícita por `@source`:** si un `<seg>` de la traducción tiene
   `@source="#id"` apuntando al `@xml:id` de la palabra virgiliana, se usa el
   valor de `@ana` como etiqueta (`∅` si está vacío).

2. **Omisión explícita:** si un `<gap @ana="#om">` tiene `@source="#id"`, la
   palabra se registra como `OM`.

3. **Fallback al CSV anterior:** si no hay anotación explícita en el XML, se
   conserva el valor que tenía esa celda en el CSV anterior. Esto es necesario
   porque muchos `<seg>` del corpus no tienen `@source` individual: su
   correspondencia con el original queda implícita en el `@corresp` de la línea.

4. **`∅` por defecto:** si no hay ni anotación explícita ni valor previo, se
   asigna `∅`.

**Consecuencia práctica:** cuando se añaden o corrigen anotaciones en los XML
con `@source` explícita, el script las recoge automáticamente. Las celdas que
dependen del fallback solo cambian si se edita manualmente el CSV anterior o si
se añade `@source` al XML correspondiente.

---

## Flujo de trabajo recomendado al actualizar el corpus

1. Editar los XML (`*_G04.xml`) añadiendo o corrigiendo `@ana`, `@source` y
   `@orig` en `<seg>` y `<gap>`.
2. Ejecutar el script apuntando a los CSV actuales como fallback:
   ```bash
   python generar_tablas.py --corpus ./corpus --out ./tablas_nuevas
   ```
3. Revisar el resumen impreso en consola (índices *I*°e por siglum).
4. Abrir `bugonia_correspondencias.csv` y verificar las celdas que hayan
   cambiado respecto a la versión anterior.
5. Actualizar manualmente `PSt`, `PAt` e `Il` en `bugonia_indices.csv` si se
   han añadido o eliminado adiciones en las traducciones.
6. Reemplazar los CSV de referencia con los nuevos para la siguiente iteración.

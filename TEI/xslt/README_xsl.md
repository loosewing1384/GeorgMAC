# Hojas de transformación XSL del corpus *Geórgicas* IV

Este directorio contiene cinco hojas de estilo XSLT 3.0 para el análisis y la
visualización del corpus TEI-XML. Todas toman como entrada uno de los archivos
`*_G04.xml` del corpus y producen texto plano, XML o LaTeX según el caso.

---

## Visión de conjunto

| Archivo | Entrada | Salida | Función |
|---|---|---|---|
| `analysetext.xsl` | `*_G04.xml` | texto plano | Estadísticas descriptivas de `@cert` en `<seg>` y `<gap>` |
| `calculate_cert_l.xsl` | `*_G04.xml` | XML TEI | Calcula y escribe el `@cert` de cada `<l>` a partir de sus segmentos |
| `l-certainty.xsl` | `*_G04.xml` | `.tex` | Grilla de cuadrados de color por verso (nivel `<l>`) |
| `seg-certainty.xsl` | `*_G04.xml` | `.tex` | Grilla de cuadrados de color por segmento (nivel `<seg>`/`<gap>`) |
| `typesettext.xsl` | `*_G04.xml` | `.tex` | Texto de la traducción con corchetes de color bajo cada segmento |

Las hojas `l-certainty.xsl`, `seg-certainty.xsl` y `typesettext.xsl` producen
archivos LaTeX que requieren el archivo `preamble.tex` para compilarse.

---

## Escala de `@cert`

Los tres niveles de certeza se mapean a valores numéricos internamente:

| Valor | Numérico | Color LaTeX |
|---|---|---|
| `high` | 3 | verde |
| `medium` | 2 | naranja |
| `low` | 1 | rojo |

---

## Descripción detallada

### `analysetext.xsl`

Extrae todos los elementos `<seg>` y `<gap>` que tienen `@cert` y calcula:
n, promedio, desviación estándar, varianza, y distribución de frecuencias
(n y % de cada nivel). La salida es texto plano con el nombre del traductor
y la fecha extraídos del `<teiHeader>`.

**Ejemplo de salida:**
```
Traducción de Miguel Antonio Caro (1873)

Estadísticas para los elementos <seg> y <gap> con atributos @cert:

Número de elementos: 161
Promedio:            2.478
Desviación estándar: 0.612
Varianza:            0.375

Distribución de frecuencias:
  high:   112  (69.6%)
  medium:  38  (23.6%)
  low:     11  (6.8%)
```

---

### `calculate_cert_l.xsl`

Transforma el XML fuente añadiendo o corrigiendo el atributo `@cert` en cada
elemento `<l>`. El valor se calcula como la media aritmética de los `@cert`
de todos los `<seg>` y `<gap>` hijos directos, convertida a categoría según
estos umbrales:

| Rango del promedio | `@cert` resultante |
|---|---|
| < 1.67 | `low` |
| ≥ 1.67 y < 2.34 | `medium` |
| ≥ 2.34 | `high` |

El resto del documento se copia sin cambios (transformación identidad con
`xsl:mode on-no-match="shallow-copy"`). Esta hoja debe ejecutarse **antes**
de las tres hojas de visualización cuando los `@cert` de `<l>` no estén al día.

---

### `l-certainty.xsl`

Produce un archivo LaTeX con una grilla compacta en la que cada verso (`<l>`)
se representa como un pequeño cuadrado de color según su `@cert`. Usa tres
macros LaTeX que deben estar definidas en `preamble.tex`:

```latex
\rectlow{}    % cuadrado rojo
\rectmed{}    % cuadrado naranja
\recthigh{}   % cuadrado verde
```

El resultado es una página con la grilla envuelta en un `minipage`, útil para
visualizar de un vistazo la distribución de certeza en todo el pasaje.

---

### `seg-certainty.xsl`

Produce una grilla similar a la de `l-certainty.xsl`, pero a resolución de
segmento: cada `<seg>` y `<gap>` genera un cuadrado de color. Los `<gap>`
se distinguen usando versiones más pálidas del color (`red!60!white`,
`orange!60!white`, `green!60!white`) y pueden mostrar su `@quantity`.
Requiere la macro `\recttext{color}{contenido}` en `preamble.tex`.

---

### `typesettext.xsl`

Produce el texto completo de la traducción en LaTeX. Para cada `<seg>`:

- Dibuja un corchete de color debajo del texto con `\bracebelow[color]{texto}`.
- Si el segmento tiene `@ana="#add"` (adición sin correlato latino), el texto
  se imprime en color carmesí con `\textcolor{Crimson}{...}`.

Para cada `<gap>` (omisión) usa `\circledtext{quantity}`.

Los números de verso aparecen como comentarios LaTeX (`%%%%%% v. 283 %%%%%%`)
y como notas marginales (`\sidepar{283}`) cada cinco versos o en versos
marcados con `@ana="#ln"`.

Requiere en `preamble.tex`:
```latex
\bracebelow[color]{texto}   % corchete de color bajo el texto
\circledtext{n}             % número encerrado en círculo (omisiones)
\sidepar{n}                 % número marginal de verso
```

---

## Uso

Las hojas requieren un procesador XSLT 3.0. Se recomienda
[Saxon-HE](https://www.saxonica.com/download/open-source.xml)
(descarga gratuita) o el comando `xslt3` de la distribución `xslt30` de npm.

### Con Saxon (Java)

```bash
# Estadísticas de una traducción
java -jar saxon-he.jar -xsl:analysetext.xsl -s:MAC_G04.xml

# Calcular @cert en <l> y guardar nuevo XML
java -jar saxon-he.jar -xsl:calculate_cert_l.xsl -s:MAC_G04.xml -o:MAC_G04_cert.xml

# Grilla de versos
java -jar saxon-he.jar -xsl:l-certainty.xsl -s:MAC_G04_cert.xml -o:l-certainty-MAC.tex

# Grilla de segmentos
java -jar saxon-he.jar -xsl:seg-certainty.xsl -s:MAC_G04_cert.xml -o:seg-certainty-MAC.tex

# Texto con corchetes
java -jar saxon-he.jar -xsl:typesettext.xsl -s:MAC_G04_cert.xml -o:typesettext-MAC.tex
```

### Con `xslt3` (npm / Node.js)

```bash
npm install -g xslt3

xslt3 -xsl:analysetext.xsl -s:MAC_G04.xml
xslt3 -xsl:calculate_cert_l.xsl -s:MAC_G04.xml -o:MAC_G04_cert.xml
xslt3 -xsl:l-certainty.xsl    -s:MAC_G04_cert.xml -o:l-certainty-MAC.tex
xslt3 -xsl:seg-certainty.xsl  -s:MAC_G04_cert.xml -o:seg-certainty-MAC.tex
xslt3 -xsl:typesettext.xsl    -s:MAC_G04_cert.xml -o:typesettext-MAC.tex
```

### Flujo de trabajo recomendado

```
*_G04.xml
    │
    ├─[calculate_cert_l.xsl]──→ *_G04_cert.xml
    │                                │
    │                    ┌───────────┼───────────────┐
    │                    ↓           ↓               ↓
    │             l-certainty   seg-certainty   typesettext
    │              .tex             .tex            .tex
    │                    └───────────┴───────────────┘
    │                                │
    │                    [pdflatex / lualatex]
    │                                │
    │                               .pdf
    │
    └─[analysetext.xsl]──→ estadísticas (stdout)
```

---

## Créditos

Nicolás Vaughan · Universidad de los Andes, Bogotá · <n.vaughan@uniandes.edu.co>

Proyecto PAPIIT IA401025 «Modernidad iberoamericana de las *Geórgicas* virgilianas»,
Instituto de Investigaciones Filológicas, UNAM.

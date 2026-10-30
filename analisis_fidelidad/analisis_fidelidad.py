"""
analisis_fidelidad.py
─────────────────────
Análisis cuantitativo de fidelidad de traducciones de las Geórgicas de Virgilio.
Produce tres salidas:
  1. Tabla de estadísticas descriptivas por traducción (stdout + CSV)
  2. Mapa de calor: versos × traducciones
  3. Perfil de fidelidad verso a verso (gráfico de líneas)

Fuente: corpus TEI-XML anotado con @cert (low / medium / high) en <l>, <seg> y <gap>.
Autor: Nicolás Vaughan
"""

import re
import statistics
from pathlib import Path
from lxml import etree
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
import seaborn as sns

# ─── Configuración ──────────────────────────────────────────────────────────

# Directorios con los XML del corpus
DIR_PROYECTO = Path("TEI/")
DIR_UPLOADS  = Path("TEI/")

# Sigla → (directorio, archivo)
TRADUCCIONES = {
    "MAC": (DIR_UPLOADS,  "MAC_G04.xml"),
    "AEP": (DIR_UPLOADS,  "AEP_G04.xml"),
    "JL":  (DIR_UPLOADS,  "JL_G04.xml"),
    "NPC": (DIR_UPLOADS,  "NPC_G04.xml"),
    "PF":  (DIR_UPLOADS,  "PF_G04.xml"),
    "RBN": (DIR_UPLOADS, "RBN_G04.xml"),
    "AB":  (DIR_UPLOADS,  "AB_G04.xml"),
    "LLA": (DIR_UPLOADS,  "LLA_G04.xml"),
}

# Pasajes del corpus
BUGONIA    = list(range(281, 317))   # vv. 281–316
FILOMENA   = list(range(511, 516))   # vv. 511–515
VERSOS_CORPUS = set(BUGONIA + FILOMENA)

# Mapeo categórico → numérico
CERT_NUM = {"low": 1, "medium": 2, "high": 3}

# Namespace TEI
NS = {"tei": "http://www.tei-c.org/ns/1.0"}

# Paleta de colores para las líneas del gráfico
COLORES = {
    "MAC": "#1b6ca8",
    "AEP": "#e07b39",
    "JL":  "#2e8b57",
    "NPC": "#9b2335",
    "PF":  "#7b5ea7",
    "RBN": "#5c5c5c",
    "AB":  "#c0873f",
    "LLA": "#3a7d8c",
}

# ─── Funciones de extracción ─────────────────────────────────────────────────

def extraer_numero_verso(corresp: str) -> list[int]:
    """
    Extrae los números de verso de un atributo @corresp.
    Maneja casos como "283", "282 283", "283 4.284".
    Devuelve solo los enteros puros dentro del rango del corpus.
    """
    numeros = []
    for token in corresp.split():
        # Quita prefijos tipo "4." y toma solo dígitos
        token_limpio = re.sub(r"^\d+\.", "", token)
        if token_limpio.isdigit():
            numeros.append(int(token_limpio))
    return numeros


def leer_xml(ruta: Path):
    """Parsea un XML TEI ignorando las instrucciones de procesamiento."""
    parser = etree.XMLParser(remove_comments=False, recover=True)
    return etree.parse(str(ruta), parser)


def extraer_cert_por_verso(sigla: str) -> dict[int, list[int]]:
    """
    Lee el XML de una traducción y devuelve un diccionario
    {verso: [valores_numéricos_de_cert]}
    Solo incluye versos del corpus con @corresp numérico.
    """
    directorio, archivo = TRADUCCIONES[sigla]; ruta = directorio / archivo
    tree = leer_xml(ruta)

    verso_cert: dict[int, list[int]] = {v: [] for v in VERSOS_CORPUS}

    for l in tree.findall(".//tei:l", NS):
        corresp = l.get("corresp", "")
        cert_str = l.get("cert", "")
        if not cert_str or cert_str not in CERT_NUM:
            continue
        numeros = extraer_numero_verso(corresp)
        valor = CERT_NUM[cert_str]
        for n in numeros:
            if n in verso_cert:
                verso_cert[n].append(valor)

    return verso_cert


def extraer_cert_segmentos(sigla: str) -> list[int]:
    """
    Lee el XML y devuelve la lista de valores numéricos de @cert
    de todos los <seg> y <gap> dentro de <l> con @corresp numérico en el corpus.
    Usado para las estadísticas descriptivas.
    """
    directorio, archivo = TRADUCCIONES[sigla]; ruta = directorio / archivo
    tree = leer_xml(ruta)
    valores = []

    for l in tree.findall(".//tei:l", NS):
        corresp = l.get("corresp", "")
        numeros = extraer_numero_verso(corresp)
        if not any(n in VERSOS_CORPUS for n in numeros):
            continue
        for elem in l.findall("tei:seg", NS) + l.findall("tei:gap", NS):
            cert_str = elem.get("cert", "")
            if cert_str in CERT_NUM:
                valores.append(CERT_NUM[cert_str])

    return valores


# ─── Construcción del DataFrame principal ───────────────────────────────────

def construir_dataframe() -> pd.DataFrame:
    """
    Construye un DataFrame con forma (versos × traducciones).
    Cada celda es el promedio de los @cert de los <l> que cubren ese verso.
    Si no hay datos para un verso, la celda es NaN.
    """
    data = {}
    for sigla in TRADUCCIONES:
        verso_cert = extraer_cert_por_verso(sigla)
        col = {}
        for verso, valores in verso_cert.items():
            col[verso] = round(sum(valores) / len(valores), 3) if valores else float("nan")
        data[sigla] = col

    df = pd.DataFrame(data, index=BUGONIA + FILOMENA)
    df.index.name = "Verso"
    return df


# ─── 1. Estadísticas descriptivas ───────────────────────────────────────────

def estadisticas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula estadísticas descriptivas a nivel de segmento (no de verso)
    para cada traducción: n, media, DE, varianza, y distribución de frecuencias
    (n y % de high, medium, low).
    """
    filas = []
    for sigla in TRADUCCIONES:
        vals = extraer_cert_segmentos(sigla)
        if not vals:
            continue
        n      = len(vals)
        n_high = vals.count(3)
        n_med  = vals.count(2)
        n_low  = vals.count(1)
        filas.append({
            "Traducción":  sigla,
            "n":           n,
            "Media":       round(statistics.mean(vals), 3),
            "DE":          round(statistics.stdev(vals), 3) if n > 1 else 0.0,
            "Varianza":    round(statistics.variance(vals), 3) if n > 1 else 0.0,
            "high (n)":    n_high,
            "high (%)":    round(n_high / n * 100, 1),
            "medium (n)":  n_med,
            "medium (%)":  round(n_med  / n * 100, 1),
            "low (n)":     n_low,
            "low (%)":     round(n_low  / n * 100, 1),
        })
    return pd.DataFrame(filas).set_index("Traducción")


# ─── 2. Mapa de calor ───────────────────────────────────────────────────────

def _heatmap_panel(datos: pd.DataFrame, titulo: str, ax, mostrar_ylabel: bool):
    """Dibuja un panel de heatmap en el eje dado."""
    cmap_continuo = mcolors.LinearSegmentedColormap.from_list(
        "cert", ["#c0392b", "#e67e22", "#27ae60"]
    )
    opciones = dict(
        cmap=cmap_continuo,
        vmin=1, vmax=3,
        linewidths=0.4,
        linecolor="#cccccc",
        square=True,
        cbar=False,
        annot=False,
        mask=datos.isna(),
    )
    sns.heatmap(datos, ax=ax, **opciones)
    ax.set_title(titulo, fontsize=11, fontweight="bold", pad=6)
    ax.set_xlabel("Verso", fontsize=9)
    ax.set_ylabel("")
    ax.tick_params(axis="x", labelsize=7, rotation=90)
    if mostrar_ylabel:
        ax.tick_params(axis="y", labelsize=9, rotation=0)
    else:
        ax.tick_params(axis="y", labelleft=False, left=False)


def _leyenda_heatmap(fig):
    leyenda = [
        mpatches.Patch(color="#c0392b", label="low"),
        mpatches.Patch(color="#e67e22", label="medium"),
        mpatches.Patch(color="#27ae60", label="high"),
        mpatches.Patch(color="#e8e8e8", label="sin dato"),
    ]
    fig.legend(handles=leyenda, loc="lower center", ncol=4,
               fontsize=9, frameon=False, bbox_to_anchor=(0.5, -0.18))


def grafico_heatmap_bugonia(df: pd.DataFrame, ruta_salida: Path):
    """Heatmap del episodio de la bugonía (vv. 281–316)."""
    datos = df.loc[BUGONIA].T.sort_index()
    fig, ax = plt.subplots(figsize=(14, 4))
    _heatmap_panel(datos, "Bugonía (vv. 281–316)", ax, mostrar_ylabel=True)
    _leyenda_heatmap(fig)
    fig.suptitle("Fidelidad por verso y traducción (@cert del ⟨l⟩)",
                 fontsize=12, fontweight="bold", y=1.04)
    plt.savefig(ruta_salida, format="svg", bbox_inches="tight")
    plt.close()
    print(f"  → Heatmap (bugonía) guardado en {ruta_salida}")


def grafico_heatmap_filomena(df: pd.DataFrame, ruta_salida: Path):
    """Heatmap del símil de Filomena (vv. 511–515)."""
    datos = df.loc[FILOMENA].T.sort_index()
    fig, ax = plt.subplots(figsize=(4, 4))
    _heatmap_panel(datos, "Símil de Filomena (vv. 511–515)", ax, mostrar_ylabel=True)
    _leyenda_heatmap(fig)
    fig.suptitle("Fidelidad por verso y traducción (@cert del ⟨l⟩)",
                 fontsize=12, fontweight="bold", y=1.04)
    plt.savefig(ruta_salida, format="svg", bbox_inches="tight")
    plt.close()
    print(f"  → Heatmap (Filomena) guardado en {ruta_salida}")


# ─── 3. Perfil verso a verso (líneas) ───────────────────────────────────────

def _lineas_panel(ax, datos: pd.DataFrame, versos: list, titulo: str,
                  mostrar_leyenda: bool, markersize: float):
    """Dibuja un panel de líneas en el eje dado."""
    for sigla in TRADUCCIONES:
        ax.plot(
            datos.index,
            datos[sigla],
            marker="o", markersize=markersize,
            linewidth=1.3, color=COLORES[sigla], label=sigla,
            alpha=0.85,
        )
    ax.set_title(titulo, fontsize=11, fontweight="bold")
    ax.set_xlim(versos[0] - 0.5, versos[-1] + 0.5)
    ax.set_ylim(0.7, 3.3)
    ax.set_yticks([1, 2, 3])
    ax.set_yticklabels(["low", "medium", "high"], fontsize=9)
    ax.set_xlabel("Verso", fontsize=9)
    ax.set_xticks(versos[::5] if len(versos) > 10 else versos)
    ax.tick_params(axis="x", labelsize=8)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.grid(axis="x", linestyle=":", alpha=0.25)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.axhspan(0.7, 1.5, alpha=0.06, color="#c0392b", zorder=0)
    ax.axhspan(1.5, 2.5, alpha=0.06, color="#e67e22", zorder=0)
    ax.axhspan(2.5, 3.3, alpha=0.06, color="#27ae60", zorder=0)
    if mostrar_leyenda:
        ax.legend(loc="lower right", fontsize=8.5,
                  framealpha=0.85, edgecolor="#cccccc")


def grafico_lineas_bugonia(df: pd.DataFrame, ruta_salida: Path):
    """Gráfico de líneas del episodio de la bugonía (vv. 281–316)."""
    fig, ax = plt.subplots(figsize=(12, 5))
    _lineas_panel(ax, df.loc[BUGONIA], BUGONIA,
                  "Perfil de fidelidad — Bugonía (vv. 281–316)",
                  mostrar_leyenda=True, markersize=3.5)
    plt.tight_layout()
    plt.savefig(ruta_salida, format="svg", bbox_inches="tight")
    plt.close()
    print(f"  → Líneas (bugonía) guardado en {ruta_salida}")


def grafico_lineas_filomena(df: pd.DataFrame, ruta_salida: Path):
    """Gráfico de líneas del símil de Filomena (vv. 511–515)."""
    fig, ax = plt.subplots(figsize=(6, 5))
    _lineas_panel(ax, df.loc[FILOMENA], FILOMENA,
                  "Perfil de fidelidad — Símil de Filomena (vv. 511–515)",
                  mostrar_leyenda=True, markersize=5)
    plt.tight_layout()
    plt.savefig(ruta_salida, format="svg", bbox_inches="tight")
    plt.close()
    print(f"  → Líneas (Filomena) guardado en {ruta_salida}")


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    print("Construyendo datos…")
    df = construir_dataframe()

    # 1. Estadísticas
    print("\n── Estadísticas descriptivas (nivel de segmento) ──")
    stats = estadisticas(df)
    print(stats.to_string())
    stats.to_csv("output/estadisticas.csv")
    print("\n  → Estadísticas guardadas en estadisticas.csv")

    # 2. Heatmaps
    print("\nGenerando mapas de calor…")
    grafico_heatmap_bugonia(df, Path("output/heatmap_bugonia.svg"))
    grafico_heatmap_filomena(df, Path("output/heatmap_filomena.svg"))

    # 3. Líneas
    print("Generando gráficos de líneas…")
    grafico_lineas_bugonia(df, Path("output/lineas_bugonia.svg"))
    grafico_lineas_filomena(df, Path("output/lineas_filomena.svg"))

    print("\nListo.")


if __name__ == "__main__":
    main()

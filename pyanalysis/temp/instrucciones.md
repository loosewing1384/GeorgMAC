# Instrucciones para recrear los gráficos de fidelidad

## 1. Instalar Python

Si no tienes Python instalado, la forma más sencilla es instalar
[Anaconda](https://www.anaconda.com/download) o
[Miniconda](https://docs.anaconda.com/miniconda/).

## 2. Instalar las bibliotecas necesarias

Abre una terminal y ejecuta:

```bash
pip install lxml matplotlib seaborn pandas
```

## 3. Configurar las rutas en el script

Abre `analisis_fidelidad.py` y localiza estas líneas cerca del principio:

```python
DIR_PROYECTO = Path("/mnt/project")
DIR_UPLOADS  = Path("/mnt/user-data/uploads")
```

Cámbialas por la carpeta donde tengas tus XML, por ejemplo:

```python
DIR_PROYECTO = Path("/Users/nicolas/corpus")
DIR_UPLOADS  = Path("/Users/nicolas/corpus")
```

Si todos los XML están en la misma carpeta, actualiza también el
diccionario `TRADUCCIONES` para que todos apunten al mismo directorio:

```python
TRADUCCIONES = {
    "MAC": (DIR_PROYECTO, "MAC_G04.xml"),
    "AEP": (DIR_PROYECTO, "AEP_G04.xml"),
    "JL":  (DIR_PROYECTO, "JL_G04.xml"),
    "NPC": (DIR_PROYECTO, "NPC_G04.xml"),
    "PF":  (DIR_PROYECTO, "PF_G04.xml"),
    "RBN": (DIR_PROYECTO, "RBN_G04.xml"),
    "AB":  (DIR_PROYECTO, "AB_G04.xml"),
    "LLA": (DIR_PROYECTO, "LLA_G04.xml"),
}
```

## 4. Configurar la carpeta de salida

Localiza la función `main()` al final del script y edita las rutas de salida:

```python
stats.to_csv("/mnt/user-data/outputs/estadisticas.csv")
grafico_heatmap(df, Path("/mnt/user-data/outputs/heatmap.svg"))
grafico_lineas(df, Path("/mnt/user-data/outputs/lineas.svg"))
```

Cámbialas por la carpeta donde quieras guardar los resultados, por ejemplo:

```python
stats.to_csv("/Users/nicolas/resultados/estadisticas.csv")
grafico_heatmap(df, Path("/Users/nicolas/resultados/heatmap.svg"))
grafico_lineas(df, Path("/Users/nicolas/resultados/lineas.svg"))
```

## 5. Ejecutar el script

Con la terminal abierta en la carpeta donde guardaste `analisis_fidelidad.py`, ejecuta:

```bash
python analisis_fidelidad.py
```

## Resultados

El script produce tres archivos:

| Archivo | Contenido |
|---------|-----------|
| `heatmap.svg` | Mapa de calor: versos × traducciones |
| `lineas.svg` | Perfil de fidelidad verso a verso |
| `estadisticas.csv` | Tabla de estadísticas descriptivas por traducción |

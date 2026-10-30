#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_tablas.py
=================
Genera las tres tablas CSV del corpus Geórgicas IV a partir de los archivos TEI-XML:

    bugonia_correspondencias.csv   — anotación por palabra latina × traducción (vv. 281-316)
    bugonia_indices.csv            — índices gasparovianos para los ocho testimonios (vv. 281-316)
    filomela_correspondencias.csv  — anotación por palabra latina × traducción (vv. 511-515)

Uso
---
    python generar_tablas.py [--corpus DIR] [--prev-bug CSV] [--prev-fil CSV]

Argumentos opcionales:
    --corpus DIR      Directorio que contiene los XML (por defecto: el directorio del script)
    --prev-bug CSV    CSV anterior de bugonía_correspondencias (para conservar celdas sin
                      anotación explícita en el XML). Por defecto: bugonia_correspondencias.csv
                      en el directorio del script.
    --prev-fil CSV    CSV anterior de filomela_correspondencias (misma lógica).
                      Por defecto: filomela_correspondencias.csv en el directorio del script.

Archivos XML esperados en el directorio del corpus:
    V_G04.xml          Texto fuente virgiliano anotado
    AB_G04.xml         Bekes
    AEP_G04.xml        Espinosa Pólit
    JL_G04.xml         Lembke
    LLA_G04.xml        López Álvarez
    MAC_G04.xml        Caro
    NPC_G04.xml        Pérez del Camino
    PF_G04.xml         Fallon
    RBN_G04.xml        Bonifaz Nuño

Lógica de anotación
-------------------
Para cada palabra significativa del texto virgiliano (cada <seg> en V_G04.xml),
el script busca en cada traducción:

  1. Correspondencia EXPLÍCITA: un <seg> con @source apuntando al xmlid de la
     palabra virgiliana → la anotación es el valor limpio de @ana
     (∅ si @ana está vacío o ausente, sem/semd/sema/sint/met/rep según corresponda).

  2. Omisión EXPLÍCITA: un <gap ana="#om"> con @source apuntando al xmlid de la
     palabra → la anotación es OM.

  3. FALLBACK al CSV anterior: si no hay anotación explícita en el XML, se conserva
     el valor del CSV anterior (si existe). Esto preserva las correspondencias
     implícitas que no tienen @source en el XML.

  4. ∅ por defecto: si no hay ni anotación explícita ni valor previo, se asigna ∅.

Los valores PSt, PAt e Il del CSV de índices NO se recalculan aquí porque requieren
contar las palabras de la traducción —tarea que depende de criterios editoriales
que deben aplicarse manualmente. Se conservan del CSV anterior.

Autor: Nicolás Vaughan <n.vaughan@uniandes.edu.co>
"""

import argparse
import csv
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict

# ── Constantes ────────────────────────────────────────────────────────────────

NS    = 'http://www.tei-c.org/ns/1.0'
XMLID = '{http://www.w3.org/XML/1998/namespace}id'

SIGLA = ['AB', 'AEP', 'JL', 'LLA', 'MAC', 'NPC', 'PF', 'RBN']

BUGONIA  = set(range(281, 317))   # vv. 281-316 inclusive
FILOMELA = set(range(511, 516))   # vv. 511-515 inclusive

# Etiquetas de desviación reconocidas en @ana
DEVIATION_TAGS = {'sem', 'semd', 'sema', 'sint', 'met', 'rep'}

# Normalización de formas latinas: en V_G04.xml algunos <seg> agrupan
# dos palabras que el CSV trata por separado (ej. "sub umbra" → "umbra")
# y hay variantes ortográficas entre versiones del XML.
LATIN_NORM = {
    'sub umbra': 'umbra',
    'implumes':  'implumis',
    'observans': 'obseruans',
}

# ── Funciones de parseo ───────────────────────────────────────────────────────

def parse_verses(verse_str):
    """Devuelve un conjunto de enteros a partir de una cadena como '282 283'."""
    nums = set()
    for part in re.split(r'\s+', verse_str or ''):
        try:
            nums.add(int(part))
        except ValueError:
            pass
    return nums


def parse_source_ids(source_str, valid_ids):
    """
    Devuelve el conjunto de xmlids referenciados en @source que existen
    en valid_ids. Elimina el '#' inicial si lo hubiera.
    """
    ids = set()
    for ref in re.split(r'\s+', source_str or ''):
        ref = ref.lstrip('#')
        if ref in valid_ids:
            ids.add(ref)
    return ids


def ana_label(ana_str):
    """
    Convierte el contenido de @ana en una etiqueta legible.
    Ejemplos:
        ''              → '∅'
        '#sem'          → 'sem'
        '#sem #sint'    → 'sem+sint'
        '#add'          → 'add'   (solo se usa internamente; no se escribe en la tabla)
    """
    tags = []
    for token in re.split(r'\s+', ana_str or ''):
        t = token.lstrip('#')
        if t in DEVIATION_TAGS:
            tags.append(t)
    if not tags:
        return '∅'
    return '+'.join(sorted(set(tags)))


def parse_virgil(v_path, verse_range):
    """
    Extrae todas las palabras significativas del texto virgiliano
    para el rango de versos indicado.

    Devuelve una lista de dicts:
        {'verse': int, 'id': str, 'latin': str}
    en el orden en que aparecen en el XML.
    """
    tree = ET.parse(v_path)
    words = []
    for lelem in tree.getroot().iter(f'{{{NS}}}l'):
        n_str = lelem.get('n', '')
        try:
            n = int(n_str)
        except ValueError:
            continue
        if n not in verse_range:
            continue
        for seg in lelem.findall(f'{{{NS}}}seg'):
            xid = seg.get(XMLID)
            txt = ''.join(seg.itertext()).strip()
            if xid:
                words.append({'verse': n, 'id': xid, 'latin': txt})
    return words


def build_explicit_annotations(trans_path, valid_ids, verse_range):
    """
    Recorre la traducción y devuelve un dict {xmlid: etiqueta}
    con SÓLO las anotaciones explícitas (las que tienen @source).

    Reglas:
    - <seg @source="#id" @ana=""> → id: '∅'
    - <seg @source="#id" @ana="#sem"> → id: 'sem'
    - <seg @source="#id" @ana="#add"> → se ignora (es adición, no reproducción)
    - <gap @ana="#om" @source="#id"> → id: 'OM'
    """
    tree = ET.parse(trans_path)
    root = tree.getroot()
    result = {}

    for lelem in root.iter(f'{{{NS}}}l'):
        corresp_raw = lelem.get('corresp', '')
        verse_nums  = parse_verses(corresp_raw)
        if not (verse_nums & verse_range):
            continue

        # Segs (reproducciones)
        for seg in lelem.findall(f'{{{NS}}}seg'):
            ana   = (seg.get('ana') or '').strip()
            ssrc  = (seg.get('source') or '').strip()
            src_ids = parse_source_ids(ssrc, valid_ids)

            if not src_ids:
                continue          # sin @source, no podemos asignar
            if '#add' in ana:
                continue          # adición: no corresponde a ninguna palabra latina

            label = ana_label(ana)
            for sid in src_ids:
                result[sid] = label

        # Gaps (omisiones)
        for gap in lelem.findall(f'{{{NS}}}gap'):
            ana   = (gap.get('ana') or '').strip()
            ssrc  = (gap.get('source') or '').strip()
            src_ids = parse_source_ids(ssrc, valid_ids)

            if '#om' in ana:
                for sid in src_ids:
                    result[sid] = 'OM'

    return result


# ── Tabla de correspondencias de la bugonía ───────────────────────────────────

def build_bugonia_correspondencias(corpus_dir, prev_bug_path):
    """
    Genera el CSV bugonia_correspondencias.csv.

    Columnas: verso, vsid, latin, AB, AEP, JL, LLA, MAC, NPC, PF, RBN
    """
    v_path = os.path.join(corpus_dir, 'V_G04.xml')
    vwords = parse_virgil(v_path, BUGONIA)
    valid_ids = {w['id'] for w in vwords}

    # Cargar CSV anterior como base
    prev = {}
    if prev_bug_path and os.path.isfile(prev_bug_path):
        with open(prev_bug_path, newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                prev[row['vsid']] = {s: row.get(s, '∅') for s in SIGLA}

    # Baseline: del CSV anterior o ∅
    table = {}
    for w in vwords:
        table[w['id']] = dict(prev.get(w['id'], {s: '∅' for s in SIGLA}))

    # Overlay: anotaciones explícitas del XML
    for s in SIGLA:
        trans_path = os.path.join(corpus_dir, f'{s}_G04.xml')
        explicit = build_explicit_annotations(trans_path, valid_ids, BUGONIA)
        for vid, ann in explicit.items():
            table[vid][s] = ann

    rows = []
    for w in vwords:
        row = {'verso': w['verse'], 'vsid': w['id'], 'latin': w['latin']}
        row.update(table[w['id']])
        rows.append(row)

    return rows, vwords, table


# ── Índices gasparovianos ─────────────────────────────────────────────────────

def compute_indices(table, vwords, prev_indices_path):
    """
    Calcula PSo, REt, POt, Ie para cada siglum.
    PSt, PAt, Il se conservan del CSV anterior (requieren conteo manual).
    """
    PSo = len(vwords)

    # Cargar valores previos de PSt, PAt, Il
    prev = {}
    if prev_indices_path and os.path.isfile(prev_indices_path):
        with open(prev_indices_path, newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                prev[row['siglum']] = row

    rows = []
    for s in SIGLA:
        POt = sum(1 for w in vwords if table[w['id']][s] == 'OM')
        REt = PSo - POt
        Ie  = round(REt / PSo * 100)

        old = prev.get(s, {})
        rows.append({
            'siglum': s,
            'PSo':    PSo,
            'PSt':    old.get('PSt', '—'),
            'REt':    REt,
            'PAt':    old.get('PAt', '—'),
            'POt':    POt,
            'Ie':     f'{Ie}%',
            'Il':     old.get('Il', '—'),
        })

    # Ordenar por Ie descendente
    rows.sort(key=lambda r: -int(r['Ie'].rstrip('%')))
    return rows


# ── Tabla de correspondencias de la filomela ──────────────────────────────────

def build_filomela_correspondencias(corpus_dir, prev_fil_path):
    """
    Genera el CSV filomela_correspondencias.csv.

    Mantiene el formato del CSV anterior (filas por palabra de la traducción,
    con listas PSºt / REºt / PAºt / POºt) y actualiza las anotaciones
    mediante las anotaciones explícitas del XML.

    Para AEP, que no estaba en el CSV anterior, genera entradas derivadas
    exclusivamente del XML.
    """
    v_path = os.path.join(corpus_dir, 'V_G04.xml')
    vwords = parse_virgil(v_path, FILOMELA)
    valid_ids = {w['id'] for w in vwords}

    # Mapa de normalización: texto latin → vsid
    def latin_key(txt):
        return LATIN_NORM.get(txt, txt)

    # Obtener anotaciones explícitas del XML para todos los sigla
    xml_ann = {}   # siglum → {vsid: label}
    for s in SIGLA:
        trans_path = os.path.join(corpus_dir, f'{s}_G04.xml')
        xml_ann[s] = build_explicit_annotations(trans_path, valid_ids, FILOMELA)

    # Cargar CSV anterior
    prev_rows = []
    if prev_fil_path and os.path.isfile(prev_fil_path):
        with open(prev_fil_path, newline='', encoding='utf-8') as f:
            prev_rows = list(csv.DictReader(f))

    # Construir mapa vsid←→latin_key para actualizar tipos
    vid_by_latin = {}
    for w in vwords:
        vid_by_latin[latin_key(w['latin'])] = w['id']

    # Actualizar filas REºt con anotaciones del XML
    updated_rows = []
    for row in prev_rows:
        row = dict(row)
        if row['lista'] == 'REºt' and row['correlato_latino']:
            lat  = row['correlato_latino'].strip()
            s    = row['siglum'].strip()
            vid  = vid_by_latin.get(lat)
            if vid and s in xml_ann and vid in xml_ann[s]:
                row['tipo'] = xml_ann[s][vid]
        elif row['lista'] == 'POºt' and row['correlato_latino']:
            lat = row['correlato_latino'].strip()
            s   = row['siglum'].strip()
            vid = vid_by_latin.get(lat)
            # Si el XML ya no lo marca como OM, eliminarlo (se mantiene como OM)
            # Para ser conservadores, mantenemos OM del CSV anterior a menos que
            # el XML lo marque explícitamente como ∅.
            if vid and s in xml_ann and vid in xml_ann[s]:
                if xml_ann[s][vid] != 'OM':
                    # El XML ahora tiene correspondencia: pasar a REºt en próxima revisión
                    row['tipo'] = xml_ann[s][vid]  # solo informativo
        updated_rows.append(row)

    # Añadir AEP si no estaba en el CSV anterior
    sigla_in_prev = {r['siglum'] for r in prev_rows}
    if 'AEP' not in sigla_in_prev:
        aep_ann = xml_ann.get('AEP', {})
        # PSºt
        for w in vwords:
            ann = aep_ann.get(w['id'], '∅')
            if ann != 'OM':
                updated_rows.append({
                    'siglum': 'AEP', 'lista': 'PSºt',
                    'palabra_traduccion': '(v. XML)',
                    'correlato_latino': '', 'tipo': '',
                })
        # REºt
        for w in vwords:
            ann = aep_ann.get(w['id'], '∅')
            if ann not in ('OM',):
                updated_rows.append({
                    'siglum': 'AEP', 'lista': 'REºt',
                    'palabra_traduccion': '(v. XML)',
                    'correlato_latino': latin_key(w['latin']),
                    'tipo': ann,
                })
        # POºt
        for w in vwords:
            ann = aep_ann.get(w['id'], '∅')
            if ann == 'OM':
                updated_rows.append({
                    'siglum': 'AEP', 'lista': 'POºt',
                    'palabra_traduccion': '',
                    'correlato_latino': latin_key(w['latin']),
                    'tipo': 'OM',
                })

    return updated_rows, vwords, xml_ann


# ── Escritura de CSVs ─────────────────────────────────────────────────────────

def write_bugonia_correspondencias(rows, out_path):
    fieldnames = ['verso', 'vsid', 'latin'] + SIGLA
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f'  → {out_path}')


def write_bugonia_indices(rows, out_path):
    fieldnames = ['siglum', 'PSo', 'PSt', 'REt', 'PAt', 'POt', 'Ie', 'Il']
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f'  → {out_path}')


def write_filomela_correspondencias(rows, out_path):
    fieldnames = ['siglum', 'lista', 'palabra_traduccion', 'correlato_latino', 'tipo']
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f'  → {out_path}')


# ── Estadísticas de resumen ───────────────────────────────────────────────────

def print_summary(idx_rows, fil_vwords, fil_xml_ann):
    print('\n  Bugonía — índices:')
    for r in idx_rows:
        print(f"    {r['siglum']:4s}  PSo={r['PSo']}  REt={r['REt']:3d}  "
              f"POt={r['POt']:2d}  Ie={r['Ie']:4s}  Il={r['Il']}")

    PSo_f = len(fil_vwords)
    print(f'\n  Filomela — Ie (PSo={PSo_f}):')
    fil_idx = []
    for s in SIGLA:
        POt = sum(1 for w in fil_vwords if fil_xml_ann.get(s, {}).get(w['id']) == 'OM')
        REt = PSo_f - POt
        fil_idx.append((s, REt, POt, round(REt/PSo_f*100)))
    for s, REt, POt, Ie in sorted(fil_idx, key=lambda x: -x[3]):
        print(f"    {s:4s}  REt={REt:2d}  POt={POt}  Ie={Ie}%")


# ── CLI ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Genera las tablas CSV del corpus Geórgicas IV.')
    parser.add_argument(
        '--corpus', default='.',
        help='Directorio con los archivos XML (por defecto: directorio actual)')
    parser.add_argument(
        '--prev-bug', default=None,
        help='CSV anterior de bugonía_correspondencias (fallback para celdas sin @source)')
    parser.add_argument(
        '--prev-fil', default=None,
        help='CSV anterior de filomela_correspondencias (fallback para celdas sin @source)')
    parser.add_argument(
        '--prev-idx', default=None,
        help='CSV anterior de bugonía_indices (para conservar PSt, PAt, Il)')
    parser.add_argument(
        '--out', default='.',
        help='Directorio de salida (por defecto: directorio actual)')
    args = parser.parse_args()

    corpus_dir = os.path.abspath(args.corpus)
    out_dir    = os.path.abspath(args.out)
    os.makedirs(out_dir, exist_ok=True)

    # Rutas de CSVs anteriores (fallback al directorio del corpus si no se especifican)
    def resolve(arg, filename):
        if arg:
            return os.path.abspath(arg)
        candidate = os.path.join(corpus_dir, filename)
        return candidate if os.path.isfile(candidate) else None

    prev_bug = resolve(args.prev_bug, 'bugonia_correspondencias.csv')
    prev_fil = resolve(args.prev_fil, 'filomela_correspondencias.csv')
    prev_idx = resolve(args.prev_idx, 'bugonia_indices.csv')

    print('Corpus:', corpus_dir)
    print('CSV anteriores:')
    print(f'  bugonía corr: {prev_bug or "(ninguno)"}')
    print(f'  filomela corr: {prev_fil or "(ninguno)"}')
    print(f'  índices:      {prev_idx or "(ninguno)"}')
    print()

    # ── Bugonía ──────────────────────────────────────────────────────────
    print('Generando bugonia_correspondencias.csv ...')
    bug_rows, vwords_bug, bug_table = build_bugonia_correspondencias(corpus_dir, prev_bug)
    write_bugonia_correspondencias(
        bug_rows, os.path.join(out_dir, 'bugonia_correspondencias.csv'))

    print('Generando bugonia_indices.csv ...')
    idx_rows = compute_indices(bug_table, vwords_bug, prev_idx)
    write_bugonia_indices(
        idx_rows, os.path.join(out_dir, 'bugonia_indices.csv'))

    # ── Filomela ─────────────────────────────────────────────────────────
    print('Generando filomela_correspondencias.csv ...')
    fil_rows, vwords_fil, fil_xml_ann = build_filomela_correspondencias(corpus_dir, prev_fil)
    write_filomela_correspondencias(
        fil_rows, os.path.join(out_dir, 'filomela_correspondencias.csv'))

    # ── Resumen ───────────────────────────────────────────────────────────
    print()
    print('Resumen de índices calculados:')
    print_summary(idx_rows, vwords_fil, fil_xml_ann)
    print('\nListo.')


if __name__ == '__main__':
    main()

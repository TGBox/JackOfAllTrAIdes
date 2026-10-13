# 🧰 JackOfAllTrAIdes

> **Kuratierte Skills für autonome Coding-Agenten.**  
> Minimiere Token-Verbrauch, schone das Kontextfenster und beschleunige Workflows mit Google Antigravity, Claude Code, Cursor, Codex und anderen KI-Entwicklungsagenten.

---

## 📖 Über dieses Repository

Große Sprachmodelle und autonome Coding-Agenten scheitern in der Praxis selten an mangelnder Intelligenz, sondern am **Kontext-Budget**:

- Ungefilterte Terminal-Dumps und Stacktraces fluten den Prompt mit Framework-Ballast.
- Repositories und Test-Datensätze (JSON/CSV/SQL mit tausenden Zeilen) sprengen das Token-Limit und verursachen Halluzinationen.
- Große Binär- oder Layout-Dateien (PDFs, DOCX, HTML, Notebooks) verschwenden bis zu 95 % ihrer Tokens an Styling und Metadaten.

**JackOfAllTrAIdes** bündelt spezialisierte, wiederverwendbare **Agent-Skills**. Jeder Skill folgt dem etablierten Skill-Standard (`SKILL.md` mit Metadaten und Anweisungen für den Agenten sowie optionalen, eigenständigen CLI-Skripten im `scripts/`-Ordner) und kann direkt in Coding-Umgebungen eingebunden oder standalone ausgeführt werden.

---

## 🗺️ Übersicht & Routing-Matrix

Wenn du dir nicht sicher bist, welcher Skill für ein Problem geeignet ist, nutze den **`token-usage-router`**.

| Skill | Zweck & Funktion | Skripte | Erwartete Ersparnis |
| :--- | :--- | :--- | :--- |
| [**`token-usage-router`**](#1-token-usage-router) | Zentraler Meta-Router für Kontext-Reduktion | *(Konzeptuell / Routing)* | — |
| [**`codebase-architecture-reporter`**](#2-codebase-architecture-reporter) | Erzeugt kompakte Architektur-Übersichten (`PROJECT_OVERVIEW.md`) | `generate_report.py` | **90 % – 99 %** |
| [**`python-code-skeletonizer`**](#3-python-code-skeletonizer) | Extrahiert AST-Skelette (Signaturen, Typen, Docstrings ohne Methodenrümpfe) | `skeletonize.py` | **60 % – 85 %** |
| [**`dependency-context-collector`**](#4-dependency-context-collector) | Traced rekursiv lokale Imports ausgehend von einem Einstiegspunkt | `trace_deps.py` | **80 % – 95 %** |
| [**`data-schema-reducer`**](#5-data-schema-reducer) | Komprimiert JSON, CSV und SQL-Dumps auf Schemata + Beispielsätze | `reduce_data.py` | **90 % – 99 %** |
| [**`document-to-markdown`**](#6-document-to-markdown) | Wandelt PDF, DOCX, HTML und `.ipynb` in reinen Markdown-Text um | `convert_doc.py` | **70 % – 95 %** |
| [**`log-stacktrace-compressor`**](#7-log-stacktrace-compressor) | Entfernt ANSI-Codes, dedupliziert Zeilen und filtert Stacktraces | `compress_log.py` | **75 % – 90 %** |
| [**`git-diff-packager`**](#8-git-diff-packager) | Bündelt Git-Diffs mit AST-Skeletten veränderter Dateien für Code-Reviews | `pack_diff.py` | **70 % – 90 %** |

---

## 📂 Detailliertes Skill-Verzeichnis

### 1. `token-usage-router`

- **Pfad:** `skills/token-usage-router/SKILL.md`

- **Funktion:** Der Einstiegspunkt für den Agenten. Anhand der Eingabe (PDF hochgeladen, Test fehlgeschlagen, neues Repo erkunden, großes JSON geliefert) entscheidet der Router sofort, welcher spezialisierte Sub-Skill aktiviert werden soll.
- **Einsatzbereich:** Wird als Meta-Regel geladen, damit der Agent vor dem Einlesen großer Dateien selbstständig die richtige Vorverarbeitung wählt.

---

### 2. `codebase-architecture-reporter`

- **Pfad:** `skills/codebase-architecture-reporter/`

- **Funktion:** Scannt ein beliebiges Repository, respektiert `.gitignore` (ignoriert `.git`, `node_modules`, `.venv`, Lockfiles), ermittelt Kennzahlen (LOC, Token-Schätzung, Top-10-Dateien) und erstellt eine strukturierte Übersicht mit bereinigtem Dateibaum und optionalen AST-Schnittstellen.
- **Skript:** `skills/codebase-architecture-reporter/scripts/generate_report.py`
  - **Parameter:**
    - `dir`: Zielverzeichnis des Projekts (Standard: `.`)
    - `-o, --output`: Ausgabedatei (z. B. `PROJECT_OVERVIEW.md`)
    - `-s, --skeletons`: Betten von AST-Skeletten wichtiger Module
    - `--max-skeletons <N>`: Maximale Anzahl an Modul-Skeletten (Standard: `5`)
  - **Beispiel:**

    ```bash
    uv run python skills/codebase-architecture-reporter/scripts/generate_report.py . -s -o PROJECT_OVERVIEW.md
    ```

---

### 3. `python-code-skeletonizer`

- **Pfad:** `skills/python-code-skeletonizer/`

- **Funktion:** Parst Python-Quellcode mittels Abstract Syntax Tree (`ast`), ersetzt alle Funktions- und Methoden-Rümpfe durch `...` (Ellipsis) und behält Klassen, Vererbungshierarchien, Typ-Annotationen, Dekoratoren und Docstrings vollständig bei. Ideal als API-Referenz für Agenten, ohne Implementierungsdetails einlesen zu müssen.
- **Skript:** `skills/python-code-skeletonizer/scripts/skeletonize.py`
  - **Parameter:**
    - `file`: Pfad zur `.py`-Datei
    - `-o, --output`: Optionale Ausgabedatei
    - `--no-docstrings`: Entfernt Docstrings für maximale Kompression
  - **Beispiel:**

    ```bash
    uv run python skills/python-code-skeletonizer/scripts/skeletonize.py src/services/database.py -o docs/database_interface.py
    ```

---

### 4. `dependency-context-collector`

- **Pfad:** `skills/dependency-context-collector/`

- **Funktion:** Startet bei einer konkreten Einstiegsdatei (z. B. einem Testfile oder `cli.py`), verfolgt rekursiv alle lokalen Modul-Imports bis zu einer konfigurierbaren Tiefe, ignoriert Standardbibliotheken sowie 3rd-Party-Pakete und bündelt nur die tatsächlich beteiligten Projektdateien in einem einzigen Markdown-Dokument.
- **Skript:** `skills/dependency-context-collector/scripts/trace_deps.py`
  - **Parameter:**
    - `entry`: Einstiegsdatei (z. B. `tests/test_login.py`)
    - `-r, --root`: Projekt-Wurzelverzeichnis
    - `-d, --depth <N>`: Maximale Rekursionstiefe (Standard: `3`)
    - `-o, --output`: Optionale Ausgabedatei
  - **Beispiel:**

    ```bash
    uv run python skills/dependency-context-collector/scripts/trace_deps.py tests/test_auth.py -d 2 -o context/auth_flow.md
    ```

---

### 5. `data-schema-reducer`

- **Pfad:** `skills/data-schema-reducer/`

- **Funktion:** Analysiert umfangreiche JSON-Arrays, CSV-Dateien oder SQL-Dumps. Anstatt tausende Datensätze in den Prompt zu laden, extrahiert der Skill Feldnamen, inferierte Datentypen und 2–3 repräsentative Beispielsätze. Massendaten werden durch einen prägnanten Hinweis ersetzt.
- **Skript:** `skills/data-schema-reducer/scripts/reduce_data.py`
  - **Parameter:**
    - `file`: Pfad zur Datendatei (`.json`, `.csv`, `.tsv`, `.sql`)
    - `-s, --samples <N>`: Anzahl der zu behaltenden Beispielsätze (Standard: `3`)
    - `-o, --output`: Optionale Ausgabedatei
  - **Beispiel:**

    ```bash
    uv run python skills/data-schema-reducer/scripts/reduce_data.py data/large_dataset.json -s 2 -o docs/dataset_schema.md
    ```

---

### 6. `document-to-markdown`

- **Pfad:** `skills/document-to-markdown/`

- **Funktion:** Konvertiert Spezifikationen, Lastenhefte und Dokumente (PDF, DOCX, HTML, Jupyter Notebooks) in sauberes, token-effizientes Markdown. Entfernt binären Ballast, Navigationsleisten, Skripte, Styles und base64-kodierte Bilddaten.
- **Skript:** `skills/document-to-markdown/scripts/convert_doc.py`
  - **Parameter:**
    - `file`: Pfad zur Dokumentdatei (`.pdf`, `.docx`, `.html`, `.ipynb`)
    - `-o, --output`: Optionale Ausgabedatei
    - `--include-outputs`: Bezieht Notebook-Ausgabezellen mit ein (Standard: `false`)
  - **Beispiel:**

    ```bash
    uv run python skills/document-to-markdown/scripts/convert_doc.py docs/specification.pdf -o docs/specification.md
    ```

---

### 7. `log-stacktrace-compressor`

- **Pfad:** `skills/log-stacktrace-compressor/`

- **Funktion:** Bereinigt Test-Ausgaben, CI/CD-Logs und Server-Crashes. Entfernt ANSI-Farbcodes, dedupliziert wiederholte Log-Zeilen (z. B. Polling-Meldungen), schneidet interne Framework-Traceback-Frames (Standardbibliothek, `site-packages`) ab und isoliert die exakte Fehlerursache mit Codezeile.
- **Skript:** `skills/log-stacktrace-compressor/scripts/compress_log.py`
  - **Parameter:**
    - `file`: Pfad zur Logdatei (optional; liest von `stdin`, falls weggelassen)
    - `-o, --output`: Optionale Ausgabedatei
  - **Beispiel:**

    ```bash
    # Aus einer Datei:
    uv run python skills/log-stacktrace-compressor/scripts/compress_log.py tests/failure.log -o tests/failure_clean.log

    # Direkt aus Pipe:
    uv run pytest | uv run python skills/log-stacktrace-compressor/scripts/compress_log.py
    ```

---

### 8. `git-diff-packager`

- **Pfad:** `skills/git-diff-packager/`

- **Funktion:** Ideal für Code-Reviews und PR-Vorbereitungen. Extrahiert den aktuellen Git-Diff (Working Tree oder `--staged`) und kombiniert ihn automatisch mit den AST-Schnittstellen (Klassen, Methoden, Signaturen) aller modifizierten Dateien. So verfügt der Review-Agent über den vollen Schnittstellen-Kontext, ohne vollständige Dateien lesen zu müssen.
- **Skript:** `skills/git-diff-packager/scripts/pack_diff.py`
  - **Parameter:**
    - `-r, --repo`: Pfad zum Git-Repository (Standard: `.`)
    - `--staged`: Berücksichtigt nur gestagte Änderungen (`git diff --staged`)
    - `--no-skeletons`: Unterdrückt die Generierung der AST-Schnittstellen
    - `-o, --output`: Optionale Ausgabedatei
  - **Beispiel:**

    ```bash
    uv run python skills/git-diff-packager/scripts/pack_diff.py --staged -o context/review_package.md
    ```

---

## 🚀 Installation & Integration

### Verwendung mit AI-Coding-Agenten

Die Skills entsprechen dem Standard-Format für Custom-Agent-Skills:

1. **Workspace-Ebene:**  
   Kopiere die gewünschten Skill-Ordner nach `.agents/skills/` (oder `.skills/`) in deinem Arbeitsbereich.
2. **Globale Konfiguration:**  
   Verlinke oder kopiere das Repository in dein globales Konfigurationsverzeichnis (z. B. `~/.gemini/config/skills/` oder den Konfigurationsordner deines Agenten).

### Lokale Ausführung der Skripte

Die Skripte sind für Python 3.10+ geschrieben. Wir empfehlen die Ausführung mit [`uv`](https://github.com/astral-sh/uv):

```bash
# Repository klonen
git clone https://github.com/DaniBani/JackOfAllTrAIdes.git
cd JackOfAllTrAIdes

# Beliebiges Skript direkt ausführen
uv run python skills/codebase-architecture-reporter/scripts/generate_report.py .
```

---

## 💡 Best Practices

1. **Vorverarbeitung statt Volltext:** Bevor du einem Agenten eine Datei übergibst (insbesondere Logs, PDFs oder Datensätze), lass den entsprechenden Skill darüberlaufen.
2. **Kombination für komplexe Tasks:** Bei größeren Refactorings empfiehlt sich die Kombination aus `dependency-context-collector` und `git-diff-packager`.
3. **Immer das Token-Budget im Blick behalten:** Durch das Reduzieren von Datenbeständen und Schnittstellen bleiben 70–95 % des Kontextfensters frei für tiefgreifende Programmierlogik und präzise Antworten.

---

## 🤝 Mitwirken

Du hast einen neuen nützlichen Skill oder eine Optimierung für bestehende Skripte?

1. Erstelle einen neuen Ordner unter `skills/<skill-name>/`.
2. Lege eine standardkonforme `SKILL.md` mit YAML-Frontmatter (`name`, `description`) und klarer Dokumentation an.
3. Ergänze optionale CLI-Werkzeuge unter `skills/<skill-name>/scripts/`.
4. Trage den neuen Skill in dieser `README.md` ein.
5. Öffne einen Pull Request!

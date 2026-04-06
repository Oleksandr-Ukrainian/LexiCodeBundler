import os
import json
import random
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional, Set, Dict, List, Tuple

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font as tkfont


# ===== CONFIG / PERSISTENCE =====

CONFIG_PATH = Path.home() / ".lexicode_bundler_config.json"
HISTORY_MAX_RECENT = 25  # скільки останніх значень зберігати для кожного поля


# ===== DEFAULT SUGGESTED FILTERS =====

DEFAULT_EXCLUDE_DIRS = {
    ".git",
    ".idea",
    ".vscode",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "public",
    ".next",
    "out",
    ".turbo",
    "venv",
    ".venv",
}

DEFAULT_EXCLUDE_FILES = {
    ".dockerignore",
    ".gitignore",
    "README",
    "README.md",
    "LICENSE",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "pnpm-lock.yml",
}

DEFAULT_EXCLUDE_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif", ".ico", ".svg",
    ".mp4", ".mov", ".avi", ".mkv",
    ".mp3", ".wav", ".flac", ".ogg",
    ".pdf", ".zip", ".tar", ".gz", ".tgz", ".7z", ".rar",
    ".exe", ".dll", ".bin",
    ".woff", ".woff2", ".eot", ".ttf", ".otf",
    ".log",
}

DEFAULT_FIELD_VALUES = {
    "src_root": "",
    "save_root": "",
    "shorten_root": "",
    "include_ext": "",
    "exclude_ext": ",".join(sorted(e.lstrip(".") for e in DEFAULT_EXCLUDE_EXTS)),
    "exclude_dirs": ",".join(sorted(DEFAULT_EXCLUDE_DIRS)),
    "exclude_files": ",".join(sorted(DEFAULT_EXCLUDE_FILES)),
    "output_name": "all_sources.txt",
}


# ===== LOCALIZATION DICTIONARY =====

LOCALES: Dict[str, Dict[str, str]] = {
    "en": {
        "title": "LexiCode Bundler",
        "lang_label": "Language:",
        "theme_label": "Theme:",
        "font_label": "Font:",
        "scaling_label": "Scaling:",
        "source_root_label": "Source root (e.g. ...\\src):",
        "output_folder_label": "Output folder (empty = same as source):",
        "shorten_prefix_label": "Shorten path prefix (optional):",
        "include_ext_label": "Include extensions (e.g. py,ts; empty = all):",
        "exclude_ext_label": "Exclude extensions (comma separated, e.g. png,jpg,log):",
        "exclude_dirs_label": "Exclude directories by name (comma separated):",
        "exclude_files_label": "Exclude files by name (comma separated):",
        "mode_label": "Mode:",
        "mode_all": "1) One big file for the whole tree",
        "mode_per_folder": "2) One file per top-level folder",
        "output_name_label": "Output file name (for mode 1):",
        "include_root_files_label": "Also bundle loose files in root (e.g. extension.ts)",
        "separator_label": "Add separator line between files",
        "list_only_names_label": "List only names (no file contents)",
        "browse": "Browse",
        "goto": "Go to",
        "auto_shorten": "Auto",
        "run": "Run",
        "status_ready": "Ready",
        "status_running": "Running...",
        "err_source_not_set": "Source folder is not set.",
        "err_source_not_dir": "Source folder does not exist or is not a directory.",
        "err_output_path_empty": "Output path is empty.",
        "warn_source_empty": "Source path is empty.",
        "success_one": "Done. Created file:\n{path}",
        "success_many": "Done. Created files:\n{paths}",
        "no_files": "No files found for the given filters.",
        "error_title": "Error",
        "success_title": "Success",
        "result_title": "Result",
        "warning_title": "Warning",
    },
    "ua": {
        "title": "LexiCode Bundler",
        "lang_label": "Мова:",
        "theme_label": "Тема:",
        "font_label": "Шрифт:",
        "scaling_label": "Масштаб:",
        "source_root_label": "Source root (наприклад, ...\\src):",
        "output_folder_label": "Папка збереження (пусто = як source):",
        "shorten_prefix_label": "Префікс для скорочення шляху (опційно):",
        "include_ext_label": "Include розширення (наприклад: py,ts; пусто = всі):",
        "exclude_ext_label": "Exclude розширення (через кому, напр. png,jpg,log):",
        "exclude_dirs_label": "Ігнорувати папки (імена через кому):",
        "exclude_files_label": "Ігнорувати файли (імена через кому):",
        "mode_label": "Режим:",
        "mode_all": "1) Один великий файл для всього дерева",
        "mode_per_folder": "2) Окремий файл для кожної верхньої папки",
        "output_name_label": "Ім'я вихідного файлу (для режиму 1):",
        "include_root_files_label": "Додати також файли з кореня (наприклад extension.ts)",
        "separator_label": "Додавати роздільну лінію між файлами",
        "list_only_names_label": "Лише список імен (без коду всередині)",
        "browse": "Обрати",
        "goto": "Перейти",
        "auto_shorten": "Авто",
        "run": "Запустити",
        "status_ready": "Готово",
        "status_running": "Працюю...",
        "err_source_not_set": "Source-папка не вказана.",
        "err_source_not_dir": "Source-папка не існує або це не папка.",
        "err_output_path_empty": "Путь збереження порожній.",
        "warn_source_empty": "Source-путь порожній.",
        "success_one": "Готово. Створено файл:\n{path}",
        "success_many": "Готово. Створено файли:\n{paths}",
        "no_files": "Не знайдено файлів з такими фільтрами.",
        "error_title": "Помилка",
        "success_title": "OK",
        "result_title": "Результат",
        "warning_title": "Увага",
    },
        "pl": {
        "title": "LexiCode Bundler",
        "lang_label": "Język:",
        "theme_label": "Motyw:",
        "font_label": "Czcionka:",
        "scaling_label": "Skalowanie:",
        "source_root_label": "Główny katalog źródłowy (np. ...\\src):",
        "output_folder_label": "Katalog wyjściowy (pusty = taki sam jak źródłowy):",
        "shorten_prefix_label": "Skróć prefiks ścieżki (opcjonalne):",
        "include_ext_label": "Rozszerzenia do włączenia (np. py,ts; puste = wszystkie):",
        "exclude_ext_label": "Rozszerzenia do wykluczenia (przecinkami, np. png,jpg,log):",
        "exclude_dirs_label": "Wyklucz katalogi po nazwie (przecinkami):",
        "exclude_files_label": "Wyklucz pliki po nazwie (przecinkami):",
        "mode_label": "Tryb:",
        "mode_all": "1) Jeden duży plik dla całego drzewa",
        "mode_per_folder": "2) Jeden plik na folder najwyższego poziomu",
        "output_name_label": "Nazwa pliku wyjściowego (dla trybu 1):",
        "include_root_files_label": "Również pakuj luźne pliki w katalogu głównym (np. extension.ts)",
        "separator_label": "Dodaj linię separatora między plikami",
        "list_only_names_label": "Tylko lista nazw (bez zawartości plików)",
        "browse": "Przeglądaj",
        "goto": "Idź do",
        "auto_shorten": "Auto",
        "run": "Uruchom",
        "status_ready": "Gotowy",
        "status_running": "Działam...",
        "err_source_not_set": "Katalog źródłowy nie jest ustawiony.",
        "err_source_not_dir": "Katalog źródłowy nie istnieje lub nie jest katalogiem.",
        "err_output_path_empty": "Ścieżka wyjściowa jest pusta.",
        "warn_source_empty": "Ścieżka źródłowa jest пusta.",
        "success_one": "Gotowe. Utworzono plik:\n{path}",
        "success_many": "Gotowe. Utworzono pliki:\n{paths}",
        "no_files": "Nie znaleziono plików dla podanych filtrów.",
        "error_title": "Błąd",
        "success_title": "Sukces",
        "result_title": "Wynik",
        "warning_title": "Ostrzeżenie",
    },
    "de": {
        "title": "LexiCode Bundler",
        "lang_label": "Sprache:",
        "theme_label": "Thema:",
        "font_label": "Schriftart:",
        "scaling_label": "Skalierung:",
        "source_root_label": "Quellordner (z.B. ...\\src):",
        "output_folder_label": "Ausgabeordner (leer = wie Quelle):",
        "shorten_prefix_label": "Pfad-Präfix kürzen (optional):",
        "include_ext_label": "Erweiterungen einbeziehen (z.B. py,ts; leer = alle):",
        "exclude_ext_label": "Erweiterungen ausschließen (kommagetrennt, z.B. png,jpg,log):",
        "exclude_dirs_label": "Ordner nach Namen ausschließen (kommagetrennt):",
        "exclude_files_label": "Dateien nach Namen ausschließen (kommagetrennt):",
        "mode_label": "Modus:",
        "mode_all": "1) Eine große Datei für den gesamten Baum",
        "mode_per_folder": "2) Eine Datei pro obersten Ordner",
        "output_name_label": "Ausgabedatei-Name (für Modus 1):",
        "include_root_files_label": "Auch lose Dateien im Root bündeln (z.B. extension.ts)",
        "separator_label": "Trennlinie zwischen Dateien hinzufügen",
        "list_only_names_label": "Nur Namen auflisten (keine Inhalte)",
        "browse": "Durchsuchen",
        "goto": "Gehe zu",
        "auto_shorten": "Auto",
        "run": "Ausführen",
        "status_ready": "Bereit",
        "status_running": "Laufe...",
        "err_source_not_set": "Quellordner nicht gesetzt.",
        "err_source_not_dir": "Quellordner existiert nicht oder ist kein Ordner.",
        "err_output_path_empty": "Ausgabepfad ist leer.",
        "warn_source_empty": "Quellpfad ist leer.",
        "success_one": "Fertig. Datei erstellt:\n{path}",
        "success_many": "Fertig. Dateien erstellt:\n{paths}",
        "no_files": "Keine Dateien für die angegebenen Filter gefunden.",
        "error_title": "Fehler",
        "success_title": "Erfolg",
        "result_title": "Ergebnis",
        "warning_title": "Warnung",
    },
    "es": {
        "title": "LexiCode Bundler",
        "lang_label": "Idioma:",
        "theme_label": "Tema:",
        "font_label": "Fuente:",
        "scaling_label": "Escalado:",
        "source_root_label": "Raíz de código fuente (ej. ...\\src):",
        "output_folder_label": "Carpeta de salida (vacía = igual que fuente):",
        "shorten_prefix_label": "Prefijo de ruta corto (opcional):",
        "include_ext_label": "Extensiones a incluir (ej. py,ts; vacío = todas):",
        "exclude_ext_label": "Extensiones a excluir (separadas por coma, ej. png,jpg,log):",
        "exclude_dirs_label": "Excluir carpetas por nombre (separadas por coma):",
        "exclude_files_label": "Excluir archivos por nombre (separados por coma):",
        "mode_label": "Modo:",
        "mode_all": "1) Un archivo grande para todo el árbol",
        "mode_per_folder": "2) Un archivo por carpeta de nivel superior",
        "output_name_label": "Nombre del archivo de salida (para modo 1):",
        "include_root_files_label": "También empaquetar archivos sueltos en raíz (ej. extension.ts)",
        "separator_label": "Agregar línea separadora entre archivos",
        "list_only_names_label": "Solo listar nombres (sin contenido de archivos)",
        "browse": "Explorar",
        "goto": "Ir a",
        "auto_shorten": "Auto",
        "run": "Ejecutar",
        "status_ready": "Listo",
        "status_running": "Ejecutando...",
        "err_source_not_set": "Carpeta de origen no establecida.",
        "err_source_not_dir": "Carpeta de origen no existe o no es una carpeta.",
        "err_output_path_empty": "Ruta de salida vacía.",
        "warn_source_empty": "Ruta de origen vacía.",
        "success_one": "Hecho. Archivo creado:\n{path}",
        "success_many": "Hecho. Archivos creados:\n{paths}",
        "no_files": "No se encontraron archivos con los filtros dados.",
        "error_title": "Error",
        "success_title": "Éxito",
        "result_title": "Resultado",
        "warning_title": "Advertencia",
    },
    "fr": {
        "title": "LexiCode Bundler",
        "lang_label": "Langue:",
        "theme_label": "Thème:",
        "font_label": "Police:",
        "scaling_label": "Échelle:",
        "source_root_label": "Racine source (ex. ...\\src):",
        "output_folder_label": "Dossier de sortie (vide = comme source):",
        "shorten_prefix_label": "Préfixe de chemin court (optionnel):",
        "include_ext_label": "Extensions à inclure (ex. py,ts; vide = toutes):",
        "exclude_ext_label": "Extensions à exclure (séparées par virgule, ex. png,jpg,log):",
        "exclude_dirs_label": "Exclure dossiers par nom (séparés par virgule):",
        "exclude_files_label": "Exclure fichiers par nom (séparés par virgule):",
        "mode_label": "Mode:",
        "mode_all": "1) Un gros fichier pour tout l'arbre",
        "mode_per_folder": "2) Un fichier par dossier de niveau supérieur",
        "output_name_label": "Nom du fichier de sortie (pour mode 1):",
        "include_root_files_label": "Aussi empaqueter fichiers libres à la racine (ex. extension.ts)",
        "separator_label": "Ajouter ligne séparatrice entre fichiers",
        "list_only_names_label": "Lister seulement les noms (sans contenu)",
        "browse": "Parcourir",
        "goto": "Aller à",
        "auto_shorten": "Auto",
        "run": "Exécuter",
        "status_ready": "Prêt",
        "status_running": "En cours...",
        "err_source_not_set": "Dossier source non défini.",
        "err_source_not_dir": "Dossier source n'existe pas ou n'est pas un dossier.",
        "err_output_path_empty": "Chemin de sortie vide.",
        "warn_source_empty": "Chemin source vide.",
        "success_one": "Terminé. Fichier créé:\n{path}",
        "success_many": "Terminé. Fichiers créés:\n{paths}",
        "no_files": "Aucun fichier trouvé avec ces filtres.",
        "error_title": "Erreur",
        "success_title": "Succès",
        "result_title": "Résultat",
        "warning_title": "Avertissement",
    },
    "it": {
        "title": "LexiCode Bundler",
        "lang_label": "Lingua:",
        "theme_label": "Tema:",
        "font_label": "Font:",
        "scaling_label": "Scala:",
        "source_root_label": "Radice sorgente (es. ...\\src):",
        "output_folder_label": "Cartella output (vuota = uguale a sorgente):",
        "shorten_prefix_label": "Prefisso percorso corto (opzionale):",
        "include_ext_label": "Estensioni da includere (es. py,ts; vuoto = tutte):",
        "exclude_ext_label": "Estensioni da escludere (separate da virgola, es. png,jpg,log):",
        "exclude_dirs_label": "Escludi cartelle per nome (separate da virgola):",
        "exclude_files_label": "Escludi file per nome (separati da virgola):",
        "mode_label": "Modalità:",
        "mode_all": "1) Un file grande per l'intero albero",
        "mode_per_folder": "2) Un file per cartella di livello superiore",
        "output_name_label": "Nome file output (per modalità 1):",
        "include_root_files_label": "Includi anche file sciolti nella radice (es. extension.ts)",
        "separator_label": "Aggiungi linea separatrice tra file",
        "list_only_names_label": "Elenca solo nomi (senza contenuto)",
        "browse": "Sfoglia",
        "goto": "Vai a",
        "auto_shorten": "Auto",
        "run": "Esegui",
        "status_ready": "Pronto",
        "status_running": "In esecuzione...",
        "err_source_not_set": "Cartella sorgente non impostata.",
        "err_source_not_dir": "Cartella sorgente non esiste o non è una cartella.",
        "err_output_path_empty": "Percorso output vuoto.",
        "warn_source_empty": "Percorso sorgente vuoto.",
        "success_one": "Fatto. File creato:\n{path}",
        "success_many": "Fatto. File creati:\n{paths}",
        "no_files": "Nessun file trovato con i filtri dati.",
        "error_title": "Errore",
        "success_title": "Successo",
        "result_title": "Risultato",
        "warning_title": "Avviso",
    },
    "pt": {
    "title": "LexiCode Bundler",
    "lang_label": "Idioma:",
    "theme_label": "Tema:",
    "font_label": "Fonte:",
    "scaling_label": "Escala:",
    "source_root_label": "Raiz de origem (ex.: ...\\\\src):",
    "output_folder_label": "Pasta de saída (vazio = mesma da origem):",
    "shorten_prefix_label": "Encurtar prefixo de caminho (opcional):",
    "include_ext_label": "Incluir extensões (ex.: py,ts; vazio = todas):",
    "exclude_ext_label": "Excluir extensões (separadas por vírgula, ex.: png,jpg,log):",
    "exclude_dirs_label": "Excluir diretórios por nome (separados por vírgula):",
    "exclude_files_label": "Excluir arquivos por nome (separados por vírgula):",
    "mode_label": "Modo:",
    "mode_all": "1) Um arquivo grande para toda a árvore",
    "mode_per_folder": "2) Um arquivo por pasta de nível superior",
    "output_name_label": "Nome do arquivo de saída (para o modo 1):",
    "include_root_files_label": "Incluir também arquivos soltos na raiz (ex.: extension.ts)",
    "separator_label": "Adicionar linha separadora entre arquivos",
    "list_only_names_label": "Listar apenas nomes (sem conteúdo dos arquivos)",
    "browse": "Procurar",
    "goto": "Ir para",
    "auto_shorten": "Automático",
    "run": "Executar",
    "status_ready": "Pronto",
    "status_running": "Executando...",
    "err_source_not_set": "Pasta de origem não definida.",
    "err_source_not_dir": "Pasta de origem não existe ou não é um diretório.",
    "err_output_path_empty": "Caminho de saída está vazio.",
    "warn_source_empty": "Caminho de origem está vazio.",
    "success_one": "Concluído. Arquivo criado:\\n{path}",
    "success_many": "Concluído. Arquivos criados:\\n{paths}",
    "no_files": "Nenhum arquivo encontrado para os filtros informados.",
    "error_title": "Erro",
    "success_title": "Sucesso",
    "result_title": "Resultado",
    "warning_title": "Aviso"
    },

    "ro": {
    "title": "LexiCode Bundler",
    "lang_label": "Limba:",
    "theme_label": "Temă:",
    "font_label": "Font:",
    "scaling_label": "Scalare:",
    "source_root_label": "Rădăcină de sursă (ex.: ...\\\\src):",
    "output_folder_label": "Dosar de ieșire (gol = același ca sursa):",
    "shorten_prefix_label": "Scurtează prefixul de cale (opțional):",
    "include_ext_label": "Include extensii (ex.: py,ts; gol = toate):",
    "exclude_ext_label": "Exclude extensii (separate prin virgulă, ex.: png,jpg,log):",
    "exclude_dirs_label": "Exclude directoare după nume (separate prin virgulă):",
    "exclude_files_label": "Exclude fișiere după nume (separate prin virgulă):",
    "mode_label": "Mod:",
    "mode_all": "1) Un fișier mare pentru tot arborele",
    "mode_per_folder": "2) Un fișier per director de nivel superior",
    "output_name_label": "Nume fișier de ieșire (pentru modul 1):",
    "include_root_files_label": "Include și fișierele izolate din rădăcină (ex.: extension.ts)",
    "separator_label": "Adaugă linie separator între fișiere",
    "list_only_names_label": "Listează doar numele (fără conținutul fișierelor)",
    "browse": "Caută",
    "goto": "Mergi la",
    "auto_shorten": "Automat",
    "run": "Rulează",
    "status_ready": "Gata",
    "status_running": "Rulează...",
    "err_source_not_set": "Directorul de sursă nu este setat.",
    "err_source_not_dir": "Directorul de sursă nu există sau nu este un director.",
    "err_output_path_empty": "Calea de ieșire este goală.",
    "warn_source_empty": "Calea de sursă este goală.",
    "success_one": "Finalizat. Fișier creat:\\n{path}",
    "success_many": "Finalizat. Fișiere create:\\n{paths}",
    "no_files": "Niciun fișier găsit pentru filtrele date.",
    "error_title": "Eroare",
    "success_title": "Succes",
    "result_title": "Rezultat",
    "warning_title": "Avertizare"
    },

    "nl": {
    "title": "LexiCode Bundler",
    "lang_label": "Taal:",
    "theme_label": "Thema:",
    "font_label": "Lettertype:",
    "scaling_label": "Schaal:",
    "source_root_label": "Bronroot (bijv. ...\\\\src):",
    "output_folder_label": "Outputmap (leeg = zelfde als bron):",
    "shorten_prefix_label": "Verminderen padvoorvoegsel (optioneel):",
    "include_ext_label": "Extensies opnemen (bijv. py,ts; leeg = alle):",
    "exclude_ext_label": "Extensies uitsluiten (komma gescheiden, bijv. png,jpg,log):",
    "exclude_dirs_label": "Directory’s uitsluiten op naam (komma gescheiden):",
    "exclude_files_label": "Bestanden uitsluiten op naam (komma gescheiden):",
    "mode_label": "Modus:",
    "mode_all": "1) Een groot bestand voor de hele boom",
    "mode_per_folder": "2) Één bestand per top‑directory",
    "output_name_label": "Naam uitvoerbestand (voor modus 1):",
    "include_root_files_label": "Neem ook losse bestanden in de root op (bijv. extension.ts)",
    "separator_label": "Voeg scheidingslijn tussen bestanden toe",
    "list_only_names_label": "Lijst alleen namen (geen bestandsinhoud)",
    "browse": "Bladeren",
    "goto": "Ga naar",
    "auto_shorten": "Automatisch",
    "run": "Uitvoeren",
    "status_ready": "Gereed",
    "status_running": "Bezig...",
    "err_source_not_set": "Bronmap is niet ingesteld.",
    "err_source_not_dir": "Bronmap bestaat niet of is geen map.",
    "err_output_path_empty": "Uitvoerpad is leeg.",
    "warn_source_empty": "Bronpad is leeg.",
    "success_one": "Gereed. Bestand aangemaakt:\\n{path}",
    "success_many": "Gereed. Bestanden aangemaakt:\\n{paths}",
    "no_files": "Geen bestanden gevonden voor de opgegeven filters.",
    "error_title": "Fout",
    "success_title": "Succes",
    "result_title": "Resultaat",
    "warning_title": "Waarschuwing"
    },

    "sv": {
    "title": "LexiCode Bundler",
    "lang_label": "Språk:",
    "theme_label": "Tema:",
    "font_label": "Typsnitt:",
    "scaling_label": "Skalning:",
    "source_root_label": "Källrot (t.ex. ...\\\\src):",
    "output_folder_label": "Utdatakatalog (tom = samma som källa):",
    "shorten_prefix_label": "Korta sökvägsrefix (valfritt):",
    "include_ext_label": "Inkludera filändelser (t.ex. py,ts; tomt = alla):",
    "exclude_ext_label": "Exkludera filändelser (kommaseparerade, t.ex. png,jpg,log):",
    "exclude_dirs_label": "Exkludera kataloger efter namn (kommaseparerade):",
    "exclude_files_label": "Exkludera filer efter namn (kommaseparerade):",
    "mode_label": "Läge:",
    "mode_all": "1) En stor fil för hela trädstrukturen",
    "mode_per_folder": "2) En fil per rotkatalog",
    "output_name_label": "Namn på utdatafil (för läge 1):",
    "include_root_files_label": "Ta även med lösa filer i roten (t.ex. extension.ts)",
    "separator_label": "Lägg till avskiljningsrad mellan filer",
    "list_only_names_label": "Lista endast namn (ingen filinnehåll)",
    "browse": "Bläddra",
    "goto": "Gå till",
    "auto_shorten": "Automatiskt",
    "run": "Kör",
    "status_ready": "Klar",
    "status_running": "Kör...",
    "err_source_not_set": "Källmappen är inte angiven.",
    "err_source_not_dir": "Källmappen finns inte eller är inte en katalog.",
    "err_output_path_empty": "Utdatavägen är tom.",
    "warn_source_empty": "Källvägen är tom.",
    "success_one": "Klar. Fil skapad:\\n{path}",
    "success_many": "Klar. Filer skapade:\\n{paths}",
    "no_files": "Inga filer hittades för de givna filtren.",
    "error_title": "Fel",
    "success_title": "Lyckades",
    "result_title": "Resultat",
    "warning_title": "Varning"
    },

    "tr": {
    "title": "LexiCode Bundler",
    "lang_label": "Dil:",
    "theme_label": "Tema:",
    "font_label": "Yazı tipi:",
    "scaling_label": "Ölçek:",
    "source_root_label": "Kaynak kök (örn.: ...\\\\src):",
    "output_folder_label": "Çıktı klasörü (boş = kaynakla aynı):",
    "shorten_prefix_label": "Yol öneki kısalt (isteğe bağlı):",
    "include_ext_label": "Uzantıları dahil et (örn.: py,ts; boş = tümü):",
    "exclude_ext_label": "Uzantıları dışla (virgülle ayrılmış, örn.: png,jpg,log):",
    "exclude_dirs_label": "Klasörleri ada göre dışla (virgülle ayrılmış):",
    "exclude_files_label": "Dosyaları ada göre dışla (virgülle ayrılmış):",
    "mode_label": "Mod:",
    "mode_all": "1) Tüm dizin ağacı için tek büyük dosya",
    "mode_per_folder": "2) Her üst düzey klasör için bir dosya",
    "output_name_label": "Çıktı dosya adı (mod 1 için):",
    "include_root_files_label": "Kökteki serbest dosyaları da dahil et (örn.: extension.ts)",
    "separator_label": "Dosyalar arasında ayırıcı satır ekle",
    "list_only_names_label": "Yalnızca isimleri listele (dosya içeriği yok)",
    "browse": "Gözat",
    "goto": "Git",
    "auto_shorten": "Otomatik",
    "run": "Çalıştır",
    "status_ready": "Hazır",
    "status_running": "Çalışıyor...",
    "err_source_not_set": "Kaynak klasör belirtilmedi.",
    "err_source_not_dir": "Kaynak klasör mevcut değil veya bir dizin değil.",
    "err_output_path_empty": "Çıktı yolu boş.",
    "warn_source_empty": "Kaynak yolu boş.",
    "success_one": "Tamam. Dosya oluşturuldu:\\n{path}",
    "success_many": "Tamam. Dosyalar oluşturuldu:\\n{paths}",
    "no_files": "Verilen filtrelerle eşleşen dosya bulunamadı.",
    "error_title": "Hata",
    "success_title": "Başarı",
    "result_title": "Sonuç",
    "warning_title": "Uyarı"
    },

    "ja": {
    "title": "LexiCode Bundler",
    "lang_label": "言語:",
    "theme_label": "テーマ:",
    "font_label": "フォント:",
    "scaling_label": "拡大縮小:",
    "source_root_label": "ソースルート (例: ...\\\\src):",
    "output_folder_label": "出力フォルダ (空 = ソースと同じ):",
    "shorten_prefix_label": "パスのプレフィックスを短くする (省略可能):",
    "include_ext_label": "拡張子を含める (例: py,ts; 空 = すべて):",
    "exclude_ext_label": "拡張子を除外 (カンマ区切り, 例: png,jpg,log):",
    "exclude_dirs_label": "ディレクトリ名で除外 (カンマ区切り):",
    "exclude_files_label": "ファイル名で除外 (カンマ区切り):",
    "mode_label": "モード:",
    "mode_all": "1) ツリー全体を1つの大きなファイルにまとめる",
    "mode_per_folder": "2) 各トップレベルフォルダごとに1ファイル",
    "output_name_label": "出力ファイル名 (モード 1):",
    "include_root_files_label": "ルートにある個別ファイルも含む (例: extension.ts)",
    "separator_label": "ファイル間に区切り行を追加",
    "list_only_names_label": "名前のみリスト (ファイル内容なし)",
    "browse": "参照",
    "goto": "移動",
    "auto_shorten": "自動",
    "run": "実行",
    "status_ready": "準備完了",
    "status_running": "実行中...",
    "err_source_not_set": "ソースフォルダが設定されていません。",
    "err_source_not_dir": "ソースフォルダが存在しないか、ディレクトリではありません。",
    "err_output_path_empty": "出力パスが空です。",
    "warn_source_empty": "ソースパスが空です。",
    "success_one": "完了。ファイルを作成しました:\\n{path}",
    "success_many": "完了。ファイルを作成しました:\\n{paths}",
    "no_files": "指定されたフィルターに一致するファイルが見つかりませんでした。",
    "error_title": "エラー",
    "success_title": "成功",
    "result_title": "結果",
    "warning_title": "警告"
    },
    "zh": {
    "title": "LexiCode Bundler",
    "lang_label": "语言:",
    "theme_label": "主题:",
    "font_label": "字体:",
    "scaling_label": "缩放:",
    "source_root_label": "源码根目录 (例如 ...\\\\src):",
    "output_folder_label": "输出文件夹 (空 = 与源码相同):",
    "shorten_prefix_label": "缩短路径前缀 (可选):",
    "include_ext_label": "包含扩展名 (例如 py,ts; 空 = 所有):",
    "exclude_ext_label": "排除扩展名 (逗号分隔, 例如 png,jpg,log):",
    "exclude_dirs_label": "按名称排除目录 (逗号分隔):",
    "exclude_files_label": "按名称排除文件 (逗号分隔):",
    "mode_label": "模式:",
    "mode_all": "1) 将整个目录树打包为一个大文件",
    "mode_per_folder": "2) 每个顶级文件夹生成一个文件",
    "output_name_label": "输出文件名 (用于模式 1):",
    "include_root_files_label": "同时包含根目录中的零散文件 (例如 extension.ts)",
    "separator_label": "在文件之间添加分隔行",
    "list_only_names_label": "仅列出文件名 (无文件内容)",
    "browse": "浏览",
    "goto": "前往",
    "auto_shorten": "自动",
    "run": "运行",
    "status_ready": "就绪",
    "status_running": "运行中...",
    "err_source_not_set": "未设置源码文件夹。",
    "err_source_not_dir": "源码文件夹不存在或不是一个目录。",
    "err_output_path_empty": "输出路径为空。",
    "warn_source_empty": "源码路径为空。",
    "success_one": "已完成。创建文件:\\n{path}",
    "success_many": "已完成。创建文件:\\n{paths}",
    "no_files": "在给定过滤器下未找到任何文件。",
    "error_title": "错误",
    "success_title": "成功",
    "result_title": "结果",
    "warning_title": "警告"
    },

    "ko": {
    "title": "LexiCode Bundler",
    "lang_label": "언어:",
    "theme_label": "테마:",
    "font_label": "폰트:",
    "scaling_label": "확대/축소:",
    "source_root_label": "소스 루트 (예: ...\\\\src):",
    "output_folder_label": "출력 폴더 (비어 있음 = 소스와 동일):",
    "shorten_prefix_label": "경로 접두어 단축 (선택 사항):",
    "include_ext_label": "확장자 포함 (예: py,ts; 비어 있음 = 모든 파일):",
    "exclude_ext_label": "확장자 제외 (쉼표로 구분, 예: png,jpg,log):",
    "exclude_dirs_label": "이름으로 디렉터리 제외 (쉼표로 구분):",
    "exclude_files_label": "이름으로 파일 제외 (쉼표로 구분):",
    "mode_label": "모드:",
    "mode_all": "1) 전체 트리를 하나의 큰 파일로 묶기",
    "mode_per_folder": "2) 상위 폴더마다 하나의 파일",
    "output_name_label": "출력 파일 이름 (모드 1):",
    "include_root_files_label": "루트의 개별 파일도 포함 (예: extension.ts)",
    "separator_label": "파일 사이에 구분선 추가",
    "list_only_names_label": "이름만 나열 (파일 내용 없음)",
    "browse": "찾아보기",
    "goto": "이동",
    "auto_shorten": "자동",
    "run": "실행",
    "status_ready": "준비 완료",
    "status_running": "실행 중...",
    "err_source_not_set": "소스 폴더가 설정되지 않았습니다.",
    "err_source_not_dir": "소스 폴더가 존재하지 않거나 디렉터리가 아닙니다.",
    "err_output_path_empty": "출력 경로가 비어 있습니다.",
    "warn_source_empty": "소스 경로가 비어 있습니다.",
    "success_one": "완료. 파일을 생성했습니다:\\n{path}",
    "success_many": "완료. 파일을 생성했습니다:\\n{paths}",
    "no_files": "지정된 필터에 해당하는 파일을 찾을 수 없습니다.",
    "error_title": "오류",
    "success_title": "성공",
    "result_title": "결과",
    "warning_title": "경고"
    },

    "ar": {
    "title": "LexiCode Bundler",
    "lang_label": "اللغة:",
    "theme_label": "السمة:",
    "font_label": "الخط:",
    "scaling_label": "التنسيق:",
    "source_root_label": "جذر المصدر (مثالًا: ...\\\\src):",
    "output_folder_label": "مجلد الإخراج (فارغ = نفس المصدر):",
    "shorten_prefix_label": "اختصار بادئة المسار (اختياري):",
    "include_ext_label": "تضمين الامتدادات (مثالًا: py,ts; فارغ = جميعها):",
    "exclude_ext_label": "استبعاد الامتدادات (مفصولة بفواصل, مثالًا: png,jpg,log):",
    "exclude_dirs_label": "استبعاد المجلدات بالاسم (مفصولة بفواصل):",
    "exclude_files_label": "استبعاد الملفات بالاسم (مفصولة بفواصل):",
    "mode_label": "الوضع:",
    "mode_all": "1) ملف واحد كبير للشجرة بأكملها",
    "mode_per_folder": "2) ملف واحد لكل مجلد علوي",
    "output_name_label": "اسم ملف الإخراج (للوضع 1):",
    "include_root_files_label": "تضمين أيضًا الملفات الفردية في الجذر (مثالًا: extension.ts)",
    "separator_label": "إضافة سطر فاصل بين الملفات",
    "list_only_names_label": "عرض الأسماء فقط (بدون محتوى الملفات)",
    "browse": "استعراض",
    "goto": "اذهب إلى",
    "auto_shorten": "تلقائي",
    "run": "تشغيل",
    "status_ready": "جاهز",
    "status_running": "يجري التشغيل...",
    "err_source_not_set": "لم يتم تعيين مجلد المصدر.",
    "err_source_not_dir": "مجلد المصدر غير موجود أو ليس دليلًا.",
    "err_output_path_empty": "مسار الإخراج فارغ.",
    "warn_source_empty": "مسار المصدر فارغ.",
    "success_one": "تمت العملية. تم إنشاء ملف:\\n{path}",
    "success_many": "تمت العملية. تم إنشاء ملفات:\\n{paths}",
    "no_files": "لم يتم العثور على ملفات مطابقة للعوامل المعطاة.",
    "error_title": "خطأ",
    "success_title": "نجاح",
    "result_title": "النتيجة",
    "warning_title": "تحذير"
    },

    "hi": {
    "title": "LexiCode Bundler",
    "lang_label": "भाषा:",
    "theme_label": "थीम:",
    "font_label": "फ़ॉन्ट:",
    "scaling_label": "स्केलिंग:",
    "source_root_label": "स्रोत रूट (उदाहरण के लिए ...\\\\src):",
    "output_folder_label": "आउटपुट फ़ोल्डर (खाली = स्रोत के समान):",
    "shorten_prefix_label": "पथ उपसर्ग छोटा करें (वैकल्पिक):",
    "include_ext_label": "विस्तार शामिल करें (उदाहरण के लिए py,ts; खाली = सभी):",
    "exclude_ext_label": "विस्तार बाहर करें (अल्पविराम द्वारा अलग, उदाहरण के लिए png,jpg,log):",
    "exclude_dirs_label": "नाम से निर्देशिकाएँ बाहर करें (अल्पविराम द्वारा अलग):",
    "exclude_files_label": "नाम से फ़ाइलें बाहर करें (अल्पविराम द्वारा अलग):",
    "mode_label": "मोड:",
    "mode_all": "1) पूरे पेड़ के लिए एक बड़ी फ़ाइल",
    "mode_per_folder": "2) प्रत्येक शीर्ष-स्तरीय फ़ोल्डर के लिए एक फ़ाइल",
    "output_name_label": "आउटपुट फ़ाइल नाम (मोड 1 के लिए):",
    "include_root_files_label": "जड़ में भी अलग-अलग फ़ाइलें शामिल करें (उदाहरण के लिए extension.ts)",
    "separator_label": "फ़ाइलों के बीच अलग करने वाली रेखा जोड़ें",
    "list_only_names_label": "केवल नामों की सूची (कोई फ़ाइल सामग्री नहीं)",
    "browse": "ब्राउज़",
    "goto": "जाएँ",
    "auto_shorten": "स्वचालित",
    "run": "चलाएँ",
    "status_ready": "तैयार",
    "status_running": "चल रहा है...",
    "err_source_not_set": "स्रोत फ़ोल्डर सेट नहीं है।",
    "err_source_not_dir": "स्रोत फ़ोल्डर मौजूद नहीं है या निर्देशिका नहीं है।",
    "err_output_path_empty": "आउटपुट पथ खाली है।",
    "warn_source_empty": "स्रोत पथ खाली है।",
    "success_one": "हो गया। फ़ाइल बनाई गई:\\n{path}",
    "success_many": "हो गया। फ़ाइलें बनाई गईं:\\n{paths}",
    "no_files": "दिए गए फ़िल्टरों के लिए कोई फ़ाइलें नहीं मिलीं।",
    "error_title": "त्रुटि",
    "success_title": "सफलता",
    "result_title": "परिणाम",
    "warning_title": "चेतावनी"
    },
}


# Емодзі для опцій
EMOJI = {
    "language": "🌐",
    "theme": "🎨",
    "font": "🔤",
    "scaling": "🔍",
    "source_root": "📂",
    "output_folder": "💾",
    "shorten_prefix": "✂️",
    "include_ext": "✅",
    "exclude_ext": "🚫",
    "exclude_dirs": "📁❌",
    "exclude_files": "📄❌",
    "mode": "⚙️",
    "output_name": "📝",
    "include_root_files": "📌",
    "separator": "〰️",
    "list_only_names": "📃",
}


# ===== HELPERS =====

def parse_ext_list(ext_list: Optional[str]) -> Optional[Set[str]]:
    if not ext_list:
        return None
    exts = set()
    for raw in ext_list.split(","):
        e = raw.strip()
        if not e:
            continue
        if not e.startswith("."):
            e = "." + e
        exts.add(e.lower())
    return exts


def parse_name_list(name_list: Optional[str]) -> Set[str]:
    if not name_list:
        return set()
    names: Set[str] = set()
    for raw in name_list.split(","):
        n = raw.strip()
        if not n:
            continue
        names.add(n)
    return names


# ===== CORE LOGIC =====

def iter_files(
    root: Path,
    include_ext: Optional[Set[str]] = None,
    exclude_ext: Optional[Set[str]] = None,
) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        filenames = sorted(filenames)
        for name in filenames:
            p = Path(dirpath) / name
            ext = p.suffix.lower()
            if include_ext and ext not in include_ext:
                continue
            if exclude_ext and ext in exclude_ext:
                continue
            yield p


def iter_files_filtered(
    root: Path,
    include_ext: Optional[Set[str]],
    exclude_ext: Optional[Set[str]],
    exclude_dirs: Set[str],
    exclude_files: Set[str],
) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

        dirnames.sort()
        filenames = sorted(filenames)
        for name in filenames:
            if name in exclude_files:
                continue
            p = Path(dirpath) / name
            ext = p.suffix.lower()
            if include_ext and ext not in include_ext:
                continue
            if exclude_ext and ext in exclude_ext:
                continue
            yield p


def shorten_path(path: Path, shorten_root: Optional[Path]) -> str:
    if not shorten_root:
        return str(path)
    try:
        rel = path.relative_to(shorten_root)
        return str(rel)
    except ValueError:
        return str(path)


def write_bundle(
    files: Iterable[Path],
    out_file: Path,
    shorten_root: Optional[Path] = None,
    header_prefix: str = "file path: ",
    encoding: str = "utf-8",
    add_separator: bool = True,
    list_only_names: bool = False,
):
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with out_file.open("w", encoding=encoding, errors="ignore") as out:
        if list_only_names:
            for f in files:
                header_path = shorten_path(f, shorten_root)
                out.write(f"{header_path}\n")
            return

        first = True
        for f in files:
            if not first:
                out.write("\n")
            first = False

            header_path = shorten_path(f, shorten_root)
            out.write(f"{header_prefix}{header_path}\n\n")
            try:
                with f.open("r", encoding=encoding, errors="ignore") as src:
                    out.write(src.read())
            except Exception as e:
                out.write(f"<<ERROR READING FILE: {e}>>\n")

            if add_separator:
                out.write("\n\n" + "-" * 80 + "\n\n")


def bundle_mode_all(
    src_root: Path,
    save_root: Path,
    output_name: str = "all_sources.txt",
    include_ext: Optional[Set[str]] = None,
    exclude_ext: Optional[Set[str]] = None,
    shorten_root: Optional[Path] = None,
    exclude_dirs: Optional[Set[str]] = None,
    exclude_files: Optional[Set[str]] = None,
    add_separator: bool = True,
    list_only_names: bool = False,
):
    if exclude_dirs or exclude_files:
        files = list(
            iter_files_filtered(
                src_root,
                include_ext=include_ext,
                exclude_ext=exclude_ext,
                exclude_dirs=exclude_dirs or set(),
                exclude_files=exclude_files or set(),
            )
        )
    else:
        files = list(iter_files(src_root, include_ext, exclude_ext))

    out_file = save_root / output_name
    write_bundle(
        files,
        out_file,
        shorten_root=shorten_root,
        add_separator=add_separator,
        list_only_names=list_only_names,
    )
    return out_file


def bundle_mode_per_top_folder(
    src_root: Path,
    save_root: Path,
    include_ext: Optional[Set[str]] = None,
    exclude_ext: Optional[Set[str]] = None,
    shorten_root: Optional[Path] = None,
    include_root_files: bool = True,
    exclude_dirs: Optional[Set[str]] = None,
    exclude_files: Optional[Set[str]] = None,
    add_separator: bool = True,
    list_only_names: bool = False,
):
    src_root = src_root.resolve()
    save_root = save_root.resolve()
    save_root.mkdir(parents=True, exist_ok=True)

    entries = sorted(src_root.iterdir(), key=lambda p: p.name.lower())
    top_dirs = [p for p in entries if p.is_dir()]
    top_files = [p for p in entries if p.is_file()]

    ex_dirs = exclude_dirs or set()
    ex_files = exclude_files or set()

    written: List[Path] = []

    for d in top_dirs:
        if d.name in ex_dirs:
            continue

        if ex_dirs or ex_files:
            files = list(
                iter_files_filtered(
                    d,
                    include_ext=include_ext,
                    exclude_ext=exclude_ext,
                    exclude_dirs=ex_dirs,
                    exclude_files=ex_files,
                )
            )
        else:
            files = list(iter_files(d, include_ext, exclude_ext))

        if not files:
            continue
        out_file = save_root / f"{d.name}_bundle.txt"
        write_bundle(
            files,
            out_file,
            shorten_root=shorten_root,
            add_separator=add_separator,
            list_only_names=list_only_names,
        )
        written.append(out_file)

    if include_root_files and top_files:
        root_files: List[Path] = []
        for f in top_files:
            if f.name in ex_files:
                continue
            ext = f.suffix.lower()
            if include_ext and ext not in include_ext:
                continue
            if exclude_ext and ext in exclude_ext:
                continue
            root_files.append(f)

        if root_files:
            out_file = save_root / "_root_files_bundle.txt"
            write_bundle(
                root_files,
                out_file,
                shorten_root=shorten_root,
                add_separator=add_separator,
                list_only_names=list_only_names,
            )
            written.append(out_file)

    return written


def open_in_explorer(path_str: str):
    if not path_str:
        return
    p = Path(path_str).expanduser()
    if p.is_file():
        p = p.parent
    if not p.exists():
        return
    try:
        os.startfile(p)  # type: ignore[attr-defined]
    except AttributeError:
        import subprocess
        if os.name == "posix":
            subprocess.Popen(["xdg-open", str(p)])
        elif os.name == "mac":
            subprocess.Popen(["open", str(p)])


# ===== TKINTER UI =====

class BundleApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # --- runtime icon (window + taskbar) ---
        try:
            import sys, os as _os
            _base = sys._MEIPASS if hasattr(sys, "_MEIPASS") else _os.path.dirname(_os.path.abspath(__file__))
            _ico = _os.path.join(_base, "icon.ico")
            if _os.path.exists(_ico):
                self.iconbitmap(_ico)
        except Exception:
            pass
        # --- end icon ---

        # базовий шрифт
        try:
            default_font = tkfont.nametofont("TkDefaultFont")
            default_font.configure(family="Segoe UI", size=10)
            self.base_font_size = int(default_font.cget("size") or 10)
            self.option_add("*Font", default_font)
        except Exception:
            self.base_font_size = 10

        # початкова геометрія
        self.geometry("950x650+100+100")

        # завантаження конфігурації
        self.config_data = self.load_config()
        geom = self.config_data.get("geometry")
        if geom:
            try:
                self.geometry(geom)
            except Exception:
                pass

        self.current_lang = self.config_data.get("language", "en")
        self.current_theme = self.config_data.get("theme", "dark_purple")
        # Mono за замовчуванням, але якщо в конфігу вже щось є – беремо звідти
        self.font_profile = self.config_data.get("font_profile", "Mono")
        self.scaling_value = float(self.config_data.get("scaling", 1.25))

        # ttk style / themes
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        self.setup_themes()
        self.apply_theme(self.current_theme)

        # поля
        self.src_var = tk.StringVar()
        self.save_var = tk.StringVar()
        self.shorten_var = tk.StringVar()

        self.ext_include_var = tk.StringVar()
        self.ext_exclude_var = tk.StringVar(value=DEFAULT_FIELD_VALUES["exclude_ext"])
        self.exclude_dirs_var = tk.StringVar(value=DEFAULT_FIELD_VALUES["exclude_dirs"])
        self.exclude_files_var = tk.StringVar(value=DEFAULT_FIELD_VALUES["exclude_files"])

        self.output_name_var = tk.StringVar(value=DEFAULT_FIELD_VALUES["output_name"])

        self.mode_var = tk.StringVar(value=self.config_data.get("mode", "all"))
        self.include_root_files_var = tk.BooleanVar(
            value=self.config_data.get("include_root_files", True)
        )
        self.add_separator_var = tk.BooleanVar(
            value=self.config_data.get("add_separator", True)
        )
        self.list_only_names_var = tk.BooleanVar(
            value=self.config_data.get("list_only_names", False)
        )

        # історії
        self.histories: Dict[str, List[Dict[str, str]]] = self.config_data.get("histories", {})
        self.history_widgets: Dict[str, Tuple[ttk.Combobox, ttk.Label, tk.StringVar, str]] = {}

        # мови
        self.lang_display_to_code = {
            "EN": "en",
            "UA": "ua",
            "PL": "pl",
            "DE": "de",
            "ES": "es",
            "FR": "fr",
            "IT": "it",
            "PT": "pt",
            "RO": "ro",
            "NL": "nl",
            "SV": "sv",
            "TR": "tr",
            "JA": "ja",
            "ZH": "zh",
            "KO": "ko",
            "AR": "ar",
            "HI": "hi",
        }
        self.lang_code_to_display = {v: k for k, v in self.lang_display_to_code.items()}
        self.lang_var = tk.StringVar(
            value=self.lang_code_to_display.get(self.current_lang, "EN")
        )

        # теми (додали ще жовто‑оранжеві й інші)
        # теми (додано Darkula, Jungle, Monokai, Nord, Cyberpunk і всі замовлені)
        self.theme_display_to_code = {
            "🌑 Dark": "dark",
            "🟣 Dark Purple": "dark_purple",
            "🟣L Dark Purple Light": "dark_purple_light",
            "🌸 Sakura": "sakura",    
            "🌙 Midnight Blue": "midnight_blue",
            "🌌 Midnight": "midnight",
            "🌲 Forest": "forest",
            "🌿 Jungle": "jungle",
            "❄️ Nord": "nord",

            "🏜️ Desert": "desert",
            "🧡 Amber": "amber",
            "🐼 Darkula": "darkula",
            "💻 Cyberpunk": "cyberpunk",
            "☀️ Solarized": "solarized",
            "🌅 Sunset": "sunset",

            "🌕 Moon": "moon",
            "🌙 Crescent Moon": "crescent_moon",
            "🎨 Monokai": "monokai",

            "🚀 Lightspeed": "lightspeed",
            "☀️ Light": "light",
        }
        self.theme_code_to_display = {v: k for k, v in self.theme_display_to_code.items()}
        self.theme_var = tk.StringVar(
            value=self.theme_code_to_display.get(self.current_theme, "Dark")
        )

        # профіль шрифту (більше варіантів)
        self.font_profiles = [
            "Default",
            "Mono",
            "Mono Large", 
            "Mono Small",
            "Coding",
            "Large",
            "Tiny",
            "Serif",
            "Rounded",
        ]
        self.font_var = tk.StringVar(value=self.font_profile)

        # масштаб (scaling) – від 15% до 250% кроком 5
        self.scaling_labels = [f"{i}%" for i in range(35, 166, 5)]
        self.scaling_var = tk.StringVar(
            value=self.scaling_to_label(self.scaling_value)
        )

        # застосовуємо профіль шрифту з урахуванням масштабу
        #self.apply_font_profile(self.font_profile, self.scaling_value)

        # змінні для easter egg
        self.scroll_at_bottom_counter = 0
        self.easter_shown = False
        self.cat_label: Optional[ttk.Label] = None
        self.cat_font: Optional[tkfont.Font] = None

        # scrollable content
        self._build_scrollable_container()
        self._build_ui()
        self.init_all_histories()
        self._apply_locale()
        # 🛠️ ПРАВИЛЬНИЙ фікс Ctrl+C/V/X для ВСІХ розкладок
        #self.bind_all("<Control-c>", self._copy_handler, add="+")
        #self.bind_all("<Control-v>", self._paste_handler, add="+") 
        #self.bind_all("<Control-x>", self._cut_handler, add="+")

        # 🛠️ УКРАЇНСЬКИЙ ФІКС Ctrl+C/V/X (по keycode!)
        #self.bind_all("<Control-KeyPress>", self._universal_shortcut)


        # 🛠️ УКРАЇНСЬКИЙ ФІКС Ctrl+C/V/X (по keycode!)
        # памʼять розміру/позиції
        self.protocol("WM_DELETE_WINDOW", self.on_close)


    def _universal_shortcut(self, event):
        """Ctrl+[C/V/X/A/Z] by keycode – works with Ukrainian layout too"""
        ctrl = event.state & 0x4  # Ctrl pressed
        if not ctrl or not hasattr(event.widget, "event_generate"):
            return

        keycode = event.keycode
        virtual = None

        if keycode == 67:      # C
            virtual = "<<Copy>>"
        elif keycode == 86:    # V
            virtual = "<<Paste>>"
        elif keycode == 88:    # X
            virtual = "<<Cut>>"
        elif keycode == 65:    # A
            virtual = "<<SelectAll>>"
        elif keycode == 90:    # Z
            virtual = "<<Undo>>"

        if virtual is not None:
            try:
                event.widget.focus_set()
                event.widget.event_generate(virtual)
            except Exception:
                pass
            return "break"   # stop further processing for this event

        # let all other Ctrl+keys behave normally
        return

    def _blend_color(self, fg: str, bg: str, alpha: float) -> str:
        """
        Blend fg over bg with given opacity alpha (0..1).
        alpha = 0.2 ≈ 80% transparent.
        """
        def _c(s):
            return int(s, 16)

        rf, gf, bf = _c(fg[1:3]), _c(fg[3:5]), _c(fg[5:7])
        rb, gb, bb = _c(bg[1:3]), _c(bg[3:5]), _c(bg[5:7])

        r = int(rf * alpha + rb * (1 - alpha))
        g = int(gf * alpha + gb * (1 - alpha))
        b = int(bf * alpha + bb * (1 - alpha))

        return f"#{r:02X}{g:02X}{b:02X}"

    # ---------- persistence ----------

    def load_config(self) -> dict:
        try:
            if CONFIG_PATH.is_file():
                return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
        return {}

    def save_config(self):
        data = {
            "language": self.current_lang,
            "theme": self.current_theme,
            "font_profile": self.font_profile,
            "scaling": self.scaling_value,
            "mode": self.mode_var.get(),
            "include_root_files": self.include_root_files_var.get(),
            "add_separator": self.add_separator_var.get(),
            "list_only_names": self.list_only_names_var.get(),
            "histories": self.histories,
            "geometry": self.winfo_geometry(),
        }
        try:
            CONFIG_PATH.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass

    # ---------- THEMES / FONT / SCALING ----------

    def setup_themes(self):
        self.style.configure("TFrame", background="#121212")
        self.style.configure("TLabel", background="#121212", foreground="#E0E0E0")
        self.style.configure("TButton", padding=4)
        self.style.configure("TCheckbutton", background="#121212", foreground="#E0E0E0")
        self.style.configure("TRadiobutton", background="#121212", foreground="#E0E0E0")
        self.style.configure("TCombobox")

    def apply_theme(self, theme: str):
        # кольори для кожної теми (bg=фон, fg=текст, accent=активний стан, entry_bg=поля вводу)
        if theme == "dark":
            bg, fg, accent, entry_bg = "#121212", "#E0E0E0", "#03DAC6", "#1E1E1E"
        elif theme == "dark_purple":
            bg, fg, accent, entry_bg = "#14001F", "#E9D8FD", "#9F7AEA", "#1F102A"
        elif theme == "dark_purple_light":
            bg, fg, accent, entry_bg = "#1E1033", "#F2E9FE", "#C4A5FF", "#271242"
        elif theme == "midnight_blue":
            bg, fg, accent, entry_bg = "#020817", "#E0F2FE", "#38BDF8", "#020617"
        elif theme == "midnight":
            bg, fg, accent, entry_bg = "#0B1020", "#E0ECFF", "#4A90E2", "#141A33"
        elif theme == "forest":
            bg, fg, accent, entry_bg = "#022C22", "#ECFDF5", "#34D399", "#064E3B"
        elif theme == "solarized":
            bg, fg, accent, entry_bg = "#002B36", "#EEE8D5", "#B58900", "#073642"
        elif theme == "sunset":  # 🥭 ніжний персиковий
            bg, fg, accent, entry_bg = "#F8EDE3", "#5D4037", "#FFCCBC", "#F5E1D8"
        elif theme == "amber":
            bg, fg, accent, entry_bg = "#FFF8E1", "#4E342E", "#FFB300", "#FFF3C4"
        elif theme == "darkula":
            bg, fg, accent, entry_bg = "#2B2B2B", "#A9B7C6", "#FFA500", "#323232"
        elif theme == "jungle":
            bg, fg, accent, entry_bg = "#062821", "#E9F5F0", "#00C896", "#0A3A30"
        elif theme == "moon":  # 🌙 ЦІКАВИЙ холодний сріблястий "білий"
            bg, fg, accent, entry_bg = "#0A0F1A", "#F0F8FF", "#E0F7FA", "#1A2338"
        elif theme == "crescent_moon":  # 🩸 КРОВАВИЙ місяць
            bg, fg, accent, entry_bg = "#1A0505", "#F5E1E2", "#D32F2F", "#2A0F10"
        elif theme == "monokai":
            bg, fg, accent, entry_bg = "#272822", "#F8F8F2", "#FD971F", "#3E3D32"
        elif theme == "nord":
            bg, fg, accent, entry_bg = "#2E3440", "#E5E9F0", "#88C0D0", "#3B4252"
        elif theme == "cyberpunk":  # 💻 ЯСKРАВИЙ НЕОН Cyberpunk 2077
            bg, fg, accent, entry_bg = "#0A0015", "#E8F0FF", "#FF00FF", "#1A0033"
        elif theme == "desert":  # ☀️ ніжний сонячно-жовтий
            bg, fg, accent, entry_bg = "#FFF8E1", "#7D5A3F", "#FFF59D", "#FFF2C1"
        elif theme == "sakura":  # 🌸 ніжний рожевий
            bg, fg, accent, entry_bg = "#F3E8F1", "#5C2D4A", "#F8BBD9", "#F1D4E5"
        elif theme == "lightspeed":
            bg, fg, accent, entry_bg = "#020617", "#E5F0FF", "#22D3EE", "#02081F"
        else:  # light
            bg, fg, accent, entry_bg = "#FFFFFF", "#202020", "#1E88E5", "#FFFFFF"

        # основний фон вікна
        self.configure(bg=bg)
        if hasattr(self, "canvas"):
            self.canvas.configure(background=bg, highlightthickness=0)

        # базові стилі ttk
        self.style.configure("TFrame", background=bg)
        self.style.configure("TLabel", background=bg, foreground=fg)

        # звичайні кнопки
        self.style.configure("TButton", background=bg, foreground=fg, padding=6)
        self.style.map("TButton", 
            foreground=[("active", fg)], 
            background=[("active", accent)]
        )

        # ✨ СПЕЦІАЛЬНИЙ СТИЛЬ Run.TButton – завжди БІЛИЙ текст + зелений градієнт ✨
        base_run_bg = "#1B5E20"      # темний зелений
        base_run_hover = "#2E7D32"   # світліший зелений
        run_bg = self._blend_color(base_run_bg, bg, 0.5)    # адаптується до теми
        run_hover = self._blend_color(base_run_hover, bg, 0.5)
        run_fg = "#FFFFFF"           # ✅ ЗАВЖДИ БІЛИЙ

        self.style.configure(
            "Run.TButton",
            background=run_bg,
            foreground=run_fg,
            padding=8,      # трохи більша
            relief="raised",
            font=("Segoe UI Bold", 10),  # жирний
        )
        self.style.map(
            "Run.TButton",
            background=[("active", run_hover)],
            foreground=[("active", run_fg)],  # білий і на hover
        )

        # чекбокси та радіо
        self.style.configure("TCheckbutton", background=bg, foreground=fg)
        self.style.map("TCheckbutton", 
            foreground=[("active", fg), ("selected", fg)],
            background=[("active", bg), ("selected", bg)]
        )
        self.style.configure("TRadiobutton", background=bg, foreground=fg)
        self.style.map("TRadiobutton", 
            foreground=[("active", fg), ("selected", fg)],
            background=[("active", bg), ("selected", bg)]
        )

        # поля вводу та комбобокси
        self.style.configure("TCombobox",
            fieldbackground=entry_bg,
            background=entry_bg,
            foreground=fg,
            arrowcolor=fg,
        )
        self.style.map("TCombobox",
            fieldbackground=[("readonly", entry_bg)],
            foreground=[("readonly", fg)],
        )
        self.style.configure("Status.TLabel", foreground=fg, background=bg)

    def apply_font_profile(self, profile: str, scale: float):
        try:
            default_font = tkfont.nametofont("TkDefaultFont")
        except Exception:
            return

        base = self.base_font_size
        factor = scale  # масштаб у відсотках

        family_candidates: List[str] = []
        extra_factor = 1.0

        # підбір сімейства шрифту залежно від профілю
        if profile == "Mono":
            family_candidates = [
                "Cascadia Mono",    # Windows 10+
                "JetBrains Mono",   # кодинговий моно
                "Fira Code",        # з лігатурами
                "Consolas",         # Windows
                "Courier New",
                "Courier",
                default_font.cget("family"),
            ]
        elif profile == "Mono Large":
            family_candidates = [
                "Cascadia Mono",
                "JetBrains Mono",
                "Fira Code",
                "Consolas",
                "Courier New",
                "Courier",
                default_font.cget("family"),
            ]
            extra_factor = 1.2  # +20%
        elif profile == "Mono Small":
            family_candidates = [
                "Cascadia Mono",
                "JetBrains Mono",
                "Fira Code",
                "Consolas",
                "Courier New",
                "Courier",
                default_font.cget("family"),
            ]
            extra_factor = 0.9  # -10%
        elif profile == "Coding":
            family_candidates = [
                "JetBrains Mono",   # топ для кодингу
                "Fira Code",        # лігатури
                "Cascadia Code",
                "Cascadia Mono",
                "Consolas",
                default_font.cget("family"),
            ]
        elif profile == "Large":
            family_candidates = [
                "Segoe UI",
                "Arial",
                "Helvetica",
                default_font.cget("family"),
            ]
            extra_factor = 1.3
        elif profile == "Tiny":
            family_candidates = [
                "Segoe UI",
                "Arial",
                "Helvetica",
                default_font.cget("family"),
            ]
            extra_factor = 0.8
        elif profile == "Serif":
            family_candidates = [
                "Georgia",
                "Times New Roman",
                "Times",
                default_font.cget("family"),
            ]
        elif profile == "Rounded":
            family_candidates = [
                "Calibri",
                "Verdana",
                "Segoe UI",
                default_font.cget("family"),
            ]
        else:  # "Default"
            family_candidates = [
                "Segoe UI",
                "Arial",
                "Helvetica",
                default_font.cget("family"),
            ]

        # обчислюємо розмір і пробуємо застосувати перший доступний шрифт
        size = max(6, int(base * factor * extra_factor))
        
        for fam in family_candidates:
            try:
                default_font.configure(family=fam, size=size)
                break
            except tk.TclError:
                continue  # наступний шрифт

        # глобально застосовуємо через option_add
        self.option_add("*Font", default_font)

        # котик теж адаптується до масштабу (якщо є)
        if self.cat_font is not None:
            self.cat_font.configure(size=max(6, int(10 * factor)))

    def scaling_to_label(self, scale: float) -> str:
        return f"{int(round(scale * 100))}%"

    def label_to_scaling(self, label: str) -> float:
        try:
            value = int(label.strip().strip("%"))
            return max(0.15, min(2.5, value / 100.0))
        except Exception:
            return 1.25

    # ---------- SCROLLABLE CONTAINER + EASTER EGG ----------

    def _build_scrollable_container(self):
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(container, borderwidth=0, highlightthickness=0)
        vscroll = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vscroll.set)

        vscroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.content = ttk.Frame(self.canvas)
        self.content_window = self.canvas.create_window(
            (0, 0), window=self.content, anchor="nw"
        )

        def on_frame_configure(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        def on_canvas_configure(event):
            self.canvas.itemconfig(self.content_window, width=event.width)

        self.content.bind("<Configure>", on_frame_configure)
        self.canvas.bind("<Configure>", on_canvas_configure)

        def _on_mousewheel(event):
            # Ctrl+Scroll → cycle scaling
            ctrl_held = (event.state & 0x4) != 0
            if ctrl_held:
                self._ctrl_scroll_scaling(event)
                return "break"

            delta = int(-1 * (event.delta / 120))
            self.canvas.yview_scroll(delta, "units")
            try:
                first, last = self.canvas.yview()
            except Exception:
                return
            if last >= 0.999 and delta > 0:
                self.scroll_at_bottom_counter += 1
                if self.scroll_at_bottom_counter >= 3 and not self.easter_shown:
                    self.show_easter_egg()
            else:
                self.scroll_at_bottom_counter = 0
            return "break"

        # bind on root window so scroll works regardless of which widget is hovered
        self.bind_all("<MouseWheel>", _on_mousewheel, add="+")

    def show_easter_egg(self):
        self.easter_shown = True
        if self.cat_label is None:
            return

        arts = [
            "✨  *  ✨     ᓚ(=՞^.^՞=)  Lexi cat thanks you under a starry night  ✨  *  ✨",
            "★ ✨    ᓚ( ՞o.o՞ )  code like a cat in the starry sky  ✨ ★",
            "✨    ᓚ(=՞^-^՞=)  Lexi Bundler purrs beneath the glowing stars  ✨",
        ]
        self.cat_label.config(text=random.choice(arts))

    # ---------- history helpers ----------

    def remember_history(self, key: str, value: str):
        value = value.strip()
        if not value:
            return
        hist = self.histories.get(key, [])
        hist = [e for e in hist if e.get("value") != value]
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        hist.insert(0, {"value": value, "ts": ts})
        if len(hist) > HISTORY_MAX_RECENT:
            hist = hist[:HISTORY_MAX_RECENT]
        self.histories[key] = hist

    def _init_history_for(
        self,
        key: str,
        combo: ttk.Combobox,
        label: ttk.Label,
        var: tk.StringVar,
        default: str,
    ):
        hist = self.histories.get(key, [])
        values = [e["value"] for e in hist]
        if default not in values:
            values.append(default)
        combo["values"] = values

        if hist:
            var.set(hist[0]["value"])
            label.config(text=hist[0].get("ts", ""))
        else:
            var.set(default)
            label.config(text="")

        def on_select(event=None):
            val = var.get()
            ts = ""
            for e in self.histories.get(key, []):
                if e["value"] == val:
                    ts = e.get("ts", "")
                    break
            label.config(text=ts)

        combo.bind("<<ComboboxSelected>>", on_select)

    def init_all_histories(self):
        for key, (combo, label, var, default) in self.history_widgets.items():
            self._init_history_for(key, combo, label, var, default)

    # ---------- locale helper ----------

    def t(self, key: str) -> str:
        return LOCALES.get(self.current_lang, LOCALES["en"]).get(key, key)

    def current_flag(self) -> str:
        flags = {
            "en": "🇬🇧",
            "ua": "🇺🇦",
            "pl": "🇵🇱",
            "de": "🇩🇪",
            "es": "🇪🇸",
            "fr": "🇫🇷",
            "it": "🇮🇹",
            "pt": "🇵🇹",
            "ro": "🇷🇴",
            "nl": "🇳🇱",
            "sv": "🇸🇪",
            "tr": "🇹🇷",
            "ja": "🇯🇵",
            "zh": "🇨🇳",
            "ko": "🇰🇷",
            "ar": "🇸🇦",
            "hi": "🇮🇳",
        }
        return flags.get(self.current_lang, "🌐")

    def on_lang_change(self, *_):
        display = self.lang_var.get()
        code = self.lang_display_to_code.get(display, "en")
        self.current_lang = code
        self._apply_locale()
        self.save_config()

    def on_theme_change(self, *_):
        display = self.theme_var.get()
        code = self.theme_display_to_code.get(display, "dark")
        self.current_theme = code
        self.apply_theme(self.current_theme)
        self.save_config()

    def on_font_change(self, *_):
        profile = self.font_var.get()
        if profile not in self.font_profiles:
            profile = "Default"
        self.font_profile = profile
        self.apply_font_profile(self.font_profile, self.scaling_value)
        self.save_config()

    def on_scaling_change(self, *_):
        label = self.scaling_var.get()
        scale = self.label_to_scaling(label)
        self.scaling_value = scale
        # динамічно оновлюємо розмір шрифту
        self.apply_font_profile(self.font_profile, self.scaling_value)
        self.save_config()

    def _ctrl_scroll_scaling(self, event):
        """Ctrl+Scroll up/down → step through scaling_labels list."""
        delta = int(-1 * (event.delta / 120))  # +1 = scroll down = decrease, -1 = increase
        current = self.scaling_var.get()
        labels = self.scaling_labels
        try:
            idx = labels.index(current)
        except ValueError:
            idx = labels.index(self.scaling_to_label(self.scaling_value)) if self.scaling_to_label(self.scaling_value) in labels else len(labels) // 2
        idx = max(0, min(len(labels) - 1, idx - delta))  # scroll up → bigger scale
        self.scaling_var.set(labels[idx])
        # on_scaling_change is triggered via trace

    # ---------- UI ----------

    def _build_ui(self):
        pad = {"padx": 8, "pady": 4}

        # Top bar: language + theme + font + scaling + RUN
        frm_top = ttk.Frame(self.content)
        frm_top.pack(fill="x", **pad)

                # language
        self.lbl_lang = ttk.Label(frm_top, text="Language:")
        self.lbl_lang.pack(side="left")
        lang_values = list(self.lang_display_to_code.keys())
        lang_combo = ttk.Combobox(
            frm_top,
            textvariable=self.lang_var,
            values=lang_values,
            width=6,
            state="readonly",
        )
        lang_combo.pack(side="left", padx=(4, 12))
        self.lang_var.trace_add("write", self.on_lang_change)

        # theme
        self.lbl_theme = ttk.Label(frm_top, text="Theme:")
        self.lbl_theme.pack(side="left")
        theme_values = list(self.theme_display_to_code.keys())
        theme_combo = ttk.Combobox(
            frm_top,
            textvariable=self.theme_var,
            values=theme_values,
            width=14,
            state="readonly",
        )
        theme_combo.pack(side="left", padx=(4, 12))
        self.theme_var.trace_add("write", self.on_theme_change)

        # font profile
        self.lbl_font = ttk.Label(frm_top, text="Font:")
        self.lbl_font.pack(side="left")
        font_combo = ttk.Combobox(
            frm_top,
            textvariable=self.font_var,
            values=self.font_profiles,
            width=10,
            state="readonly",
        )
        font_combo.pack(side="left", padx=(4, 12))
        self.font_var.trace_add("write", self.on_font_change)

        # scaling
        self.lbl_scaling = ttk.Label(frm_top, text="Scaling:")
        self.lbl_scaling.pack(side="left")
        scaling_combo = ttk.Combobox(
            frm_top,
            textvariable=self.scaling_var,
            values=self.scaling_labels,
            width=6,
            state="readonly",
        )
        scaling_combo.pack(side="left", padx=(4, 12))
        self.scaling_var.trace_add("write", self.on_scaling_change)


        # RUN button — трохи більший, одразу після scaling
        self.btn_run = ttk.Button(frm_top, text="", command=self.run, style="Run.TButton")
        self.btn_run.pack(side="left", padx=6)
        self.btn_run.config(width=10)

        # Source root
        frm_src = ttk.Frame(self.content)
        frm_src.pack(fill="x", **pad)
        self.lbl_source_root = ttk.Label(frm_src, text="")
        self.lbl_source_root.pack(anchor="w")
        src_entry_frame = ttk.Frame(frm_src)
        src_entry_frame.pack(fill="x")
        self.src_combo = ttk.Combobox(src_entry_frame, textvariable=self.src_var)
        self.src_combo.pack(side="left", fill="x", expand=True)
        ttk.Button(
            src_entry_frame, text=self.t("browse"), command=self.browse_src
        ).pack(side="left", padx=4)
        ttk.Button(
            src_entry_frame, text=self.t("goto"), command=self.goto_src
        ).pack(side="left", padx=2)
        self.src_hist_label = ttk.Label(src_entry_frame, text="", width=16)
        self.src_hist_label.pack(side="left", padx=4)
        self.history_widgets["src_root"] = (
            self.src_combo,
            self.src_hist_label,
            self.src_var,
            DEFAULT_FIELD_VALUES["src_root"],
        )

        # Shorten path prefix
        frm_short = ttk.Frame(self.content)
        frm_short.pack(fill="x", **pad)
        self.lbl_shorten_prefix = ttk.Label(frm_short, text="")
        self.lbl_shorten_prefix.pack(anchor="w")
        short_entry_frame = ttk.Frame(frm_short)
        short_entry_frame.pack(fill="x")
        self.shorten_combo = ttk.Combobox(short_entry_frame, textvariable=self.shorten_var)
        self.shorten_combo.pack(side="left", fill="x", expand=True)
        ttk.Button(
            short_entry_frame, text=self.t("auto_shorten"), command=self.auto_shorten
        ).pack(side="left", padx=4)
        ttk.Button(
            short_entry_frame, text=self.t("browse"), command=self.browse_shorten
        ).pack(side="left", padx=2)
        self.shorten_hist_label = ttk.Label(short_entry_frame, text="", width=16)
        self.shorten_hist_label.pack(side="left", padx=4)
        self.history_widgets["shorten_root"] = (
            self.shorten_combo,
            self.shorten_hist_label,
            self.shorten_var,
            DEFAULT_FIELD_VALUES["shorten_root"],
        )

        # Output folder
        frm_save = ttk.Frame(self.content)
        frm_save.pack(fill="x", **pad)
        self.lbl_output_folder = ttk.Label(frm_save, text="")
        self.lbl_output_folder.pack(anchor="w")
        save_entry_frame = ttk.Frame(frm_save)
        save_entry_frame.pack(fill="x")
        self.save_combo = ttk.Combobox(save_entry_frame, textvariable=self.save_var)
        self.save_combo.pack(side="left", fill="x", expand=True)
        ttk.Button(
            save_entry_frame, text=self.t("browse"), command=self.browse_save
        ).pack(side="left", padx=4)
        ttk.Button(
            save_entry_frame, text=self.t("goto"), command=self.goto_save
        ).pack(side="left", padx=2)
        self.save_hist_label = ttk.Label(save_entry_frame, text="", width=16)
        self.save_hist_label.pack(side="left", padx=4)
        self.history_widgets["save_root"] = (
            self.save_combo,
            self.save_hist_label,
            self.save_var,
            DEFAULT_FIELD_VALUES["save_root"],
        )

        # Extensions include/exclude
        frm_ext = ttk.Frame(self.content)
        frm_ext.pack(fill="x", **pad)
        self.lbl_include_ext = ttk.Label(frm_ext, text="")
        self.lbl_include_ext.pack(anchor="w")
        self.include_combo = ttk.Combobox(frm_ext, textvariable=self.ext_include_var)
        self.include_combo.pack(fill="x")
        self.include_hist_label = ttk.Label(frm_ext, text="", width=16)
        self.include_hist_label.pack(anchor="e", pady=(0, 2))
        self.history_widgets["include_ext"] = (
            self.include_combo,
            self.include_hist_label,
            self.ext_include_var,
            DEFAULT_FIELD_VALUES["include_ext"],
        )

        self.lbl_exclude_ext = ttk.Label(frm_ext, text="")
        self.lbl_exclude_ext.pack(anchor="w")
        self.exclude_combo = ttk.Combobox(frm_ext, textvariable=self.ext_exclude_var)
        self.exclude_combo.pack(fill="x")
        self.exclude_hist_label = ttk.Label(frm_ext, text="", width=16)
        self.exclude_hist_label.pack(anchor="e", pady=(0, 2))
        self.history_widgets["exclude_ext"] = (
            self.exclude_combo,
            self.exclude_hist_label,
            self.ext_exclude_var,
            DEFAULT_FIELD_VALUES["exclude_ext"],
        )


        # Exclude dirs / files
        frm_excl = ttk.Frame(self.content)
        frm_excl.pack(fill="x", **pad)
        self.lbl_exclude_dirs = ttk.Label(frm_excl, text="")
        self.lbl_exclude_dirs.pack(anchor="w")
        self.exclude_dirs_combo = ttk.Combobox(
            frm_excl, textvariable=self.exclude_dirs_var
        )
        self.exclude_dirs_combo.pack(fill="x")
        self.exclude_dirs_hist_label = ttk.Label(frm_excl, text="", width=16)
        self.exclude_dirs_hist_label.pack(anchor="e", pady=(0, 2))
        self.history_widgets["exclude_dirs"] = (
            self.exclude_dirs_combo,
            self.exclude_dirs_hist_label,
            self.exclude_dirs_var,
            DEFAULT_FIELD_VALUES["exclude_dirs"],
        )

        self.lbl_exclude_files = ttk.Label(frm_excl, text="")
        self.lbl_exclude_files.pack(anchor="w")
        self.exclude_files_combo = ttk.Combobox(
            frm_excl, textvariable=self.exclude_files_var
        )
        self.exclude_files_combo.pack(fill="x")
        self.exclude_files_hist_label = ttk.Label(frm_excl, text="", width=16)
        self.exclude_files_hist_label.pack(anchor="e", pady=(0, 2))
        self.history_widgets["exclude_files"] = (
            self.exclude_files_combo,
            self.exclude_files_hist_label,
            self.exclude_files_var,
            DEFAULT_FIELD_VALUES["exclude_files"],
        )

        # Modes
        frm_mode = ttk.Frame(self.content)
        frm_mode.pack(fill="x", **pad)
        self.lbl_mode = ttk.Label(frm_mode, text="")
        self.lbl_mode.pack(anchor="w")

        self.rb_all = ttk.Radiobutton(
            frm_mode,
            text="",
            variable=self.mode_var,
            value="all",
            command=self._toggle_mode_widgets,
        )
        self.rb_per = ttk.Radiobutton(
            frm_mode,
            text="",
            variable=self.mode_var,
            value="per_folder",
            command=self._toggle_mode_widgets,
        )
        self.rb_all.pack(anchor="w")
        self.rb_per.pack(anchor="w")

        # Mode-specific options
        frm_mode_opts = ttk.Frame(self.content)
        frm_mode_opts.pack(fill="x", **pad)
        self.frm_mode_opts = frm_mode_opts

        # For mode=all – output file name
        self.frm_all_name = ttk.Frame(frm_mode_opts)
        self.lbl_output_name = ttk.Label(self.frm_all_name, text="")
        self.lbl_output_name.pack(anchor="w")
        output_entry_frame = ttk.Frame(self.frm_all_name)
        output_entry_frame.pack(fill="x")
        self.output_name_combo = ttk.Combobox(
            output_entry_frame, textvariable=self.output_name_var
        )
        self.output_name_combo.pack(side="left", fill="x", expand=True)
        self.output_name_hist_label = ttk.Label(output_entry_frame, text="", width=16)
        self.output_name_hist_label.pack(side="left", padx=4)
        self.history_widgets["output_name"] = (
            self.output_name_combo,
            self.output_name_hist_label,
            self.output_name_var,
            DEFAULT_FIELD_VALUES["output_name"],
        )

        # For mode=per_folder – include root files
        self.frm_per_root = ttk.Frame(frm_mode_opts)
        self.chk_include_root = ttk.Checkbutton(
            self.frm_per_root,
            text="",
            variable=self.include_root_files_var,
        )
        self.chk_include_root.pack(anchor="w")

        self._toggle_mode_widgets()

        # Separator option
        frm_sep = ttk.Frame(self.content)
        frm_sep.pack(fill="x", **pad)
        self.chk_separator = ttk.Checkbutton(
            frm_sep,
            text="",
            variable=self.add_separator_var,
        )
        self.chk_separator.pack(anchor="w")

        # List only names
        frm_names = ttk.Frame(self.content)
        frm_names.pack(fill="x", **pad)
        self.chk_list_only_names = ttk.Checkbutton(
            frm_names,
            text="",
            variable=self.list_only_names_var,
        )
        self.chk_list_only_names.pack(anchor="w")

        # статус бар – ніжно-білий З ЧОРНОЮ ТІННЮ
        self.style.configure(
            "Status.TLabel",
            #foreground="#F5F5F5",           # білий текст
            #background="#cccccc",         # напівпрозорий темний фон
            font=("TkDefaultFont", 11, "bold"),
            relief="sunken",                # вдавлена рамка
            borderwidth=1,
            padding=(10, 5),
        )
        # Status bar внизу – ніжно-білий
        self.status_var = tk.StringVar(value="")
        self.lbl_status = ttk.Label(self.content, textvariable=self.status_var)
        self.lbl_status.configure(style="Status.TLabel")  # динамічно застосовуємо
        self.lbl_status.pack(anchor="w", padx=8, pady=4)

        # порожній простір + котик (моношрифт)
        spacer = ttk.Frame(self.content)
        spacer.pack(fill="both", expand=True, pady=10)

        cat_frame = ttk.Frame(self.content)
        cat_frame.pack(fill="x", pady=10)
        self.cat_label = ttk.Label(cat_frame, text="", anchor="center", justify="center")
        self.cat_label.pack(anchor="center", pady=10)

        # моношрифт для ASCII, незалежний від профілю
        try:
            self.cat_font = tkfont.Font(family="Consolas", size=10)
        except Exception:
            self.cat_font = tkfont.Font(family="Courier New", size=10)
        self.cat_label.configure(font=self.cat_font)

        def _combo_scroll_redirect(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            return "break"  # prevent combobox from also scrolling itself

        for cb in (lang_combo, theme_combo, font_combo, scaling_combo,
                   self.src_combo, self.save_combo, self.shorten_combo,
                   self.include_combo, self.exclude_combo,
                   self.exclude_dirs_combo, self.exclude_files_combo,
                   self.output_name_combo):
            cb.bind("<MouseWheel>", _combo_scroll_redirect, add="+")

        

    def _apply_locale(self):
        self.title(self.t("title"))

        self.lbl_lang.config(
            text=f"{EMOJI['language']} {self.current_flag()} {self.t('lang_label')}"
        )
        self.lbl_theme.config(
            text=f"{EMOJI['theme']} {self.t('theme_label')}"
        )
        self.lbl_font.config(
            text=f"{EMOJI['font']} {self.t('font_label')}"
        )
        self.lbl_scaling.config(
            text=f"{EMOJI['scaling']} {self.t('scaling_label')}"
        )

        self.lbl_source_root.config(
            text=f"{EMOJI['source_root']} {self.t('source_root_label')}"
        )
        self.lbl_output_folder.config(
            text=f"{EMOJI['output_folder']} {self.t('output_folder_label')}"
        )
        self.lbl_shorten_prefix.config(
            text=f"{EMOJI['shorten_prefix']} {self.t('shorten_prefix_label')}"
        )
        self.lbl_include_ext.config(
            text=f"{EMOJI['include_ext']} {self.t('include_ext_label')}"
        )
        self.lbl_exclude_ext.config(
            text=f"{EMOJI['exclude_ext']} {self.t('exclude_ext_label')}"
        )
        self.lbl_exclude_dirs.config(
            text=f"{EMOJI['exclude_dirs']} {self.t('exclude_dirs_label')}"
        )
        self.lbl_exclude_files.config(
            text=f"{EMOJI['exclude_files']} {self.t('exclude_files_label')}"
        )
        self.lbl_mode.config(
            text=f"{EMOJI['mode']} {self.t('mode_label')}"
        )
        self.rb_all.config(text=self.t("mode_all"))
        self.rb_per.config(text=self.t("mode_per_folder"))
        self.lbl_output_name.config(
            text=f"{EMOJI['output_name']} {self.t('output_name_label')}"
        )
        self.chk_include_root.config(
            text=f"{EMOJI['include_root_files']} {self.t('include_root_files_label')}"
        )
        self.chk_separator.config(
            text=f"{EMOJI['separator']} {self.t('separator_label')}"
        )
        self.chk_list_only_names.config(
            text=f"{EMOJI['list_only_names']} {self.t('list_only_names_label')}"
        )

        self.btn_run.config(text=self.t("run"))
        self.status_var.set(self.t("status_ready"))

    def _toggle_mode_widgets(self):
        for child in self.frm_mode_opts.winfo_children():
            child.pack_forget()
        if self.mode_var.get() == "all":
            self.frm_all_name.pack(fill="x")
        else:
            self.frm_per_root.pack(fill="x")

    # ---------- browse / goto / auto shorten ----------

    def browse_src(self):
        folder = filedialog.askdirectory(title=self.t("source_root_label"))
        if folder:
            self.src_var.set(folder)

    def goto_src(self):
        path_str = self.src_var.get().strip()
        if not path_str:
            messagebox.showwarning(
                self.t("warning_title"), self.t("warn_source_empty")
            )
            return
        open_in_explorer(path_str)

    def browse_save(self):
        folder = filedialog.askdirectory(title=self.t("output_folder_label"))
        if folder:
            self.save_var.set(folder)

    def goto_save(self):
        path_str = self.save_var.get().strip()
        if not path_str:
            messagebox.showwarning(
                self.t("warning_title"), self.t("err_output_path_empty")
            )
            return
        open_in_explorer(path_str)

    def browse_shorten(self):
        folder = filedialog.askdirectory(title=self.t("shorten_prefix_label"))
        if folder:
            self.shorten_var.set(folder)

    def auto_shorten(self):
        """
        Try to pick a good shorten_root automatically:

        1) If the source is under a well‑known workspace folder
           (Downloads, Desktop, Documents, WebstormProjects, Projects, etc.),
           cut at that folder.
        2) Otherwise, if it's inside the user's home, cut at home.
        3) Otherwise, try to detect a project root (.git/.idea/.vscode/package.json/pyproject.toml).
        4) Fallback to drive root (Windows) or "/" (POSIX).
        """
        src = self.src_var.get().strip()
        if not src:
            messagebox.showwarning(
                self.t("warning_title"),
                self.t("warn_source_empty"),
            )
            return

        try:
            p = Path(src).expanduser().resolve()
        except Exception:
            return

        parts = p.parts

        # Workspace‑like folder names (you can extend this set any time).
        workspace_keywords = {
            "Downloads", "Desktop", "Documents",
            "WebstormProjects", "IdeaProjects",
            "Projects", "Project", "Workspace",
            "source", "src",
            "Завантаження", "Робочий стіл", "Документи",
        }

        chosen: Optional[Path] = None

        # 1) Cut at a workspace keyword, e.g.
        #    C:\Users\Admin\WebstormProjects\MyApp\src -> C:\Users\Admin\WebstormProjects
        for i, part in enumerate(parts):
            if part in workspace_keywords:
                chosen = Path(*parts[: i + 1])
                break

        # 2) If nothing found, but it's under the user's home, use home
        home = None
        try:
            home = Path.home().resolve()
        except Exception:
            pass

        if chosen is None and home is not None:
            try:
                p.relative_to(home)
            except ValueError:
                pass
            else:
                chosen = home

        # 3) Try to detect a project root by marker files/dirs
        if chosen is None:
            markers = {
                ".git", ".idea", ".vscode",
                "package.json", "pyproject.toml", "Pipfile",
            }
            cur = p if p.is_dir() else p.parent
            while True:
                try:
                    names = {child.name for child in cur.iterdir()}
                except Exception:
                    names = set()

                if markers & names:
                    # Use parent of project root as shorten_root,
                    # so bundled paths start with the project folder name.
                    chosen = cur.parent if cur.parent != cur else cur
                    break

                if cur.parent == cur:
                    break
                cur = cur.parent

        # 4) Final fallback: drive root or "/"
        if chosen is None:
            if os.name == "nt" and parts:
                chosen = Path(parts[0])   # e.g. 'C:\\'
            else:
                chosen = Path("/")

        self.shorten_var.set(str(chosen))
        self.remember_history("shorten_root", str(chosen))
        self.save_config()

    # ---------- RUN ----------

    def run(self):
        try:
            self.status_var.set(self.t("status_running"))
            self.update_idletasks()

            src_root_str = self.src_var.get().strip()
            if not src_root_str:
                messagebox.showerror(self.t("error_title"), self.t("err_source_not_set"))
                return
            src_root = Path(src_root_str).expanduser().resolve()
            if not src_root.is_dir():
                messagebox.showerror(
                    self.t("error_title"), self.t("err_source_not_dir")
                )
                return

            save_root_str = self.save_var.get().strip()
            if save_root_str:
                save_root = Path(save_root_str).expanduser().resolve()
            else:
                save_root = src_root

            shorten_str = self.shorten_var.get().strip()
            shorten_root = (
                Path(shorten_str).expanduser().resolve() if shorten_str else None
            )

            include_ext = parse_ext_list(self.ext_include_var.get().strip())
            exclude_ext = parse_ext_list(self.ext_exclude_var.get().strip())
            exclude_dirs = parse_name_list(self.exclude_dirs_var.get())
            exclude_files = parse_name_list(self.exclude_files_var.get())

            mode = self.mode_var.get()
            add_sep = self.add_separator_var.get()
            list_only_names = self.list_only_names_var.get()

            # історія
            self.remember_history("src_root", self.src_var.get())
            self.remember_history("save_root", self.save_var.get())
            self.remember_history("shorten_root", self.shorten_var.get())
            self.remember_history("include_ext", self.ext_include_var.get())
            self.remember_history("exclude_ext", self.ext_exclude_var.get())
            self.remember_history("exclude_dirs", self.exclude_dirs_var.get())
            self.remember_history("exclude_files", self.exclude_files_var.get())
            self.remember_history("output_name", self.output_name_var.get())
            self.save_config()

            if mode == "all":
                output_name = (
                    self.output_name_var.get().strip() or "all_sources.txt"
                )
                out_file = bundle_mode_all(
                    src_root=src_root,
                    save_root=save_root,
                    output_name=output_name,
                    include_ext=include_ext,
                    exclude_ext=exclude_ext,
                    shorten_root=shorten_root,
                    exclude_dirs=exclude_dirs,
                    exclude_files=exclude_files,
                    add_separator=add_sep,
                    list_only_names=list_only_names,
                )
                msg = self.t("success_one").format(path=out_file)
                full_msg = msg + "\n\nOpen output folder?"

                if messagebox.askyesno(self.t("success_title"), full_msg):
                    # open_in_explorer will normalize file -> parent directory
                    open_in_explorer(str(out_file))

                self.status_var.set(self.t("status_ready"))
            else:
                written = bundle_mode_per_top_folder(
                    src_root=src_root,
                    save_root=save_root,
                    include_ext=include_ext,
                    exclude_ext=exclude_ext,
                    shorten_root=shorten_root,
                    include_root_files=self.include_root_files_var.get(),
                    exclude_dirs=exclude_dirs,
                    exclude_files=exclude_files,
                    add_separator=add_sep,
                    list_only_names=list_only_names,
                )

                if not written:
                    msg = self.t("no_files")
                    messagebox.showinfo(self.t("result_title"), msg)
                else:
                    msg = self.t("success_many").format(
                        paths="\n".join(str(p) for p in written)
                    )
                    full_msg = msg + "\n\nOpen output folder?"
                    if messagebox.askyesno(self.t("result_title"), full_msg):
                        # open the common save_root folder
                        open_in_explorer(str(save_root))

                self.status_var.set(self.t("status_ready"))

            self.init_all_histories()
        except Exception as e:
            self.status_var.set(self.t("status_ready"))
            messagebox.showerror(self.t("error_title"), str(e))

    def on_close(self):
        self.save_config()
        self.destroy()


if __name__ == "__main__":
    app = BundleApp()
    app.mainloop()

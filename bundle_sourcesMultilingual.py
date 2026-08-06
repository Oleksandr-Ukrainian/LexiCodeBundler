# -*- coding: utf-8 -*-
import os
import re
import json
import random
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional, Set, Dict, List, Tuple

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font as tkfont

CONFIG_PATH = Path.home() / ".lexicode_bundler_config.json"
HISTORY_MAX_RECENT = 25
CONFIG_EXPORT_SCHEMA = 1

DEFAULT_EXCLUDE_DIRS = {
    ".git", ".idea", ".vscode", "node_modules", "dist", "build",
    "coverage", "public", ".next", "out", ".turbo", "venv", ".venv",
}

DEFAULT_EXCLUDE_FILES = {
    ".dockerignore", ".gitignore", "README", "README.md", "LICENSE",
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "pnpm-lock.yml",
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

LEXI_CAT_MESSAGES = [
    "    ᓚ(=՞^.^՞=) Lexi cat meows at you under a starry night   ",
    "    ᓚ(=^• ω •^=) Lexi cat found a bug... and ate it   ",
    "    ᓚ(=^-ω-^=) Lexi cat is napping on your source code   ",
    "    ᓚ(=òωó=) Lexi cat demands more RAM   ",
    "    ᓚ(=^∇^=) Lexi cat bundled 9 lives successfully   ",
    "    ᓚ(=^ ͟ʖ^=) Lexi cat stares into the void of noodle_modules   ",
    "    ᓚ(=^-^=)ﾉ Lexi cat waves goodbye to your .git folder   ",
    "    ᓚ(=ΦωΦ=) Lexi cat is scanning the directory tree   ",
    "    ᓚ(=^ↀωↀ^=) Lexi cat knocked your output file off the desk   ",
    "    ᓚ(=｀ω´=) Lexi cat refuses to exclude .log files   ",
    "    ᓚ(=^o^=)~ Lexi cat is dreaming of infinite loops   ",
    "    ᓚ(=^·ω·^=) Lexi cat purrs at 3000 lines per second   ",
]

DEFAULT_FIELD_VALUES = {
    "src_root": "",
    "save_root": "",
    "shorten_root": "",
    "include_ext": "",
    "exclude_ext": ",".join(sorted(e.lstrip(".") for e in DEFAULT_EXCLUDE_EXTS)),
    "exclude_dirs": ",".join(sorted(DEFAULT_EXCLUDE_DIRS)),
    "exclude_files": ",".join(sorted(DEFAULT_EXCLUDE_FILES)),
    "output_name": "all_sources.txt",
    "copy_out_folder": "",
    "unbundle_src": "",
    "unbundle_out": "",
    "unbundle_ext": "",
    "unbundle_shorten": "",
}

LOCALES: Dict[str, Dict[str, str]] = {
    'en': {
        'title': 'LexiCode Bundler',
        'lang_label': 'Language:',
        'theme_label': 'Theme:',
        'font_label': 'Font:',
        'scaling_label': 'Scaling:',
        'action_label': 'Action:',
        'action_bundle': 'Bundle',
        'action_unbundle': 'Unbundle',
        'source_root_label': 'Source root (e.g. ...\\src):',
        'output_folder_label': 'Output folder (empty = same as source):',
        'shorten_prefix_label': 'Shorten path prefix (optional):',
        'include_ext_label': 'Include extensions (e.g. py,ts; empty = all):',
        'exclude_ext_label': 'Exclude extensions (comma separated, e.g. png,jpg,log):',
        'exclude_dirs_label': 'Exclude directories by name (comma separated):',
        'exclude_files_label': 'Exclude files by name (comma separated):',
        'output_ext_label': 'Output file extension:',
        'mode_label': 'Mode:',
        'mode_all': '1) One big file for the whole tree',
        'mode_copy_tree': '2) Copy full project tree',
        'mode_per_folder': '3) One bundle per folder',
        'output_name_label': 'Output file name (for mode 1):',
        'copy_out_label': 'Copy output folder (for mode 2):',
        'include_root_files_label': 'Also bundle loose files in root (e.g. extension.ts)',
        'separator_label': 'Add separator line between files',
        'list_only_names_label': 'List only names (no file contents)',
        'unbundle_src_label': 'Folder with bundle files:',
        'unbundle_out_label': 'Reconstruct into folder:',
        'unbundle_shorten_label': 'Strip path prefix (empty = keep full path from header):',
        'unbundle_ext_label': 'Override output extension (empty = use original from header):',
        'browse': 'Browse',
        'goto': 'Go to',
        'auto_shorten': 'Auto',
        'run': 'Run',
        'status_ready': 'Ready',
        'status_running': 'Running...',
        'err_source_not_set': 'Source folder is not set.',
        'err_source_not_dir': 'Source folder does not exist or is not a directory.',
        'err_output_path_empty': 'Output path is empty.',
        'warn_source_empty': 'Source path is empty.',
        'success_one': 'Done. Created file:\n{path}',
        'success_many': 'Done. Created files:\n{paths}',
        'no_files': 'No files found for the given filters.',
        'error_title': 'Error',
        'success_title': 'Success',
        'result_title': 'Result',
        'warning_title': 'Warning',
        'unbundle_success': 'Unbundled {n} file(s) into:\n{path}',
        'unbundle_no_files': 'No bundle files found in the source folder.',
        'err_unbundle_src_empty': 'Unbundle source folder is not set.',
        'err_unbundle_out_empty': 'Reconstruct-to folder is not set.',
        'profiles_label': 'Profile',
        'import_all': 'Import',
        'export_all': 'Export',
        'import_success': 'Settings imported successfully.',
        'export_success': 'Settings exported successfully:\\n{path}',
        'import_invalid': 'Selected file is not a valid LexiCode config export.',
        'import_confirm': 'Import settings and memories from file? This will replace current UI state.',
        'open_output_folder': 'Open output folder?',
        'clear_field': 'Clear current field value',
        'explorer': 'Explorer'
    },
    'ua': {
        'title': 'LexiCode Bundler',
        'lang_label': 'Мова:',
        'theme_label': 'Тема:',
        'font_label': 'Шрифт:',
        'scaling_label': 'Масштаб:',
        'action_label': 'Дія:',
        'action_bundle': 'Бандл',
        'action_unbundle': 'Розбандл',
        'source_root_label': 'Source root (наприклад, ...\\src):',
        'output_folder_label': 'Папка збереження (пусто = як source):',
        'shorten_prefix_label': 'Префікс для скорочення шляху (опційно):',
        'include_ext_label': 'Include розширення (наприклад: py,ts; пусто = всі):',
        'exclude_ext_label': 'Exclude розширення (через кому, напр. png,jpg,log):',
        'exclude_dirs_label': 'Ігнорувати папки (імена через кому):',
        'exclude_files_label': 'Ігнорувати файли (імена через кому):',
        'output_ext_label': 'Розширення вихідного файлу:',
        'mode_label': 'Режим:',
        'mode_all': '1) Один великий файл для всього дерева',
        'mode_copy_tree': '2) Копія дерева проєкту',
        'mode_per_folder': '3) Окремий файл для кожної верхньої папки',
        'output_name_label': "Ім'я вихідного файлу (для режиму 1):",
        'copy_out_label': 'Папка для копії дерева (режим 2):',
        'include_root_files_label': 'Додати також файли з кореня (наприклад extension.ts)',
        'separator_label': 'Додавати роздільну лінію між файлами',
        'list_only_names_label': 'Лише список імен (без коду всередині)',
        'unbundle_src_label': 'Папка з бандл-файлами:',
        'unbundle_out_label': 'Відновити у папку:',
        'unbundle_shorten_label': 'Відрізати префікс шляху (пусто = зберегти повний шлях):',
        'unbundle_ext_label': 'Замінити розширення (пусто = оригінал з заголовку):',
        'browse': 'Обрати',
        'goto': 'Перейти',
        'auto_shorten': 'Авто',
        'run': 'Запустити',
        'status_ready': 'Готово',
        'status_running': 'Працюю...',
        'err_source_not_set': 'Source-папка не вказана.',
        'err_source_not_dir': 'Source-папка не існує або це не папка.',
        'err_output_path_empty': 'Путь збереження порожній.',
        'warn_source_empty': 'Source-путь порожній.',
        'success_one': 'Готово. Створено файл:\n{path}',
        'success_many': 'Готово. Створено файли:\n{paths}',
        'no_files': 'Не знайдено файлів з такими фільтрами.',
        'error_title': 'Помилка',
        'success_title': 'OK',
        'result_title': 'Результат',
        'warning_title': 'Увага',
        'unbundle_success': 'Розбандловано {n} файл(ів) у:\n{path}',
        'unbundle_no_files': 'Бандл-файли не знайдено у вказаній папці.',
        'err_unbundle_src_empty': 'Папка з бандлами не вказана.',
        'err_unbundle_out_empty': 'Папка відновлення не вказана.',
        'profiles_label': 'Профіль',
        'import_all': 'Імпорт',
        'export_all': 'Експорт',
        'import_success': 'Налаштування успішно імпортовано.',
        'export_success': 'Налаштування успішно експортовано:\n{path}',
        'import_invalid': 'Вибраний файл не є дійсним експортом конфігурації LexiCode.',
        'import_confirm': 'Імпортувати налаштування та пам’ять із файлу? Це замінить поточний стан інтерфейсу.',
        'open_output_folder': 'Відкрити папку результату?',
        'clear_field': 'Очистити поточне значення поля',
        'explorer': 'Провідник'
    },
    'pl': {
        'title': 'LexiCode Bundler',
        'lang_label': 'Język:',
        'theme_label': 'Motyw:',
        'font_label': 'Czcionka:',
        'scaling_label': 'Skalowanie:',
        'action_label': 'Akcja:',
        'action_bundle': 'Bundluj',
        'action_unbundle': 'Rozbundluj',
        'source_root_label': 'Główny katalog źródłowy (np. ...\\src):',
        'output_folder_label': 'Katalog wyjściowy (pusty = taki sam jak źródłowy):',
        'shorten_prefix_label': 'Skróć prefiks ścieżki (opcjonalne):',
        'include_ext_label': 'Rozszerzenia do włączenia (np. py,ts; puste = wszystkie):',
        'exclude_ext_label': 'Rozszerzenia do wykluczenia (przecinkami, np. png,jpg,log):',
        'exclude_dirs_label': 'Wyklucz katalogi po nazwie (przecinkami):',
        'exclude_files_label': 'Wyklucz pliki po nazwie (przecinkami):',
        'output_ext_label': 'Rozszerzenie pliku wyjściowego:',
        'mode_label': 'Tryb:',
        'mode_all': '1) Jeden duży plik dla całego drzewa',
        'mode_copy_tree': '2) Kopia drzewa projektu',
        'mode_per_folder': '3) Jeden plik na folder najwyższego poziomu',
        'output_name_label': 'Nazwa pliku wyjściowego (dla trybu 1):',
        'copy_out_label': 'Katalog dla kopii drzewa (tryb 2):',
        'include_root_files_label': 'Również pakuj luźne pliki w katalogu głównym',
        'separator_label': 'Dodaj linię separatora między plikami',
        'list_only_names_label': 'Tylko lista nazw (bez zawartości plików)',
        'unbundle_src_label': 'Folder z plikami bundle:',
        'unbundle_out_label': 'Odtwórz do folderu:',
        'unbundle_shorten_label': 'Usuń prefiks ścieżki (puste = zachowaj pełną ścieżkę):',
        'unbundle_ext_label': 'Zastąp rozszerzenie (puste = oryginalne z nagłówka):',
        'browse': 'Przeglądaj',
        'goto': 'Idź do',
        'auto_shorten': 'Auto',
        'run': 'Uruchom',
        'status_ready': 'Gotowy',
        'status_running': 'Działam...',
        'err_source_not_set': 'Katalog źródłowy nie jest ustawiony.',
        'err_source_not_dir': 'Katalog źródłowy nie istnieje lub nie jest katalogiem.',
        'err_output_path_empty': 'Ścieżka wyjściowa jest pusta.',
        'warn_source_empty': 'Ścieżka źródłowa jest pusta.',
        'success_one': 'Gotowe. Utworzono plik:\n{path}',
        'success_many': 'Gotowe. Utworzono pliki:\n{paths}',
        'no_files': 'Nie znaleziono plików dla podanych filtrów.',
        'error_title': 'Błąd',
        'success_title': 'Sukces',
        'result_title': 'Wynik',
        'warning_title': 'Ostrzeżenie',
        'unbundle_success': 'Rozbundlowano {n} plik(ów) do:\n{path}',
        'unbundle_no_files': 'Nie znaleziono plików bundle w źródle.',
        'err_unbundle_src_empty': 'Folder źródłowy bundle nie jest ustawiony.',
        'err_unbundle_out_empty': 'Folder docelowy nie jest ustawiony.',
        'profiles_label': 'Profil',
        'import_all': 'Importuj',
        'export_all': 'Eksportuj',
        'import_success': 'Ustawienia zostały pomyślnie zaimportowane.',
        'export_success': 'Ustawienia zostały pomyślnie wyeksportowane:\n{path}',
        'import_invalid': 'Wybrany plik nie jest prawidłowym eksportem konfiguracji LexiCode.',
        'import_confirm': 'Importować ustawienia i pamięć z pliku? Spowoduje to zastąpienie bieżącego stanu interfejsu.',
        'open_output_folder': 'Otworzyć folder wyjściowy?',
        'clear_field': 'Wyczyść bieżącą wartość pola',
        'explorer': 'Eksplorator'
    },
    'de': {
        'title': 'LexiCode Bundler',
        'lang_label': 'Sprache:',
        'theme_label': 'Thema:',
        'font_label': 'Schriftart:',
        'scaling_label': 'Skalierung:',
        'action_label': 'Aktion:',
        'action_bundle': 'Bündeln',
        'action_unbundle': 'Entbündeln',
        'source_root_label': 'Quellordner (z.B. ...\\\\src):',
        'output_folder_label': 'Ausgabeordner (leer = wie Quelle):',
        'shorten_prefix_label': 'Pfad-Präfix kürzen (optional):',
        'include_ext_label': 'Erweiterungen einbeziehen (z.B. py,ts; leer = alle):',
        'exclude_ext_label': 'Erweiterungen ausschließen (kommagetrennt, z.B. png,jpg,log):',
        'exclude_dirs_label': 'Verzeichnisse nach Namen ausschließen (kommagetrennt):',
        'exclude_files_label': 'Dateien nach Namen ausschließen (kommagetrennt):',
        'output_ext_label': 'Ausgabe-Dateiendung:',
        'mode_label': 'Modus:',
        'mode_all': '1) Eine große Datei für den gesamten Baum',
        'mode_copy_tree': '2) Komplettes Projektbaum kopieren',
        'mode_per_folder': '3) Eine Datei pro obersten Ordner',
        'output_name_label': 'Ausgabedatei-Name (für Modus 1):',
        'copy_out_label': 'Ausgabeordner (Modus 2):',
        'include_root_files_label': 'Auch lose Dateien im Root bündeln (z.B. extension.ts)',
        'separator_label': 'Trennlinie zwischen Dateien hinzufügen',
        'list_only_names_label': 'Nur Namen auflisten (ohne Dateiinhalte)',
        'unbundle_src_label': 'Ordner mit Bundle-Dateien:',
        'unbundle_out_label': 'Wiederherstellen in Ordner:',
        'unbundle_shorten_label': 'Pfad-Präfix entfernen (leer = vollständigen Pfad aus Kopfzeile behalten):',
        'unbundle_ext_label': 'Erweiterung überschreiben (leer = Original):',
        'browse': 'Durchsuchen',
        'goto': 'Gehe zu',
        'auto_shorten': 'Auto',
        'run': 'Starten',
        'status_ready': 'Bereit',
        'status_running': 'Laufe...',
        'err_source_not_set': 'Quellordner nicht gesetzt.',
        'err_source_not_dir': 'Quellordner existiert nicht oder ist kein Ordner.',
        'err_output_path_empty': 'Ausgabepfad ist leer.',
        'warn_source_empty': 'Quellpfad ist leer.',
        'success_one': 'Fertig. Datei erstellt:\n{path}',
        'success_many': 'Fertig. Dateien erstellt:\n{paths}',
        'no_files': 'Keine Dateien für die angegebenen Filter gefunden.',
        'error_title': 'Fehler',
        'success_title': 'Erfolg',
        'result_title': 'Ergebnis',
        'warning_title': 'Warnung',
        'unbundle_success': '{n} Datei(en) entbündelt nach:\n{path}',
        'unbundle_no_files': 'Keine Bundle-Dateien gefunden.',
        'err_unbundle_src_empty': 'Bundle-Quellordner nicht gesetzt.',
        'err_unbundle_out_empty': 'Zielordner nicht gesetzt.',
        'profiles_label': 'Profil',
        'export_all': 'Exportieren',
        'import_all': 'Importieren',
        'import_success': 'Einstellungen erfolgreich importiert.',
        'export_success': 'Einstellungen erfolgreich exportiert:\n{path}',
        'import_invalid': 'Die ausgewählte Datei ist kein gültiger LexiCode-Konfigurationsexport.',
        'import_confirm': 'Einstellungen und Speicher aus der Datei importieren? Dadurch wird der aktuelle UI-Zustand ersetzt.',
        'open_output_folder': 'Ausgabeordner öffnen?',
        'clear_field': 'Aktuellen Feldwert löschen',
        'explorer': 'Explorer'
    },
    'es': {
        'title': 'LexiCode Bundler',
        'lang_label': 'Idioma:',
        'theme_label': 'Tema:',
        'font_label': 'Fuente:',
        'scaling_label': 'Escala:',
        'action_label': 'Acción:',
        'action_bundle': 'Empaquetar',
        'action_unbundle': 'Desempaquetar',
        'source_root_label': 'Raíz de código fuente (ej. ...\\\\src):',
        'output_folder_label': 'Carpeta de salida (vacía = igual que fuente):',
        'shorten_prefix_label': 'Acortar prefijo de ruta (opcional):',
        'include_ext_label': 'Extensiones a incluir (ej. py,ts; vacío = todas):',
        'exclude_ext_label': 'Extensiones a excluir (separadas por coma, ej. png,jpg,log):',
        'exclude_dirs_label': 'Excluir carpetas por nombre (separadas por comas):',
        'exclude_files_label': 'Excluir archivos por nombre (separados por coma):',
        'output_ext_label': 'Extensión de archivo de salida:',
        'mode_label': 'Modo:',
        'mode_all': '1) Un archivo grande para todo el árbol',
        'mode_copy_tree': '2) Copiar árbol del proyecto',
        'mode_per_folder': '3) Un archivo por carpeta de nivel superior',
        'output_name_label': 'Nombre del archivo de salida (para modo 1):',
        'copy_out_label': 'Carpeta de salida (modo 2):',
        'include_root_files_label': 'También empaquetar archivos sueltos en raíz (ej. extension.ts)',
        'separator_label': 'Agregar línea separadora entre archivos',
        'list_only_names_label': 'Listar solo nombres (sin contenido de archivos)',
        'unbundle_src_label': 'Carpeta con archivos bundle:',
        'unbundle_out_label': 'Reconstruir en carpeta:',
        'unbundle_shorten_label': 'Eliminar prefijo de ruta (vacío = conservar ruta completa del encabezado):',
        'unbundle_ext_label': 'Sobreescribir extensión (vacío = original):',
        'browse': 'Explorar',
        'goto': 'Ir a',
        'auto_shorten': 'Auto',
        'run': 'Ejecutar',
        'status_ready': 'Listo',
        'status_running': 'Ejecutando...',
        'err_source_not_set': 'Carpeta de origen no establecida.',
        'err_source_not_dir': 'Carpeta de origen no existe o no es una carpeta.',
        'err_output_path_empty': 'Ruta de salida vacía.',
        'warn_source_empty': 'Ruta de origen vacía.',
        'success_one': 'Hecho. Archivo creado:\n{path}',
        'success_many': 'Hecho. Archivos creados:\n{paths}',
        'no_files': 'No se encontraron archivos con los filtros dados.',
        'error_title': 'Error',
        'success_title': 'Éxito',
        'result_title': 'Resultado',
        'warning_title': 'Advertencia',
        'unbundle_success': '{n} archivo(s) desempaquetados en:\n{path}',
        'unbundle_no_files': 'No se encontraron archivos bundle.',
        'err_unbundle_src_empty': 'Carpeta bundle no establecida.',
        'err_unbundle_out_empty': 'Carpeta destino no establecida.',
        'profiles_label': 'Perfil',
        'export_all': 'Exportar',
        'import_all': 'Importar',
        'import_success': 'Configuración importada correctamente.',
        'export_success': 'Configuración exportada correctamente:\n{path}',
        'import_invalid': 'El archivo seleccionado no es un exportación válida de configuración de LexiCode.',
        'import_confirm': '¿Importar configuración y memorias del archivo? Esto reemplazará el estado actual de la interfaz.',
        'open_output_folder': '¿Abrir carpeta de salida?',
        'clear_field': 'Borrar valor del campo actual',
        'explorer': 'Explorador'
    },
    'fr': {
        'title': 'LexiCode Bundler',
        'lang_label': 'Langue:',
        'theme_label': 'Thème:',
        'font_label': 'Police:',
        'scaling_label': 'Échelle:',
        'action_label': 'Action:',
        'action_bundle': 'Empaqueter',
        'action_unbundle': 'Désempaqueter',
        'source_root_label': 'Racine source (ex. ...\\\\src):',
        'output_folder_label': 'Dossier de sortie (vide = comme source):',
        'shorten_prefix_label': 'Raccourcir le préfixe du chemin (optionnel):',
        'include_ext_label': 'Extensions à inclure (ex. py,ts; vide = toutes):',
        'exclude_ext_label': 'Extensions à exclure (séparées par virgule, ex. png,jpg,log):',
        'exclude_dirs_label': 'Exclure les dossiers par nom (séparés par des virgules):',
        'exclude_files_label': 'Exclure fichiers par nom (séparés par virgule):',
        'output_ext_label': 'Extension fichier de sortie:',
        'mode_label': 'Mode:',
        'mode_all': "1) Un gros fichier pour tout l'arbre",
        'mode_copy_tree': "2) Copier l'arbre du projet",
        'mode_per_folder': '3) Un fichier par dossier de niveau supérieur',
        'output_name_label': 'Nom du fichier de sortie (pour mode 1):',
        'copy_out_label': 'Dossier de sortie (mode 2):',
        'include_root_files_label': 'Aussi empaqueter fichiers libres à la racine (ex. extension.ts)',
        'separator_label': 'Ajouter ligne séparatrice entre fichiers',
        'list_only_names_label': 'Lister uniquement les noms (sans contenu de fichier)',
        'unbundle_src_label': 'Dossier avec fichiers bundle:',
        'unbundle_out_label': 'Reconstruire dans le dossier:',
        'unbundle_shorten_label': "Supprimer le préfixe du chemin (vide = conserver le chemin complet de l'en-tête):",
        'unbundle_ext_label': "Remplacer l'extension (vide = original):",
        'browse': 'Parcourir',
        'goto': 'Aller à',
        'auto_shorten': 'Auto',
        'run': 'Exécuter',
        'status_ready': 'Prêt',
        'status_running': 'En cours...',
        'err_source_not_set': 'Dossier source non défini.',
        'err_source_not_dir': "Dossier source n'existe pas ou n'est pas un dossier.",
        'err_output_path_empty': 'Chemin de sortie vide.',
        'warn_source_empty': 'Chemin source vide.',
        'success_one': 'Terminé. Fichier créé:\n{path}',
        'success_many': 'Terminé. Fichiers créés:\n{paths}',
        'no_files': 'Aucun fichier trouvé avec ces filtres.',
        'error_title': 'Erreur',
        'success_title': 'Succès',
        'result_title': 'Résultat',
        'warning_title': 'Avertissement',
        'unbundle_success': '{n} fichier(s) désempaquetés dans:\n{path}',
        'unbundle_no_files': 'Aucun fichier bundle trouvé.',
        'err_unbundle_src_empty': 'Dossier bundle non défini.',
        'err_unbundle_out_empty': 'Dossier cible non défini.',
        'profiles_label': 'Profil',
        'export_all': 'Exporter',
        'import_all': 'Importer',
        'import_success': 'Paramètres importés avec succès.',
        'export_success': 'Paramètres exportés avec succès:\n{path}',
        'import_invalid': "Le fichier sélectionné n'est pas un export de configuration LexiCode valide.",
        'import_confirm': "Importer les paramètres et la mémoire depuis le fichier? Cela remplacera l'état actuel de l'interface.",
        'open_output_folder': 'Ouvrir le dossier de sortie?',
        'clear_field': 'Effacer la valeur du champ actuel',
        'explorer': 'Explorateur'
    },
    'it': {
        'title': 'LexiCode Bundler',
        'lang_label': 'Lingua:',
        'theme_label': 'Tema:',
        'font_label': 'Carattere:',
        'scaling_label': 'Scala:',
        'action_label': 'Azione:',
        'action_bundle': 'Impacchetta',
        'action_unbundle': 'Disimpacchetta',
        'source_root_label': 'Radice sorgente (es. ...\\\\src):',
        'output_folder_label': 'Cartella output (vuota = uguale a sorgente):',
        'shorten_prefix_label': 'Abbrevia prefisso percorso (opzionale):',
        'include_ext_label': 'Estensioni da includere (es. py,ts; vuoto = tutte):',
        'exclude_ext_label': 'Estensioni da escludere (separate da virgola, es. png,jpg,log):',
        'exclude_dirs_label': 'Escludi cartelle per nome (separate da virgole):',
        'exclude_files_label': 'Escludi file per nome (separati da virgola):',
        'output_ext_label': 'Estensione file output:',
        'mode_label': 'Modalità:',
        'mode_all': "1) Un file grande per l'intero albero",
        'mode_copy_tree': '2) Copia albero del progetto',
        'mode_per_folder': '3) Un file per cartella di livello superiore',
        'output_name_label': 'Nome file output (per modalità 1):',
        'copy_out_label': 'Cartella output (modalità 2):',
        'include_root_files_label': 'Includi anche file sciolti nella radice (es. extension.ts)',
        'separator_label': 'Aggiungi linea separatrice tra file',
        'list_only_names_label': 'Elenca solo i nomi (senza contenuto file)',
        'unbundle_src_label': 'Cartella con file bundle:',
        'unbundle_out_label': 'Ricostruisci nella cartella:',
        'unbundle_shorten_label': "Rimuovi prefisso percorso (vuoto = mantieni percorso completo dall'intestazione):",
        'unbundle_ext_label': 'Sostituisci estensione (vuoto = originale):',
        'browse': 'Sfoglia',
        'goto': 'Vai a',
        'auto_shorten': 'Auto',
        'run': 'Esegui',
        'status_ready': 'Pronto',
        'status_running': 'In esecuzione...',
        'err_source_not_set': 'Cartella sorgente non impostata.',
        'err_source_not_dir': 'Cartella sorgente non esiste o non è una cartella.',
        'err_output_path_empty': 'Percorso output vuoto.',
        'warn_source_empty': 'Percorso sorgente vuoto.',
        'success_one': 'Fatto. File creato:\n{path}',
        'success_many': 'Fatto. File creati:\n{paths}',
        'no_files': 'Nessun file trovato con i filtri dati.',
        'error_title': 'Errore',
        'success_title': 'Successo',
        'result_title': 'Risultato',
        'warning_title': 'Avviso',
        'unbundle_success': '{n} file(s) disimpacchettati in:\n{path}',
        'unbundle_no_files': 'Nessun file bundle trovato.',
        'err_unbundle_src_empty': 'Cartella bundle non impostata.',
        'err_unbundle_out_empty': 'Cartella destinazione non impostata.',
        'profiles_label': 'Profilo',
        'export_all': 'Esporta',
        'import_all': 'Importa',
        'import_success': 'Impostazioni importate con successo.',
        'export_success': 'Impostazioni esportate con successo:\n{path}',
        'import_invalid': "Il file selezionato non è un'esportazione di configurazione LexiCode valida.",
        'import_confirm': "Importare impostazioni e memoria dal file? Questo sostituirà lo stato corrente dell'interfaccia.",
        'open_output_folder': 'Aprire la cartella di output?',
        'clear_field': 'Cancella il valore del campo corrente',
        'explorer': 'Esplora risorse'
    },
    'pt': {
        'title': 'LexiCode Bundler',
        'lang_label': 'Idioma:',
        'theme_label': 'Tema:',
        'font_label': 'Fonte:',
        'scaling_label': 'Escala:',
        'action_label': 'Ação:',
        'action_bundle': 'Empacotar',
        'action_unbundle': 'Desempacotar',
        'source_root_label': 'Raiz de origem (ex.: ...\\\\src):',
        'output_folder_label': 'Pasta de saída (vazio = mesma da origem):',
        'shorten_prefix_label': 'Encurtar prefixo do caminho (opcional):',
        'include_ext_label': 'Incluir extensões (ex.: py,ts; vazio = todas):',
        'exclude_ext_label': 'Excluir extensões (separadas por vírgula, ex.: png,jpg,log):',
        'exclude_dirs_label': 'Excluir pastas por nome (separadas por vírgula):',
        'exclude_files_label': 'Excluir arquivos por nome (separados por vírgula):',
        'output_ext_label': 'Extensão do arquivo de saída:',
        'mode_label': 'Modo:',
        'mode_all': '1) Um arquivo grande para toda a árvore',
        'mode_copy_tree': '2) Copiar árvore do projeto',
        'mode_per_folder': '3) Um arquivo por pasta de nível superior',
        'output_name_label': 'Nome do arquivo de saída (para o modo 1):',
        'copy_out_label': 'Pasta de saída (modo 2):',
        'include_root_files_label': 'Incluir também arquivos soltos na raiz (ex.: extension.ts)',
        'separator_label': 'Adicionar linha separadora entre arquivos',
        'list_only_names_label': 'Listar apenas nomes (sem conteúdo dos arquivos)',
        'unbundle_src_label': 'Pasta com arquivos bundle:',
        'unbundle_out_label': 'Reconstruir na pasta:',
        'unbundle_shorten_label': 'Remover prefixo do caminho (vazio = manter caminho completo do cabeçalho):',
        'unbundle_ext_label': 'Substituir extensão (vazio = original):',
        'browse': 'Procurar',
        'goto': 'Ir para',
        'auto_shorten': 'Automático',
        'run': 'Executar',
        'status_ready': 'Pronto',
        'status_running': 'Executando...',
        'err_source_not_set': 'Pasta de origem não definida.',
        'err_source_not_dir': 'Pasta de origem não existe ou não é um diretório.',
        'err_output_path_empty': 'Caminho de saída está vazio.',
        'warn_source_empty': 'Caminho de origem está vazio.',
        'success_one': 'Concluído. Arquivo criado:\n{path}',
        'success_many': 'Concluído. Arquivos criados:\n{paths}',
        'no_files': 'Nenhum arquivo encontrado para os filtros informados.',
        'error_title': 'Erro',
        'success_title': 'Sucesso',
        'result_title': 'Resultado',
        'warning_title': 'Aviso',
        'unbundle_success': '{n} arquivo(s) desempacotado(s) em:\n{path}',
        'unbundle_no_files': 'Nenhum arquivo bundle encontrado.',
        'err_unbundle_src_empty': 'Pasta bundle não definida.',
        'err_unbundle_out_empty': 'Pasta destino não definida.',
        'profiles_label': 'Perfil',
        'export_all': 'Exportar',
        'import_all': 'Importar',
        'import_success': 'Configurações importadas com sucesso.',
        'export_success': 'Configurações exportadas com sucesso:\n{path}',
        'import_invalid': 'O arquivo selecionado não é uma exportação válida de configuração do LexiCode.',
        'import_confirm': 'Importar configurações e memórias do arquivo? Isso substituirá o estado atual da interface.',
        'open_output_folder': 'Abrir pasta de saída?',
        'clear_field': 'Limpar valor do campo atual',
        'explorer': 'Explorador'
    },
    'ro': {
        'title': 'LexiCode Bundler',
        'lang_label': 'Limbă:',
        'theme_label': 'Temă:',
        'font_label': 'Font:',
        'scaling_label': 'Scalare:',
        'action_label': 'Acțiune:',
        'action_bundle': 'Împachetează',
        'action_unbundle': 'Dezîmpachetează',
        'source_root_label': 'Rădăcină de sursă (ex.: ...\\\\src):',
        'output_folder_label': 'Dosar de ieșire (gol = același ca sursa):',
        'shorten_prefix_label': 'Scurtează prefixul căii (opțional):',
        'include_ext_label': 'Include extensii (ex.: py,ts; gol = toate):',
        'exclude_ext_label': 'Exclude extensii (separate prin virgulă, ex.: png,jpg,log):',
        'exclude_dirs_label': 'Exclude dosarele după nume (separate prin virgulă):',
        'exclude_files_label': 'Exclude fișiere după nume (separate prin virgulă):',
        'output_ext_label': 'Extensie fișier ieșire:',
        'mode_label': 'Mod:',
        'mode_all': '1) Un fișier mare pentru tot arborele',
        'mode_copy_tree': '2) Copiază arborele proiectului',
        'mode_per_folder': '3) Un fișier per director de nivel superior',
        'output_name_label': 'Nume fișier de ieșire (pentru modul 1):',
        'copy_out_label': 'Dosar ieșire (modul 2):',
        'include_root_files_label': 'Include și fișierele izolate din rădăcină (ex.: extension.ts)',
        'separator_label': 'Adaugă linie separator între fișiere',
        'list_only_names_label': 'Listează doar numele (fără conținutul fișierelor)',
        'unbundle_src_label': 'Dosar cu fișiere bundle:',
        'unbundle_out_label': 'Reconstituie în dosar:',
        'unbundle_shorten_label': 'Elimina prefixul căii (gol = păstrează calea completă din antet):',
        'unbundle_ext_label': 'Înlocuiește extensia (gol = original):',
        'browse': 'Caută',
        'goto': 'Mergi la',
        'auto_shorten': 'Automat',
        'run': 'Rulează',
        'status_ready': 'Gata',
        'status_running': 'Rulează...',
        'err_source_not_set': 'Directorul de sursă nu este setat.',
        'err_source_not_dir': 'Directorul de sursă nu există sau nu este un director.',
        'err_output_path_empty': 'Calea de ieșire este goală.',
        'warn_source_empty': 'Calea de sursă este goală.',
        'success_one': 'Finalizat. Fișier creat:\n{path}',
        'success_many': 'Finalizat. Fișiere create:\n{paths}',
        'no_files': 'Niciun fișier găsit pentru filtrele date.',
        'error_title': 'Eroare',
        'success_title': 'Succes',
        'result_title': 'Rezultat',
        'warning_title': 'Avertizare',
        'unbundle_success': '{n} fișier(e) dezîmpachetate în:\n{path}',
        'unbundle_no_files': 'Nu s-au găsit fișiere bundle.',
        'err_unbundle_src_empty': 'Dosarul bundle nu este setat.',
        'err_unbundle_out_empty': 'Dosarul destinație nu este setat.',
        'profiles_label': 'Profil',
        'export_all': 'Exportare',
        'import_all': 'Importare',
        'import_success': 'Setările au fost importate cu succes.',
        'export_success': 'Setările au fost exportate cu succes:\n{path}',
        'import_invalid': 'Fișierul selectat nu este un export valid de configurație LexiCode.',
        'import_confirm': 'Importați setările și memoria din fișier? Aceasta va înlocui starea actuală a interfeței.',
        'open_output_folder': 'Deschideți dosarul de ieșire?',
        'clear_field': 'Șterge valoarea câmpului curent',
        'explorer': 'Explorer'
    },
    'nl': {
        'title': 'LexiCode Bundler',
        'lang_label': 'Taal:',
        'theme_label': 'Thema:',
        'font_label': 'Lettertype:',
        'scaling_label': 'Schaal:',
        'action_label': 'Actie:',
        'action_bundle': 'Bundelen',
        'action_unbundle': 'Ontvouwen',
        'source_root_label': 'Bronroot (bijv. ...\\\\src):',
        'output_folder_label': 'Outputmap (leeg = zelfde als bron):',
        'shorten_prefix_label': 'Padprefix inkorten (optioneel):',
        'include_ext_label': 'Extensies opnemen (bijv. py,ts; leeg = alle):',
        'exclude_ext_label': 'Extensies uitsluiten (komma gescheiden, bijv. png,jpg,log):',
        'exclude_dirs_label': 'Mappen op naam uitsluiten (komma-gescheiden):',
        'exclude_files_label': 'Bestanden uitsluiten op naam (komma gescheiden):',
        'output_ext_label': 'Uitvoerbestandextensie:',
        'mode_label': 'Modus:',
        'mode_all': '1) Een groot bestand voor de hele boom',
        'mode_copy_tree': '2) Volledig projectboom kopiëren',
        'mode_per_folder': '3) Één bestand per top-directory',
        'output_name_label': 'Naam uitvoerbestand (voor modus 1):',
        'copy_out_label': 'Uitvoermap (modus 2):',
        'include_root_files_label': 'Neem ook losse bestanden in de root op (bijv. extension.ts)',
        'separator_label': 'Voeg scheidingslijn tussen bestanden toe',
        'list_only_names_label': 'Alleen namen weergeven (geen bestandsinhoud)',
        'unbundle_src_label': 'Map met bundlebestanden:',
        'unbundle_out_label': 'Reconstrueer naar map:',
        'unbundle_shorten_label': 'Verwijder padprefix (leeg = volledig pad uit koptekst behouden):',
        'unbundle_ext_label': 'Extensie overschrijven (leeg = origineel):',
        'browse': 'Bladeren',
        'goto': 'Ga naar',
        'auto_shorten': 'Automatisch',
        'run': 'Uitvoeren',
        'status_ready': 'Gereed',
        'status_running': 'Bezig...',
        'err_source_not_set': 'Bronmap is niet ingesteld.',
        'err_source_not_dir': 'Bronmap bestaat niet of is geen map.',
        'err_output_path_empty': 'Uitvoerpad is leeg.',
        'warn_source_empty': 'Bronpad is leeg.',
        'success_one': 'Gereed. Bestand aangemaakt:\n{path}',
        'success_many': 'Gereed. Bestanden aangemaakt:\n{paths}',
        'no_files': 'Geen bestanden gevonden voor de opgegeven filters.',
        'error_title': 'Fout',
        'success_title': 'Succes',
        'result_title': 'Resultaat',
        'warning_title': 'Waarschuwing',
        'unbundle_success': '{n} bestand(en) ontvouwen naar:\n{path}',
        'unbundle_no_files': 'Geen bundlebestanden gevonden.',
        'err_unbundle_src_empty': 'Bundle-bronmap niet ingesteld.',
        'err_unbundle_out_empty': 'Doelmap niet ingesteld.',
        'profiles_label': 'Profiel',
        'export_all': 'Exporteren',
        'import_all': 'Importeren',
        'import_success': 'Instellingen succesvol geïmporteerd.',
        'export_success': 'Instellingen succesvol geëxporteerd:\n{path}',
        'import_invalid': 'Het geselecteerde bestand is geen geldig LexiCode configuratie-export.',
        'import_confirm': 'Instellingen en geheugen importeren uit bestand? Dit vervangt de huidige UI-status.',
        'open_output_folder': 'Uitvoermap openen?',
        'clear_field': 'Huidige veldwaarde wissen',
        'explorer': 'Verkenner'
    },
    'sv': {
        'title': 'LexiCode Bundler',
        'lang_label': 'Språk:',
        'theme_label': 'Tema:',
        'font_label': 'Typsnitt:',
        'scaling_label': 'Skalning:',
        'action_label': 'Åtgärd:',
        'action_bundle': 'Paketera',
        'action_unbundle': 'Uppacka',
        'source_root_label': 'Källrot (t.ex. ...\\\\src):',
        'output_folder_label': 'Utdatakatalog (tom = samma som källa):',
        'shorten_prefix_label': 'Förkorta sökvägsprefix (valfritt):',
        'include_ext_label': 'Inkludera filändelser (t.ex. py,ts; tomt = alla):',
        'exclude_ext_label': 'Exkludera filändelser (kommaseparerade, t.ex. png,jpg,log):',
        'exclude_dirs_label': 'Uteslut mappar efter namn (kommaseparerat):',
        'exclude_files_label': 'Exkludera filer efter namn (kommaseparerade):',
        'output_ext_label': 'Utdatafilsändelse:',
        'mode_label': 'Läge:',
        'mode_all': '1) En stor fil för hela trädstrukturen',
        'mode_copy_tree': '2) Kopiera hela projektträdet',
        'mode_per_folder': '3) En fil per rotkatalog',
        'output_name_label': 'Namn på utdatafil (för läge 1):',
        'copy_out_label': 'Utdatakatalog (läge 2):',
        'include_root_files_label': 'Ta även med lösa filer i roten (t.ex. extension.ts)',
        'separator_label': 'Lägg till avskiljningsrad mellan filer',
        'list_only_names_label': 'Visa endast namn (utan filinnehåll)',
        'unbundle_src_label': 'Mapp med bundlefiler:',
        'unbundle_out_label': 'Återskapa till mapp:',
        'unbundle_shorten_label': 'Ta bort sökvägprefix (tomt = behåll fullständig sökväg från rubrik):',
        'unbundle_ext_label': 'Åsidosätt ändelse (tom = originalet):',
        'browse': 'Bläddra',
        'goto': 'Gå till',
        'auto_shorten': 'Automatiskt',
        'run': 'Kör',
        'status_ready': 'Klar',
        'status_running': 'Kör...',
        'err_source_not_set': 'Källmappen är inte angiven.',
        'err_source_not_dir': 'Källmappen finns inte eller är inte en katalog.',
        'err_output_path_empty': 'Utdatavägen är tom.',
        'warn_source_empty': 'Källvägen är tom.',
        'success_one': 'Klar. Fil skapad:\n{path}',
        'success_many': 'Klar. Filer skapade:\n{paths}',
        'no_files': 'Inga filer hittades för de givna filtren.',
        'error_title': 'Fel',
        'success_title': 'Lyckades',
        'result_title': 'Resultat',
        'warning_title': 'Varning',
        'unbundle_success': '{n} fil(er) uppackade till:\n{path}',
        'unbundle_no_files': 'Inga bundlefiler hittades.',
        'err_unbundle_src_empty': 'Bundle-källmapp ej angiven.',
        'err_unbundle_out_empty': 'Målmapp ej angiven.',
        'profiles_label': 'Profil',
        'export_all': 'Exportera',
        'import_all': 'Importera',
        'import_success': 'Inställningar importerades framgångsrikt.',
        'export_success': 'Inställningar exporterades framgångsrikt:\n{path}',
        'import_invalid': 'Den valda filen är inte en giltig LexiCode-konfigurationsexport.',
        'import_confirm': 'Importera inställningar och minne från fil? Detta ersätter det nuvarande UI-tillståndet.',
        'open_output_folder': 'Öppna utdatakatalog?',
        'clear_field': 'Rensa aktuellt fältvärde',
        'explorer': 'Utforskaren'
    },
    'tr': {
        'title': 'LexiCode Bundler',
        'lang_label': 'Dil:',
        'theme_label': 'Tema:',
        'font_label': 'Yazı tipi:',
        'scaling_label': 'Ölçek:',
        'action_label': 'Eylem:',
        'action_bundle': 'Paketle',
        'action_unbundle': 'Paketi Aç',
        'source_root_label': 'Kaynak kök (örn.: ...\\\\src):',
        'output_folder_label': 'Çıktı klasörü (boş = kaynakla aynı):',
        'shorten_prefix_label': 'Yol önekini kısalt (isteğe bağlı):',
        'include_ext_label': 'Uzantıları dahil et (örn.: py,ts; boş = tümü):',
        'exclude_ext_label': 'Uzantıları dışla (virgülle ayrılmış, örn.: png,jpg,log):',
        'exclude_dirs_label': 'Klasörleri ada göre hariç tut (virgülle ayır):',
        'exclude_files_label': 'Dosyaları ada göre dışla (virgülle ayrılmış):',
        'output_ext_label': 'Çıktı dosya uzantısı:',
        'mode_label': 'Mod:',
        'mode_all': '1) Tüm dizin ağacı için tek büyük dosya',
        'mode_copy_tree': '2) Tam proje ağacını kopyala',
        'mode_per_folder': '3) Her üst düzey klasör için bir dosya',
        'output_name_label': 'Çıktı dosya adı (mod 1 için):',
        'copy_out_label': 'Çıktı klasörü (mod 2):',
        'include_root_files_label': 'Kökteki serbest dosyaları da dahil et (örn.: extension.ts)',
        'separator_label': 'Dosyalar arasında ayırıcı satır ekle',
        'list_only_names_label': 'Yalnızca adları listele (dosya içeriği yok)',
        'unbundle_src_label': 'Bundle dosyaları klasörü:',
        'unbundle_out_label': 'Yeniden oluşturma klasörü:',
        'unbundle_shorten_label': 'Yol önekini kaldır (boş = başlıktan tam yolu koru):',
        'unbundle_ext_label': 'Uzantıyı geçersiz kıl (boş = orijinal):',
        'browse': 'Gözat',
        'goto': 'Git',
        'auto_shorten': 'Otomatik',
        'run': 'Çalıştır',
        'status_ready': 'Hazır',
        'status_running': 'Çalışıyor...',
        'err_source_not_set': 'Kaynak klasör belirtilmedi.',
        'err_source_not_dir': 'Kaynak klasör mevcut değil veya bir dizin değil.',
        'err_output_path_empty': 'Çıktı yolu boş.',
        'warn_source_empty': 'Kaynak yolu boş.',
        'success_one': 'Tamam. Dosya oluşturuldu:\n{path}',
        'success_many': 'Tamam. Dosyalar oluşturuldu:\n{paths}',
        'no_files': 'Verilen filtrelerle eşleşen dosya bulunamadı.',
        'error_title': 'Hata',
        'success_title': 'Başarı',
        'result_title': 'Sonuç',
        'warning_title': 'Uyarı',
        'unbundle_success': '{n} dosya açıldı:\n{path}',
        'unbundle_no_files': 'Bundle dosyası bulunamadı.',
        'err_unbundle_src_empty': 'Bundle kaynak klasörü belirtilmedi.',
        'err_unbundle_out_empty': 'Hedef klasör belirtilmedi.',
        'profiles_label': 'Profil',
        'export_all': 'Dışa aktar',
        'import_all': 'İçe aktar',
        'import_success': 'Ayarlar başarıyla içe aktarıldı.',
        'export_success': 'Ayarlar başarıyla dışa aktarıldı:\n{path}',
        'import_invalid': 'Seçilen dosya geçerli bir LexiCode yapılandırma dışa aktarması değil.',
        'import_confirm': 'Dosyadan ayarları ve belleği içe aktarmak istiyor musunuz? Bu, mevcut UI durumunun yerini alacaktır.',
        'open_output_folder': 'Çıktı klasörü açılsın mı?',
        'clear_field': 'Mevcut alan değerini temizle',
        'explorer': 'Dosya Gezgini'
    },
    'ja': {
        'title': 'LexiCode Bundler',
        'lang_label': '言語:',
        'theme_label': 'テーマ:',
        'font_label': 'フォント:',
        'scaling_label': '拡大率:',
        'action_label': 'アクション:',
        'action_bundle': 'バンドル',
        'action_unbundle': 'アンバンドル',
        'source_root_label': 'ソースルート (例: ...\\\\src):',
        'output_folder_label': '出力フォルダ (空 = ソースと同じ):',
        'shorten_prefix_label': 'パス接頭辞を短縮 (任意):',
        'include_ext_label': '拡張子を含める (例: py,ts; 空 = すべて):',
        'exclude_ext_label': '拡張子を除外 (カンマ区切り, 例: png,jpg,log):',
        'exclude_dirs_label': '名前でフォルダを除外 (カンマ区切り):',
        'exclude_files_label': 'ファイル名で除外 (カンマ区切り):',
        'output_ext_label': '出力ファイル拡張子:',
        'mode_label': 'モード:',
        'mode_all': '1) ツリー全体を1つの大きなファイルにまとめる',
        'mode_copy_tree': '2) プロジェクトツリーをコピー',
        'mode_per_folder': '3) 各トップレベルフォルダごとに1ファイル',
        'output_name_label': '出力ファイル名 (モード 1):',
        'copy_out_label': '出力フォルダ (モード2):',
        'include_root_files_label': 'ルートにある個別ファイルも含む (例: extension.ts)',
        'separator_label': 'ファイル間に区切り行を追加',
        'list_only_names_label': '名前のみ一覧表示 (ファイル内容なし)',
        'unbundle_src_label': 'バンドルファイルフォルダ:',
        'unbundle_out_label': '復元先フォルダ:',
        'unbundle_shorten_label': 'パスプレフィックスを削除（空=ヘッダーのフルパスを保持）:',
        'unbundle_ext_label': '拡張子を上書き (空=元の拡張子):',
        'browse': '参照',
        'goto': '移動',
        'auto_shorten': '自動',
        'run': '実行',
        'status_ready': '準備完了',
        'status_running': '実行中...',
        'err_source_not_set': 'ソースフォルダが設定されていません。',
        'err_source_not_dir': 'ソースフォルダが存在しないか、ディレクトリではありません。',
        'err_output_path_empty': '出力パスが空です。',
        'warn_source_empty': 'ソースパスが空です。',
        'success_one': '完了。ファイルを作成しました:\n{path}',
        'success_many': '完了。ファイルを作成しました:\n{paths}',
        'no_files': '指定されたフィルターに一致するファイルが見つかりませんでした。',
        'error_title': 'エラー',
        'success_title': '成功',
        'result_title': '結果',
        'warning_title': '警告',
        'unbundle_success': '{n}個のファイルを展開:\n{path}',
        'unbundle_no_files': 'バンドルファイルが見つかりません。',
        'err_unbundle_src_empty': 'バンドルソースフォルダが未設定です。',
        'err_unbundle_out_empty': '復元先フォルダが未設定です。',
        'profiles_label': 'プロフィール',
        'export_all': 'エクスポート',
        'import_all': 'インポート',
        'import_success': '設定のインポートに成功しました。',
        'export_success': '設定のエクスポートに成功しました:\n{path}',
        'import_invalid': '選択したファイルは有効なLexiCode設定エクスポートではありません。',
        'import_confirm': 'ファイルから設定とメモリをインポートしますか？現在のUI状態が置き換えられます。',
        'open_output_folder': '出力フォルダを開きますか？',
        'clear_field': '現在のフィールド値をクリア',
        'explorer': 'エクスプローラー'
    },
    'zh': {
        'title': 'LexiCode Bundler',
        'lang_label': '语言:',
        'theme_label': '主题:',
        'font_label': '字体:',
        'scaling_label': '缩放:',
        'action_label': '操作:',
        'action_bundle': '打包',
        'action_unbundle': '解包',
        'source_root_label': '源码根目录 (例如 ...\\\\src):',
        'output_folder_label': '输出文件夹 (空 = 与源码相同):',
        'shorten_prefix_label': '缩短路径前缀 (可选):',
        'include_ext_label': '包含扩展名 (例如 py,ts; 空 = 所有):',
        'exclude_ext_label': '排除扩展名 (逗号分隔, 例如 png,jpg,log):',
        'exclude_dirs_label': '按名称排除文件夹 (逗号分隔):',
        'exclude_files_label': '按名称排除文件 (逗号分隔):',
        'output_ext_label': '输出文件扩展名:',
        'mode_label': '模式:',
        'mode_all': '1) 将整个目录树打包为一个大文件',
        'mode_copy_tree': '2) 复制完整项目树',
        'mode_per_folder': '3) 每个顶级文件夹生成一个文件',
        'output_name_label': '输出文件名 (用于模式 1):',
        'copy_out_label': '输出文件夹 (模式2):',
        'include_root_files_label': '同时包含根目录中的零散文件 (例如 extension.ts)',
        'separator_label': '在文件之间添加分隔行',
        'list_only_names_label': '仅列出名称 (不含文件内容)',
        'unbundle_src_label': '包含捆绑文件的文件夹:',
        'unbundle_out_label': '还原到文件夹:',
        'unbundle_shorten_label': '删除路径前缀（空=保留标头中的完整路径）:',
        'unbundle_ext_label': '覆盖扩展名 (空=保留原始):',
        'browse': '浏览',
        'goto': '前往',
        'auto_shorten': '自动',
        'run': '运行',
        'status_ready': '就绪',
        'status_running': '运行中...',
        'err_source_not_set': '未设置源码文件夹。',
        'err_source_not_dir': '源码文件夹不存在或不是一个目录。',
        'err_output_path_empty': '输出路径为空。',
        'warn_source_empty': '源码路径为空。',
        'success_one': '已完成。创建文件:\n{path}',
        'success_many': '已完成。创建文件:\n{paths}',
        'no_files': '在给定过滤器下未找到任何文件。',
        'error_title': '错误',
        'success_title': '成功',
        'result_title': '结果',
        'warning_title': '警告',
        'unbundle_success': '已解包 {n} 个文件到:\n{path}',
        'unbundle_no_files': '未找到捆绑文件。',
        'err_unbundle_src_empty': '未设置捆绑源文件夹。',
        'err_unbundle_out_empty': '未设置目标文件夹。',
        'profiles_label': '配置文件',
        'export_all': '导出',
        'import_all': '导入',
        'import_success': '设置导入成功。',
        'export_success': '设置导出成功:\n{path}',
        'import_invalid': '所选文件不是有效的 LexiCode 配置导出。',
        'import_confirm': '从文件导入设置和记忆？这将替换当前的 UI 状态。',
        'open_output_folder': '打开输出文件夹？',
        'clear_field': '清除当前字段值',
        'explorer': '资源管理器'
    },
    'ko': {
        'title': 'LexiCode Bundler',
        'lang_label': '언어:',
        'theme_label': '테마:',
        'font_label': '글꼴:',
        'scaling_label': '배율:',
        'action_label': '작업:',
        'action_bundle': '번들',
        'action_unbundle': '언번들',
        'source_root_label': '소스 루트 (예: ...\\\\src):',
        'output_folder_label': '출력 폴더 (비어 있음 = 소스와 동일):',
        'shorten_prefix_label': '경로 접두사 줄이기 (선택 사항):',
        'include_ext_label': '확장자 포함 (예: py,ts; 비어 있음 = 모든 파일):',
        'exclude_ext_label': '확장자 제외 (쉼표로 구분, 예: png,jpg,log):',
        'exclude_dirs_label': '이름으로 폴더 제외 (쉼표로 구분):',
        'exclude_files_label': '이름으로 파일 제외 (쉼표로 구분):',
        'output_ext_label': '출력 파일 확장자:',
        'mode_label': '모드:',
        'mode_all': '1) 전체 트리를 하나의 큰 파일로 묶기',
        'mode_copy_tree': '2) 전체 프로젝트 트리 복사',
        'mode_per_folder': '3) 상위 폴더마다 하나의 파일',
        'output_name_label': '출력 파일 이름 (모드 1):',
        'copy_out_label': '출력 폴더 (모드 2):',
        'include_root_files_label': '루트의 개별 파일도 포함 (예: extension.ts)',
        'separator_label': '파일 사이에 구분선 추가',
        'list_only_names_label': '이름만 나열 (파일 내용 제외)',
        'unbundle_src_label': '번들 파일 폴더:',
        'unbundle_out_label': '복원 폴더:',
        'unbundle_shorten_label': '경로 접두사 제거 (비어 있으면 헤더의 전체 경로 유지):',
        'unbundle_ext_label': '확장자 재정의 (비어 있음=원본):',
        'browse': '찾아보기',
        'goto': '이동',
        'auto_shorten': '자동',
        'run': '실행',
        'status_ready': '준비 완료',
        'status_running': '실행 중...',
        'err_source_not_set': '소스 폴더가 설정되지 않았습니다.',
        'err_source_not_dir': '소스 폴더가 존재하지 않거나 디렉터리가 아닙니다.',
        'err_output_path_empty': '출력 경로가 비어 있습니다.',
        'warn_source_empty': '소스 경로가 비어 있습니다.',
        'success_one': '완료. 파일을 생성했습니다:\n{path}',
        'success_many': '완료. 파일을 생성했습니다:\n{paths}',
        'no_files': '지정된 필터에 해당하는 파일을 찾을 수 없습니다.',
        'error_title': '오류',
        'success_title': '성공',
        'result_title': '결과',
        'warning_title': '경고',
        'unbundle_success': '{n}개 파일 언번들 완료:\n{path}',
        'unbundle_no_files': '번들 파일을 찾을 수 없습니다.',
        'err_unbundle_src_empty': '번들 소스 폴더가 설정되지 않았습니다.',
        'err_unbundle_out_empty': '대상 폴더가 설정되지 않았습니다.',
        'profiles_label': '프로필',
        'export_all': '내보내기',
        'import_all': '가져오기',
        'import_success': '설정을 성공적으로 가져왔습니다.',
        'export_success': '설정을 성공적으로 내보냈습니다:\n{path}',
        'import_invalid': '선택한 파일은 유효한 LexiCode 구성 내보내기가 아닙니다.',
        'import_confirm': '파일에서 설정과 메모리를 가져오시겠습니까? 이렇게 하면 현재 UI 상태가 교체됩니다.',
        'open_output_folder': '출력 폴더를 여시겠습니까?',
        'clear_field': '현재 필드 값 지우기',
        'explorer': '파일 탐색기'
    },
    'ar': {
        'title': 'LexiCode Bundler',
        'lang_label': 'اللغة:',
        'theme_label': 'السمة:',
        'font_label': 'الخط:',
        'scaling_label': 'التحجيم:',
        'action_label': 'الإجراء:',
        'action_bundle': 'تجميع',
        'action_unbundle': 'فك التجميع',
        'source_root_label': 'جذر المصدر (مثالًا: ...\\\\src):',
        'output_folder_label': 'مجلد الإخراج (فارغ = نفس المصدر):',
        'shorten_prefix_label': 'اختصار بادئة المسار (اختياري):',
        'include_ext_label': 'تضمين الامتدادات (مثالًا: py,ts; فارغ = جميعها):',
        'exclude_ext_label': 'استبعاد الامتدادات (مفصولة بفواصل, مثالًا: png,jpg,log):',
        'exclude_dirs_label': 'استبعاد المجلدات حسب الاسم (مفصولة بفواصل):',
        'exclude_files_label': 'استبعاد الملفات بالاسم (مفصولة بفواصل):',
        'output_ext_label': 'امتداد ملف الإخراج:',
        'mode_label': 'الوضع:',
        'mode_all': '1) ملف واحد كبير للشجرة بأكملها',
        'mode_copy_tree': '2) نسخ شجرة المشروع بالكامل',
        'mode_per_folder': '3) ملف واحد لكل مجلد علوي',
        'output_name_label': 'اسم ملف الإخراج (للوضع 1):',
        'copy_out_label': 'مجلد الإخراج (الوضع 2):',
        'include_root_files_label': 'تضمين أيضًا الملفات الفردية في الجذر (مثالًا: extension.ts)',
        'separator_label': 'إضافة سطر فاصل بين الملفات',
        'list_only_names_label': 'عرض الأسماء فقط (بدون محتوى الملفات)',
        'unbundle_src_label': 'المجلد الذي يحتوي على ملفات الحزمة:',
        'unbundle_out_label': 'إعادة البناء في المجلد:',
        'unbundle_shorten_label': 'إزالة بادئة المسار (فارغ = الاحتفاظ بالمسار الكامل من الرأس):',
        'unbundle_ext_label': 'تجاوز الامتداد (فارغ = أصلي):',
        'browse': 'استعراض',
        'goto': 'اذهب إلى',
        'auto_shorten': 'تلقائي',
        'run': 'تشغيل',
        'status_ready': 'جاهز',
        'status_running': 'يجري التشغيل...',
        'err_source_not_set': 'لم يتم تعيين مجلد المصدر.',
        'err_source_not_dir': 'مجلد المصدر غير موجود أو ليس دليلًا.',
        'err_output_path_empty': 'مسار الإخراج فارغ.',
        'warn_source_empty': 'مسار المصدر فارغ.',
        'success_one': 'تمت العملية. تم إنشاء ملف:\n{path}',
        'success_many': 'تمت العملية. تم إنشاء ملفات:\n{paths}',
        'no_files': 'لم يتم العثور على ملفات مطابقة للعوامل المعطاة.',
        'error_title': 'خطأ',
        'success_title': 'نجاح',
        'result_title': 'النتيجة',
        'warning_title': 'تحذير',
        'unbundle_success': 'تم فك تجميع {n} ملف(ات) في:\n{path}',
        'unbundle_no_files': 'لم يتم العثور على ملفات حزمة.',
        'err_unbundle_src_empty': 'لم يتم تعيين مجلد مصدر الحزمة.',
        'err_unbundle_out_empty': 'لم يتم تعيين مجلد الوجهة.',
        'profiles_label': 'الملف الشخصي',
        'export_all': 'تصدير',
        'import_all': 'استيراد',
        'import_success': 'تم استيراد الإعدادات بنجاح.',
        'export_success': 'تم تصدير الإعدادات بنجاح:\n{path}',
        'import_invalid': 'الملف المحدد ليس تصديرًا صالحًا لتهيئة LexiCode.',
        'import_confirm': 'استيراد الإعدادات والذاكرة من الملف؟ سيؤدي هذا إلى استبدال حالة واجهة المستخدم الحالية.',
        'open_output_folder': 'فتح مجلد الإخراج؟',
        'clear_field': 'مسح قيمة الحقل الحالي',
        'explorer': 'المستكشف'
    },
    'hi': {
        'title': 'LexiCode Bundler',
        'lang_label': 'भाषा:',
        'theme_label': 'थीम:',
        'font_label': 'फ़ॉन्ट:',
        'scaling_label': 'स्केलिंग:',
        'action_label': 'क्रिया:',
        'action_bundle': 'बंडल',
        'action_unbundle': 'अनबंडल',
        'source_root_label': 'स्रोत रूट (उदाहरण के लिए ...\\\\src):',
        'output_folder_label': 'आउटपुट फ़ोल्डर (खाली = स्रोत के समान):',
        'shorten_prefix_label': 'पाथ प्रीफ़िक्स छोटा करें (वैकल्पिक):',
        'include_ext_label': 'विस्तार शामिल करें (उदाहरण के लिए py,ts; खाली = सभी):',
        'exclude_ext_label': 'विस्तार बाहर करें (अल्पविराम द्वारा अलग, उदाहरण के लिए png,jpg,log):',
        'exclude_dirs_label': 'नाम के आधार पर फ़ोल्डर बाहर रखें (कॉमा से अलग):',
        'exclude_files_label': 'नाम से फ़ाइलें बाहर करें (अल्पविराम द्वारा अलग):',
        'output_ext_label': 'आउटपुट फ़ाइल एक्सटेंशन:',
        'mode_label': 'मोड:',
        'mode_all': '1) पूरे पेड़ के लिए एक बड़ी फ़ाइल',
        'mode_copy_tree': '2) पूरा प्रोजेक्ट ट्री कॉपी करें',
        'mode_per_folder': '3) प्रत्येक शीर्ष-स्तरीय फ़ोल्डर के लिए एक फ़ाइल',
        'output_name_label': 'आउटपुट फ़ाइल नाम (मोड 1 के लिए):',
        'copy_out_label': 'आउटपुट फ़ोल्डर (मोड 2):',
        'include_root_files_label': 'जड़ में भी अलग-अलग फ़ाइलें शामिल करें (उदाहरण के लिए extension.ts)',
        'separator_label': 'फ़ाइलों के बीच अलग करने वाली रेखा जोड़ें',
        'list_only_names_label': 'केवल नाम सूचीबद्ध करें (फ़ाइल सामग्री नहीं)',
        'unbundle_src_label': 'बंडल फ़ाइलों वाला फ़ोल्डर:',
        'unbundle_out_label': 'फ़ोल्डर में पुनर्निर्माण करें:',
        'unbundle_shorten_label': 'पाथ प्रीफ़िक्स हटाएँ (खाली = हेडर का पूरा पाथ रखें):',
        'unbundle_ext_label': 'एक्सटेंशन ओवरराइड करें (खाली = मूल):',
        'browse': 'ब्राउज़',
        'goto': 'जाएँ',
        'auto_shorten': 'स्वचालित',
        'run': 'चलाएँ',
        'status_ready': 'तैयार',
        'status_running': 'चल रहा है...',
        'err_source_not_set': 'स्रोत फ़ोल्डर सेट नहीं है।',
        'err_source_not_dir': 'स्रोत फ़ोल्डर मौजूद नहीं है या डायरेक्टरी नहीं है।',
        'err_output_path_empty': 'आउटपुट पथ खाली है।',
        'warn_source_empty': 'स्रोत पथ खाली है।',
        'success_one': 'पूर्ण। फ़ाइल बनाई गई:\n{path}',
        'success_many': 'पूर्ण। फ़ाइलें बनाई गईं:\n{paths}',
        'no_files': 'दिए गए फ़िल्टर के लिए कोई फ़ाइल नहीं मिली।',
        'error_title': 'त्रुटि',
        'success_title': 'सफलता',
        'result_title': 'परिणाम',
        'warning_title': 'चेतावनी',
        'unbundle_success': '{n} फ़ाइलें अनबंडल की गईं:\n{path}',
        'unbundle_no_files': 'कोई बंडल फ़ाइलें नहीं मिलीं।',
        'err_unbundle_src_empty': 'बंडल स्रोत फ़ोल्डर सेट नहीं है।',
        'err_unbundle_out_empty': 'लक्ष्य फ़ोल्डर सेट नहीं है।',
        'profiles_label': 'प्रोफ़ाइल',
        'export_all': 'निर्यात',
        'import_all': 'आयात',
        'import_success': 'सेटिंग्स सफलतापूर्वक आयात की गईं।',
        'export_success': 'सेटिंग्स सफलतापूर्वक निर्यात की गईं:\n{path}',
        'import_invalid': 'चुनी गई फ़ाइल मान्य LexiCode कॉन्फ़िगरेशन निर्यात नहीं है।',
        'import_confirm': 'फ़ाइल से सेटिंग्स और मेमोरी आयात करें? यह वर्तमान UI स्थिति को बदल देगा।',
        'open_output_folder': 'आउटपुट फ़ोल्डर खोलें?',
        'clear_field': 'वर्तमान फ़ील्ड मान साफ़ करें',
        'explorer': 'एक्सप्लोरर'
    }
}
LOCALE_NATIVE_NAMES = {'en': 'English', 'ua': 'Українська', 'pl': 'Polski', 'de': 'Deutsch', 'es': 'Español', 'fr': 'Français', 'it': 'Italiano', 'pt': 'Português', 'ro': 'Română', 'nl': 'Nederlands', 'sv': 'Svenska', 'tr': 'Türkçe', 'ja': '日本語', 'zh': '中文', 'ko': '한국어', 'ar': 'العربية', 'hi': 'हिन्दी'}

EMOJI = {'language': '🌐', 'theme': '🎨', 'font': '🔤', 'scaling': '📏', 'source_root': '📁', 'output_folder': '📦', 'shorten_prefix': '✂️', 'include_ext': '➕', 'exclude_ext': '🚫', 'exclude_dirs': '🗂️', 'exclude_files': '📄', 'output_ext': '📝', 'mode': '⚙️', 'output_name': '📝', 'include_root_files': '🧷', 'separator': '➖', 'list_only_names': '📋', 'action': '⚙️', 'unbundle_src': '📥', 'unbundle_out': '🧩', 'copy_out': '📂', 'list_only': '📋', 'run': '🚀', 'profiles': '✦', 'import': '📤', 'export': '📥', 'explorer': '🧭', 'unbundle_shorten': '✂️', 'unbundle_ext': '📝', 'bundle': '📦'}

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

def iter_files(root: Path, include_ext: Optional[Set[str]] = None, exclude_ext: Optional[Set[str]] = None) -> Iterable[Path]:
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

def iter_files_filtered(root: Path, include_ext: Optional[Set[str]], exclude_ext: Optional[Set[str]], exclude_dirs: Set[str], exclude_files: Set[str]) -> Iterable[Path]:
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
        return str(path.relative_to(shorten_root))
    except ValueError:
        return str(path)

def write_bundle(files: Iterable[Path], out_file: Path, shorten_root: Optional[Path] = None, header_prefix: str = "file path: ", encoding: str = "utf-8", add_separator: bool = True, list_only_names: bool = False):
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with out_file.open("w", encoding=encoding, errors="ignore") as out:
        if list_only_names:
            for f in files:
                out.write(f"{shorten_path(f, shorten_root)}\n")
            return
        first = True
        for f in files:
            if not first:
                out.write("\n")
            first = False
            out.write(f"{header_prefix}{shorten_path(f, shorten_root)}\n\n")
            try:
                with f.open("r", encoding=encoding, errors="ignore") as src:
                    out.write(src.read())
            except Exception as e:
                out.write(f"\nERROR READING FILE: {e}\n")
            if add_separator:
                out.write("\n\n" + "-" * 80 + "\n\n")

def bundle_mode_all(src_root: Path, save_root: Path, output_name: str = "all_sources.txt", include_ext: Optional[Set[str]] = None, exclude_ext: Optional[Set[str]] = None, shorten_root: Optional[Path] = None, exclude_dirs: Optional[Set[str]] = None, exclude_files: Optional[Set[str]] = None, add_separator: bool = True, list_only_names: bool = False):
    if exclude_dirs or exclude_files:
        files = list(iter_files_filtered(src_root, include_ext, exclude_ext, exclude_dirs or set(), exclude_files or set()))
    else:
        files = list(iter_files(src_root, include_ext, exclude_ext))
    out_file = save_root / output_name
    write_bundle(files, out_file, shorten_root=shorten_root, add_separator=add_separator, list_only_names=list_only_names)
    return out_file

def bundle_mode_copy_tree(src_root: Path, save_root: Path, include_ext: Optional[Set[str]] = None, exclude_ext: Optional[Set[str]] = None, shorten_root: Optional[Path] = None, exclude_dirs: Optional[Set[str]] = None, exclude_files: Optional[Set[str]] = None, add_separator: bool = True, list_only_names: bool = False, out_ext: str = "txt") -> List[Path]:
    src_root = src_root.resolve()
    save_root = save_root.resolve()
    ex_dirs = exclude_dirs or set()
    ex_files = exclude_files or set()
    clean_ext = out_ext.lstrip(".")
    written: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(src_root, topdown=True):
        dirnames[:] = sorted([d for d in dirnames if d not in ex_dirs])
        dp = Path(dirpath)
        rel_dir = dp.relative_to(src_root)
        for name in sorted(filenames):
            if name in ex_files:
                continue
            p = dp / name
            ext = p.suffix.lower()
            if include_ext and ext not in include_ext:
                continue
            if exclude_ext and ext in exclude_ext:
                continue
            out_dir = save_root / rel_dir
            out_dir.mkdir(parents=True, exist_ok=True)
            out_file = out_dir / f"{p.stem}.{clean_ext}"
            write_bundle([p], out_file, shorten_root=shorten_root, add_separator=False, list_only_names=list_only_names)
            written.append(out_file)
    return written

def bundle_mode_per_top_folder_mirror(src_root: Path, save_root: Path, include_ext: Optional[Set[str]] = None, exclude_ext: Optional[Set[str]] = None, shorten_root: Optional[Path] = None, exclude_dirs: Optional[Set[str]] = None, exclude_files: Optional[Set[str]] = None, add_separator: bool = True, list_only_names: bool = False, out_ext: str = "txt") -> List[Path]:
    src_root = src_root.resolve()
    save_root = save_root.resolve()
    save_root.mkdir(parents=True, exist_ok=True)
    ex_dirs = exclude_dirs or set()
    ex_files = exclude_files or set()
    clean_ext = out_ext.lstrip(".")
    written: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(src_root, topdown=True):
        dirnames[:] = sorted([d for d in dirnames if d not in ex_dirs])
        dp = Path(dirpath)
        rel_dir = dp.relative_to(src_root)
        dir_files = []
        for name in sorted(filenames):
            if name in ex_files:
                continue
            p = dp / name
            ext = p.suffix.lower()
            if include_ext and ext not in include_ext:
                continue
            if exclude_ext and ext in exclude_ext:
                continue
            dir_files.append(p)
        if not dir_files:
            continue
        folder_name = dp.name if dp != src_root else "_root"
        out_dir = save_root / rel_dir
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f"{folder_name}.{clean_ext}"
        write_bundle(dir_files, out_file, shorten_root=shorten_root, add_separator=add_separator, list_only_names=list_only_names)
        written.append(out_file)
    return written

def unbundle_files(src_folder: Path, out_folder: Path, override_ext: Optional[str] = None, strip_prefix: Optional[str] = None, encoding: str = "utf-8") -> List[Path]:
    header_prefix = "file path: "
    sep_pattern = re.compile(r"^-{10,}$")
    out_folder.mkdir(parents=True, exist_ok=True)
    written: List[Path] = []
    norm_strip = strip_prefix.rstrip("/\\").lower() if strip_prefix else None
    bundle_files: List[Path] = []
    for dirpath, _, filenames in os.walk(src_folder):
        for name in filenames:
            bundle_files.append(Path(dirpath) / name)
    for bfile in bundle_files:
        try:
            text = bfile.read_text(encoding=encoding, errors="ignore")
        except Exception:
            continue
        if header_prefix not in text:
            continue
        segments: List[Tuple[str, str]] = []
        current_path: Optional[str] = None
        current_lines: List[str] = []
        for line in text.splitlines(keepends=True):
            stripped = line.rstrip("\n\r")
            if stripped.startswith(header_prefix):
                if current_path is not None:
                    segments.append((current_path, "".join(current_lines)))
                current_path = stripped[len(header_prefix):].strip()
                current_lines = []
            else:
                if current_path is not None:
                    current_lines.append(line)
        if current_path is not None:
            segments.append((current_path, "".join(current_lines)))
        for orig_path_str, content in segments:
            path_str = orig_path_str.strip()
            if norm_strip:
                norm_path = path_str.replace("\\", "/")
                norm_prefix = norm_strip.replace("\\", "/")
                if norm_path.lower().startswith(norm_prefix.lower()):
                    path_str = path_str[len(norm_strip):].lstrip("/\\")
            orig_path = Path(path_str.replace("\\", "/"))
            if override_ext:
                ext = override_ext if override_ext.startswith(".") else "." + override_ext
                orig_path = orig_path.with_suffix(ext)
            if orig_path.is_absolute():
                parts = orig_path.parts
                start = 1 if parts and (parts[0].endswith("\\") or parts[0] == "/") else 0
                orig_path = Path(*parts[start:]) if len(parts) > start else Path(orig_path.name)
            lines = content.splitlines()
            while lines and (sep_pattern.match(lines[-1].strip()) or not lines[-1].strip()):
                lines.pop()
            while lines and not lines[0].strip():
                lines.pop(0)
            content_clean = "\n".join(lines)
            dest = out_folder / orig_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                dest.write_text(content_clean, encoding=encoding, errors="ignore")
                written.append(dest)
            except Exception:
                pass
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
        os.startfile(p)
    except AttributeError:
        import subprocess
        if os.name == "posix":
            subprocess.Popen(["xdg-open", str(p)])
        elif os.name == "mac":
            subprocess.Popen(["open", str(p)])

class BundleApp(tk.Tk):
    PROFILE_COLORS = ["#E53935", "#8E24AA", "#1E88E5", "#43A047", "#FB8C00"]

    def __init__(self):
        super().__init__()
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            pass
        try:
            import sys
            base = sys._MEIPASS if hasattr(sys, "_MEIPASS") else os.path.dirname(os.path.abspath(__file__))
            ico = os.path.join(base, "icon.ico")
            if os.path.exists(ico):
                self.iconbitmap(ico)
        except Exception:
            pass
        try:
            default_font = tkfont.nametofont("TkDefaultFont")
            default_font.configure(family="Segoe UI", size=10)
            self.base_font_size = int(default_font.cget("size") or 10)
            self.option_add("*Font", default_font)
        except Exception:
            self.base_font_size = 10

        self.geometry("1100x760+100+100")
        self.config_data = self.load_config()
        geom = self.config_data.get("geometry")
        if geom:
            try:
                self.geometry(geom)
            except Exception:
                pass

        self.current_lang = self.config_data.get("language", "en")
        self.current_theme = self.config_data.get("theme", "nord")
        self.font_profile = self.config_data.get("font_profile", "Mono")
        self.scaling_value = float(self.config_data.get("scaling", 1.75))

        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        self.src_var = tk.StringVar(value=self.config_data.get("src_root", DEFAULT_FIELD_VALUES["src_root"]))
        self.save_var = tk.StringVar(value=self.config_data.get("save_root", DEFAULT_FIELD_VALUES["save_root"]))
        self.shorten_var = tk.StringVar(value=self.config_data.get("shorten_root", DEFAULT_FIELD_VALUES["shorten_root"]))
        self.ext_include_var = tk.StringVar(value=self.config_data.get("include_ext", DEFAULT_FIELD_VALUES["include_ext"]))
        self.ext_exclude_var = tk.StringVar(value=self.config_data.get("exclude_ext", DEFAULT_FIELD_VALUES["exclude_ext"]))
        self.exclude_dirs_var = tk.StringVar(value=self.config_data.get("exclude_dirs", DEFAULT_FIELD_VALUES["exclude_dirs"]))
        self.exclude_files_var = tk.StringVar(value=self.config_data.get("exclude_files", DEFAULT_FIELD_VALUES["exclude_files"]))
        self.output_name_var = tk.StringVar(value=self.config_data.get("output_name", DEFAULT_FIELD_VALUES["output_name"]))
        self.output_ext_var = tk.StringVar(value=self.config_data.get("output_ext", "txt"))
        self.copy_out_var = tk.StringVar(value=self.config_data.get("copy_out_folder", DEFAULT_FIELD_VALUES["copy_out_folder"]))
        self.mode_var = tk.StringVar(value=self.config_data.get("mode", "all"))
        self.include_root_files_var = tk.BooleanVar(value=self.config_data.get("include_root_files", True))
        self.add_separator_var = tk.BooleanVar(value=self.config_data.get("add_separator", True))
        self.list_only_names_var = tk.BooleanVar(value=self.config_data.get("list_only_names", False))
        self.action_var = tk.StringVar(value=self.config_data.get("action", "bundle"))
        self.unbundle_src_var = tk.StringVar(value=self.config_data.get("unbundle_src", DEFAULT_FIELD_VALUES["unbundle_src"]))
        self.unbundle_out_var = tk.StringVar(value=self.config_data.get("unbundle_out", DEFAULT_FIELD_VALUES["unbundle_out"]))
        self.unbundle_ext_var = tk.StringVar(value=self.config_data.get("unbundle_ext", DEFAULT_FIELD_VALUES["unbundle_ext"]))
        self.unbundle_shorten_var = tk.StringVar(value=self.config_data.get("unbundle_shorten", DEFAULT_FIELD_VALUES["unbundle_shorten"]))

        self._profiles: List[dict] = self.config_data.get("profiles", [
            {"name": "Profile 1", "color": "#E53935", "text_color": "#FFFFFF", "histories": {}},
            {"name": "Profile 2", "color": "#8E24AA", "text_color": "#FFFFFF", "histories": {}},
            {"name": "Profile 3", "color": "#1E88E5", "text_color": "#FFFFFF", "histories": {}},
            {"name": "Profile 4", "color": "#43A047", "text_color": "#FFFFFF", "histories": {}},
            {"name": "Profile 5", "color": "#FB8C00", "text_color": "#FFFFFF", "histories": {}},
        ])
        while len(self._profiles) < 5:
            idx = len(self._profiles)
            self._profiles.append({"name": f"Profile {idx+1}", "color": self.PROFILE_COLORS[idx % 5], "text_color": "#FFFFFF", "histories": {}})
        self._active_profile = int(self.config_data.get("active_profile", 0))
        self._active_profile = max(0, min(self._active_profile, len(self._profiles) - 1))
        self.histories: Dict[str, List[Dict[str, str]]] = self._profiles[self._active_profile].get("histories", {})
        self.history_widgets: Dict[str, Tuple[ttk.Combobox, ttk.Label, tk.StringVar, str]] = {}
        self.clear_buttons: List[tk.Widget] = []
        self.theme_widgets: List[tk.Widget] = []
        self.profile_dot_buttons: List[tk.Button] = []
        self.scroll_passthrough_widgets: List[tk.Widget] = []

        self.lang_display_to_code = {"EN": "en", "UA": "ua", "PL": "pl", "DE": "de", "ES": "es", "FR": "fr", "IT": "it", "PT": "pt", "RO": "ro", "NL": "nl", "SV": "sv", "TR": "tr", "JA": "ja", "ZH": "zh", "KO": "ko", "AR": "ar", "HI": "hi"}
        self.lang_code_to_display = {v: k for k, v in self.lang_display_to_code.items()}
        self.lang_native_names = {'en': 'English', 'ua': 'Українська', 'pl': 'Polski', 'de': 'Deutsch', 'es': 'Español', 'fr': 'Français', 'it': 'Italiano', 'pt': 'Português', 'ro': 'Română', 'nl': 'Nederlands', 'sv': 'Svenska', 'tr': 'Türkçe', 'ja': '日本語', 'zh': '中文', 'ko': '한국어', 'ar': 'العربية', 'hi': 'हिन्दी'}
        self.lang_code_to_label = {code: f"{disp} · {self.lang_native_names.get(code, disp)}" for disp, code in self.lang_display_to_code.items()}
        self.lang_label_to_code = {label: code for code, label in self.lang_code_to_label.items()}
        self.lang_var = tk.StringVar(value=self.lang_code_to_label.get(self.current_lang, "EN · English"))

        self.theme_display_to_code = {
        "Dark": "dark", "Dark Purple": "dark_purple", "Dark Purple Light": "dark_purple_light",
        "Sakura": "sakura", "Midnight Blue": "midnight_blue", "Midnight": "midnight",
        "Forest": "forest", "Jungle": "jungle", "Nord": "nord", "Desert": "desert",
        "Amber": "amber", "Darkula": "darkula", "Cyberpunk": "cyberpunk", "Solarized": "solarized",
        "Sunset": "sunset", "Moon": "moon", "Crescent Moon": "crescent_moon", "Monokai": "monokai",
        "Lightspeed": "lightspeed", "Light": "light",
    }
        self.theme_code_to_display = {v: k for k, v in self.theme_display_to_code.items()}
        self.theme_emojis = {
            "dark": "🌑",
            "dark_purple": "🟣",
            "dark_purple_light": "🟣L",
            "sakura": "🌸",
            "midnight_blue": "🌙",
            "midnight": "🌌",
            "forest": "🌲",
            "jungle": "🌿",
            "nord": "❄️",
            "desert": "🏜",
            "amber": "🧡",
            "darkula": "🐼",
            "cyberpunk": "💻",
            "solarized": "☀️",
            "sunset": "🌅",
            "moon": "🌕",
            "crescent_moon": "🌙",
            "monokai": "🎨",
            "lightspeed": "🚀",
            "light": "☀️",
        }
        self.theme_code_to_label = {code: f"{self.theme_emojis.get(code, "🎨")} {label}" for code, label in self.theme_code_to_display.items()}
        self.theme_label_to_code = {label: code for code, label in self.theme_code_to_label.items()}
        self.theme_var = tk.StringVar(value=self.theme_code_to_label.get(self.current_theme, "❄️ Nord"))
        self.font_profiles = ["Default", "Mono", "Mono Large", "Mono Small", "Coding", "Large", "Tiny", "Serif", "Rounded"]
        self.font_var = tk.StringVar(value=self.font_profile)
        self.scaling_labels = [f"{i}%" for i in range(50, 305, 5)]
        self.scaling_var = tk.StringVar(value=self.scaling_to_label(self.scaling_value))
        self.status_var = tk.StringVar(value=self.t("status_ready"))

        self.setup_themes()
        self._build_scrollable_container()
        self._build_ui()
        self.apply_theme(self.current_theme)
        self.init_all_histories()
        self._apply_locale()
        self.apply_font_profile(self.font_profile, self.scaling_value)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def t(self, key: str) -> str:
        return LOCALES.get(self.current_lang, LOCALES["en"]).get(key, LOCALES["en"].get(key, key))

    def e(self, key: str) -> str:
        return EMOJI.get(key, "")

    def load_config(self) -> dict:
        try:
            if CONFIG_PATH.is_file():
                return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
        return {}

    def collect_config_data(self) -> dict:
        self._profiles[self._active_profile]["histories"] = dict(self.histories)
        return {
            "schema": CONFIG_EXPORT_SCHEMA,
            "language": self.current_lang,
            "theme": self.current_theme,
            "font_profile": self.font_profile,
            "scaling": self.scaling_value,
            "mode": self.mode_var.get(),
            "action": self.action_var.get(),
            "src_root": self.src_var.get(),
            "save_root": self.save_var.get(),
            "shorten_root": self.shorten_var.get(),
            "include_ext": self.ext_include_var.get(),
            "exclude_ext": self.ext_exclude_var.get(),
            "exclude_dirs": self.exclude_dirs_var.get(),
            "exclude_files": self.exclude_files_var.get(),
            "output_name": self.output_name_var.get(),
            "output_ext": self.output_ext_var.get(),
            "copy_out_folder": self.copy_out_var.get(),
            "include_root_files": self.include_root_files_var.get(),
            "add_separator": self.add_separator_var.get(),
            "list_only_names": self.list_only_names_var.get(),
            "unbundle_src": self.unbundle_src_var.get(),
            "unbundle_out": self.unbundle_out_var.get(),
            "unbundle_ext": self.unbundle_ext_var.get(),
            "unbundle_shorten": self.unbundle_shorten_var.get(),
            "histories": self.histories,
            "profiles": self._profiles,
            "active_profile": self._active_profile,
            "geometry": self.winfo_geometry(),
        }

    def save_config(self):
        try:
            CONFIG_PATH.write_text(json.dumps(self.collect_config_data(), ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    def export_all_settings(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")], title=self.t("export_all"))
        if not path:
            return
        data = self.collect_config_data()
        Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        messagebox.showinfo(self.t("success_title"), self.t("export_success").format(path=path))

    def import_all_settings(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")], title=self.t("import_all"))
        if not path:
            return
        if not messagebox.askyesno(self.t("warning_title"), self.t("import_confirm")):
            return
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
        except Exception:
            messagebox.showerror(self.t("error_title"), self.t("import_invalid"))
            return
        if not isinstance(data, dict):
            messagebox.showerror(self.t("error_title"), self.t("import_invalid"))
            return
        self.apply_imported_config(data)
        messagebox.showinfo(self.t("success_title"), self.t("import_success"))

    def apply_imported_config(self, data: dict):
        self.config_data = dict(data)
        self.current_lang = data.get("language", self.current_lang)
        self.current_theme = data.get("theme", self.current_theme)
        self.font_profile = data.get("font_profile", self.font_profile)
        self.scaling_value = float(data.get("scaling", self.scaling_value))
        self.src_var.set(data.get("src_root", DEFAULT_FIELD_VALUES["src_root"]))
        self.save_var.set(data.get("save_root", DEFAULT_FIELD_VALUES["save_root"]))
        self.shorten_var.set(data.get("shorten_root", DEFAULT_FIELD_VALUES["shorten_root"]))
        self.ext_include_var.set(data.get("include_ext", DEFAULT_FIELD_VALUES["include_ext"]))
        self.ext_exclude_var.set(data.get("exclude_ext", DEFAULT_FIELD_VALUES["exclude_ext"]))
        self.exclude_dirs_var.set(data.get("exclude_dirs", DEFAULT_FIELD_VALUES["exclude_dirs"]))
        self.exclude_files_var.set(data.get("exclude_files", DEFAULT_FIELD_VALUES["exclude_files"]))
        self.output_name_var.set(data.get("output_name", DEFAULT_FIELD_VALUES["output_name"]))
        self.output_ext_var.set(data.get("output_ext", "txt"))
        self.copy_out_var.set(data.get("copy_out_folder", DEFAULT_FIELD_VALUES["copy_out_folder"]))
        self.mode_var.set(data.get("mode", "all"))
        self.action_var.set(data.get("action", "bundle"))
        self.include_root_files_var.set(data.get("include_root_files", True))
        self.add_separator_var.set(data.get("add_separator", True))
        self.list_only_names_var.set(data.get("list_only_names", False))
        self.unbundle_src_var.set(data.get("unbundle_src", DEFAULT_FIELD_VALUES["unbundle_src"]))
        self.unbundle_out_var.set(data.get("unbundle_out", DEFAULT_FIELD_VALUES["unbundle_out"]))
        self.unbundle_ext_var.set(data.get("unbundle_ext", DEFAULT_FIELD_VALUES["unbundle_ext"]))
        self.unbundle_shorten_var.set(data.get("unbundle_shorten", DEFAULT_FIELD_VALUES["unbundle_shorten"]))
        self._profiles = data.get("profiles", self._profiles)
        while len(self._profiles) < 5:
            idx = len(self._profiles)
            self._profiles.append({"name": f"Profile {idx+1}", "color": self.PROFILE_COLORS[idx % 5], "text_color": "#FFFFFF", "histories": {}})
        self._active_profile = max(0, min(int(data.get("active_profile", 0)), len(self._profiles) - 1))
        self.histories = self._profiles[self._active_profile].get("histories", {})
        self.lang_var.set(self.lang_code_to_label.get(self.current_lang, "EN · English"))
        self.theme_var.set(self.theme_code_to_label.get(self.current_theme, "❄️ Nord"))
        self.font_var.set(self.font_profile)
        self.scaling_var.set(self.scaling_to_label(self.scaling_value))
        self.refresh_profile_bar()
        self._apply_locale()
        self.apply_theme(self.current_theme)
        self.apply_font_profile(self.font_profile, self.scaling_value)
        self.init_all_histories()
        self._update_action_buttons()
        self.save_config()

    def setup_themes(self):
        self.style.configure("TFrame", background="#121212")
        self.style.configure("TLabel", background="#121212", foreground="#E0E0E0")
        self.style.configure("TButton", padding=4)
        self.style.configure("TCheckbutton", background="#121212", foreground="#E0E0E0")
        self.style.configure("TRadiobutton", background="#121212", foreground="#E0E0E0")

    def _blend_color(self, fg: str, bg: str, alpha: float) -> str:
        def c(s): return int(s, 16)
        rf, gf, bf = c(fg[1:3]), c(fg[3:5]), c(fg[5:7])
        rb, gb, bb = c(bg[1:3]), c(bg[3:5]), c(bg[5:7])
        r = int(rf * alpha + rb * (1 - alpha))
        g = int(gf * alpha + gb * (1 - alpha))
        b = int(bf * alpha + bb * (1 - alpha))
        return f"#{r:02X}{g:02X}{b:02X}"

    def apply_theme(self, theme: str):
        themes = {
            "dark": ("#121212", "#E0E0E0", "#03DAC6", "#1E1E1E"),
            "dark_purple": ("#14001F", "#E9D8FD", "#9F7AEA", "#1F102A"),
            "dark_purple_light": ("#1E1033", "#F2E9FE", "#C4A5FF", "#271242"),
            "midnight_blue": ("#020817", "#E0F2FE", "#38BDF8", "#020617"),
            "midnight": ("#0B1020", "#E0ECFF", "#4A90E2", "#141A33"),
            "forest": ("#022C22", "#ECFDF5", "#34D399", "#064E3B"),
            "solarized": ("#002B36", "#EEE8D5", "#B58900", "#073642"),
            "sunset": ("#F8EDE3", "#5D4037", "#FFCCBC", "#F5E1D8"),
            "amber": ("#FFF8E1", "#4E342E", "#FFB300", "#FFF3C4"),
            "darkula": ("#2B2B2B", "#A9B7C6", "#FFA500", "#323232"),
            "jungle": ("#062821", "#E9F5F0", "#00C896", "#0A3A30"),
            "moon": ("#0A0F1A", "#F0F8FF", "#E0F7FA", "#1A2338"),
            "crescent_moon": ("#1A0505", "#F5E1E2", "#D32F2F", "#2A0F10"),
            "monokai": ("#272822", "#F8F8F2", "#FD971F", "#3E3D32"),
            "nord": ("#2E3440", "#E5E9F0", "#88C0D0", "#3B4252"),
            "cyberpunk": ("#0A0015", "#E8F0FF", "#FF00FF", "#1A0033"),
            "desert": ("#FFF8E1", "#7D5A3F", "#FFF59D", "#FFF2C1"),
            "sakura": ("#F3E8F1", "#5C2D4A", "#F8BBD9", "#F1D4E5"),
            "lightspeed": ("#020617", "#E5F0FF", "#22D3EE", "#02081F"),
            "light": ("#FFFFFF", "#202020", "#1E88E5", "#FFFFFF"),
        }
        bg, fg, accent, entry_bg = themes.get(theme, themes["nord"])
        self.configure(bg=bg)
        if hasattr(self, "outer_container"):
            self.outer_container.configure(style="TFrame")
        if hasattr(self, "canvas"):
            self.canvas.configure(background=bg, highlightthickness=0, bd=0)
        if hasattr(self, "content"):
            self.content.configure(style="TFrame")
        self.style.configure("TFrame", background=bg)
        self.style.configure("TLabel", background=bg, foreground=fg)
        self.style.configure("TButton", background=bg, foreground=fg, padding=6)
        self.style.map("TButton", foreground=[("active", fg)], background=[("active", accent)])
        self.style.configure("TCheckbutton", background=bg, foreground=fg)
        self.style.configure("TRadiobutton", background=bg, foreground=fg)
        self.style.configure("TCombobox", fieldbackground=entry_bg, background=entry_bg, foreground=fg, arrowcolor=fg)
        self.style.map("TCombobox", fieldbackground=[("readonly", entry_bg)], foreground=[("readonly", fg)])
        self.style.configure("Status.TLabel", foreground=fg, background=bg)
        run_bg = self._blend_color("#1B5E20", bg, 0.5)
        run_hover = self._blend_color("#2E7D32", bg, 0.5)
        self.style.configure("Run.TButton", background=run_bg, foreground="#FFFFFF", padding=(14, 6), relief="raised", anchor="center", justify="center", compound="center")
        self.style.map("Run.TButton", background=[("active", run_hover)], foreground=[("active", "#FFFFFF")])
        bundle_bg = self._blend_color(accent, bg, 0.35)
        bundle_active_bg = self._blend_color(accent, bg, 0.55)
        self.style.configure("ActionActive.TButton", background=bundle_bg, foreground=fg, padding=5, relief="sunken")
        self.style.map("ActionActive.TButton", background=[("active", bundle_active_bg)], foreground=[("active", fg)])
        self.style.configure("ActionInactive.TButton", background=bg, foreground=fg, padding=5, relief="raised")
        self.style.map("ActionInactive.TButton", background=[("active", bundle_bg)], foreground=[("active", fg)])
        for widget in self.clear_buttons:
            try:
                widget.configure(bg=bg, fg=fg, activebackground=accent, activeforeground=fg, highlightthickness=1, highlightbackground=self._blend_color(fg, bg, 0.2), bd=1)
            except Exception:
                pass
        for widget in self.theme_widgets:
            try:
                widget.configure(bg=bg)
            except Exception:
                pass

    def scaling_to_label(self, scale: float) -> str:
        return f"{int(round(scale * 100))}%"

    def label_to_scaling(self, label: str) -> float:
        try:
            value = int(label.strip().strip("%"))
            return max(0.50, min(3.0, value / 100.0))
        except Exception:
            return 1.25

    def apply_font_profile(self, profile: str, scale: float):
        try:
            default_font = tkfont.nametofont("TkDefaultFont")
        except Exception:
            return
        base = self.base_font_size
        extra_factor = 1.0
        family_candidates = [default_font.cget("family")]
        if profile in ("Mono", "Mono Large", "Mono Small", "Coding"):
            family_candidates = ["Cascadia Mono", "JetBrains Mono", "Fira Code", "Consolas", "Courier New", default_font.cget("family")]
            if profile == "Mono Large":
                extra_factor = 1.2
            elif profile == "Mono Small":
                extra_factor = 0.9
        elif profile == "Large":
            family_candidates = ["Segoe UI", "Arial", default_font.cget("family")]
            extra_factor = 1.3
        elif profile == "Tiny":
            family_candidates = ["Segoe UI", "Arial", default_font.cget("family")]
            extra_factor = 0.8
        elif profile == "Serif":
            family_candidates = ["Georgia", "Times New Roman", default_font.cget("family")]
        elif profile == "Rounded":
            family_candidates = ["Calibri", "Verdana", "Segoe UI", default_font.cget("family")]
        size = max(6, int(base * scale * extra_factor))
        chosen = default_font.cget("family")
        for fam in family_candidates:
            try:
                default_font.configure(family=fam, size=size)
                chosen = fam
                break
            except tk.TclError:
                continue
        self.option_add("*Font", default_font)
        font_tuple = (chosen, size)
        for style_name in ["TLabel", "TButton", "TCheckbutton", "TRadiobutton", "TCombobox", "TEntry", "TFrame", "Status.TLabel"]:
            try:
                self.style.configure(style_name, font=font_tuple)
            except Exception:
                pass

    def _build_scrollable_container(self):
        self.outer_container = ttk.Frame(self)
        self.outer_container.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(self.outer_container, borderwidth=0, highlightthickness=0, bd=0)
        vscroll = ttk.Scrollbar(self.outer_container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.content = ttk.Frame(self.canvas)
        self.content_window = self.canvas.create_window((0, 0), window=self.content, anchor="nw")
        self.theme_widgets.extend([self.outer_container, self.canvas])

        def on_frame_configure(_event=None):
            bbox = self.canvas.bbox("all")
            if bbox:
                self.canvas.configure(scrollregion=(0, 0, bbox[2], max(bbox[3], 0)))
                start, _ = self.canvas.yview()
                if start < 0.0:
                    self.canvas.yview_moveto(0.0)
        def on_canvas_configure(event):
            self.canvas.itemconfigure(self.content_window, width=event.width)
        self.content.bind("<Configure>", on_frame_configure)
        self.canvas.bind("<Configure>", on_canvas_configure)
        self.bind_all("<MouseWheel>", self._on_mousewheel, add="+")
        self.bind_all("<Button-4>", self._on_mousewheel_linux, add="+")
        self.bind_all("<Button-5>", self._on_mousewheel_linux, add="+")

    def _wheel_delta(self, event):
        if getattr(event, "num", None) == 4:
            return -1
        if getattr(event, "num", None) == 5:
            return 1
        if getattr(event, "delta", 0):
            steps = int(-1 * (event.delta / 120))
            return steps if steps != 0 else (-1 if event.delta > 0 else 1)
        return 0

    def _change_scaling_by_wheel(self, direction: int):
        if direction == 0:
            return "break"
        current = self.label_to_scaling(self.scaling_var.get())
        current_percent = int(round(current * 100))
        available = [int(v.strip('%')) for v in self.scaling_labels]
        if current_percent not in available:
            available.append(current_percent)
            available.sort()
        try:
            idx = available.index(current_percent)
        except ValueError:
            idx = min(range(len(available)), key=lambda i: abs(available[i] - current_percent))
        new_idx = max(0, min(len(available) - 1, idx + direction))
        self.scaling_var.set(f"{available[new_idx]}%")
        return "break"

    def _redirect_wheel_to_page(self, event):
        return self._on_mousewheel(event)

    def _register_scroll_passthrough(self, widget):
        self.scroll_passthrough_widgets.append(widget)
        widget.bind("<MouseWheel>", self._redirect_wheel_to_page, add="+")
        widget.bind("<Button-4>", self._redirect_wheel_to_page, add="+")
        widget.bind("<Button-5>", self._redirect_wheel_to_page, add="+")
        widget.bind("<Control-MouseWheel>", self._on_mousewheel, add="+")
        widget.bind("<Control-Button-4>", self._on_mousewheel_linux, add="+")
        widget.bind("<Control-Button-5>", self._on_mousewheel_linux, add="+")

    def _on_mousewheel_linux(self, event):
        return self._on_mousewheel(event)

    def _on_mousewheel(self, event):
        direction = self._wheel_delta(event)
        ctrl_held = (event.state & 0x4) != 0
        if ctrl_held:
            return self._change_scaling_by_wheel(-direction)
        if direction == 0:
            return "break"
        start, end = self.canvas.yview()
        if direction < 0 and start <= 0.0:
            self.canvas.yview_moveto(0.0)
            return "break"
        if direction > 0 and end >= 1.0:
            return "break"
        self.canvas.yview_scroll(direction, "units")
        start, _ = self.canvas.yview()
        if start < 0.0:
            self.canvas.yview_moveto(0.0)
        return "break"

    def _build_input_row(self, parent, label_attr: str, key: str, variable: tk.StringVar, default: str, browse=None, goto=None, extra_buttons=None, combo_values=None, width=None, readonly=False):
        frame = ttk.Frame(parent)
        frame.pack(fill="x", padx=8, pady=4)
        label = ttk.Label(frame, text="")
        label.pack(anchor="w")
        setattr(self, label_attr, label)
        row = ttk.Frame(frame)
        row.pack(fill="x")
        combo = ttk.Combobox(row, textvariable=variable, values=combo_values or (), state="readonly" if readonly else "normal", width=width)
        combo.pack(side="left", fill="x", expand=True)
        self._register_scroll_passthrough(combo)
        right = tk.Frame(row, bd=0, highlightthickness=0)
        right.pack(side="right")
        self.theme_widgets.append(right)
        hist_label = ttk.Label(right, text="", width=16)
        hist_label.pack(side="right", padx=(4, 0))
        clear_btn = tk.Button(right, text="✕", width=2, command=lambda k=key, var=variable, cb=combo, lbl=hist_label, d=default: self.delete_history_entry(k, var, cb, lbl, d))
        clear_btn.pack(side="right", padx=(4, 0))
        self.clear_buttons.append(clear_btn)
        if extra_buttons:
            for text, command in reversed(extra_buttons):
                btn = ttk.Button(right, text=text, command=command)
                btn.pack(side="right", padx=(4, 0))
        if goto is not None:
            ttk.Button(right, text=self.t("goto"), command=goto).pack(side="right", padx=(4, 0))
        if browse is not None:
            ttk.Button(right, text=self.t("browse"), command=browse).pack(side="right", padx=(4, 0))
        self.history_widgets[key] = (combo, hist_label, variable, default)
        return frame, combo, hist_label

    def _build_ui(self):
        pad = {"padx": 8, "pady": 4}
        frm_top = ttk.Frame(self.content)
        frm_top.pack(fill="x", **pad)
        self.lbllang = ttk.Label(frm_top, text="")
        self.lbllang.pack(side="left")
        self.lang_combo = ttk.Combobox(frm_top, textvariable=self.lang_var, values=list(self.lang_code_to_label.values()), width=18, state="readonly")
        self.lang_combo.pack(side="left", padx=(4, 12))
        self._register_scroll_passthrough(self.lang_combo)
        self.lang_var.trace_add("write", self.on_lang_change)
        self.lbltheme = ttk.Label(frm_top, text="")
        self.lbltheme.pack(side="left")
        self.theme_combo = ttk.Combobox(frm_top, textvariable=self.theme_var, values=list(self.theme_code_to_label.values()), width=20, state="readonly")
        self.theme_combo.pack(side="left", padx=(4, 12))
        self._register_scroll_passthrough(self.theme_combo)
        self.theme_var.trace_add("write", self.on_theme_change)
        self.lblfont = ttk.Label(frm_top, text="")
        self.lblfont.pack(side="left")
        self.font_combo = ttk.Combobox(frm_top, textvariable=self.font_var, values=self.font_profiles, width=10, state="readonly")
        self.font_combo.pack(side="left", padx=(4, 12))
        self._register_scroll_passthrough(self.font_combo)
        self.font_var.trace_add("write", self.on_font_change)
        self.lblscaling = ttk.Label(frm_top, text="")
        self.lblscaling.pack(side="left")
        self.scaling_combo = ttk.Combobox(frm_top, textvariable=self.scaling_var, values=self.scaling_labels, width=6, state="readonly")
        self.scaling_combo.pack(side="left", padx=(4, 12))
        self._register_scroll_passthrough(self.scaling_combo)
        self.scaling_var.trace_add("write", self.on_scaling_change)
        self.btn_run = ttk.Button(frm_top, text="🚀 Run", command=self.run, style="Run.TButton", width=16)
        self.btn_run.pack(side="left", padx=(12, 4))
        self.btn_bundle = ttk.Button(frm_top, text="Bundle", command=lambda: self._set_action("bundle"), style="ActionActive.TButton")
        self.btn_bundle.pack(side="left", padx=(4, 0))
        self.btn_unbundle = ttk.Button(frm_top, text="Unbundle", command=lambda: self._set_action("unbundle"), style="ActionInactive.TButton")
        self.btn_unbundle.pack(side="left", padx=(2, 12))
        self._update_action_buttons()

        self.frm_profile = ttk.Frame(self.content)
        self.frm_profile.pack(fill="x", padx=8, pady=(0, 4))
        self._build_profile_bar(self.frm_profile)

        self.frm_switch = ttk.Frame(self.content)
        self.frm_switch.pack(fill="x")
        extra_src = [(self.t("explorer"), self._open_explorer)]
        self.frm_src, self.src_combo, self.src_hist_label = self._build_input_row(self.frm_switch, "lbl_source_root", "src_root", self.src_var, DEFAULT_FIELD_VALUES["src_root"], browse=self.browse_src, goto=self.goto_src, extra_buttons=extra_src)

        self.frm_bundle_panel = ttk.Frame(self.frm_switch)
        self.frm_bundle_panel.pack(fill="x")
        extra_short = [(self.t("auto_shorten"), self.auto_shorten)]
        self.frm_short, self.shorten_combo, self.shorten_hist_label = self._build_input_row(self.frm_bundle_panel, "lbl_shorten_prefix", "shorten_root", self.shorten_var, DEFAULT_FIELD_VALUES["shorten_root"], browse=self.browse_shorten, extra_buttons=extra_short)
        self.frm_save, self.save_combo, self.save_hist_label = self._build_input_row(self.frm_bundle_panel, "lbl_output_folder", "save_root", self.save_var, DEFAULT_FIELD_VALUES["save_root"], browse=self.browse_save, goto=self.goto_save)
        self.frm_include, self.include_combo, self.include_hist_label = self._build_input_row(self.frm_bundle_panel, "lbl_include_ext", "include_ext", self.ext_include_var, DEFAULT_FIELD_VALUES["include_ext"])
        self.frm_exclude, self.exclude_combo, self.exclude_hist_label = self._build_input_row(self.frm_bundle_panel, "lbl_exclude_ext", "exclude_ext", self.ext_exclude_var, DEFAULT_FIELD_VALUES["exclude_ext"])
        self.frm_ex_dirs, self.exclude_dirs_combo, self.exclude_dirs_hist_label = self._build_input_row(self.frm_bundle_panel, "lbl_exclude_dirs", "exclude_dirs", self.exclude_dirs_var, DEFAULT_FIELD_VALUES["exclude_dirs"])
        self.frm_ex_files, self.exclude_files_combo, self.exclude_files_hist_label = self._build_input_row(self.frm_bundle_panel, "lbl_exclude_files", "exclude_files", self.exclude_files_var, DEFAULT_FIELD_VALUES["exclude_files"])

        frm_output_ext = ttk.Frame(self.frm_bundle_panel)
        frm_output_ext.pack(fill="x", **pad)
        self.lbl_output_ext = ttk.Label(frm_output_ext, text="")
        self.lbl_output_ext.pack(side="left")
        self.output_ext_combo = ttk.Combobox(frm_output_ext, textvariable=self.output_ext_var, values=["txt", "md", "py", "js", "ts", "json", "html", "css", "xml", "yaml"], width=8, state="normal")
        self.output_ext_combo.pack(side="left", padx=(6, 0))
        self._register_scroll_passthrough(self.output_ext_combo)

        frm_mode = ttk.Frame(self.frm_bundle_panel)
        frm_mode.pack(fill="x", **pad)
        self.lbl_mode = ttk.Label(frm_mode, text="")
        self.lbl_mode.pack(anchor="w")
        self.rb_all = ttk.Radiobutton(frm_mode, variable=self.mode_var, value="all")
        self.rb_all.pack(anchor="w")
        self.rb_copy = ttk.Radiobutton(frm_mode, variable=self.mode_var, value="copy_tree")
        self.rb_copy.pack(anchor="w")
        self.rb_folder = ttk.Radiobutton(frm_mode, variable=self.mode_var, value="per_folder")
        self.rb_folder.pack(anchor="w")

        self.frm_output_name, self.output_name_combo, self.output_name_hist_label = self._build_input_row(self.frm_bundle_panel, "lbl_output_name", "output_name", self.output_name_var, DEFAULT_FIELD_VALUES["output_name"])
        self.frm_copy_out, self.copy_out_combo, self.copy_out_hist_label = self._build_input_row(self.frm_bundle_panel, "lbl_copy_out", "copy_out_folder", self.copy_out_var, DEFAULT_FIELD_VALUES["copy_out_folder"], browse=self.browse_copy_out, goto=self.goto_copy_out)

        frm_checks = ttk.Frame(self.frm_bundle_panel)
        frm_checks.pack(fill="x", **pad)
        self.chk_include_root = ttk.Checkbutton(frm_checks, variable=self.include_root_files_var)
        self.chk_include_root.pack(anchor="w")
        self.chk_separator = ttk.Checkbutton(frm_checks, variable=self.add_separator_var)
        self.chk_separator.pack(anchor="w")
        self.chk_list_only = ttk.Checkbutton(frm_checks, variable=self.list_only_names_var)
        self.chk_list_only.pack(anchor="w")

        self.frm_unbundle_panel = ttk.Frame(self.frm_switch)
        self.frm_unbundle_panel.pack_forget()
        extra_unshort = [(self.t("auto_shorten"), self._auto_unbundle_shorten)]
        self.frm_ubsrc, self.unbundle_src_combo, self.unbundle_src_hist_label = self._build_input_row(self.frm_unbundle_panel, "lbl_unbundle_src", "unbundle_src", self.unbundle_src_var, DEFAULT_FIELD_VALUES["unbundle_src"], browse=self.browse_unbundle_src, goto=self.goto_unbundle_src)
        self.frm_ubout, self.unbundle_out_combo, self.unbundle_out_hist_label = self._build_input_row(self.frm_unbundle_panel, "lbl_unbundle_out", "unbundle_out", self.unbundle_out_var, DEFAULT_FIELD_VALUES["unbundle_out"], browse=self.browse_unbundle_out, goto=self.goto_unbundle_out)
        self.frm_ubshort, self.unbundle_shorten_combo, self.unbundle_shorten_hist_label = self._build_input_row(self.frm_unbundle_panel, "lbl_unbundle_shorten", "unbundle_shorten", self.unbundle_shorten_var, DEFAULT_FIELD_VALUES["unbundle_shorten"], extra_buttons=extra_unshort)
        self.frm_ubext, self.unbundle_ext_combo, self.unbundle_ext_hist_label = self._build_input_row(self.frm_unbundle_panel, "lbl_unbundle_ext", "unbundle_ext", self.unbundle_ext_var, DEFAULT_FIELD_VALUES["unbundle_ext"])

        self.lbl_status = ttk.Label(self.content, textvariable=self.status_var, style="Status.TLabel")
        self.lbl_status.pack(anchor="w", padx=8, pady=(8, 4))
        # Cat label
        self.cat_label = ttk.Label(self.content, text=random.choice(LEXI_CAT_MESSAGES))
        self.cat_label.pack(pady=(8, 14))
        self._toggle_panels()

    def _build_profile_bar(self, parent):
        self.profbtn = ttk.Button(parent, text=self.get_profile_label(), command=self.open_profile_menu, width=18)
        self.profbtn.pack(side="left", padx=(0, 8))
        self.btn_import_all = ttk.Button(parent, text=self.t("import_all"), command=self.import_all_settings, width=10)
        self.btn_import_all.pack(side="left", padx=(0, 4))
        self.btn_export_all = ttk.Button(parent, text=self.t("export_all"), command=self.export_all_settings, width=10)
        self.btn_export_all.pack(side="left", padx=(0, 8))
        self.profile_dots_frame = tk.Frame(parent, bd=0, highlightthickness=0)
        self.profile_dots_frame.pack(side="left")
        self.theme_widgets.append(self.profile_dots_frame)
        self.refresh_profile_bar()

    def refresh_profile_bar(self):
        self.profbtn.config(text=self.get_profile_label())
        for btn in self.profile_dot_buttons:
            btn.destroy()
        self.profile_dot_buttons.clear()
        for i in range(len(self._profiles)):
            p = self._profiles[i]
            btn = tk.Button(self.profile_dots_frame, text="✦" if i == self._active_profile else "•", bg=p.get("color", self.PROFILE_COLORS[i % 5]), fg=p.get("text_color", "#FFFFFF"), relief="sunken" if i == self._active_profile else "raised", bd=3 if i == self._active_profile else 2, width=2, height=1, command=lambda idx=i: self.switch_profile(idx))
            btn.pack(side="left", padx=2)
            self.profile_dot_buttons.append(btn)
        self.apply_theme(self.current_theme)

    def get_profile_label(self) -> str:
        p = self._profiles[self._active_profile]
        return p.get('name', f'Profile {self._active_profile + 1}')

    def switch_profile(self, idx: int):
        if idx == self._active_profile:
            return
        self._profiles[self._active_profile]["histories"] = dict(self.histories)
        self._active_profile = idx
        self.histories = self._profiles[self._active_profile].get("histories", {})
        self.refresh_profile_bar()
        self.init_all_histories()
        self.save_config()

    def open_profile_menu(self):
        win = tk.Toplevel(self)
        win.title("Manage Profiles ✦")
        win.resizable(False, False)
        win.grab_set()
        frm = ttk.Frame(win)
        frm.pack(fill="both", expand=True, padx=10, pady=10)
        ttk.Label(frm, text="Profiles ✦", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 6))
        listbox = ttk.Frame(frm)
        listbox.pack(fill="x")
        def rebuild():
            for child in listbox.winfo_children():
                child.destroy()
            for i, p in enumerate(self._profiles):
                row = ttk.Frame(listbox)
                row.pack(fill="x", pady=2)
                dot = tk.Button(row, text="", bg=p.get("color", self.PROFILE_COLORS[i % 5]), width=2, command=lambda idx=i: pick_color(idx))
                dot.pack(side="left", padx=(0, 4))
                name_var = tk.StringVar(value=p.get("name", f"Profile {i+1}"))
                ent = ttk.Entry(row, textvariable=name_var, width=18)
                ent.pack(side="left")
                def rename(_event=None, idx=i, var=name_var):
                    self._profiles[idx]["name"] = var.get().strip() or f"Profile {idx+1}"
                    self.refresh_profile_bar()
                    self.save_config()
                ent.bind("<FocusOut>", rename)
                ent.bind("<Return>", rename)
                ttk.Button(row, text="◀", width=3, command=lambda idx=i: move_profile(idx, -1)).pack(side="left", padx=2)
                ttk.Button(row, text="▶", width=3, command=lambda idx=i: move_profile(idx, 1)).pack(side="left", padx=2)
                ttk.Button(row, text="Use", width=5, command=lambda idx=i: use_profile(idx)).pack(side="left", padx=2)
                del_btn = ttk.Button(row, text="🗑", width=3, command=lambda idx=i: delete_profile(idx))
                del_btn.pack(side="left", padx=2)
                if len(self._profiles) <= 1:
                    del_btn.state(["disabled"])
        def use_profile(idx):
            self.switch_profile(idx)
            rebuild()
        def delete_profile(idx):
            if len(self._profiles) <= 1:
                return
            p = self._profiles[idx]
            confirm = messagebox.askyesno(
                "Delete Profile",
                f"Are you sure you want to delete profile '{p.get('name', f'Profile {idx+1}')}'? This cannot be undone.",
                parent=win,
            )
            if not confirm:
                return
            del self._profiles[idx]
            if self._active_profile == idx:
                self._active_profile = max(0, idx - 1)
                self.histories = self._profiles[self._active_profile].get("histories", {})
                self.init_all_histories()
            elif self._active_profile > idx:
                self._active_profile -= 1
            self.refresh_profile_bar()
            self.save_config()
            rebuild()
        def move_profile(idx, direction):
            new_idx = idx + direction
            if 0 <= new_idx < len(self._profiles):
                self._profiles[idx], self._profiles[new_idx] = self._profiles[new_idx], self._profiles[idx]
                if self._active_profile == idx:
                    self._active_profile = new_idx
                elif self._active_profile == new_idx:
                    self._active_profile = idx
                self.refresh_profile_bar()
                self.save_config()
                rebuild()
        def pick_color(idx):
            from tkinter import colorchooser
            chosen = colorchooser.askcolor(color=self._profiles[idx].get("color", self.PROFILE_COLORS[idx % 5]), parent=win)
            if chosen and chosen[1]:
                self._profiles[idx]["color"] = chosen[1]
                self.refresh_profile_bar()
                self.save_config()
                rebuild()
        rebuild()
        btnrow = ttk.Frame(frm)
        btnrow.pack(fill="x", pady=(10, 0))
        ttk.Button(btnrow, text="Add Profile", command=lambda: add_profile()).pack(side="left")
        ttk.Button(btnrow, text="Close", command=win.destroy).pack(side="right")
        def add_profile():
            idx = len(self._profiles)
            self._profiles.append({"name": f"Profile {idx+1}", "color": self.PROFILE_COLORS[idx % 5], "text_color": "#FFFFFF", "histories": {}})
            self.refresh_profile_bar()
            self.save_config()
            rebuild()

    def init_all_histories(self):
        for key, (combo, label, var, default) in self.history_widgets.items():
            self.init_history_for(key, combo, label, var, default)

    def init_history_for(self, key, combo, label, var, default):
        hist = self.histories.get(key, [])
        values = [e.get("value", "") for e in hist]
        if default and default not in values:
            values.append(default)
        combo["values"] = values
        if hist:
            var.set(hist[0].get("value", default))
            label.config(text=hist[0].get("ts", ""))
        elif not var.get():
            var.set(default)
            label.config(text="")
        else:
            label.config(text="")
        def on_select(_event=None):
            val = var.get()
            ts = ""
            for e in self.histories.get(key, []):
                if e.get("value") == val:
                    ts = e.get("ts", "")
                    break
            label.config(text=ts)
        combo.bind("<<ComboboxSelected>>", on_select)

    def remember_history(self, key: str, value: str):
        value = value.strip()
        if not value:
            return
        hist = self.histories.get(key, [])
        hist = [e for e in hist if e.get("value") != value]
        hist.insert(0, {"value": value, "ts": datetime.now().strftime("%Y-%m-%d %H:%M")})
        self.histories[key] = hist[:HISTORY_MAX_RECENT]
        self._profiles[self._active_profile]["histories"] = self.histories

    def delete_history_entry(self, key: str, var: tk.StringVar, combo: ttk.Combobox, label: ttk.Label, default: str):
        val = var.get().strip()
        if not val:
            var.set(default)
            label.config(text="")
            return
        hist = self.histories.get(key, [])
        self.histories[key] = [e for e in hist if e.get("value") != val]
        var.set(default)
        self.init_history_for(key, combo, label, var, default)
        self.save_config()

    def on_lang_change(self, *_):
        lang_value = self.lang_var.get()
        self.current_lang = self.lang_label_to_code.get(lang_value, self.lang_display_to_code.get(lang_value, "en"))
        self._apply_locale()
        self.save_config()

    def on_theme_change(self, *_):
        theme_value = self.theme_var.get()
        self.current_theme = self.theme_label_to_code.get(theme_value, self.theme_display_to_code.get(theme_value, "nord"))
        self.apply_theme(self.current_theme)
        self.save_config()

    def on_font_change(self, *_):
        self.font_profile = self.font_var.get() if self.font_var.get() in self.font_profiles else "Default"
        self.apply_font_profile(self.font_profile, self.scaling_value)
        self.save_config()

    def on_scaling_change(self, *_):
        self.scaling_value = self.label_to_scaling(self.scaling_var.get())
        self.apply_font_profile(self.font_profile, self.scaling_value)
        self.save_config()

    def _apply_locale(self):
        self.title(self.t("title"))
        self.lbllang.config(text=f"{self.e('language')} {self.t('lang_label')}")
        self.lbltheme.config(text=f"{self.e('theme')} {self.t('theme_label')}")
        self.lblfont.config(text=f"{self.e('font')} {self.t('font_label')}")
        self.lblscaling.config(text=f"{self.e('scaling')} {self.t('scaling_label')}")
        self.btn_run.config(text=f"🚀 {self.t('run')}")
        self.btn_bundle.config(text=self.t("action_bundle"))
        self.btn_unbundle.config(text=self.t("action_unbundle"))
        self.lbl_source_root.config(text=f"{self.e('source_root')} {self.t('source_root_label')}")
        self.lbl_shorten_prefix.config(text=f"{self.e('shorten_prefix')} {self.t('shorten_prefix_label')}")
        self.lbl_output_folder.config(text=f"{self.e('output_folder')} {self.t('output_folder_label')}")
        self.lbl_include_ext.config(text=f"{self.e('include_ext')} {self.t('include_ext_label')}")
        self.lbl_exclude_ext.config(text=f"{self.e('exclude_ext')} {self.t('exclude_ext_label')}")
        self.lbl_exclude_dirs.config(text=f"{self.e('exclude_dirs')} {self.t('exclude_dirs_label')}")
        self.lbl_exclude_files.config(text=f"{self.e('exclude_files')} {self.t('exclude_files_label')}")
        self.lbl_output_ext.config(text=f"{self.e('output_ext')} {self.t('output_ext_label')}")
        self.lbl_mode.config(text=f"{self.e('mode')} {self.t('mode_label')}")
        self.rb_all.config(text=self.t("mode_all"))
        self.rb_copy.config(text=self.t("mode_copy_tree"))
        self.rb_folder.config(text=self.t("mode_per_folder"))
        self.lbl_output_name.config(text=f"{self.e('output_name')} {self.t('output_name_label')}")
        self.lbl_copy_out.config(text=f"{self.e('output_folder')} {self.t('copy_out_label')}")
        self.chk_include_root.config(text=f"{self.e('include_root_files')} {self.t('include_root_files_label')}")
        self.chk_separator.config(text=f"{self.e('separator')} {self.t('separator_label')}")
        self.chk_list_only.config(text=f"{self.e('list_only_names')} {self.t('list_only_names_label')}")
        self.lbl_unbundle_src.config(text=f"{self.e('unbundle_src')} {self.t('unbundle_src_label')}")
        self.lbl_unbundle_out.config(text=f"{self.e('unbundle_out')} {self.t('unbundle_out_label')}")
        self.lbl_unbundle_shorten.config(text=f"{self.e('shorten_prefix')} {self.t('unbundle_shorten_label')}")
        self.lbl_unbundle_ext.config(text=f"{self.e('output_ext')} {self.t('unbundle_ext_label')}")
        self.status_var.set(self.t("status_ready"))
        self.btn_import_all.config(text=f"{self.e('import')} {self.t('import_all')}")
        self.btn_export_all.config(text=f"{self.e('export')} {self.t('export_all')}")
        self.profbtn.config(text=self.get_profile_label())

    def _set_action(self, action: str):
        self.action_var.set(action)
        self._update_action_buttons()
        self._toggle_panels()
        self.save_config()

    def _update_action_buttons(self):
        action = self.action_var.get()
        self.btn_bundle.config(style="ActionActive.TButton" if action == "bundle" else "ActionInactive.TButton")
        self.btn_unbundle.config(style="ActionActive.TButton" if action == "unbundle" else "ActionInactive.TButton")

    def _toggle_panels(self):
        if self.action_var.get() == "unbundle":
            self.frm_bundle_panel.pack_forget()
            self.frm_unbundle_panel.pack(fill="x")
            self.frm_src.pack_forget()
        else:
            self.frm_unbundle_panel.pack_forget()
            self.frm_src.pack(fill="x", padx=8, pady=4)
            self.frm_bundle_panel.pack(fill="x")

    def browse_src(self):
        path = filedialog.askdirectory()
        if path:
            self.src_var.set(path)

    def goto_src(self):
        open_in_explorer(self.src_var.get())

    def browse_shorten(self):
        path = filedialog.askdirectory()
        if path:
            self.shorten_var.set(path)

    def browse_save(self):
        path = filedialog.askdirectory()
        if path:
            self.save_var.set(path)

    def goto_save(self):
        open_in_explorer(self.save_var.get())

    def browse_copy_out(self):
        path = filedialog.askdirectory()
        if path:
            self.copy_out_var.set(path)

    def goto_copy_out(self):
        open_in_explorer(self.copy_out_var.get())

    def browse_unbundle_src(self):
        path = filedialog.askdirectory()
        if path:
            self.unbundle_src_var.set(path)

    def goto_unbundle_src(self):
        open_in_explorer(self.unbundle_src_var.get())

    def browse_unbundle_out(self):
        path = filedialog.askdirectory()
        if path:
            self.unbundle_out_var.set(path)

    def goto_unbundle_out(self):
        open_in_explorer(self.unbundle_out_var.get())

    def auto_shorten(self):
        src = self.src_var.get().strip()
        if src:
            self.shorten_var.set(src)

    def _open_explorer(self):
        src = self.src_var.get().strip()
        if not src:
            messagebox.showwarning(self.t("warning_title"), self.t("warn_source_empty"))
            return
        open_in_explorer(src)

    def _auto_unbundle_shorten(self):
        ub_src_str = self.unbundle_src_var.get().strip()
        if not ub_src_str:
            messagebox.showwarning(self.t("warning_title"), "Set source folder first.")
            return
        ub_src = Path(ub_src_str).expanduser().resolve()
        header_prefix = "file path: "
        all_paths = []
        for dirpath, _, filenames in os.walk(ub_src):
            for name in filenames:
                try:
                    text = (Path(dirpath) / name).read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue
                for line in text.splitlines():
                    if line.startswith(header_prefix):
                        p = line[len(header_prefix):].strip()
                        if p:
                            all_paths.append(p.replace("\\", "/"))
        if not all_paths:
            messagebox.showinfo(self.t("result_title"), "No 'file path:' headers found in source folder.")
            return
        common = list(Path(all_paths[0]).parts)
        for p in all_paths[1:]:
            new_common = []
            for a, b in zip(common, Path(p).parts):
                if a == b:
                    new_common.append(a)
                else:
                    break
            common = new_common
            if not common:
                break
        if common:
            self.unbundle_shorten_var.set("/".join(common))

    def run(self):
        try:
            self.status_var.set(self.t("status_running"))
            self.update_idletasks()
            if self.action_var.get() == "unbundle":
                self._run_unbundle()
            else:
                self._run_bundle()
        except Exception as e:
            self.status_var.set(self.t("status_ready"))
            messagebox.showerror(self.t("error_title"), str(e))

    def _run_unbundle(self):
        ub_src_str = self.unbundle_src_var.get().strip()
        ub_out_str = self.unbundle_out_var.get().strip()
        if not ub_src_str:
            messagebox.showerror(self.t("error_title"), self.t("err_unbundle_src_empty"))
            self.status_var.set(self.t("status_ready"))
            return
        if not ub_out_str:
            messagebox.showerror(self.t("error_title"), self.t("err_unbundle_out_empty"))
            self.status_var.set(self.t("status_ready"))
            return
        ub_src = Path(ub_src_str).expanduser().resolve()
        ub_out = Path(ub_out_str).expanduser().resolve()
        override_ext = self.unbundle_ext_var.get().strip() or None
        strip_prefix = self.unbundle_shorten_var.get().strip() or None
        self.remember_history("unbundle_src", self.unbundle_src_var.get())
        self.remember_history("unbundle_out", self.unbundle_out_var.get())
        self.remember_history("unbundle_ext", self.unbundle_ext_var.get())
        self.remember_history("unbundle_shorten", self.unbundle_shorten_var.get())
        written = unbundle_files(ub_src, ub_out, override_ext=override_ext, strip_prefix=strip_prefix)
        self.status_var.set(self.t("status_ready"))
        if not written:
            messagebox.showinfo(self.t("result_title"), self.t("unbundle_no_files"))
        else:
            msg = self.t("unbundle_success").format(n=len(written), path=ub_out)
            if messagebox.askyesno(self.t("success_title"), msg + "\n\n" + self.t("open_output_folder")):
                open_in_explorer(str(ub_out))
        self.init_all_histories()
        self.save_config()

    def _run_bundle(self):
        src_root_str = self.src_var.get().strip()
        if not src_root_str:
            messagebox.showerror(self.t("error_title"), self.t("err_source_not_set"))
            self.status_var.set(self.t("status_ready"))
            return
        src_root = Path(src_root_str).expanduser().resolve()
        if not src_root.is_dir():
            messagebox.showerror(self.t("error_title"), self.t("err_source_not_dir"))
            self.status_var.set(self.t("status_ready"))
            return
        save_root_str = self.save_var.get().strip()
        save_root = Path(save_root_str).expanduser().resolve() if save_root_str else src_root
        shorten_str = self.shorten_var.get().strip()
        shorten_root = Path(shorten_str).expanduser().resolve() if shorten_str else None
        include_ext = parse_ext_list(self.ext_include_var.get().strip())
        exclude_ext = parse_ext_list(self.ext_exclude_var.get().strip())
        exclude_dirs = parse_name_list(self.exclude_dirs_var.get())
        exclude_files = parse_name_list(self.exclude_files_var.get())
        mode = self.mode_var.get()
        add_sep = self.add_separator_var.get()
        list_only_names = self.list_only_names_var.get()
        out_ext = self.output_ext_var.get().strip() or "txt"
        for key, var in [("src_root", self.src_var), ("save_root", self.save_var), ("shorten_root", self.shorten_var), ("include_ext", self.ext_include_var), ("exclude_ext", self.ext_exclude_var), ("exclude_dirs", self.exclude_dirs_var), ("exclude_files", self.exclude_files_var), ("output_name", self.output_name_var), ("copy_out_folder", self.copy_out_var)]:
            self.remember_history(key, var.get())
        self.save_config()
        if mode == "all":
            raw_name = self.output_name_var.get().strip() or "all_sources"
            output_name = f"{Path(raw_name).stem}.{out_ext.lstrip('.')}"
            out_file = bundle_mode_all(src_root=src_root, save_root=save_root, output_name=output_name, include_ext=include_ext, exclude_ext=exclude_ext, shorten_root=shorten_root, exclude_dirs=exclude_dirs, exclude_files=exclude_files, add_separator=add_sep, list_only_names=list_only_names)
            msg = self.t("success_one").format(path=out_file)
            if messagebox.askyesno(self.t("success_title"), msg + "\n\n" + self.t("open_output_folder")):
                open_in_explorer(str(out_file))
        elif mode == "copy_tree":
            written = bundle_mode_copy_tree(src_root=src_root, save_root=save_root, include_ext=include_ext, exclude_ext=exclude_ext, shorten_root=shorten_root, exclude_dirs=exclude_dirs, exclude_files=exclude_files, add_separator=add_sep, list_only_names=list_only_names, out_ext=out_ext)
            if not written:
                messagebox.showinfo(self.t("result_title"), self.t("no_files"))
            else:
                msg = self.t("success_many").format(paths="\n".join(str(p) for p in written))
                if messagebox.askyesno(self.t("result_title"), msg + "\n\n" + self.t("open_output_folder")):
                    open_in_explorer(str(save_root))
        else:
            written = bundle_mode_per_top_folder_mirror(src_root=src_root, save_root=save_root, include_ext=include_ext, exclude_ext=exclude_ext, shorten_root=shorten_root, exclude_dirs=exclude_dirs, exclude_files=exclude_files, add_separator=add_sep, list_only_names=list_only_names, out_ext=out_ext)
            if not written:
                messagebox.showinfo(self.t("result_title"), self.t("no_files"))
            else:
                msg = self.t("success_many").format(paths="\n".join(str(p) for p in written))
                if messagebox.askyesno(self.t("result_title"), msg + "\n\n" + self.t("open_output_folder")):
                    open_in_explorer(str(save_root))
        self.status_var.set(self.t("status_ready"))
        self.init_all_histories()

    def on_close(self):
        self.save_config()
        self.destroy()

if __name__ == "__main__":
    app = BundleApp()
    app.mainloop()

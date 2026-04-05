import os
import shutil
from pathlib import Path
from typing import Optional, Set

import tkinter as tk
from tkinter import ttk, filedialog, messagebox


# ===== CORE LOGIC =====

def parse_ext_list(ext_list: Optional[str]) -> Set[str]:
    """'ts,tsx, js' -> {'.ts', '.tsx', '.js'}."""
    if not ext_list:
        return set()
    exts = set()
    for raw in ext_list.split(","):
        e = raw.strip()
        if not e:
            continue
        if not e.startswith("."):
            e = "." + e
        exts.add(e.lower())
    return exts


def copy_project_with_txt_conversion(
    src_root: Path,
    dst_root: Path,
    convert_exts: Set[str],
    include_ext: Optional[Set[str]] = None,
    exclude_ext: Optional[Set[str]] = None,
):
    """
    Copy whole project tree from src_root to dst_root.
    - If file extension in convert_exts -> write as .txt (text copy).
    - Otherwise copy as-is (binary safe).
    - include_ext: if set, only these extensions are copied at all.
    - exclude_ext: if set, these extensions are skipped.
    """
    src_root = src_root.resolve()
    dst_root = dst_root.resolve()

    if not src_root.is_dir():
        raise ValueError(f"Source folder does not exist or is not a directory: {src_root}")

    dst_root.mkdir(parents=True, exist_ok=True)

    for dirpath, dirnames, filenames in os.walk(src_root):
        rel_dir = os.path.relpath(dirpath, src_root)
        if rel_dir == ".":
            rel_dir = ""
        target_dir = dst_root / rel_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        for name in filenames:
            src_file = Path(dirpath) / name
            ext = src_file.suffix.lower()

            if include_ext and ext not in include_ext:
                continue
            if exclude_ext and ext in exclude_ext:
                continue

            if ext in convert_exts:
                dst_file = target_dir / (src_file.stem + ".txt")
                with src_file.open("r", encoding="utf-8", errors="ignore") as f_src, \
                     dst_file.open("w", encoding="utf-8", errors="ignore") as f_dst:
                    f_dst.write(f_src.read())
            else:
                dst_file = target_dir / name
                shutil.copy2(src_file, dst_file)


def open_in_explorer(path_str: str):
    """Open path in system file manager (Explorer on Windows)."""
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

class TxtCopyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Project to .txt Copier")
        self.geometry("700x350")

        self.src_var = tk.StringVar()
        self.dst_var = tk.StringVar()
        self.convert_ext_var = tk.StringVar(value="ts,tsx")
        self.include_ext_var = tk.StringVar()
        self.exclude_ext_var = tk.StringVar()

        self._build_ui()

    def _build_ui(self):
        pad = {"padx": 8, "pady": 4}

        # Source folder
        frm_src = ttk.Frame(self)
        frm_src.pack(fill="x", **pad)
        ttk.Label(frm_src, text="Source project folder:").pack(anchor="w")
        src_entry_frame = ttk.Frame(frm_src)
        src_entry_frame.pack(fill="x")
        ttk.Entry(src_entry_frame, textvariable=self.src_var).pack(
            side="left", fill="x", expand=True
        )
        ttk.Button(src_entry_frame, text="Browse", command=self.browse_src).pack(
            side="left", padx=4
        )
        ttk.Button(src_entry_frame, text="Go to", command=self.goto_src).pack(
            side="left", padx=2
        )

        # Destination folder
        frm_dst = ttk.Frame(self)
        frm_dst.pack(fill="x", **pad)
        ttk.Label(frm_dst, text="Destination folder (copy here):").pack(anchor="w")
        dst_entry_frame = ttk.Frame(frm_dst)
        dst_entry_frame.pack(fill="x")
        ttk.Entry(dst_entry_frame, textvariable=self.dst_var).pack(
            side="left", fill="x", expand=True
        )
        ttk.Button(dst_entry_frame, text="Browse", command=self.browse_dst).pack(
            side="left", padx=4
        )
        ttk.Button(dst_entry_frame, text="Go to", command=self.goto_dst).pack(
            side="left", padx=2
        )

        # Extensions config
        frm_ext = ttk.Frame(self)
        frm_ext.pack(fill="x", **pad)
        ttk.Label(
            frm_ext, text="Extensions to convert to .txt (e.g. ts,tsx,js):"
        ).pack(anchor="w")
        ttk.Entry(frm_ext, textvariable=self.convert_ext_var).pack(fill="x")

        ttk.Label(
            frm_ext, text="Include only these extensions (optional, e.g. ts,tsx; empty = all):"
        ).pack(anchor="w")
        ttk.Entry(frm_ext, textvariable=self.include_ext_var).pack(fill="x")

        ttk.Label(
            frm_ext, text="Exclude these extensions (optional, e.g. png,exe):"
        ).pack(anchor="w")
        ttk.Entry(frm_ext, textvariable=self.exclude_ext_var).pack(fill="x")

        # Run button
        frm_run = ttk.Frame(self)
        frm_run.pack(fill="x", pady=12)
        ttk.Button(frm_run, text="Run copy", command=self.run_copy).pack()

        # Status
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self, textvariable=self.status_var, foreground="blue").pack(
            anchor="w", padx=8, pady=4
        )

    def browse_src(self):
        folder = filedialog.askdirectory(title="Select source project folder")
        if folder:
            self.src_var.set(folder)

    def goto_src(self):
        path_str = self.src_var.get().strip()
        if not path_str:
            messagebox.showwarning("Warning", "Source path is empty.")
            return
        open_in_explorer(path_str)

    def browse_dst(self):
        folder = filedialog.askdirectory(title="Select destination folder")
        if folder:
            self.dst_var.set(folder)

    def goto_dst(self):
        path_str = self.dst_var.get().strip()
        if not path_str:
            messagebox.showwarning("Warning", "Destination path is empty.")
            return
        open_in_explorer(path_str)

    def run_copy(self):
        try:
            self.status_var.set("Running...")
            self.update_idletasks()

            src_str = self.src_var.get().strip()
            dst_str = self.dst_var.get().strip()

            if not src_str:
                messagebox.showerror("Error", "Source folder is not set.")
                return
            if not dst_str:
                messagebox.showerror("Error", "Destination folder is not set.")
                return

            src_root = Path(src_str).expanduser().resolve()
            dst_root = Path(dst_str).expanduser().resolve()

            if not src_root.is_dir():
                messagebox.showerror(
                    "Error", "Source folder does not exist or is not a directory."
                )
                return

            convert_exts = parse_ext_list(self.convert_ext_var.get().strip())
            include_ext = parse_ext_list(self.include_ext_var.get().strip()) or None
            exclude_ext = parse_ext_list(self.exclude_ext_var.get().strip()) or None

            copy_project_with_txt_conversion(
                src_root=src_root,
                dst_root=dst_root,
                convert_exts=convert_exts,
                include_ext=include_ext,
                exclude_ext=exclude_ext,
            )

            messagebox.showinfo(
                "Success",
                f"Copy completed.\nSource:\n{src_root}\nDestination:\n{dst_root}",
            )
            self.status_var.set("Ready")
        except Exception as e:
            self.status_var.set("Error")
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    app = TxtCopyApp()
    app.mainloop()

from __future__ import annotations

import math
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
from tkinter import filedialog, messagebox, scrolledtext, ttk

from translator.dna_utils import gc_content
from translator.export import export_xlsx
from translator.parser import SUPPORTED_EXTENSIONS, collect_input_files
from translator.processor import process_file
from translator.protein_translation import STOP_CODONS


class ProteinTranslatorGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.selected_path = ""
        root.title("Protein Translator")
        root.geometry("720x520")
        root.minsize(680, 500)
        self._build_ui()

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, padding=14)
        outer.pack(expand=True, fill=tk.BOTH)

        input_frame = ttk.LabelFrame(outer, text="Input", padding=10)
        input_frame.pack(fill=tk.X)

        self.input_type = tk.StringVar(value="file")
        ttk.Radiobutton(input_frame, text="Single file", variable=self.input_type, value="file").grid(
            row=0, column=0, sticky="w", padx=(0, 12)
        )
        ttk.Radiobutton(input_frame, text="Folder", variable=self.input_type, value="folder").grid(
            row=0, column=1, sticky="w"
        )
        ttk.Button(input_frame, text="Browse", command=self._browse).grid(row=0, column=2, sticky="e")
        input_frame.columnconfigure(3, weight=1)

        self.path_label = ttk.Label(input_frame, text="No file/folder selected", foreground="#1f5fbf")
        self.path_label.grid(row=1, column=0, columnspan=4, sticky="we", pady=(8, 0))

        options = ttk.Frame(outer)
        options.pack(fill=tk.X, pady=(12, 0))

        translation_frame = ttk.LabelFrame(options, text="Output", padding=10)
        translation_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.translation_type = tk.StringVar(value="both")
        for row, (text, value) in enumerate(
            (
                ("DNA -> RNA + proteins", "both"),
                ("DNA -> RNA only", "rna"),
                ("Proteins only", "protein"),
            )
        ):
            ttk.Radiobutton(
                translation_frame,
                text=text,
                variable=self.translation_type,
                value=value,
            ).grid(row=row, column=0, sticky="w", pady=1)

        filter_frame = ttk.LabelFrame(options, text="Protein filters", padding=10)
        filter_frame.grid(row=0, column=1, sticky="nsew")
        options.columnconfigure(0, weight=1)
        options.columnconfigure(1, weight=1)

        ttk.Label(filter_frame, text="Minimum amino acids").grid(row=0, column=0, sticky="w")
        self.min_aa = tk.IntVar(value=0)
        ttk.Spinbox(filter_frame, from_=0, to=100000, textvariable=self.min_aa, width=8).grid(
            row=0, column=1, sticky="w", padx=(8, 0)
        )
        self.complete_only = tk.BooleanVar(value=False)
        ttk.Checkbutton(filter_frame, text="Complete ORFs only", variable=self.complete_only).grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(6, 0)
        )
        self.longest_only = tk.BooleanVar(value=False)
        ttk.Checkbutton(filter_frame, text="Longest protein only", variable=self.longest_only).grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(2, 0)
        )

        actions = ttk.Frame(outer)
        actions.pack(fill=tk.X, pady=(14, 0))
        ttk.Button(actions, text="Translate DNA", command=self._translate).pack(side=tk.LEFT)
        ttk.Label(actions, text="Analyzes +1/+2/+3 and reverse-complement frames.").pack(
            side=tk.LEFT, padx=(12, 0)
        )

        notes = ttk.LabelFrame(outer, text="Biological analysis included", padding=10)
        notes.pack(expand=True, fill=tk.BOTH, pady=(12, 0))
        ttk.Label(
            notes,
            text=(
                "The app detects all AUG-started ORFs, computes reverse complement, "
                "GC%, base counts, start/stop codons, and exports advanced Excel tables."
            ),
            wraplength=640,
            justify="left",
        ).pack(anchor="w")

    def _browse(self) -> None:
        if self.input_type.get() == "file":
            path = filedialog.askopenfilename(
                filetypes=[("Supported files", " ".join(f"*{ext}" for ext in SUPPORTED_EXTENSIONS))]
            )
        else:
            path = filedialog.askdirectory()
        if path:
            self.selected_path = path
            self.path_label.config(text=path)

    def _translate(self) -> None:
        if not self.selected_path:
            messagebox.showwarning("Warning", "Please select a file or folder first.")
            return

        files = collect_input_files(self.selected_path, self.input_type.get())
        if not files:
            messagebox.showerror("Error", "No supported files found.")
            return

        min_aa = max(self.min_aa.get(), 0)
        translation_type = self.translation_type.get()
        complete_only = self.complete_only.get()
        longest_only = self.longest_only.get()

        if len(files) == 1:
            name, path = next(iter(files.items()))
            results_dict = {
                name: process_file(
                    path,
                    translation_type,
                    min_amino_acids=min_aa,
                    complete_only=complete_only,
                    longest_only=longest_only,
                )
            }
        else:
            with ThreadPoolExecutor() as executor:
                futures = {
                    name: executor.submit(
                        process_file,
                        path,
                        translation_type,
                        min_aa,
                        complete_only,
                        longest_only,
                    )
                    for name, path in files.items()
                }
                results_dict = {name: future.result() for name, future in futures.items()}

        self._show_results(results_dict)

    def _show_results(self, results_dict: dict) -> None:
        win = tk.Toplevel(self.root)
        win.title("Translation Results")
        win.geometry("860x640")
        win.minsize(760, 560)

        notebook = ttk.Notebook(win)
        notebook.pack(expand=True, fill=tk.BOTH, padx=8, pady=8)

        text_tab = ttk.Frame(notebook)
        graph_tab = ttk.Frame(notebook)
        notebook.add(text_tab, text="Results")
        notebook.add(graph_tab, text="Graphs")

        legend = ttk.Frame(text_tab)
        legend.pack(fill=tk.X, padx=8, pady=(6, 0))
        ttk.Label(legend, text="Legend:").pack(side=tk.LEFT)
        tk.Label(legend, text=" AUG ", bg="#2ecc71", fg="white", font=("Courier", 9, "bold")).pack(
            side=tk.LEFT, padx=4
        )
        tk.Label(
            legend,
            text=" UAA/UAG/UGA ",
            bg="#e74c3c",
            fg="white",
            font=("Courier", 9, "bold"),
        ).pack(side=tk.LEFT, padx=4)

        txt = scrolledtext.ScrolledText(
            text_tab,
            wrap=tk.WORD,
            font=("Courier", 10),
            background="#ffffff",
            foreground="#111827",
            insertbackground="#111827",
        )
        txt.pack(expand=True, fill=tk.BOTH, padx=6, pady=6)

        txt.tag_configure("start_codon", background="#B7F7C8", foreground="#064E3B", font=("Courier", 10, "bold"))
        txt.tag_configure("stop_codon", background="#FFD1D1", foreground="#8A1111", font=("Courier", 10, "bold"))
        txt.tag_configure("header", foreground="#0B3A75", font=("Courier", 10, "bold"))
        txt.tag_configure("muted", foreground="#4B5563")

        for filename, data in results_dict.items():
            self._insert_file_results(txt, filename, data)

        txt.configure(state="disabled")

        canvas = tk.Canvas(graph_tab, bg="white", highlightthickness=0)
        canvas.pack(expand=True, fill=tk.BOTH, padx=8, pady=8)
        canvas.bind("<Configure>", lambda _event: self._draw_visualization(canvas, results_dict))

        footer = ttk.Frame(win)
        footer.pack(fill=tk.X, padx=8, pady=(0, 8))
        ttk.Button(footer, text="Export XLSX", command=lambda: self._export_xlsx(results_dict)).pack(side=tk.RIGHT)

    def _insert_file_results(self, txt: scrolledtext.ScrolledText, filename: str, data: dict) -> None:
        txt.insert(tk.END, f"--- {filename} ---\n", "header")
        stats = data.get("Stats")
        if not data.get("Valid", False):
            txt.insert(tk.END, "No valid DNA sequence found.\n\n", "muted")
            return

        counts = stats.base_counts
        txt.insert(
            tk.END,
            (
                f"Length: {stats.length} bp | GC: {stats.gc_percent}% | "
                f"A:{counts['A']} T:{counts['T']} C:{counts['C']} G:{counts['G']}\n"
                f"Start codons: {stats.start_codon_count} | Stop codons: {stats.stop_codon_count} | "
                f"Longest protein: {stats.longest_protein_length} aa\n"
                f"Detected ORFs: {len(data['AllORFs'])} | Displayed after filters: {len(data['ORFs'])}\n"
            ),
        )

        if data.get("RNA"):
            txt.insert(tk.END, "RNA codons: ")
            self._insert_colored_codons(txt, self._codon_preview(data["RNA"]))

        txt.insert(tk.END, "Reverse complement preview: ", "muted")
        txt.insert(tk.END, self._sequence_preview(data["ReverseComplement"]) + "\n", "muted")

        if not data["ORFs"]:
            txt.insert(tk.END, "No proteins match the current filters.\n\n", "muted")
            return

        for index, orf in enumerate(data["ORFs"], 1):
            txt.insert(
                tk.END,
                (
                    f"\nProtein {index}: frame {orf.frame}, {orf.direction}, "
                    f"start {orf.start_position}, stop {orf.stop_position or '-'}, "
                    f"{orf.length_nt} nt, {orf.protein_length} aa, "
                    f"{'complete' if orf.complete else 'incomplete'}\n"
                ),
                "header",
            )
            txt.insert(tk.END, "Protein: ")
            txt.insert(tk.END, self._sequence_preview(orf.protein, limit=1200) + "\n")
            txt.insert(tk.END, "Codons: ")
            self._insert_colored_codons(txt, " ".join(f"{codon}:{aa}" for codon, aa in orf.codon_pairs[:120]))
            if len(orf.codon_pairs) > 120:
                txt.insert(tk.END, "... [codon list truncated in GUI]\n", "muted")
            if orf.stop_codon:
                txt.insert(tk.END, "Stop codon: ")
                txt.insert(tk.END, orf.stop_codon + "\n", "stop_codon")

        txt.insert(tk.END, "\n" + "=" * 72 + "\n\n")

    def _insert_colored_codons(self, txt: scrolledtext.ScrolledText, text: str) -> None:
        tokens = text.split()
        for index, token in enumerate(tokens):
            space = "" if index == 0 else " "
            clean = token.split(":", 1)[0].strip("(),[]'\"")
            if clean == "AUG":
                txt.insert(tk.END, space + token, "start_codon")
            elif clean in STOP_CODONS:
                txt.insert(tk.END, space + token, "stop_codon")
            else:
                txt.insert(tk.END, space + token)
        txt.insert(tk.END, "\n")

    def _draw_visualization(self, canvas: tk.Canvas, results_dict: dict) -> None:
        canvas.delete("all")
        valid_items = [(filename, data) for filename, data in results_dict.items() if data.get("Valid", False)]
        if not valid_items:
            canvas.create_text(20, 20, anchor="nw", text="No valid DNA sequence to visualize.", fill="#69727d")
            return

        filename, data = valid_items[0]
        stats = data["Stats"]
        width = max(canvas.winfo_width(), 760)
        margin = 48
        plot_width = width - margin * 2

        canvas.create_text(margin, 18, anchor="nw", text=f"{filename} | {stats.length} bp | GC {stats.gc_percent}%", font=("TkDefaultFont", 11, "bold"))

        axis_y = 72
        canvas.create_line(margin, axis_y, margin + plot_width, axis_y, fill="#34495e", width=2)
        canvas.create_text(margin, axis_y + 14, anchor="nw", text="1")
        canvas.create_text(margin + plot_width, axis_y + 14, anchor="ne", text=str(stats.length))

        def x_for_position(position: int) -> int:
            if stats.length <= 1:
                return margin
            return int(margin + ((position - 1) / (stats.length - 1)) * plot_width)

        for position in self._thin_positions(data["StartPositions"], 280):
            x = x_for_position(position)
            canvas.create_line(x, axis_y - 22, x, axis_y, fill="#2ecc71", width=2)
        for position in self._thin_positions(data["StopPositions"], 280):
            x = x_for_position(position)
            canvas.create_line(x, axis_y, x, axis_y + 22, fill="#e74c3c", width=2)

        canvas.create_text(margin, 122, anchor="nw", text="GC distribution", font=("TkDefaultFont", 10, "bold"))
        gc_y = 152
        windows = self._gc_windows(data["DNA"], 48)
        bar_width = plot_width / max(len(windows), 1)
        for index, gc_value in enumerate(windows):
            x0 = margin + index * bar_width
            x1 = margin + (index + 1) * bar_width - 1
            height = max(2, int((gc_value / 100) * 54))
            color = "#1f9d72" if gc_value >= 50 else "#8dc9a8"
            canvas.create_rectangle(x0, gc_y + 56 - height, x1, gc_y + 56, fill=color, outline="")
        canvas.create_line(margin, gc_y + 56, margin + plot_width, gc_y + 56, fill="#c8d0d8")

        canvas.create_text(margin, 238, anchor="nw", text="Longest displayed proteins", font=("TkDefaultFont", 10, "bold"))
        longest_orfs = sorted(data["ORFs"], key=lambda orf: orf.protein_length, reverse=True)[:10]
        max_length = max((orf.protein_length for orf in longest_orfs), default=1)
        y = 270
        for orf in longest_orfs:
            bar_len = int((orf.protein_length / max_length) * (plot_width - 160))
            canvas.create_text(margin, y + 7, anchor="w", text=f"{orf.frame} {orf.start_position}->{orf.stop_position or '-'}")
            canvas.create_rectangle(margin + 130, y, margin + 130 + bar_len, y + 16, fill="#4a90e2", outline="")
            canvas.create_text(margin + 138 + bar_len, y + 8, anchor="w", text=f"{orf.protein_length} aa")
            y += 28

    def _export_xlsx(self, results_dict: dict) -> None:
        filepath = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if not filepath:
            return
        if export_xlsx(results_dict, filepath):
            messagebox.showinfo("Success", f"Exported to:\n{filepath}")
        else:
            messagebox.showerror("Error", "Export failed. Check console for details.")

    @staticmethod
    def _sequence_preview(sequence: str, limit: int = 600) -> str:
        if len(sequence) <= limit:
            return sequence
        return sequence[:limit] + "... [truncated]"

    @staticmethod
    def _codon_preview(rna: str, limit_codons: int = 160) -> str:
        codons = [rna[index:index + 3] for index in range(0, len(rna) - 2, 3)]
        text = " ".join(codons[:limit_codons])
        if len(codons) > limit_codons:
            text += " ... [truncated]"
        return text

    @staticmethod
    def _thin_positions(positions: list[int], limit: int) -> list[int]:
        if len(positions) <= limit:
            return positions
        step = math.ceil(len(positions) / limit)
        return positions[::step]

    @staticmethod
    def _gc_windows(dna: str, window_count: int) -> list[float]:
        if not dna:
            return []
        size = max(math.ceil(len(dna) / window_count), 1)
        return [gc_content(dna[index:index + size]) for index in range(0, len(dna), size)]

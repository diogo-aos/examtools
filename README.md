# ExamTools

Single-file, offline-friendly web tools for building, filling and presenting exams.

| File | What it does |
|---|---|
| `exam-bench-v9.html` | Exam Bench: turns a JSON question bank into shuffled exam versions (per-version JSON) and ZipGrade answer-key CSVs. |
| `odt-template-filler.html` | ODT Template Filler: fills an ODT template with each version's JSON, one printable `.odt` per version. |
| `exam-presenter.html` | Exam Presenter: slide-show style presenter for exam corrections: load an `exam-bench-bank` JSON (drop or paste), click **Present**, then `Space`/`→` next, `←` previous, `R` hide/reveal answers, `F` fullscreen, `Esc` exit. Tailwind is inlined, so it works offline. |
| `manual.md` / `manual.html` | The user manual. Edit `manual.md`, then run `python3 render-manual.py` to regenerate `manual.html` and the landing page's "Copy AI prompt" text (no dependencies). |
| `workflow.svg` | Diagram of the whole workflow, from writing or converting a bank to the correction in class. |
| `exam-template.odt` | Exam template for the ODT Template Filler (Cyber Warfare test): cover page with guidelines, case study, then the multiple-choice questions, filled from Exam Bench's per-version JSON. |

Open any of the HTML files directly in a browser — no build step or server needed.

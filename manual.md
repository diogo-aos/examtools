# ExamTools — User Manual

From a JSON question bank to printed exam versions, ZipGrade answer keys and a correction slide show.

## 1. Overview

ExamTools is three single-file web apps. Each one runs entirely in your browser, and nothing is uploaded.

| Tool | What it does |
|---|---|
| **Exam Bench** (`exam-bench-v9.html`) | Edit the question bank, batch-edit scores, generate shuffled versions, export the ZipGrade key and one JSON file per version. |
| **ODT Template Filler** (`odt-template-filler.html`) | Fill an ODT template (made in LibreOffice Writer) with each version's JSON, producing one printable `.odt` per version. |
| **Exam Presenter** (`exam-presenter.html`) | Show the bank as slides to go through the correction with students, with answers and justifications. |

The workflow, in order:

1. Open your bank in **Exam Bench** (**Open**, drag a `.json` file onto the editor, or paste it). The format is in Section 2.
2. Fix every error (red) in the Problems panel under the editor. Warnings (amber) do not block anything.
3. Optionally batch-edit scores and penalties in **Scoring** (Section 3).
4. Open **Versions**, choose how many versions and how they are shuffled, and generate them (Section 4).
5. Click **Export** to download one `.zip` with the ZipGrade key, one JSON file per version and an answer-key table (Section 5).
6. Import the CSV into ZipGrade as the quiz's answer key (Section 6).
7. Load your ODT template and the version JSON files into the **ODT Template Filler** to produce the printable exams (Section 7).
8. After the test, load the bank into the **Exam Presenter** to correct it in class (Section 8).
9. Use **Save** to keep the bank as a `.json` file under version control.

## 2. The question bank

The bank is one JSON object. The editor in Exam Bench is the single source of truth: the preview, the scoring tools and every export read from it.

### 2.1 A complete bank

```json
{
  "format": "exam-bench-bank",
  "meta": {
    "title": "Cyber Warfare A 2026/27",
    "symbols": { "multiple": "Ψ" }
  },
  "defaults": {
    "points": 1,
    "penalty": { "single": 0, "multiple": 0.25 }
  },
  "tags": {
    "case:ubiquiti": { "symbol": "🔷", "title": "Ubiquiti case study", "keep_together": true }
  },
  "questions": [
    {
      "id": "ubq-root-access",
      "type": "single",
      "tags": ["uc:defensive", "case:ubiquiti"],
      "text": "Which access did Sharp hold to Ubiquiti's AWS environment?",
      "score": { "points": 2, "penalty": 0.5 },
      "choices": [
        { "text": "Root-level access", "correct": true, "justification": "He led the cloud team." },
        { "text": "Read-only access", "correct": false },
        { "text": "None of the others.", "correct": false }
      ]
    },
    {
      "id": "cia-triad",
      "type": "multiple",
      "tags": ["uc:fundamentals"],
      "text": "Which of the following belong to the CIA triad?",
      "choices": [
        { "text": "Confidentiality", "correct": true },
        { "text": "Integrity", "correct": true },
        { "text": "Authenticity", "correct": false },
        { "text": "Availability", "correct": true }
      ]
    }
  ]
}
```

Only `questions` is required. Every other top-level field is optional.

### 2.2 Questions

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | Unique, stable name (kebab-case). It identifies the question in the Problems panel, the answer-key table and the exports. |
| `type` | no | `single` (exactly one correct choice, the default) or `multiple` (one or more correct choices). |
| `text` | yes | The question, as printed. |
| `tags` | no | Categories, see Section 2.4. A question without tags gets a warning. |
| `score` | no | `points` and `penalty`, see Section 2.3. Missing values come from `defaults`. |
| `choices` | yes | 2 to 5 choices. Each has `text` and `correct`, plus optional `justification` and `fixed`. |
| `active` | no | `false` keeps the question in the bank but leaves it out of totals, versions and exports. |

About choices:

- At most **5 choices**, because ZipGrade's standard answer sheet holds A–E. A question with more is an error and is left out of the versions.
- `justification` is optional. It is shown in the Exam Bench preview and in the Presenter, and is **never** exported to the printed versions.
- Choices such as "None of the others." and "None of the above." are marked `fixed` automatically: when choices are shuffled they stay last. You can set `"fixed": true` on any other choice.

### 2.3 Scoring and penalties

Each question has `points` (for a fully correct answer) and `penalty` (points lost for wrong answers). A blank answer never costs points.

| Type | Points | Penalty |
|---|---|---|
| `single` | All points for the correct choice. | Deducted **once** if the answer is wrong. Default **0**. |
| `multiple` | Split equally between the correct choices: with 3 correct, each one marked earns a third. | Deducted **for each incorrect option marked**. Default **0.25**. |

So a `multiple` question worth 1 point with correct choices A, C and D scores:

- A + C + D → 1
- A + C → 0.67
- A + B → 0.33 − 0.25 = 0.08
- B alone → −0.25

The defaults can be changed for the whole bank in `defaults`, and any question can override them in `score`:

```json
"defaults": { "points": 1, "penalty": { "single": 0, "multiple": 0.25 } }
```

```json
"score": { "points": 2, "penalty": 0.5 }
```

Write `"penalty": 0` to turn the penalty off for a `multiple` question.

### 2.4 Tags and tag definitions

Tags are lowercase strings, optionally written as `namespace:value` — for example `uc:defensive`, `topic:ransomware` or `case:ubiquiti`. You can invent any namespaces. Tags are used in four places:

- the **Scoring** panel can act on the questions carrying one or more tags (Section 3);
- the **Versions** panel can keep the questions sharing a tag together (Section 4);
- the **ZipGrade** CSV can carry them in its Tags column, for per-category statistics (Section 6);
- the **version JSON** carries each question's tags, and its symbols (below).

A tag can be given extra meaning in the bank's `tags` object:

```json
"tags": {
  "case:ubiquiti": { "symbol": "🔷", "title": "Ubiquiti case study", "keep_together": true }
}
```

| Field | Meaning |
|---|---|
| `symbol` | Printed next to the number of every question carrying the tag (via `question_symbols`, Section 7). Use one per case study, so students can tell which text a question refers to. |
| `title` | A readable name, shown in the Exam Bench preview and as a chip on the Presenter's slides. |
| `keep_together` | `true` = questions carrying the tag are never separated when versions are shuffled. They are printed one after the other, in any order. |

The text of a case study itself is not part of the bank: write it in the ODT template.

### 2.5 Metadata

```json
"meta": { "title": "Cyber Warfare A 2026/27", "symbols": { "multiple": "Ψ" } }
```

- `title` names the exported files, and is copied into every version JSON as `title`.
- `symbols.multiple` is the mark printed next to `multiple` questions (in `question_symbols`). It is also copied to the version JSON, so the template can explain it ("Questions marked with Ψ may have more than one correct answer").

### 2.6 What the format does not support

- **Open (free-text) questions.** Write them directly in the ODT template. The bank, the versions and ZipGrade only handle questions with choices.
- **More than 5 choices** per question.
- **Unequal credit** between the correct choices of a `multiple` question (points are always split equally).
- **Images, tables or LaTeX** inside a question.

Older banks may still contain `groups`, `taxonomy`, `score.wrong_discounts` or `score.penalty_per_option`. Exam Bench ignores them and shows a warning, so you can move each one to the new fields (`tags` definitions, `score.penalty`).

### 2.7 The Problems panel

Each message shows the line of the offending question.

- **Errors** make the question not ready: it is shown in red, left out of the totals in the header and left out of versions and exports. Examples: invalid JSON, duplicate `id`, empty text, no correct choice, several correct choices in a `single` question, more than five choices, an open question.
- **Warnings** do not block anything. Examples: missing `id`, no tags, a malformed tag, a tag definition that no question carries, a field that is no longer used.

### 2.8 Dropping JSON files onto the editor

Drag one or more `.json` banks onto the editor. If the editor is empty, the file is loaded. Otherwise a dialog asks what to do:

- **Append questions** adds the dropped questions after the current ones, plus any tag definitions not already in the bank. A question whose `id` already exists is skipped, so the current text always wins.
- **Replace entire text** discards the current text and loads the dropped file. With several files, the first becomes the bank and the others are appended to it.
- **Cancel** (or Esc) changes nothing.

A file that is not valid JSON, or has no `questions` array, is rejected and the current text is left untouched. After an append or a replace, the generated versions are cleared.

## 3. Scoring panel

**Scoring** edits many questions at once by rewriting their `score` objects in the editor.

**Apply to** chooses the questions: click one or more chips — a question type (`single`, `multi`) or a tag. A question is changed when it belongs to at least one highlighted chip. With none highlighted, every active question is changed. The panel header shows how many questions are in scope and their total points.

- **Score** sets `score.points`.
- **Wrong-answer penalty** sets `score.penalty`:
    - **Bank default** removes it, so the question falls back to `defaults.penalty`.
    - **No penalty** writes `0`.
    - **25% / 50% of score** write that fraction of each question's points.
    - **Fixed** writes one amount.
- **Normalize total** rescales the points so the questions in scope add up to a target (20, 100 or a custom value). Explicit penalties are rescaled too.

Inactive questions are never changed. Any change clears the generated versions, since their scores would be stale.

## 4. Generating versions

**Versions** builds shuffled variants of the bank, lettered A, B, C…

| Setting | Effect |
|---|---|
| How many | Number of versions (up to 12). |
| Shuffle seed | The same seed always rebuilds the same versions. Change it to get a different shuffle. |
| Shuffle questions & groups | Reorders questions — and blocks of questions kept together — relative to each other. A block always stays together. |
| Shuffle within groups | Reorders the questions inside each block. |
| Shuffle choices | Reorders each question's choices independently per version. `fixed` choices stay last. |
| Keep together by tag | Every tag shared by two or more questions is listed. Tick one and its questions are never separated. Tags with `keep_together` in the bank are ticked and locked (🔒). |
| ZipGrade tag namespaces | Which tag namespaces go into the CSV's Tags column (default `uc`). Empty = the question `id` is used instead. |

Binding is transitive: if Q1 and Q2 share one bound tag and Q2 and Q3 share another, all three stay together.

Each version is shown as a row of chips such as `case:ubiquiti │ Q12 │ B` — the block (if any), the question's number in the bank and the correct letter(s) in that version — so you can check the shuffle at a glance.

## 5. Exporting

**Export** downloads one `.zip` with:

- `<title>-zipgrade-keys.csv` — the answer key of every version, in ZipGrade's import format (Section 6);
- `<title>-version-A.json`, `-B.json`, … — one JSON file per version, for the ODT Template Filler (Section 7);
- `<title>-answer-keys.md` — a table per version with the answer, points, penalty and tags of each question, for your own reference.

If the browser blocks the download, the **Files** list in the Versions panel lets you save, view or copy each file on its own.

## 6. ZipGrade answer key

The CSV has one row per accepted response: `Key Letter, Question Number, Response/Mapping, Point Value, Tags`. ZipGrade compares the whole response a student marked against these rows, so every response that should score needs its own row. Each question's first row is always the fully correct response, and only that row carries the tags.

- **Single, no penalty**: one row — the correct letter, full points. Anything else scores 0.
- **Single with a penalty**: the same row, plus a row whose response is the literal `[a&i]` ("attempted but incorrect") with the negative penalty.
- **Multiple, no penalty**: one row for every combination of correct letters, worth its share of the points.
- **Multiple with a penalty**: one row for **every** combination of options, worth the share of correct letters minus the penalty for each incorrect letter.

Example: a 1-point `multiple` question with correct answers A, C, D and the default 0.25 penalty is written as:

```text
A,1,ACD,1,fundamentals
A,1,A,0.3333,
A,1,B,-0.25,
A,1,C,0.3333,
A,1,D,0.3333,
A,1,AB,0.0833,
A,1,AC,0.6667,
…
A,1,ABCD,0.75,
```

The file always holds every version's key. Importing it replaces the quiz's whole answer key, so import all versions together rather than one at a time.

## 7. Printing with the ODT Template Filler

### 7.1 The version JSON

Each `-version-X.json` file looks like this:

```json
{
  "version": "A",
  "title": "Cyber Warfare A 2026/27",
  "symbols": { "multiple": "Ψ" },
  "mcq": [
    {
      "question_number": 1,
      "question_id": "cia-triad",
      "question_text": "Which of the following belong to the CIA triad?",
      "question_score": 1,
      "question_penalty": 0.25,
      "question_symbols": "Ψ",
      "tags": ["uc:fundamentals"],
      "options": [
        { "option_number": "A", "option_text": "Integrity" },
        { "option_number": "B", "option_text": "Authenticity" }
      ]
    }
  ]
}
```

| Field | Meaning |
|---|---|
| `version` | The version letter. |
| `title`, `symbols` | Copied from the bank's `meta`. |
| `question_number` | 1, 2, 3… in this version's order. |
| `question_score` | The question's points. |
| `question_penalty` | The penalty as a positive number — the template prints the minus sign. `0` when there is none. |
| `question_symbols` | The symbols of the question's defined tags, then the `multiple` symbol, separated by spaces. Empty when none apply. |
| `option_number` | The option's letter (A, B, C…), ready to print. |

The JSON deliberately contains **no correct answers and no justifications**, so a printed version can never leak the key. The answers are in the CSV and in `answer-keys.md`.

### 7.2 Writing the template

Make the template in LibreOffice Writer and save it as `.odt`. Placeholders are written in curly braces:

| Syntax | Effect |
|---|---|
| `{version}` | Replaced by the field's value. `{symbols.multiple}` reads a nested field. |
| `{#mcq} … {/mcq}` | Repeats everything in between once per question. Inside, the question's fields are available directly. |
| `{#options} … {/options}` | Inside the question loop: repeats once per option. |
| `{#field} … {/field}` | When `field` is not a list: keeps the content only if the field has a value (not empty, `0` or `false`). |

A loop marker alone in a paragraph removes that paragraph, so each marker can sit on its own line. Placeholders work in the page header and footer too.

The included `exam-template.odt` prints each question like this:

```text
{#mcq}
Q {question_number}{#question_symbols} {question_symbols}{/question_symbols} [{question_score} points, -{question_penalty} penalty]. {question_text}
{#options}
{option_number}. {option_text}
{/options}
{/mcq}
```

The conditional around `question_symbols` avoids a stray space on questions without a symbol. The case-study text, the guidelines and any open questions are written directly in the template.

> Keep the printed rules consistent with the bank. For example, if the guidelines say a penalty applies "for each wrong answer" on multiple-answer questions, that is the default behaviour (Section 2.3). If you change `defaults.penalty`, update the guidelines to match.

### 7.3 Filling

1. Open the **ODT Template Filler** and load the template (step 1). No template yet? Download `exam-template.odt` from the same page.
2. Drop the `-version-*.json` files from the export (step 2). Each one becomes one filled document. The tool starts with a sample version, so you can try a template before you have a bank.
3. Click **Fill all versions**, then download each `.odt`, or all of them as one `.zip`.

## 8. Correcting with the Exam Presenter

Load the **bank** JSON (the same file Exam Bench saves — not a version JSON) by dropping it on the page or pasting it, then click **Present**.

Each question becomes one slide, in bank order, with:

- chips for the question number, the `multiple` symbol, the title and symbol of its defined tags, its `uc:` and `topic:` tags, and the points and penalty;
- the choices, with correct ones in green and wrong ones in pink;
- each choice's `justification`, when answers are shown.

Keys: `Space` or `→` next, `←` previous, `R` hide or show the answers, `F` full screen, `Esc` exit. Inactive questions are skipped unless you tick the option to include them.

## 9. Converting an existing bank with an AI assistant

An AI assistant can usually convert questions from a Word document, spreadsheet or PDF into this format. To get a clean result:

- **Give it the format, not just an example.** Paste Sections 2.1–2.4 of this manual. A model shown only one example tends to invent fields that look plausible.
- **Be explicit** about the rules that do not show up in an example: at most 5 choices; a `single` question has exactly one `"correct": true`; tags are lowercase `namespace:value`; text kept verbatim; no open questions.

A prompt that works well:

> Convert the attached questions into the JSON bank format described below. Output one JSON object with a `questions` array only. For every question: a unique kebab-case `id`; `type` (`single`, or `multiple` when several answers are correct); `tags` with exactly one `uc:` tag from this list — [your units] — and one or two `topic:` tags; and `choices` with `text` and `correct`. Leave out `score` unless the source gives points. Keep all text verbatim. Add a `justification` only if the source explains the answer. If a question has more than five choices, is open-ended, or depends on an image or a table, list it at the end under "COULD NOT CONVERT" instead of guessing.

Then always:

1. Paste the result into Exam Bench and fix every error in the Problems panel.
2. Skim the preview: a wrong choice marked correct, or a truncated choice, is easy to miss.
3. Check the choice count of questions that had more than five options in the source.
4. Check the tag counts in the Scoring panel's chips against what you expect.

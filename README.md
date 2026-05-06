# LR(0) Parser with GUI Visualizer

> A fully interactive bottom-up parser built in Python — featuring real-time DFA visualization, canonical collection construction, and step-by-step parse tracing through a modern dark-themed GUI.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Grammar Input Format](#grammar-input-format)
6. [Algorithm Pipeline](#algorithm-pipeline)
7. [Test Example](#test-example)
8. [Module Reference](#module-reference)
9. [GUI Components](#gui-components)
10. [Dependencies](#dependencies)
11. [Author](#author)

---

## Overview

`lr0_parser.py` implements the complete **LR(0) parsing pipeline** from scratch, wrapped in a Tkinter GUI. It accepts any context-free grammar, constructs the LR(0) canonical collection of items, builds the ACTION/GOTO parsing table, and parses arbitrary input strings with a full step-by-step trace — all within a single Python file.

**Course:** Compiler Construction — CS-636  
**Author:** Mohammad Sami | SAP ID: 53199  
**University:** Riphah International University

---

## Features

| Feature | Description |
|---------|-------------|
| **Grammar Augmentation** | Automatically adds `S' → S` for LR(0) acceptance |
| **Closure & GOTO** | Full LR(0) closure and GOTO computation |
| **Canonical Collection** | Builds all LR(0) states via BFS |
| **Parsing Table** | Constructs complete ACTION and GOTO tables |
| **Conflict Detection** | Flags shift/reduce and reduce/reduce conflicts in table cells |
| **Shift-Reduce Parser** | Parses input strings with complete stack trace |
| **DFA Visualizer** | Interactive state diagram using NetworkX + Matplotlib |
| **Dark Theme GUI** | Professional Tkinter interface with colour-coded output |

---

## Installation

**Requirements:** Python 3.8 or higher

```bash
# Install dependencies
pip install networkx matplotlib numpy

# Run the parser
python lr0_parser.py
```

No virtual environment is required. All three external libraries (`networkx`, `matplotlib`, `numpy`) install cleanly with pip. `tkinter` is bundled with the standard Python distribution.

---

## Usage

1. **Enter Grammar** — Type your context-free grammar in the left panel grammar box.
2. **Enter Input String** — Type the string to parse in the input entry field.
3. **Click "Parse String"** — Builds the parser and shows the step-by-step trace in the *Parse Trace* tab.
4. **Click "Show Table"** — Displays the full ACTION/GOTO parsing table in the *Parsing Table* tab.
5. **Click "Show DFA"** — Opens a new window with the LR(0) automaton state diagram.
6. **Click "Clear"** — Resets all inputs and output panels.

> **Tip:** You can also press **Enter** in the input field to trigger parsing immediately.

---

## Grammar Input Format

```
Rule 1: Separate EVERY symbol with spaces
Rule 2: Use  ->  for productions
Rule 3: Use  |  for alternatives
Rule 4: Use  ebs  for epsilon (empty production)
```

**Examples:**

```
S -> A A
A -> a A | b
```

```
E -> E + T | T
T -> T * F | F
F -> ( E ) | id
```

```
S -> a S b | ebs
```

---

## Algorithm Pipeline

```
User Grammar Text
        │
        ▼
 parse_grammar()        ──► OrderedDict of productions
        │
        ▼
 augment_grammar()      ──► Adds S' → S
        │
        ▼
 canonical_collection()
   ├── closure()        ──► Fixed-point closure of LR(0) items
   └── goto()           ──► GOTO(I, X) transitions
        │
        ▼
 build_lr0_table()
   └── add_table_entry() ──► Populates ACTION & GOTO; detects conflicts
        │
        ▼
 lr_parse_with_trace()  ──► Shift-Reduce parsing with stack trace
        │
        ▼
      GUI Display
   ├── Parsing Table Tab  (ACTION / GOTO)
   └── Parse Trace Tab    (Step-by-step stack trace)
```

---

## Test Example

### Grammar

```
S -> A A
A -> a A | b
```

### Augmented Grammar

| # | LHS | RHS |
|---|-----|-----|
| 1 | S'  | S   |
| 2 | S   | A A |
| 3 | A   | a A |
| 4 | A   | b   |

### LR(0) States

| State | Items |
|-------|-------|
| **I0** | `S' → · S`,  `S → · A A`,  `A → · a A`,  `A → · b` |
| **I1** | `S' → S ·` &nbsp;&nbsp; *(accept)* |
| **I2** | `S → A · A`,  `A → · a A`,  `A → · b` |
| **I3** | `A → a · A`,  `A → · a A`,  `A → · b` &nbsp;&nbsp; *(self-loop on a)* |
| **I4** | `A → b ·` &nbsp;&nbsp; *(reduce)* |
| **I5** | `S → A A ·` &nbsp;&nbsp; *(reduce)* |
| **I6** | `A → a A ·` &nbsp;&nbsp; *(reduce)* |

### LR(0) Parsing Table

|State| a   | b   | $   | S  | A  |
|-----|-----|-----|-----|----|----|
| I0  | s3  | s4  |     | 1  | 2  |
| I1  |     |     | acc |    |    |
| I2  | s3  | s4  |     |    | 5  |
| I3  | s3  | s4  |     |    | 6  |
| I4  | r4  | r4  | r4  |    |    |
| I5  | r2  | r2  | r2  |    |    |
| I6  | r3  | r3  | r3  |    |    |

> `sN` = Shift to state N &nbsp;|&nbsp; `rN` = Reduce by production N &nbsp;|&nbsp; `acc` = Accept &nbsp;|&nbsp; blank = Error

**Result:** No conflicts — this grammar is a valid LR(0) grammar.

### Parse Trace for input `a b b`

| # | Stack         | Input   | Action                              |
|---|---------------|---------|-------------------------------------|
| 1 | `0`           | `a b b $` | Shift → s3                        |
| 2 | `0 a 3`       | `b b $`   | Shift → s4                        |
| 3 | `0 a 3 b 4`   | `b $`     | Reduce by (4) A → b               |
| 4 | `0 a 3 A 6`   | `b $`     | Reduce by (3) A → a A             |
| 5 | `0 A 2`       | `b $`     | Shift → s4                        |
| 6 | `0 A 2 b 4`   | `$`       | Reduce by (4) A → b               |
| 7 | `0 A 2 A 5`   | `$`       | Reduce by (2) S → A A             |
| 8 | `0 S 1`       | `$`       | **Accept**                        |

---

## Module Reference

### Grammar Layer

| Function | Signature | Purpose |
|----------|-----------|---------|
| `tokenize_rhs` | `(prod: str) → list` | Splits a single RHS alternative into symbol tokens; handles all epsilon variants |
| `parse_grammar` | `(text) → (grammar, productions)` | Converts multi-line grammar text to OrderedDict + flat production list |
| `augment_grammar` | `(base_grammar) → (grammar, augmented, start_symbol)` | Prepends `S' → S` and returns augmented grammar |
| `collect_terminals` | `(grammar) → list` | Returns all terminal symbols in first-occurrence order |

### Automata Layer

| Function | Signature | Purpose |
|----------|-----------|---------|
| `closure` | `(items, grammar) → frozenset` | Computes LR(0) closure via fixed-point iteration |
| `goto` | `(items, symbol, grammar) → frozenset` | Computes `GOTO(I, X)` — advances dot over symbol X then applies closure |
| `canonical_collection` | `(grammar) → (states, transitions)` | BFS construction of all LR(0) states and transitions |

### Table Layer

| Function | Signature | Purpose |
|----------|-----------|---------|
| `add_table_entry` | `(cell_dict, symbol, value) → bool` | Sets table cell; detects and records conflicts with `/` separator |
| `build_lr0_table` | `(states, transitions, …) → (terminals, nonterminals, action, goto, has_conflict)` | Constructs complete ACTION/GOTO tables |

### Parser Layer

| Function | Signature | Purpose |
|----------|-----------|---------|
| `tokenize_input` | `(s) → list` | Splits input string; appends `$` end marker |
| `lr_parse_with_trace` | `(input_string, action, goto_table, productions) → (bool, str, trace)` | Full shift-reduce parser with per-step trace recording |
| `lr_parse` | `(input_string, action, goto_table, productions) → (bool, str)` | Thin wrapper — calls trace version, discards trace |

### GUI Actions

| Function | Purpose |
|----------|---------|
| `build_all()` | Orchestrates layers 1–3; returns all parser data |
| `update_production_box()` | Refreshes numbered productions display |
| `show_dfa()` | Builds DFA graph and opens Toplevel visualizer window |
| `show_table()` | Populates the Parsing Table Treeview |
| `check_string()` | Runs parse and populates the Parse Trace Treeview |
| `clear_all()` | Resets all GUI inputs and outputs |

---

## GUI Components

```
┌──────────────────────────────────────────────────────────┐
│  LR(0) Parser                              [dark theme]  │
├───────────────────────┬──────────────────────────────────┤
│  Grammar Input        │  ┌──────────┬──────────────────┐ │
│  ─────────────────    │  │ Parsing  │   Parse Trace    │ │
│  S -> A A             │  │  Table   │                  │ │
│  A -> a A | b         │  │          │  #  Stack  Input │ │
│                       │  │  State a │  1  0      a b $ │ │
│  Productions          │  │  I0   s3 │  2  0 a 3  b b $ │ │
│  ─────────────────    │  │  I1  acc │  ...             │ │
│  (1) S' → S           │  │  ...     │                  │ │
│  (2) S  → A A         │  └──────────┴──────────────────┘ │
│  ...                  │                                  │
│                       │                                  │
│  Input String         │                                  │
│  [  a b b          ]  │                                  │
│                       │                                  │
│  [ Parse String    ]  │                                  │
│  [ Show Table ] [DFA] │                                  │
│  [ Clear           ]  │                                  │
│                       │                                  │
│  ✓ Accepted.          │                                  │
├───────────────────────┴──────────────────────────────────┤
│  LR(0) Parser  ·  Separate all symbols with spaces       │
└──────────────────────────────────────────────────────────┘
```

### Colour Coding in Parse Trace

| Colour | Meaning |
|--------|---------|
| 🔵 Blue (`#60a5fa`) | Shift action |
| 🟣 Purple (`#a78bfa`) | Reduce action |
| 🟢 Green (bold) | Accept |
| 🔴 Red | Parse error |

---

## Dependencies

| Library | Install | Version |
|---------|---------|---------|
| `tkinter` | Built-in | stdlib |
| `networkx` | `pip install networkx` | ≥ 2.8 |
| `matplotlib` | `pip install matplotlib` | ≥ 3.5 |
| `numpy` | `pip install numpy` | ≥ 1.21 |

---

## Author

**Mohammad Sami**  
SAP ID: 53199  
Compiler Construction — CS-636  
Riphah International University  
May 2026

---

*This program is submitted as part of the Compiler Construction course. All algorithm implementations are original and based on standard LR(0) parsing theory as covered in lectures.*

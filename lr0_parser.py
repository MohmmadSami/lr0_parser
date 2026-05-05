# =============================================================================
#                            LR(0) PARSER 
# =============================================================================
# REFERENCE TABLE: Function/Module Purpose Mapping
# =============================================================================
# | Component              | Line Range | Purpose                                      |
# |------------------------|------------|----------------------------------------------|
# | HEADER COMMENT BLOCK   | 1-69       | Program title and reference tables           |
# | IMPORTS                | 70-75      | GUI, graph, plotting libraries               |
# | EPSILON                | 77         | Empty string representation                  |
# | tokenize_rhs()         | 79-93      | Splits RHS of production into tokens         |
# | parse_grammar()        | 96-123     | Converts grammar text to data structures     |
# | augment_grammar()      | 126-146    | Adds S' start symbol for LR(0)               |
# | collect_terminals()    | 149-166    | Extracts all terminal symbols                |
# | closure()              | 171-192    | Computes LR(0) closure of items              |
# | goto()                 | 195-202    | Moves dot over a symbol                      |
# | canonical_collection() | 205-239    | Builds all LR(0) states                      |
# | format_item()          | 243-250    | Formats single LR(0) item                    |
# | format_state()         | 253-262    | Formats entire state as string               |
# | productions_text()     | 265-274    | Creates readable production list             |
# | add_table_entry()      | 279-293    | Adds entry to parsing table cell             |
# | build_lr0_table()      | 296-338    | Constructs ACTION and GOTO tables            |
# | tokenize_input()       | 344-361    | Tokenizes input string with $ marker         |
# | lr_parse_with_trace()  | 364-443    | Parses with step-by-step trace               |
# | lr_parse()             | 446-449    | Simple parse without trace                   |
# | build_all()            | 454-487    | Central function building all components     |
# | update_production_box()| 490-495    | Updates productions display in GUI           |
# | show_dfa()             | 498-691    | Displays DFA visualization in new window     |
# | show_table()           | 694-734    | Shows parsing table in GUI                   |
# | check_string()         | 737-774    | Parses input and shows trace                 |
# | clear_all()            | 777-790    | Resets all GUI components                    |
# | THEME CONSTANTS        | 795-804    | BG, FG, colors, fonts                        |
# | ROOT WINDOW            | 808-813    | Main tkinter window setup                    |
# | STYLES                 | 816-846    | ttk styling for notebook, treeview, scrollbar|
# | HEADER                 | 850-863    | Title bar and separator                      |
# | MAIN LAYOUT            | 867-870    | Left/right panel container                   |
# | LEFT PANEL             | 873-977    | Grammar box, productions, input, buttons     |
# | RIGHT PANEL/NOTEBOOK   | 980-984    | Tabbed interface container                   |
# | TABLE TAB              | 987-1028   | Parsing table with Treeview                  |
# | TRACE TAB              | 1031-1076  | Parse trace with colored actions             |
# | STATUS BAR             | 1080-1085  | Bottom instruction bar                       |
# | MAINLOOP               | 1087       | Starts GUI event loop                        |
# =============================================================================
#
# ALGORITHM REFERENCE:
# =============================================================================
# | Algorithm           | Function(s)              | Description                              |
# |---------------------|--------------------------|------------------------------------------|
# | Grammar Parsing     | tokenize_rhs, parse_grammar| Converts user input to internal format |
# | Augmented Grammar   | augment_grammar          | Adds S' -> S for LR(0) acceptance       |
# | LR(0) Closure       | closure                  | Adds all possible items from nonterminal|
# | LR(0) GOTO          | goto                     | Moves dot over symbol X                 |
# | Canonical Collection| canonical_collection     | Builds C = {I0, I1, ..., In} states     |
# | LR(0) Table         | build_lr0_table          | Constructs ACTION(s,a) and GOTO(s,A)    |
# | LR Parsing          | lr_parse_with_trace      | Shift-reduce parsing with stack trace   |
# | DFA Visualization   | show_dfa                 | Draws state transition diagram          |
# =============================================================================
#
# GRAMMAR RULES FORMAT:
# =============================================================================
# Rule 1: Separate EVERY symbol with SPACES
# Rule 2: Use -> for production (arrow)
# Rule 3: Use | for alternatives
# Rule 4: Empty production = epsilon or ebs
# Example: S -> a S b | ebs
# Example: E -> E + T | T
# Example: statement -> if condition then statement
# =============================================================================

import tkinter as tk                                 # GUI framework for parser interface window
from tkinter import ttk, Toplevel, messagebox       # ttk=styled tables/tabs, Toplevel=DFA window, messagebox=errors/warnings
from collections import OrderedDict                 # Preserves grammar rule order for consistent production numbering
import networkx as nx                               # Builds DFA graph from LR(0) canonical collection states
import matplotlib.pyplot as plt                     # Renders DFA visualization with states and transitions
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Embeds DFA graph inside tkinter window (not separate)

EPSILON = "ebs"                                 # Empty string representation for grammar rules
# ---------------- GRAMMAR PARSING ---------------- #
def tokenize_rhs(prod: str):                    # Splits RHS of production into tokens
    """
    Always split by whitespace.
    'statement a' → ['statement', 'a']
    'a'           → ['a']
    ''            → []
    Epsilon forms → []
    """
    prod = prod.strip()                         # Remove leading/trailing whitespace
    if prod in ("", EPSILON, "e", "ebs", "ebs", "epsilon", "EPSILON", "ebsilon"):  # Check for epsilon variants
        return []                               # Empty RHS represents epsilon
    # Always split on whitespace — multi-char symbols MUST be space-separated
    return [tok for tok in prod.split() if tok] # Return list of non-empty tokens


def parse_grammar(text):                        # Converts grammar text to internal data structures
    grammar = OrderedDict()                     # Preserves production order for nonterminals
    productions = []                            # Flat list of all productions (lhs, rhs pairs)

    for line in text.strip().splitlines():      # Process each line separately
        line = line.strip()                     # Remove whitespace from line ends
        if not line or "->" not in line:        # Skip empty lines and lines without arrow
            continue

        left, right = line.split("->", 1)       # Split at first occurrence of ->
        lhs = left.strip()                      # Left-hand side nonterminal
        rhs_part = right.strip()                # Right-hand side part with alternatives

        if lhs not in grammar:                  # Initialize list for new nonterminal
            grammar[lhs] = []                   # Empty list for productions

        for alt in rhs_part.split("|"):         # Handle alternatives separated by |
            rhs = tuple(tokenize_rhs(alt))      # Convert each alternative to tuple of symbols
            grammar[lhs].append(rhs)            # Add to grammar dictionary
            productions.append((lhs, rhs))      # Add to flat productions list

    return grammar, productions                 # Return both organized structures


def augment_grammar(base_grammar):              # Adds new start symbol for LR(0) parsing
    if not base_grammar:
        raise ValueError("Grammar is empty.")   # Error for empty input

    start_symbol = next(iter(base_grammar))     # Get first nonterminal as start symbol
    augmented = start_symbol + "'"              # Create augmented symbol by adding apostrophe
    while augmented in base_grammar:            # Ensure unique name
        augmented += "'"                        # Add more apostrophes if needed

    grammar = OrderedDict()                     # New grammar with augmented start
    grammar[augmented] = [(start_symbol,)]      # Production: S' -> S
    for lhs, prods in base_grammar.items():     # Copy all original productions
        grammar[lhs] = list(prods)              # Keep original order

    return grammar, augmented, start_symbol     # New grammar, new start, original start


def collect_terminals(grammar):                 # Extracts all terminal symbols from grammar
    nonterminals = set(grammar.keys())          # Set of all nonterminal symbols
    terminals = []                              # List to store unique terminals
    seen = set()                                # Track seen symbols to avoid duplicates

    for lhs, prods in grammar.items():          # Iterate through all productions
        for rhs in prods:                       # Check each production's RHS
            for sym in rhs:                     # Check each symbol in RHS
                if sym not in nonterminals and sym != EPSILON and sym not in seen:  # Symbol is terminal and not seen
                    seen.add(sym)               # Mark as seen
                    terminals.append(sym)       # Add to terminals list

    return terminals                            # Return list of terminal symbols


# ---------------- LR(0) CORE ---------------- #
def closure(items, grammar):                    # Computes LR(0) closure of a set of items
    result = set(items)                         # Start with initial items
    while True:
        new_result = set(result)                # Create copy for iteration
        for lhs, rhs, dot in result:            # Check each item in current closure
            if dot < len(rhs):                  # If dot is not at the end
                sym = rhs[dot]                  # Get symbol after dot
                if sym in grammar:              # If symbol is a nonterminal
                    for prod in grammar[sym]:   # Add all its productions with dot at 0
                        new_result.add((sym, prod, 0))  # New item: [B -> ·γ]
        if new_result == result:                # Fixed point reached
            break                               # No more items to add
        result = new_result                     # Update result with new items
    return result                               # Return closed set of items


def goto(items, symbol, grammar):               # Computes GOTO(I, X) - move dot over symbol X
    moved = []                                  # Items after moving dot
    for lhs, rhs, dot in items:                 # Check each item in current set
        if dot < len(rhs) and rhs[dot] == symbol:  # If dot before our symbol
            moved.append((lhs, rhs, dot + 1))   # Move dot one position right
    return closure(moved, grammar) if moved else set()  # Return closure of moved items


def canonical_collection(grammar):              # Builds canonical collection of LR(0) states
    start_aug = next(iter(grammar))             # Get augmented start symbol
    start_symbol = grammar[start_aug][0][0]     # Extract original start symbol

    I0 = frozenset(closure({(start_aug, (start_symbol,), 0)}, grammar))  # Initial state
    states = [I0]                               # List of all states (frozensets)
    state_index = {I0: 0}                       # Map state to index number
    transitions = {}                            # Dictionary for state transitions

    all_symbols = list(grammar.keys()) + collect_terminals(grammar)  # All grammar symbols
    queue = [I0]                                # Queue for processing states

    while queue:                                # Process until all states processed
        current = queue.pop(0)                  # Get next state from front
        i = state_index[current]                # Get index of current state
        for sym in all_symbols:                 # Try transition on every symbol
            nxt = frozenset(goto(set(current), sym, grammar))  # Compute target state
            if not nxt:                         # Skip empty transitions
                continue
            if nxt not in state_index:          # New state discovered
                state_index[nxt] = len(states)  # Assign new index
                states.append(nxt)              # Add to states list
                queue.append(nxt)               # Add to processing queue
            transitions[(i, sym)] = state_index[nxt]  # Record transition

    return states, transitions                  # Return collection and transition map

# ---------------- FORMATTING ---------------- #
def format_item(lhs, rhs, dot):                 # Converts LR(0) item to readable string
    if len(rhs) == 0:                           # Handle epsilon production
        return f"{lhs} → ·"                     # Special format for empty RHS
    parts = list(rhs)                           # Convert tuple to list for modification
    parts.insert(dot, "·")                      # Insert dot at specified position
    return f"{lhs} → {' '.join(parts)}"         # Return formatted item


def format_state(state_items, state_no):        # Formats entire state as multi-line string
    lines = [f"I{state_no}"]                    # State header line
    for item in sorted(state_items):            # Sort items for consistent display
        lhs, rhs, dot = item                    # Extract item components
        lines.append(format_item(lhs, rhs, dot))  # Add formatted item
    return "\n".join(lines)                     # Join all lines with newlines


def productions_text(productions):              # Creates readable production list
    lines = []                                  # List to store formatted lines
    for i, (lhs, rhs) in enumerate(productions, start=1):  # Number starting from 1
        rhs_txt = " ".join(rhs) if rhs else EPSILON  # Handle epsilon display
        lines.append(f"({i})  {lhs} → {rhs_txt}")  # Format as (n) LHS -> RHS
    return "\n".join(lines)                     # Return newline-separated text


# ---------------- PARSING TABLE ---------------- #
def add_table_entry(cell_dict, symbol, value):  # Adds entry to parsing table cell
    current = cell_dict.get(symbol, "")         # Get current cell content
    if not current:                             # Empty cell
        cell_dict[symbol] = value               # Simply set value
        return False                            # No conflict
    parts = current.split("/")                  # Split existing entries
    if value not in parts:                      # Avoid duplicate entries
        parts.append(value)                     # Add new value
        cell_dict[symbol] = "/".join(parts)     # Update cell with conflicts
        return True                             # Conflict detected
    return False                                # No new conflict


def build_lr0_table(states, transitions, base_grammar, augmented, productions):  # Constructs LR(0) parsing table
    terminals = collect_terminals(base_grammar) # Get terminal symbols
    nonterminals = list(base_grammar.keys())    # Get nonterminal symbols

    action = [{t: "" for t in terminals + ["$"]} for _ in states]  # Initialize ACTION table
    goto_table = [{nt: "" for nt in nonterminals} for _ in states]  # Initialize GOTO table
    has_conflict = False                        # Flag for grammar conflicts

    prod_index = {}                             # Map productions to numbers
    for i, prod in enumerate(productions, start=1):  # Index from 1 (0 reserved)
        if prod not in prod_index:              # Avoid duplicate indexing
            prod_index[prod] = i                # Store production number

    for (i, sym), j in transitions.items():     # Process all transitions
        if sym in terminals:                    # Shift action for terminals
            if add_table_entry(action[i], sym, f"s{j}"):  # Add shift j
                has_conflict = True             # Conflict occurred
        elif sym in nonterminals:               # GOTO for nonterminals
            goto_table[i][sym] = str(j)         # Store goto state

    for i, state in enumerate(states):          # Process reduce actions for each state
        for lhs, rhs, dot in state:             # Check each item in state
            if dot == len(rhs):                 # Reduce item (dot at end)
                if lhs == augmented:            # Accept state
                    if add_table_entry(action[i], "$", "acc"):  # Add accept
                        has_conflict = True     # Conflict in accept state
                else:                           # Regular reduce
                    pnum = prod_index.get((lhs, rhs))  # Get production number
                    if pnum is None:            # Skip if not found
                        continue
                    for t in terminals + ["$"]: # Add reduce for all lookaheads
                        if add_table_entry(action[i], t, f"r{pnum}"):
                            has_conflict = True # Reduce-reduce or shift-reduce conflict

    return terminals, nonterminals, action, goto_table, has_conflict  # Return complete table


# ---------------- LR(0) PARSER (with trace) ---------------- #
def tokenize_input(s):                          # Tokenizes input string for parsing
    """
    Always split by whitespace — must match how the grammar was tokenized.
    'statement a'  → ['statement', 'a', '$']
    'a b c'        → ['a', 'b', 'c', '$']
    """
    s = s.strip()                               # Remove leading/trailing spaces
    if not s:                                   # Empty input
        return ["$"]                            # Just end marker
    tokens = [tok for tok in s.split() if tok]  # Split by whitespace
    if not tokens or tokens[-1] != "$":         # Check for end marker
        tokens.append("$")                      # Add end marker if missing
    return tokens                               # Return token list with $


def lr_parse_with_trace(input_string, action, goto_table, productions):  # Parses with step-by-step trace
    tokens = tokenize_input(input_string)       # Convert input to tokens
    stack = [0]                                 # Parse stack with initial state 0
    i = 0                                       # Input pointer
    trace = []                                  # List to store trace steps

    step = 1                                    # Step counter for trace
    while True:                                 # Main parsing loop
        state = stack[-1]                       # Current state from top of stack
        current = tokens[i] if i < len(tokens) else "$"  # Current input symbol
        cell = action[state].get(current, "")   # Look up action in table

        stack_str = " ".join(str(x) for x in stack)  # String representation of stack
        input_str = " ".join(tokens[i:])        # String representation of remaining input

        if not cell:                            # No action defined
            trace.append({
                "step": step,
                "stack": stack_str,
                "input": input_str,
                "action": f"Error on '{current}'"  # Record error
            })
            return False, f"Rejected at state I{state} on symbol '{current}'.", trace

        chosen = cell.split("/")[0]             # Pick first action in case of conflict

        if chosen == "acc":                     # Accept action
            trace.append({
                "step": step,
                "stack": stack_str,
                "input": input_str,
                "action": "Accept"              # Record accept
            })
            return True, "Accepted.", trace     # Parsing successful

        if chosen.startswith("s"):              # Shift action
            next_state = int(chosen[1:])        # Extract target state number
            trace.append({
                "step": step,
                "stack": stack_str,
                "input": input_str,
                "action": f"Shift → s{next_state}"  # Record shift
            })
            stack.append(current)               # Push current symbol
            stack.append(next_state)            # Push new state
            i += 1                              # Advance input pointer
            step += 1                           # Increment step counter
            continue

        if chosen.startswith("r"):              # Reduce action
            prod_no = int(chosen[1:])           # Extract production number
            lhs, rhs = productions[prod_no - 1]  # Get production (0-indexed)
            rhs_str = " ".join(rhs) if rhs else EPSILON  # Format RHS for display
            trace.append({
                "step": step,
                "stack": stack_str,
                "input": input_str,
                "action": f"Reduce by ({prod_no}) {lhs} → {rhs_str}"  # Record reduce
            })

            if len(rhs) > 0:                    # Non-epsilon production
                pop_count = 2 * len(rhs)        # Pop symbols and states (2 per symbol)
                if pop_count > len(stack) - 1:  # Check stack underflow
                    return False, "Rejected due to invalid stack reduction.", trace
                stack = stack[:-pop_count]      # Remove popped elements

            state_after_pop = stack[-1]         # State after popping
            goto_state = goto_table[state_after_pop].get(lhs, "")  # Look up GOTO

            if not goto_state:                  # Missing GOTO entry
                return False, f"Rejected: missing GOTO[{state_after_pop}, {lhs}].", trace

            stack.append(lhs)                   # Push LHS nonterminal
            stack.append(int(goto_state))       # Push GOTO state
            step += 1                           # Increment step counter
            continue

        return False, f"Rejected due to invalid action '{chosen}'.", trace  # Unknown action


def lr_parse(input_string, action, goto_table, productions):  # Simple parse without trace
    accepted, msg, _ = lr_parse_with_trace(input_string, action, goto_table, productions)  # Call traced version
    return accepted, msg                        # Return just acceptance and message


# ---------------- GUI ACTIONS ---------------- #
def build_all():                                # Central function to build all parser components
    text = grammar_box.get("1.0", tk.END)       # Get grammar text from GUI
    base_grammar, productions = parse_grammar(text)  # Parse grammar input

    if not base_grammar:                        # Validate grammar exists
        raise ValueError("Please enter a valid grammar.")

    grammar, augmented, start_symbol = augment_grammar(base_grammar)  # Add augmented start
    states, transitions = canonical_collection(grammar)  # Build LR(0) states
    terminals, nonterminals, action, goto_table, has_conflict = build_lr0_table(
        states, transitions, base_grammar, augmented, productions
    )                                           # Build parsing table

    return {                                    # Return all data in dictionary
        "base_grammar": base_grammar,
        "productions": productions,
        "grammar": grammar,
        "augmented": augmented,
        "start_symbol": start_symbol,
        "states": states,
        "transitions": transitions,
        "terminals": terminals,
        "nonterminals": nonterminals,
        "action": action,
        "goto": goto_table,
        "has_conflict": has_conflict
    }


def update_production_box(productions):         # Updates productions display in GUI
    prod_box.config(state="normal")             # Enable editing temporarily
    prod_box.delete("1.0", tk.END)              # Clear current content
    prod_box.insert(tk.END, productions_text(productions))  # Insert formatted productions
    prod_box.config(state="disabled")           # Make read-only again


def show_dfa():                                 # Displays DFA visualization in new window
    try:
        import matplotlib.patches as mpatches   # For custom shapes
        import numpy as np                      # For mathematical operations

        data = build_all()                      # Build parser data
        update_production_box(data["productions"])  # Update productions display

        win = Toplevel(root)                    # Create new top-level window
        win.title("LR(0) — Canonical Collection (DFA)")
        win.geometry("1300x800")                # Set window size
        win.configure(bg=BG)                    # Apply background color

        toolbar = tk.Frame(win, bg=BG2, pady=6)  # Create toolbar frame
        toolbar.pack(fill="x")                  # Pack at top
        tk.Label(toolbar, text="  Scroll / drag to navigate  ·  Close window to dismiss",
                 font=(SANS, 8), bg=BG2, fg=FG2).pack(side="left")  # Instructions

        G = nx.DiGraph()                        # Create directed graph for states
        states = data["states"]                 # Get LR(0) states
        transitions = data["transitions"]       # Get transitions between states

        for i, st in enumerate(states):
            G.add_node(i, label=format_state(st, i))  # Add node with formatted label

        edge_syms = {}                          # Collect symbols on edges
        for (i, sym), j in transitions.items():
            edge_syms.setdefault((i, j), []).append(sym)  # Group multiple symbols
            G.add_edge(i, j)                    # Add edge to graph

        pos = nx.spring_layout(G, seed=42, k=2.8, iterations=120)  # Compute node positions

        fig, ax = plt.subplots(figsize=(15, 10))  # Create matplotlib figure
        fig.patch.set_facecolor("#1a1a1e")      # Dark background for figure
        ax.set_facecolor("#1a1a1e")             # Dark background for axes
        ax.set_aspect("equal")                  # Equal aspect ratio
        ax.axis("off")                          # Turn off axes

        PAD_X, PAD_Y = 0.15, 0.12               # Padding around nodes
        FONT_SIZE = 7                           # Font size for node text

        node_boxes = {}                         # Store node bounding boxes

        tmp_texts = {}                          # Temporary text objects for measurement
        for node in G.nodes():
            lbl = G.nodes[node]["label"]        # Get node label
            x, y = pos[node]                    # Get node position
            t = ax.text(x, y, lbl,
                        fontsize=FONT_SIZE, fontfamily="Courier New",
                        color="white", ha="center", va="center",
                        visible=False)          # Create invisible text
            tmp_texts[node] = t                 # Store text object

        fig.canvas.draw()                       # Render to measure text extents
        renderer = fig.canvas.get_renderer()    # Get renderer for measurement

        for node, t in tmp_texts.items():       # Calculate bounding boxes
            bb = t.get_window_extent(renderer=renderer)  # Get pixel extent
            inv = ax.transData.inverted()       # Invert transform for data coords
            x0d, y0d = inv.transform((bb.x0, bb.y0))  # Bottom-left in data coords
            x1d, y1d = inv.transform((bb.x1, bb.y1))  # Top-right in data coords
            w = (x1d - x0d) + 2 * PAD_X         # Width with padding
            h = (y1d - y0d) * 1.35 + 2 * PAD_Y  # Height with padding
            node_boxes[node] = (pos[node][0], pos[node][1], w, h)  # Store box
            t.remove()                          # Remove temporary text

        def box_border_point(node, toward_x, toward_y):  # Find point on box border
            cx, cy, w, h = node_boxes[node]     # Box center and dimensions
            dx, dy = toward_x - cx, toward_y - cy  # Direction vector
            if dx == 0 and dy == 0:             # Same point
                return cx, cy
            half_w, half_h = w / 2, h / 2       # Half dimensions
            if dy == 0:                         # Horizontal line
                t_val = half_w / abs(dx)
            elif dx == 0:                       # Vertical line
                t_val = half_h / abs(dy)
            else:                               # Diagonal
                t_val = min(half_w / abs(dx), half_h / abs(dy))
            return cx + dx * t_val, cy + dy * t_val  # Return intersection point

        drawn_pairs = set()                     # Track drawn edges to avoid overlap

        for (i, j), syms in edge_syms.items():  # Draw all edges
            label_str = " / ".join(sorted(syms))  # Combine multiple symbols
            cx_i, cy_i, _, _ = node_boxes[i]    # Get source box
            cx_j, cy_j, _, _ = node_boxes[j]    # Get target box

            if i == j:                          # Self-loop edge
                cx, cy, w, h = node_boxes[i]    # Node dimensions
                loop_r = max(w, h) * 0.45       # Loop radius
                theta = np.linspace(np.pi * 0.1, np.pi * 0.9, 60)  # Arc angles
                lx = cx + loop_r * np.cos(theta)  # X coordinates of arc
                ly = (cy + h / 2 + loop_r * 0.3) + loop_r * 0.7 * np.sin(theta)  # Y coordinates
                ax.plot(lx, ly, color="#f59e0b", lw=1.4, zorder=2)  # Draw arc
                ax.annotate("", xy=(lx[-1], ly[-1]),  # Arrowhead
                             xytext=(lx[-2], ly[-2]),
                             arrowprops=dict(arrowstyle="-|>", color="#f59e0b",
                                             lw=1.2, mutation_scale=10),
                             zorder=3)
                ax.text(cx, cy + h / 2 + loop_r * 1.05 + loop_r * 0.3,  # Label position
                        label_str,
                        fontsize=8, fontfamily="Courier New",
                        color="#fbbf24", ha="center", va="bottom",
                        bbox=dict(boxstyle="round,pad=0.25",
                                  facecolor="#1a1a1e", edgecolor="none",
                                  alpha=0.85),
                        zorder=5)
                continue

            curved = (j, i) in edge_syms        # Check if bidirectional
            pair_key = tuple(sorted([i, j]))    # Unique pair key
            is_first = pair_key not in drawn_pairs  # First time drawing this pair
            drawn_pairs.add(pair_key)           # Mark as drawn

            bx_i, by_i = box_border_point(i, cx_j, cy_j)  # Start point on box
            bx_j, by_j = box_border_point(j, cx_i, cy_i)  # End point on box

            if curved:                          # Curved edge for bidirectional
                dx, dy = bx_j - bx_i, by_j - by_i  # Direction vector
                length = max((dx**2 + dy**2)**0.5, 1e-9)  # Edge length
                perp = np.array([-dy, dx]) / length  # Perpendicular vector
                sign = 1 if is_first else -1   # Direction of curve
                offset = 0.12 * sign           # Offset amount

                ax.annotate("",                 # Curved arrow
                    xy=(bx_j, by_j), xytext=(bx_i, by_i),
                    arrowprops=dict(
                        arrowstyle="-|>",
                        color="#60a5fa", lw=1.2,
                        mutation_scale=12,
                        connectionstyle=f"arc3,rad={0.28 * sign}"),
                    zorder=2)
                lx_m = (bx_i + bx_j) / 2 + perp[0] * offset * 1.8  # Midpoint X
                ly_m = (by_i + by_j) / 2 + perp[1] * offset * 1.8  # Midpoint Y
            else:                               # Straight edge
                ax.annotate("",                 # Straight arrow
                    xy=(bx_j, by_j), xytext=(bx_i, by_i),
                    arrowprops=dict(
                        arrowstyle="-|>",
                        color="#60a5fa", lw=1.2,
                        mutation_scale=12,
                        connectionstyle="arc3,rad=0.0"),
                    zorder=2)
                lx_m = (bx_i + bx_j) / 2        # Midpoint X
                ly_m = (by_i + by_j) / 2        # Midpoint Y

            ax.text(lx_m, ly_m, label_str,      # Edge label
                    fontsize=8, fontfamily="Courier New",
                    color="#e2e8f0", ha="center", va="center",
                    bbox=dict(boxstyle="round,pad=0.22",
                              facecolor="#1a1a1e", edgecolor="none",
                              alpha=0.9),
                    zorder=4)

        for node in G.nodes():                  # Draw all state nodes
            lbl = G.nodes[node]["label"]        # Get node label
            cx, cy, w, h = node_boxes[node]     # Box dimensions

            lines = lbl.split("\n")             # Split into lines
            header = lines[0]                   # First line is header I#
            body = "\n".join(lines[1:])         # Rest are items

            rect = mpatches.FancyBboxPatch(     # Main rounded rectangle
                (cx - w/2, cy - h/2), w, h,
                boxstyle="round,pad=0.01",
                facecolor="#1e3a5f", edgecolor="#3b82f6",
                linewidth=1.3, zorder=5)
            ax.add_patch(rect)                  # Add to plot

            header_h = h * 0.28                 # Header height
            hrect = mpatches.FancyBboxPatch(    # Header rectangle
                (cx - w/2, cy + h/2 - header_h), w, header_h,
                boxstyle="round,pad=0.01",
                facecolor="#2563eb", edgecolor="none",
                linewidth=0, zorder=6)
            ax.add_patch(hrect)                 # Add to plot

            ax.text(cx, cy + h/2 - header_h/2, header,  # Header text
                    fontsize=FONT_SIZE + 1, fontfamily="Courier New",
                    fontweight="bold", color="white",
                    ha="center", va="center", zorder=7)

            if body:                            # Body text for items
                ax.text(cx, cy + h/2 - header_h - (h * 0.05), body,
                        fontsize=FONT_SIZE, fontfamily="Courier New",
                        color="#bfdbfe", ha="center", va="top",
                        zorder=7, linespacing=1.4)

        ax.autoscale_view()                     # Adjust view limits
        fig.tight_layout(pad=0.3)               # Tight layout with padding

        frame = tk.Frame(win, bg=BG)            # Frame for canvas
        frame.pack(fill="both", expand=True)    # Pack to fill window

        canvas = FigureCanvasTkAgg(fig, master=frame)  # Embed matplotlib figure
        canvas.draw()                           # Render canvas

        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk  # For navigation
        nav_frame = tk.Frame(win, bg=BG2)       # Toolbar frame
        nav_frame.pack(fill="x", side="bottom") # Pack at bottom
        toolbar_mpl = NavigationToolbar2Tk(canvas, nav_frame)  # Add matplotlib toolbar
        toolbar_mpl.config(background=BG2)      # Style toolbar
        toolbar_mpl.update()                    # Update display

        canvas.get_tk_widget().pack(fill="both", expand=True)  # Pack canvas
        plt.close(fig)                          # Close figure to free memory

    except Exception as e:                      # Handle any errors
        import traceback                        # For detailed error info
        messagebox.showerror("Error", traceback.format_exc())  # Show error dialog


def show_table():                               # Displays parsing table in GUI
    try:
        data = build_all()                      # Build parser data
        update_production_box(data["productions"])  # Update productions display

        terminals = data["terminals"]           # Get terminal symbols
        nonterminals = data["nonterminals"]     # Get nonterminal symbols
        action = data["action"]                 # Get ACTION table
        goto_table = data["goto"]               # Get GOTO table

        cols = ["State"] + terminals + ["$"] + nonterminals  # Table columns
        table["columns"] = cols                 # Set treeview columns
        table["show"] = "headings"              # Show only headings

        for c in cols:                          # Configure each column
            table.heading(c, text=c)            # Set heading text
            table.column(c, width=max(80, len(c) * 10), anchor="center", minwidth=60)  # Column width

        table.delete(*table.get_children())     # Clear existing rows

        for i in range(len(data["states"])):    # Process each state
            row = [f"I{i}"]                     # State column
            for t in terminals + ["$"]:         # Terminal and $ columns
                row.append(action[i].get(t, ""))  # Add action entry
            for nt in nonterminals:             # GOTO columns
                row.append(goto_table[i].get(nt, ""))  # Add goto entry
            table.insert("", "end", values=row)  # Insert row

        if data["has_conflict"]:                # Check for grammar conflicts
            messagebox.showwarning("LR(0) Conflict", "Grammar is not LR(0). Conflicts (s/r or r/r) were found and are marked with '/' in the table.")

        notebook.select(tab_table)              # Switch to table tab

    except Exception as e:                      # Handle any errors
        messagebox.showerror("Error", str(e))   # Show error dialog


def check_string():                             # Parses input string and shows trace
    try:
        data = build_all()                      # Build parser data
        update_production_box(data["productions"])  # Update productions display

        inp = entry.get().strip()               # Get input from entry widget
        if not inp:                             # Empty input check
            messagebox.showwarning("Input Required", "Please enter an input string.")
            return

        accepted, msg, trace = lr_parse_with_trace(  # Parse with trace
            inp,
            data["action"],
            data["goto"],
            data["productions"],
        )

        if accepted:                            # Parsing successful
            result_var.set("✓  " + msg)         # Set success message
            result_label.config(fg=GREEN)       # Green color for success
        else:                                   # Parsing failed
            result_var.set("✗  " + msg)         # Set error message
            result_label.config(fg=RED)         # Red color for error

        trace_tree.delete(*trace_tree.get_children())  # Clear trace tree
        for row in trace:                       # Add each trace step
            tag = "accept" if row["action"] == "Accept" else (  # Determine tag
                "error" if "Error" in row["action"] else (
                    "shift" if "Shift" in row["action"] else (
                        "reduce" if "Reduce" in row["action"] else "")))
            trace_tree.insert("", "end",        # Insert row with tag
                              values=(row["step"], row["stack"], row["input"], row["action"]),
                              tags=(tag,))

        notebook.select(tab_trace)              # Switch to trace tab

    except Exception as e:                      # Handle any errors
        messagebox.showerror("Error", str(e))   # Show error dialog


def clear_all():                                # Resets all GUI components
    grammar_box.delete("1.0", tk.END)           # Clear grammar input
    entry.delete(0, tk.END)                     # Clear input string
    result_var.set("")                          # Clear result message
    result_label.config(fg=FG)                  # Reset result color
    prod_box.config(state="normal")             # Enable production box
    prod_box.delete("1.0", tk.END)              # Clear productions
    prod_box.config(state="disabled")           # Disable production box
    table.delete(*table.get_children())         # Clear table rows
    table["columns"] = []                       # Clear table columns
    trace_tree.delete(*trace_tree.get_children())  # Clear trace rows
    grammar_box.focus_set()                     # Set focus to grammar box


# ===================== THEME CONSTANTS =====================
BG      = "#1a1a1e"                            # Main background color (dark)
BG2     = "#242428"                            # Secondary background (slightly lighter)
BG3     = "#2e2e34"                            # Tertiary background for contrast
FG      = "#d4d4d8"                            # Main foreground text color
FG2     = "#a1a1aa"                            # Secondary text color (grayish)
ACCENT  = "#3b82f6"                            # Accent color for highlights (blue)
GREEN   = "#22c55e"                            # Success/accept color
RED     = "#ef4444"                            # Error/reject color
BORDER  = "#3f3f46"                            # Border color for separators
MONO    = "Courier New"                        # Monospaced font for code/text
SANS    = "Segoe UI"                           # Sans-serif font for UI

# ===================== ROOT WINDOW =====================
root = tk.Tk()                                  # Create main application window
root.title("LR(0) Parser")                     # Set window title
root.geometry("1050x800")                      # Set initial window size
root.configure(bg=BG)                          # Apply background color
root.resizable(True, True)                     # Allow window resizing

# ===================== STYLES =====================
style = ttk.Style()                             # Create style manager
style.theme_use("clam")                        # Use clam theme as base

style.configure("TNotebook", background=BG, borderwidth=0)  # Notebook background
style.configure("TNotebook.Tab",               # Tab styling
                background=BG2, foreground=FG2,
                padding=[16, 6], font=(SANS, 9))
style.map("TNotebook.Tab",                     # Tab hover/selected states
          background=[("selected", BG3)],
          foreground=[("selected", FG)])

style.configure("Treeview",                    # Treeview (table) styling
                background=BG2, foreground=FG,
                fieldbackground=BG2,
                rowheight=26,
                font=(MONO, 9),
                borderwidth=0)
style.configure("Treeview.Heading",            # Column header styling
                background=BG3, foreground=FG2,
                font=(SANS, 9, "bold"),
                relief="flat")
style.map("Treeview",                          # Row selection styling
          background=[("selected", ACCENT)],
          foreground=[("selected", "white")])
style.map("Treeview.Heading", background=[("active", BG3)])  # Header hover

style.configure("TScrollbar",                  # Scrollbar styling
                background=BG3, troughcolor=BG2,
                arrowcolor=FG2, borderwidth=0, relief="flat")

# ===================== HEADER =====================
header = tk.Frame(root, bg=BG, pady=0)         # Header container
header.pack(fill="x", padx=0)                  # Pack at top

title_bar = tk.Frame(header, bg=BG2, pady=12)  # Title bar frame
title_bar.pack(fill="x")                       # Pack across full width

tk.Label(title_bar, text="LR(0)  PARSER",      # Main title label
         font=("Courier New", 15, "bold"),
         bg=BG2, fg=FG).pack(side="left", padx=20)

sep = tk.Frame(root, bg=BORDER, height=1)       # Separator line
sep.pack(fill="x")                             # Pack below header

# ===================== MAIN LAYOUT =====================
main = tk.Frame(root, bg=BG)                   # Main content container
main.pack(fill="both", expand=True, padx=18, pady=14)  # Pack with padding

# ---- LEFT PANEL ---- #
left = tk.Frame(main, bg=BG, width=300)        # Left panel (input section)
left.pack(side="left", fill="y", padx=(0, 12)) # Pack on left
left.pack_propagate(False)                     # Prevent shrinking

def section_label(parent, text):               # Helper for section headers
    f = tk.Frame(parent, bg=BG)                # Frame for header
    f.pack(fill="x", pady=(10, 4))             # Pack with top padding
    tk.Label(f, text=text.upper(), font=(SANS, 7, "bold"),  # Uppercase label
             bg=BG, fg=FG2, anchor="w").pack(side="left")
    tk.Frame(f, bg=BORDER, height=1).pack(side="left", fill="x", expand=True, padx=(8, 0), pady=6)  # Line

section_label(left, "Grammar")                 # Grammar section header

grammar_frame = tk.Frame(left, bg=BORDER, pady=1, padx=1)  # Border container
grammar_frame.pack(fill="x")                   # Pack horizontally
inner_g = tk.Frame(grammar_frame, bg=BG2)      # Inner frame
inner_g.pack(fill="both")                      # Fill container

grammar_box = tk.Text(inner_g, height=7,       # Text widget for grammar input
                       bg=BG2, fg=FG, insertbackground=FG,
                       font=(MONO, 10), relief="flat",
                       padx=10, pady=8, wrap="none",
                       selectbackground=ACCENT)
grammar_box.pack(fill="both")                  # Pack to fill

# ── Updated hint: spaces are REQUIRED between every symbol ──
grammar_hint = tk.Label(left,                  # Hint label for grammar format
    text="Separate every symbol with spaces  ·  Use | for alternatives\n"
         "Example:  S -> statement | a\n"
         "Example:  E -> E + T | T",
    font=(SANS, 8), bg=BG, fg=FG2, justify="left", anchor="w")
grammar_hint.pack(fill="x", pady=(4, 0))       # Pack below grammar box

section_label(left, "Productions")             # Productions section header

prod_frame = tk.Frame(left, bg=BORDER, pady=1, padx=1)  # Border container
prod_frame.pack(fill="x")                      # Pack horizontally
inner_p = tk.Frame(prod_frame, bg=BG2)         # Inner frame
inner_p.pack(fill="both")                      # Fill container

prod_box = tk.Text(inner_p, height=6,          # Read-only text for productions
                    bg=BG2, fg=FG2,
                    font=(MONO, 9), relief="flat",
                    padx=10, pady=8, state="disabled",
                    wrap="none")
prod_box.pack(fill="both")                     # Pack to fill

section_label(left, "Input String")            # Input section header

# ── Updated hint for input ──
input_hint = tk.Label(left,                    # Hint for input format
    text="Separate tokens with spaces  ·  e.g.:  statement a",
    font=(SANS, 8), bg=BG, fg=FG2, justify="left", anchor="w")
input_hint.pack(fill="x", pady=(0, 2))         # Pack with bottom margin

entry_frame = tk.Frame(left, bg=BORDER, pady=1, padx=1)  # Border container
entry_frame.pack(fill="x")                     # Pack horizontally
entry = tk.Entry(entry_frame,                  # Entry widget for input string
                 bg=BG2, fg=FG, insertbackground=FG,
                 font=(MONO, 11), relief="flat",
                 bd=8)
entry.pack(fill="x")                           # Pack to fill

entry.bind("<Return>", lambda e: check_string())  # Enter key triggers parsing

# ---- BUTTONS ---- #
btns = tk.Frame(left, bg=BG)                   # Button container
btns.pack(fill="x", pady=(14, 0))              # Pack with top padding

def mk_btn(parent, text, cmd, primary=False): # Button factory function
    bg_c  = ACCENT if primary else BG3         # Background based on primary flag
    fg_c  = "white" if primary else FG         # Foreground based on primary flag
    hbg   = "#2563eb" if primary else BG2      # Hover background
    b = tk.Button(parent, text=text, command=cmd,  # Create button
                  bg=bg_c, fg=fg_c,
                  activebackground=hbg, activeforeground="white",
                  font=(SANS, 9, "bold" if primary else "normal"),
                  relief="flat", cursor="hand2",
                  padx=0, pady=7, bd=0)
    b.bind("<Enter>", lambda e: b.config(bg=hbg))  # Hover effect
    b.bind("<Leave>", lambda e: b.config(bg=bg_c))  # Leave effect
    return b                                    # Return button widget

mk_btn(btns, "Parse String", check_string, primary=True).pack(fill="x", pady=(0, 5))  # Primary parse button

row2 = tk.Frame(btns, bg=BG)                   # Second row for buttons
row2.pack(fill="x")                            # Pack horizontally
mk_btn(row2, "Show Table",  show_table).pack(side="left", fill="x", expand=True, padx=(0, 4))  # Table button
mk_btn(row2, "Show DFA",    show_dfa  ).pack(side="left", fill="x", expand=True, padx=(4, 0))   # DFA button
mk_btn(btns, "Clear",       clear_all ).pack(fill="x", pady=(5, 0))  # Clear button

# ---- RESULT LABEL ---- #
result_var = tk.StringVar()                    # String variable for result text
result_label = tk.Label(left, textvariable=result_var,  # Result display label
                         font=(SANS, 10, "bold"),
                         bg=BG, fg=GREEN, wraplength=270, justify="left")
result_label.pack(fill="x", pady=(10, 0))      # Pack below buttons

# ---- RIGHT PANEL (Notebook) ---- #
right = tk.Frame(main, bg=BG)                  # Right panel (output section)
right.pack(side="left", fill="both", expand=True)  # Pack on right, expand to fill

notebook = ttk.Notebook(right)                 # Tabbed interface
notebook.pack(fill="both", expand=True)        # Pack to fill right panel

# ---- TAB: Parsing Table ---- #
tab_table = tk.Frame(notebook, bg=BG2)         # Table tab content
notebook.add(tab_table, text="  Parsing Table  ")  # Add tab

tbl_scroll_y = ttk.Scrollbar(tab_table, orient="vertical")  # Vertical scrollbar
tbl_scroll_x = ttk.Scrollbar(tab_table, orient="horizontal")  # Horizontal scrollbar

table = ttk.Treeview(tab_table,                # Treeview widget for table
                     yscrollcommand=tbl_scroll_y.set,
                     xscrollcommand=tbl_scroll_x.set)

tbl_scroll_y.config(command=table.yview)       # Connect scrollbar
tbl_scroll_x.config(command=table.xview)       # Connect scrollbar

tbl_scroll_x.pack(side="bottom", fill="x")     # Pack horizontal scrollbar
tbl_scroll_y.pack(side="right", fill="y")      # Pack vertical scrollbar
table.pack(fill="both", expand=True)           # Pack table to fill

table.tag_configure("oddrow",  background="#27272b")  # Alternate row color
table.tag_configure("evenrow", background=BG2)        # Alternate row color

def on_table_populate(event=None):             # Auto-alternate row colors
    children = table.get_children()            # Get all rows
    for idx, item in enumerate(children):      # Iterate through rows
        table.item(item, tags=("oddrow" if idx % 2 else "evenrow",))  # Assign tag

table.bind("<<TreeviewOpen>>", on_table_populate)  # Trigger on population

# ---- TAB: Parse Trace ---- #
tab_trace = tk.Frame(notebook, bg=BG2)         # Trace tab content
notebook.add(tab_trace, text="  Parse Trace  ")  # Add tab

trace_frame = tk.Frame(tab_trace, bg=BG2)      # Frame for trace tree
trace_frame.pack(fill="both", expand=True)     # Pack to fill

trace_scroll_y = ttk.Scrollbar(trace_frame, orient="vertical")  # Vertical scrollbar
trace_scroll_x = ttk.Scrollbar(tab_trace, orient="horizontal")  # Horizontal scrollbar

trace_tree = ttk.Treeview(trace_frame,         # Treeview for trace steps
                           columns=("step", "stack", "input", "action"),
                           show="headings",
                           yscrollcommand=trace_scroll_y.set,
                           xscrollcommand=trace_scroll_x.set)

trace_tree.heading("step",   text="#")         # Step column heading
trace_tree.heading("stack",  text="Stack")     # Stack column heading
trace_tree.heading("input",  text="Input")     # Input column heading
trace_tree.heading("action", text="Action")    # Action column heading

trace_tree.column("step",   width=40,  anchor="center", minwidth=40)  # Step column config
trace_tree.column("stack",  width=240, anchor="w",      minwidth=120)  # Stack column
trace_tree.column("input",  width=180, anchor="w",      minwidth=80)   # Input column
trace_tree.column("action", width=300, anchor="w",      minwidth=120)  # Action column

trace_tree.tag_configure("shift",  foreground="#60a5fa")  # Blue for shift actions
trace_tree.tag_configure("reduce", foreground="#a78bfa")  # Purple for reduce actions
trace_tree.tag_configure("accept", foreground=GREEN, font=(MONO, 9, "bold"))  # Green bold for accept
trace_tree.tag_configure("error",  foreground=RED)  # Red for errors

trace_scroll_y.config(command=trace_tree.yview)  # Connect vertical scrollbar
trace_scroll_x.config(command=trace_tree.xview)  # Connect horizontal scrollbar

trace_scroll_x.pack(side="bottom", fill="x")    # Pack horizontal scrollbar
trace_scroll_y.pack(side="right", fill="y")     # Pack vertical scrollbar
trace_tree.pack(fill="both", expand=True)       # Pack treeview to fill

# ===================== STATUS BAR =====================
status_bar = tk.Frame(root, bg=BG2, pady=5)    # Bottom status bar
status_bar.pack(fill="x", side="bottom")       # Pack at bottom
tk.Label(status_bar,                           # Status text label
         text="  LR(0) Parser  ·  Separate all symbols with spaces  ·  Enter grammar and press Parse String or Show Table",
         font=(SANS, 8), bg=BG2, fg=FG2).pack(side="left")  # Pack on left

root.mainloop()                                 # Start GUI event loop
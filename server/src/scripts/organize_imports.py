import ast
from collections import defaultdict
import os
import sys

def categorize_import(module_name):
    base_module = module_name.split('.')[0]
    
    # Category 1: STDLIB
    if hasattr(sys, 'stdlib_module_names'):
        if base_module in sys.stdlib_module_names:
            return 1
            
    # Category 3: INTERNAL (Absolute and Relative)
    if module_name.startswith('server.src') or module_name.startswith('.'):
        return 3
        
    # Category 2: THIRD PARTY
    return 2

class Imports:
    def __init__(self):
        self.modules = set()
        self.from_imports = defaultdict(set)

def generate_block(cat: Imports):
    combined = []
    
    # Collect absolute imports 'import os'
    for mod in cat.modules:
        combined.append((mod, f"import {mod}"))
        
    # Collect from imports 'from os import path'
    for mod, names in cat.from_imports.items():
        names_str = ", ".join(sorted(names))
        combined.append((mod, f"from {mod} import {names_str}"))
        
    # Sort by module name, and prefer 'import' over 'from'
    combined.sort(key=lambda x: (x[0], 1 if x[1].startswith('from') else 0, x[1]))
    
    # Return formatted block
    return "\n".join(x[1] for x in combined)

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        source_lines = f.readlines()
        source = "".join(source_lines)

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False

    # Extract all top-level import statements
    import_nodes = [node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))]

    if not import_nodes:
        return False

    cat1 = Imports()
    cat2 = Imports()
    cat3 = Imports()

    def get_cat(mod):
        c = categorize_import(mod)
        if c == 1: return cat1
        if c == 2: return cat2
        return cat3

    for node in import_nodes:
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod = alias.name
                as_name = alias.asname
                stmt = mod if not as_name else f"{mod} as {as_name}"
                cat = get_cat(mod)
                cat.modules.add(stmt)
        elif isinstance(node, ast.ImportFrom):
            level = node.level
            dots = "." * level
            mod_name = node.module or ""
            full_module = dots + mod_name
            cat = get_cat(full_module)
            
            for alias in node.names:
                name = alias.name
                as_name = alias.asname
                stmt = name if not as_name else f"{name} as {as_name}"
                cat.from_imports[full_module].add(stmt)

    blocks = []
    
    b1 = generate_block(cat1)
    if b1: blocks.append(b1)
        
    b2 = generate_block(cat2)
    if b2: blocks.append(b2)
        
    b3 = generate_block(cat3)
    if b3: blocks.append(b3)

    if not blocks:
        return False

    # Create replacement text string, category blocks separated by an empty line
    new_imports_str = "\n\n".join(blocks)

    first_import_line = min(node.lineno for node in import_nodes)
    last_import_line = max(node.end_lineno for node in import_nodes)

    import_lines_to_remove = set()
    for node in import_nodes:
        # Standardize for removing the entire blocks 
        for line in range(node.lineno, node.end_lineno + 1):
            import_lines_to_remove.add(line)

    output_lines = []
    import_inserted = False
    
    for i, line in enumerate(source_lines, 1):
        if i in import_lines_to_remove:
            continue
            
        # Eliminate whitespace lines captured tightly between import blocks 
        if first_import_line <= i <= last_import_line and line.strip() == '':
            continue
            
        output_lines.append(line)

    # Re-insert the imported block exactly starting at where the first import was detected!
    insert_idx = first_import_line - 1

    # Cleanup any hanging blank lines directly underneath where our new block goes
    while insert_idx < len(output_lines) and output_lines[insert_idx].strip() == '':
        output_lines.pop(insert_idx)

    # Explode the block logic recursively over newlines
    new_imports_lines = [line + '\n' for line in new_imports_str.split('\n')]
    
    # Enforce one trailing empty line down to whatever valid python logic lies next
    if insert_idx < len(output_lines):
        new_imports_lines.extend(['\n'])
        
    # Splice together
    final_lines = output_lines[:insert_idx] + new_imports_lines + output_lines[insert_idx:]

    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(final_lines)

    return True

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    src_directory = os.path.abspath(os.path.join(script_dir, ".."))
    
    processed = 0
    for root, _, files in os.walk(src_directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                if process_file(filepath):
                    processed += 1
                    
    print(f"Organized exact import priority in {processed} files.")

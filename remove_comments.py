import re
import os
from pathlib import Path

def remove_comments_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    new_lines = []
    in_docstring = False
    docstring_char = None
    
    for line in lines:
        stripped = line.lstrip()
        
        if stripped.startswith('"""') or stripped.startswith("'''"):
            quote = '"""' if stripped.startswith('"""') else "'''"
            if in_docstring and docstring_char == quote:
                in_docstring = False
                docstring_char = None
                continue
            elif not in_docstring:
                if stripped.count(quote) == 2:
                    continue
                in_docstring = True
                docstring_char = quote
                continue
        
        if in_docstring:
            continue
        
        if '#' in line:
            code_part = ''
            in_string = False
            string_char = None
            i = 0
            while i < len(line):
                char = line[i]
                
                if char in ['"', "'"] and (i == 0 or line[i-1] != '\\'):
                    if in_string:
                        if char == string_char:
                            in_string = False
                            string_char = None
                    else:
                        in_string = True
                        string_char = char
                
                if char == '#' and not in_string:
                    code_part = line[:i].rstrip()
                    break
                
                i += 1
            else:
                code_part = line
            
            new_lines.append(code_part)
        else:
            new_lines.append(line)
    
    result = '\n'.join(new_lines)
    
    result = re.sub(r'\n{3,}', '\n\n', result)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(result)
    
    print(f"✅ Procesado: {file_path}")

def process_directory(directory):
    path = Path(directory)
    for py_file in path.rglob('*.py'):
        if '__pycache__' not in str(py_file) and 'remove_comments.py' not in str(py_file):
            remove_comments_from_file(py_file)

if __name__ == "__main__":
    process_directory("app")
    print("\n✅ Todos los comentarios han sido eliminados")

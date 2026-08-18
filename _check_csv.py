import sys
sys.stdout.reconfigure(encoding='utf-8')

# Check raw bytes of dados_completos.csv
with open('dados_completos.csv', 'rb') as f:
    raw = f.read(500)

print('Raw bytes (first 500):')
print(raw[:200].hex(' '))
print()

# Decode as UTF-8
text_utf8 = raw.decode('utf-8')
print('As UTF-8:')
for line in text_utf8.split('\n')[:5]:
    print(f'  {line[:100]}')

print()

# The issue: to_csv() defaults to encoding='utf-8' but the notebook
# source code might not specify encoding
import json
with open('analise_precos.ipynb', encoding='utf-8') as f:
    nb = json.load(f)

# Find the to_csv call
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] != 'code':
        continue
    src = ''.join(cell.get('source', []))
    if 'to_csv' in src:
        print(f'Cell {i} to_csv call:')
        for line in src.split('\n'):
            if 'to_csv' in line:
                print(f'  {line.strip()}')

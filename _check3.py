with open('guanabara.txt', 'rb') as f:
    raw = f.read()

# Find first few non-ASCII bytes
count = 0
for i, b in enumerate(raw):
    if b > 127:
        context_before = raw[max(0,i-10):i]
        context_after = raw[i:i+10]
        print(f'Byte {i}: 0x{b:02x}')
        print(f'  hex around: {raw[max(0,i-3):i+3].hex(" ")}')
        print(f'  latin-1 around: ', end='')
        for j in range(max(0,i-3), min(len(raw), i+3)):
            bb = raw[j]
            ch = chr(bb) if 32 <= bb < 127 else f'[{bb:02x}]'
            print(ch, end='')
        print()
        count += 1
        if count >= 5:
            break

# Check if file is actually cp1252 or latin-1
print()
print('Trying cp1252 decode...')
try:
    text = raw.decode('cp1252')
    print(f'cp1252: OK, length={len(text)}')
    # Show first few lines
    for line in text.split('\n')[1:4]:
        print(f'  {line[:100]}')
except Exception as e:
    print(f'cp1252: FAILED - {e}')

print()
print('Trying latin-1 decode...')
text = raw.decode('latin-1')
print(f'latin-1: OK, length={len(text)}')
for line in text.split('\n')[1:4]:
    print(f'  {line[:100]}')

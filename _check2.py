with open('guanabara.txt', 'rb') as f:
    raw = f.read()

text_utf8 = raw.decode('utf-8', errors='replace')
replacement = text_utf8.count('\ufffd')
print(f'UTF-8 replacement chars: {replacement}')

text_latin = raw.decode('latin-1')
print(f'Latin-1: no replacements possible')

# Show bytes around first non-ASCII
for i, b in enumerate(raw[:500]):
    if b > 127:
        context = raw[max(0,i-5):i+5]
        latin_text = context.decode('latin-1', errors='replace')
        print(f'Non-ASCII at byte {i}: 0x{b:02x} context_latin="{latin_text}"')
        break

# Check specific word ACOUGUE
idx = raw.find(b'ACOUGUE')
if idx == -1:
    # Try finding it with accent
    for enc in ['latin-1', 'utf-8']:
        target = 'AÇOUGUE'.encode(enc)
        idx2 = raw.find(target)
        if idx2 >= 0:
            print(f'Found "AÇOUGUE" at byte {idx2} with {enc} encoding')
            print(f'  Bytes: {raw[idx2:idx2+10].hex()}')
            break
    else:
        # Search for A followed by non-ASCII
        for i in range(len(raw)-1):
            if raw[i] == ord('A') and raw[i+1] > 127:
                print(f'Found "A" + non-ASCII at byte {i}: {raw[i:i+5].hex()}')
                print(f'  latin-1: {raw[i:i+5].decode("latin-1")}')
                break

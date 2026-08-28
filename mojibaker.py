import sys

to_mojibake = str(input('Character(s) to mojibake: '))
if to_mojibake == '':
    print('Please enter something.')
    sys.exit(1)
try:
    if to_mojibake == to_mojibake.encode('latin-1').decode('utf-8'):
        print("Can't be mojibaked.")
        sys.exit(1)
except (UnicodeEncodeError, UnicodeDecodeError):
    print('Spicy!')

layers = abs(int(input('How many layers: ')))

s = to_mojibake
print(f'Layer 0: {s}')
for i in range(0,layers):
    if not s == s.encode('utf-8').decode('latin-1'):
        s = s.encode('utf-8').decode('latin-1')
        t = ''
        for char in s:
            char2 = char[:]
            if not char2.isprintable():
                char2 = '[' + hex(ord(char2)).upper()[2:] + ']'
            t = t+char2
        print(f'Layer {i+1}: {t}')
    else:
        print("Can't mojibake further.")

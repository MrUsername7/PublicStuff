import sys, codecs
print(f'Platform: {sys.platform}')

encoding = str(input('Encoding of desire: ')) or 'latin-1'

try:
    codecs.lookup(encoding)
except LookupError:
    print("Encoding doesn't exist!")
    sys.exit(1)

j = ''
for i in range(256):
    try:
        j += bytes([i]).decode(encoding)
    except UnicodeDecodeError:
        j += '�'

print(j)

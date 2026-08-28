import random

generated_chars = ''

for i in range(abs(int(input('how many chars? ')))):
    # Generate a random code point in the 5-digit hex range (U+10000 to U+10FFFF)
    code_point = random.randint(0x0, 0x10FFFF)

    # Convert to character and format the hex string
    unicode_char = chr(code_point)
    generated_chars += unicode_char
    hex_code = f"U+{code_point:05X}"

    print(f"Character: {unicode_char}")
    print(f"Code Point: {hex_code}")

print(f'All together: {generated_chars}')

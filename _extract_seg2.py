import io
import re

lines = io.open('utils/ui/Service.ui', encoding='utf-8').read().splitlines()
seg = lines[2300:3170]
txt = '\n'.join(seg)

out = []
out.append('=== WIDGETS ===')
for m in re.finditer(r'<widget class="([^"]+)" name="([^"]+)">', txt):
    out.append('%s: %s' % (m.group(1), m.group(2)))

out.append('')
out.append('=== COMBOBOX ITEMS ===')
for m in re.finditer(r'<widget class="QComboBox" name="([^"]+)">([\s\S]*?)</widget>', txt):
    items = re.findall(r'<string[^>]*>([^<]*)</string>', m.group(2))
    out.append('%s => %r' % (m.group(1), items))

out.append('')
out.append('=== STRINGS ===')
for s in re.findall(r'<string[^>]*>([^<]*)</string>', txt):
    out.append(s)

io.open('_seg2.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('ok', len(seg))
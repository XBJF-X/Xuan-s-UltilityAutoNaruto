import io
lines = io.open('utils/ui/Service.ui', encoding='utf-8').read().splitlines()
seg = lines[1310:1700]
io.open('_seg.txt', 'w', encoding='utf-8').write('\n'.join(seg))
print('ok', len(seg))
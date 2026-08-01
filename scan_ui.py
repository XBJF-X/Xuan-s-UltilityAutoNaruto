import json, sys
sys.stdout.reconfigure(encoding='utf-8')
cfg = json.load(open('src/DefaultConfig.json', encoding='utf-8'))
dics = cfg.get('setting_dics', cfg)
for k, v in dics.items():
    print(repr(k), '=', repr(v)[:150])
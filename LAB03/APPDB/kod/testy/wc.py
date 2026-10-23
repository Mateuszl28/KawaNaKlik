"""Pomocnik: wywołania WooCommerce REST (testowe klucze z dane_testowe). użycie: wc.py METHOD path [json]"""
import json, ssl, sys, base64, urllib.request
ck, cs = [l.strip() for l in open('dane_testowe/woocommerce_api_test.txt') if l.strip()][:2]
m, path = sys.argv[1], sys.argv[2]
body = sys.argv[3].encode() if len(sys.argv) > 3 else None
r = urllib.request.Request('https://kawanaklik.local/wp-json/wc/v3/' + path, data=body, method=m,
    headers={'Content-Type': 'application/json', 'Authorization': 'Basic ' + base64.b64encode(f'{ck}:{cs}'.encode()).decode()})
ctx = ssl._create_unverified_context()
try:
    print(urllib.request.urlopen(r, context=ctx, timeout=60).read().decode())
except urllib.error.HTTPError as e:
    print(e.code, e.read().decode()[:500])

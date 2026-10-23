"""Wysyła do n8n podpisany (HMAC-SHA256, jak WooCommerce) webhook z plikiem JSON. użycie: signed_post.py plik.json [topic]"""
import base64, hashlib, hmac, sys, time, urllib.request
body = open(sys.argv[1], 'rb').read()
secret = open('C:/Users/lagoc/.n8n-kawanaklik/wc_webhook_secret.txt').read().strip().encode()
sig = base64.b64encode(hmac.new(secret, body, hashlib.sha256).digest()).decode()
r = urllib.request.Request('http://localhost:5690/webhook/zamowienie', data=body, method='POST', headers={
    'Content-Type': 'application/json', 'X-WC-Webhook-Topic': sys.argv[2] if len(sys.argv) > 2 else 'order.created',
    'X-WC-Webhook-Signature': sig, 'X-WC-Webhook-Source': 'https://kawanaklik.local/'})
t = time.time()
try:
    resp = urllib.request.urlopen(r, timeout=90); print(resp.status, resp.read().decode(), f'{time.time()-t:.1f}s')
except urllib.error.HTTPError as e:
    print(e.code, e.read().decode(), f'{time.time()-t:.1f}s')

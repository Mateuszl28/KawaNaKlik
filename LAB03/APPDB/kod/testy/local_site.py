"""Zatrzymanie / uruchomienie strony w aplikacji Local (API GraphQL Local) – symulacja awarii sklepu w teście T7.
użycie: local_site.py stop|start [site_id]"""
import json, os, sys, urllib.request
info = json.load(open(os.path.expanduser('~/AppData/Roaming/Local/graphql-connection-info.json')))
site = sys.argv[2] if len(sys.argv) > 2 else 'bqJE9fRP1q'
q = {'query': 'mutation($id: ID!) { %sSite(id: $id) { id status } }' % sys.argv[1], 'variables': {'id': site}}
r = urllib.request.Request(info['url'], data=json.dumps(q).encode(), method='POST',
                           headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + info['authToken']})
print(urllib.request.urlopen(r, timeout=180).read().decode())

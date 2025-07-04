from flask import Flask
import requests
import json

reg = ['ZZ416', 'ZZ418', 'ZZ419', 'ZZ504', 'ZZ507']

app = Flask(__name__)
@app.route('/check')
def check():
    found = 0
    for i in reg:
        r = requests.get(f'''https://api.adsb.lol/v2/reg/{i}''')
        rjson = r.json()
        if rjson['ac'] != []:
            found += 1
            with open('planes.json', 'w') as o:
                json.dump({'reg': rjson['ac'][0]['r'], 
                            'lat': rjson['ac'][0]['lat'],
                            'lon': rjson['ac'][0]['lon'],
                            'time': rjson['ctime']}, o)

    return f'Success: {found} planes found'

if __name__ == '__main__':
    app.run()
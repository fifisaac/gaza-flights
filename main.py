from flask import Flask
import requests
import json

reg = ['ZZ416', 'ZZ418', 'ZZ419', 'ZZ504', 'ZZ507']
bbox = {"gaza": [[34.609, 32.820], [30.929, 34.659]],
        "uk": [[60.479, -10.979], [50.378, 3.515]]}

app = Flask(__name__)
@app.route('/check')
def check():
    found = 0
    for i in reg:
        r = requests.get(f'''https://api.adsb.lol/v2/reg/{i}''')

        if r.status_code != 200:
            return f'An error occured in the adsb.lol API.', r.status_code
            ## adsb.lol seems to intermittently return 503 errors. adsb.fi or adsb.one may be an alternative
        
        rjson = r.json()
        if rjson['ac'] != []:
            found += 1

            # Need JSON formatting
            with open('planes.json', 'a+') as o:
                o.seek(0)
                file = json.loads(o.read())
                flights = file["flights"]
                time = rjson['ctime']
                newFlight = True
                for j in range(1, len(reg)+1):
                    if j >= len(flights):
                        break
                    
                    if (flights[-j]["reg"] == i) and (flights[-j]['locs'][-1]["time"] + 12000 <= time):
                        newFlight = False
                        flights[-j]['locs'].append({'lat': rjson['ac'][0]['lat'],
                                            'lon': rjson['ac'][0]['lon'],
                                            'time': time})
                        break
                        
                if newFlight:
                    flights.append({
                                    "reg": i,
                                    "locs": [
                                        {
                                            "lat": rjson['ac'][0]['lat'],
                                            "lon": rjson['ac'][0]['lon'],
                                            "time": time
                                        }
                                        ]
                                    })

            with open('woahplanes.json', 'w') as o:
                json.dump({"flights": flights}, o, indent=4)

    return f'Success: {found} planes found'

if __name__ == '__main__':
    app.run()
from flask import Flask, render_template
import requests
import json

reg = ['ZZ416', 'ZZ418', 'ZZ419', 'ZZ504', 'ZZ507']
bbox = {"gaza": [[34.609, 32.820], [30.929, 34.659]],
        "uk": [[60.479, -10.979], [50.378, 3.515]]}

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# Returns the JSON store of data
@app.route('/raw')
def raw():
    with open('planes.json', 'r') as f:
        return json.load(f)


# /check will be pinged every 15 minutes to see which if any planes are currently flying
# Could be automated to call the function locally instead of accessing /check
@app.route('/check')
def check():

    found = 0

    for i in reg:
        r = requests.get(f'''https://api.adsb.lol/v2/reg/{i}''')

        if r.status_code != 200:
            return f'An error occured in the adsb.lol API.', r.status_code
            ## adsb.lol seems to intermittently return 503 errors. adsb.fi or adsb.one may be alternatives
        
        rjson = r.json()

        # If no plane was found, the 'ac' field will be an empty array
        if rjson['ac'] != []:
            found += 1

            # Opens to access previous flights
            with open('planes.json', 'r') as o:
                o.seek(0)
                file = json.loads(o.read())
                flights = file["flights"]
                time = rjson['ctime']
                newFlight = True
                for j in range(1, len(reg)+1):
                    if j >= len(flights):
                        break
                    
                    # Checks if there is an existing flight with same reg and within 21000000ms (approx 6hrs)
                    if (flights[-j]["reg"] == i) and (flights[-j]['locs'][-1]["time"] + 21000000 >= time):
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
            
            # Re-opens file, this time to write the new data
            with open('planes.json', 'w') as o:
                json.dump({"flights": flights}, o, indent=4)

    return f'Success: {found} planes found'

if __name__ == '__main__':
    app.run()
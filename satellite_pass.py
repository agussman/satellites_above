import requests
from os import path, environ

# A lot of this code was taken from / based on https://github.com/dronir/N2YOtools

BASE_URL = "https://www.n2yo.com/rest/v1/satellite/"
# Using a default search_radius of 45 degrees and assuming sea level alitude (0) and all categories (the last 0)
TEMPLATE = "above/{observer_lat:.5f}/{observer_lng:.5f}/0/45/0"

def _get_api_key():
    # Load N2YO API key from file (get your own key by registering at N2YO.com)
    if "N2YO_API_KEY" in environ:
        apiKey = environ.get("N2YO_API_KEY")
    elif path.exists("config/N2YO_API_KEY.txt"):
        apiKey = open("config/N2YO_API_KEY.txt").read().strip()
    else:
        print("Error: Missing API key. Set N2YO_API_KEY env or store in config/N2YO_API_KEY.txt")
        apiKey = "NOTFOUND"
    return { "apiKey": apiKey}

def parse_query(params, debug=False):
    " Produce URL from parameter dictionary."
    url = "".join([BASE_URL, TEMPLATE.format(**params)])
    if debug:
        print("Created query: {}".format(url))
    return url

def retrieve_data(QUERY_URL, params, debug=False):
    "Retrieve data from given URL."
    if debug:
        print("Requesting data from: {}".format(QUERY_URL))
    r = requests.get(QUERY_URL, params=params)
    if r.status_code == requests.codes.ok:
        if debug:
            print("Success.")
        return r.json()
    elif debug:
        print("Failed! (status code {})".format(r.status_code))
    return "{}"

def get_sats_above(lat, lon):
    params = {
        "observer_lat": lat,
        "observer_lng": lon
    }
    url = parse_query(params)
    apiKey = _get_api_key()

    data = retrieve_data(url, apiKey, True)
    #print("info.satcount: {}".format(data["info"]["satcount"]))
    #print("Returned data: {}".format(data))

    return data["info"]["satcount"]

def get_fake_count(lat, lon):
    return 101

def z():
    sat_count = get_sats_above(38.99651, -77.320582)

    return "There are {} satellites above you!".format(sat_count)


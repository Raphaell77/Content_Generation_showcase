import requests
import time



def send_http_request(keywords: list[str], niche_name: str, hostlanguage: str, geolocation: str) -> dict[str, list[str]]:
    hl = hostlanguage.lower()
    gl = geolocation.lower()

    data = {}
    for keyword in keywords:
        search_query = niche_name + ' ' + keyword
        # client=firefox: ausgabefortmat, hl=en&gl=EN: hostlanguage & geolocation, ds=yt: nur yt suche, keine google websuche
        URL = f"https://suggestqueries-clients6.youtube.com/complete/search?client=firefox&q={search_query}&hl={hl}&gl={gl}&ds=yt" # host language und geo location auch als customer params

        data[keyword] = []
        try:
            response = requests.get(URL)
            search_query = response.json()   # ANPASSEN DES FORMATS
            # print(f'{response.content}\n')

            for elem in search_query[1]:
                data[keyword].append(elem)
            

        except requests.exceptions.HTTPError as error:
            print("\nHTTP Error")
            print(error.args[0])

        time.sleep(1.5) # warten sonst bann

    return data



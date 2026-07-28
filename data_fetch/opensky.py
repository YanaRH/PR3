import requests
import psycopg2


def fetch_aircraft_data(db_config: dict) -> int:
    """
    Загружает данные о текущих самолётах из API OpenSky Network
    и сохраняет/обновляет их в таблице aircraft.
    """
    url = "https://opensky-network.org/api/states/all"
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Не удалось получить данные от OpenSky: {e}")
        return 0

    if not data or not data.get('states'):
        return 0

    states = data['states']
    count = 0

    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()

    for state in states:
        # state: [0: icao24, 1: callsign, 2: origin_country, 3: time_position,
        #         4: last_contact, 5: longitude, 6: latitude, 7: baro_altitude,
        #         8: on_ground, 9: velocity, 10: true_track, 11: vertical_rate,
        #         12: sensors, 13: geo_altitude, 14: squawk, 15: spi]

        icao24 = state[0]
        callsign = state[1]
        origin_country = state[2]
        time_pos = state[3]
        last_contact = state[4]
        lon = state[5]
        lat = state[6]
        velocity = state[9] if state[9] is not None else 0.0
        squawk = str(state[14])[:4] if state[14] else ""

        try:
            query = """
                INSERT INTO aircraft (icao24, callsign, origin_country, time_position, 
                                      last_contact, longitude, latitude, velocity, squawk)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (icao24) DO UPDATE SET
                    callsign = EXCLUDED.callsign,
                    velocity = EXCLUDED.velocity,
                    last_contact = EXCLUDED.last_contact;
            """
            cursor.execute(query, (icao24, callsign, origin_country, time_pos,
                                   last_contact, lon, lat, velocity, squawk))
            count += 1
        except Exception:
            continue

    conn.commit()
    cursor.close()
    conn.close()
    return count

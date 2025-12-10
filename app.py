from flask import Flask, render_template, jsonify, request
import oracledb
import json

app = Flask(__name__)

# ⚠️ Remember to update credentials with your real username/password
def get_db_connection():
    conn = oracledb.connect("s2677882/weiheng0502@@geoslearn", config_dir="/etc/")
    return conn

@app.route("/")
def index():
    return render_template("map.html")

# API 1: Get Greenspace Data (Points)
@app.route("/api/greenspaces")
def api_greenspaces():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Query facilities as well
    sql = "SELECT id, name, type, quality_score, lat, lon, facilities FROM MOCK_GREENSPACES"
    cur.execute(sql)
    
    features = []
    for row in cur:
        features.append({
            "type": "Feature",
            "properties": {
                "id": row[0],
                "name": row[1],
                "type": row[2],
                "quality": row[3],
                "facilities": row[6]
            },
            "geometry": {
                "type": "Point",
                "coordinates": [row[5], row[4]]  # GeoJSON is [Lon, Lat]
            }
        })
    
    cur.close()
    conn.close()
    return jsonify({"type": "FeatureCollection", "features": features})

# API 2: Get Neighbourhood Data (Polygons)
@app.route("/api/neighbourhoods")
def api_neighbourhoods():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Query extra attributes: stress_index, population
    sql = """
        SELECT id, name, health_index, simd_rank, geojson_text, 
               stress_index, population, center_lat, center_lon 
        FROM MOCK_NEIGHBOURHOODS
    """
    cur.execute(sql)
    
    features = []
    for row in cur:
        # row[4] is CLOB, needs read()
        geom_str = row[4].read() if row[4] else None
        if geom_str:
            geometry = json.loads(geom_str)
            features.append({
                "type": "Feature",
                "properties": {
                    "id": row[0],
                    "name": row[1],
                    "health": row[2],
                    "simd": row[3],
                    "stress": row[5],
                    "pop": row[6],
                    "lat": row[7],
                    "lon": row[8]
                },
                "geometry": geometry
            })

    cur.close()
    conn.close()
    return jsonify({"type": "FeatureCollection", "features": features})

if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, render_template, jsonify, request
import oracledb

app = Flask(__name__)

def get_db_connection():
    conn = oracledb.connect("user/password@geoslearn", config_dir="/etc/")
    return conn

@app.route("/")
def index():
    return render_template("map.html")

@app.route("/api/greenspace")
def api_greenspace():
    postcode = request.args.get("postcode")

    conn = get_db_connection()
    cur = conn.cursor()

    sql = """
        SELECT id, name, quality_score,
               SDO_UTIL.TO_GEOJSON(geom) as geojson
        FROM greenspace
        WHERE postcode = :pc
    """
    cur.execute(sql, pc=postcode)

    features = []
    for row in cur:
        features.append({
            "type": "Feature",
            "properties": {
                "id": row[0],
                "name": row[1],
                "quality": row[2],
            },
            "geometry": row[3]   # 假设已经是 GeoJSON 字符串或 dict
        })

    cur.close()
    conn.close()

    return jsonify({
        "type": "FeatureCollection",
        "features": features
    })

if __name__ == "__main__":
    # 本地用 geos-flask 调试时可以用
    app.run(debug=True)

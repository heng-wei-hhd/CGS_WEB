from flask import Flask, render_template, jsonify, request
import oracledb

app = Flask(__name__)

def get_db_connection():
    # 格式说明： "用户名/密码@数据库名"
    # config_dir="/etc/" 是学校服务器特有的配置，不要删除
    conn = oracledb.connect("s2677882/weiheng0502@@geoslearn", config_dir="/etc/") 
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

# ... (上面的代码保持不变) ...

if __name__ == "__main__":
    # === 临时测试代码开始 ===
    try:
        print("正在尝试连接数据库并查询数据...")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 执行组员提供的查询命令
        # 注意：这里我们只取前 5 行 (fetchmany(5)) 看看样子，避免数据太多刷屏
        sql = "Select * from s2891816.OPEN_SPACE_AUDIT_DATA"
        cursor.execute(sql)
        
        rows = cursor.fetchmany(5)
        
        print("--- 查询成功！以下是前5条数据 ---")
        for row in rows:
            print(row)
        print("--------------------------------")
        
        # 顺便打印一下列名（表头），这对后面写代码很有帮助
        print("列名（表头）如下：")
        for description in cursor.description:
            print(description[0])
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print("发生错误:", e)
    # === 临时测试代码结束 ===

    # 启动 Flask 网站
    app.run(debug=True)

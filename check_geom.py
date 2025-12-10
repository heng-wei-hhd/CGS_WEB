import oracledb

# === 配置你的数据库连接 ===
def get_db_connection():
    # 请替换为你的真实账号密码
    conn = oracledb.connect("s2677882/weiheng0502@@geoslearn", config_dir="/etc/")
    return conn

def check_geometry_column():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 我们要测试的两个常见名字
    possible_names = ["SHAPE", "GEOM", "GEOMETRY"]
    found_column = None

    print("正在寻找坐标列...")

    for col_name in possible_names:
        try:
            # 尝试只查询这一列，看数据库会不会报错
            # 我们使用 SDO_UTIL.TO_GEOJSON 函数来测试它是不是真正的地理数据
            sql = f"SELECT SDO_UTIL.TO_GEOJSON({col_name}) FROM s2891816.OPEN_SPACE_AUDIT_DATA WHERE ROWNUM <= 1"
            cursor.execute(sql)
            row = cursor.fetchone()
            
            if row:
                print(f"✅ 找到了！坐标列的名字是: {col_name}")
                print(f"   数据预览 (GeoJSON): {str(row[0])[:50]}...") # 只打印前50个字符
                found_column = col_name
                break
        except oracledb.DatabaseError as e:
            print(f"❌ 不是 {col_name}...")
            # print(e) # 如果想看具体错误可以取消注释

    cursor.close()
    conn.close()

    if found_column:
        print("\n🎉 成功！请在下一步的 app.py 中使用这个列名。")
    else:
        print("\n⚠️ 警告：没有找到标准的几何列。请询问提供数据的组员，存放坐标(Geometry)的列名叫什么？")

if __name__ == "__main__":
    check_geometry_column()
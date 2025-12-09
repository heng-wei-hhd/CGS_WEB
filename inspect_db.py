import oracledb

# 1. 这里填入你的数据库连接信息
def get_db_connection():
    # 记得把 user 和 password 改成你真实的账号密码
    conn = oracledb.connect("s2677882/weiheng0502@@geoslearn", config_dir="/etc/")
    return conn

try:
    print("正在连接数据库...")
    conn = get_db_connection()
    cursor = conn.cursor()

    # 2. 查询数据
    print("正在查询 s2891816.OPEN_SPACE_AUDIT_DATA 表...")
    sql = "Select * from s2891816.OPEN_SPACE_AUDIT_DATA"
    cursor.execute(sql)
    
    # 3. 获取并打印列名（表头）
    print("\n========== 表头 (列名) ==========")
    columns = [col[0] for col in cursor.description]
    print(columns)
    print("=================================\n")

    # 4. 打印第一条数据看看样子
    row = cursor.fetchone()
    print("第一条数据内容:", row)

    cursor.close()
    conn.close()
    print("\n测试结束，连接已关闭。")

except Exception as e:
    print("\n发生错误:", e)
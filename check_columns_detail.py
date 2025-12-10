import oracledb

# 记得填入你的真实账号密码
def get_db_connection():
    conn = oracledb.connect("s2677882/weiheng0502@@geoslearn", config_dir="/etc/")
    return conn

def check_table_structure():
    conn = get_db_connection()
    cursor = conn.cursor()

    print("正在查询表结构详细信息...")
    
    # 注意：表名和用户名在 Oracle 内部通常是大写的
    # 我们查询 ALL_TAB_COLUMNS 系统表
    target_owner = "S2891816" 
    target_table = "OPEN_SPACE_AUDIT_DATA"
    
    sql = """
        SELECT column_name, data_type 
        FROM all_tab_columns 
        WHERE table_name = :tb AND owner = :ow
        ORDER BY column_name
    """
    
    cursor.execute(sql, tb=target_table, ow=target_owner)
    
    rows = cursor.fetchall()
    
    if not rows:
        print(f"⚠️ 找不到表 {target_owner}.{target_table}，请检查表名是否正确。")
    else:
        print(f"\n=== 表 {target_table} 的所有列 ===")
        found_spatial = False
        for row in rows:
            col_name = row[0]
            data_type = row[1]
            print(f"列名: {col_name:<15} 类型: {data_type}")
            
            # 检查是否有空间类型
            if "SDO" in data_type or "GEOMETRY" in data_type:
                found_spatial = True
                print(f"   >>> ✨ 发现空间列！名字是: {col_name}")

        print("==================================")
        if not found_spatial:
            print("\n❌ 结论：这张表里没有任何几何/空间数据列。")
            print("💡 可能原因：导入时只选择了属性，丢失了空间数据。")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_table_structure()
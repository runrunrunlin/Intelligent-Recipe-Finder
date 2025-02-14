import sqlite3
import os

# 指定数据库文件的路径
db_path = r'C:\Users\Run\Desktop\cm\project\backend\recipes.db'

# 检查文件是否存在
if not os.path.exists(db_path):
    print(f"数据库文件不存在: {db_path}")
else:
    print(f"正在打开数据库: {db_path}")
    
    try:
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        if not tables:
            print("数据库中没有表")
        else:
            print("数据库中的表:")
            for table in tables:
                table_name = table[0]
                print(f"\n表名: {table_name}")
                
                # 获取表结构
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                print("列:")
                for column in columns:
                    print(f"  - {column[1]} ({column[2]})")
                
                # 获取表中的数据（仅显示前5行）
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                rows = cursor.fetchall()
                if rows:
                    print("数据样本（前5行）:")
                    for row in rows:
                        print(f"  {row}")
                else:
                    print("  表中没有数据")

        conn.close()

    except sqlite3.Error as e:
        print(f"SQLite 错误: {e}")
    except Exception as e:
        print(f"发生错误: {e}")

print("脚本执行完毕")
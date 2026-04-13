import os

# 查看当前目录
print("当前目录:", os.getcwd())
print("\n目录内容:")
for item in os.listdir('.'):
    print(f"  {item}")

# 检查 app 目录
if os.path.exists('app'):
    print("\napp 目录内容:")
    for item in os.listdir('app'):
        print(f"  {item}")
    
    # 检查 routers 目录
    if os.path.exists('app/routers'):
        print("\napp/routers 目录内容:")
        for item in os.listdir('app/routers'):
            print(f"  {item}")
    
    # 检查 services 目录
    if os.path.exists('app/services'):
        print("\napp/services 目录内容:")
        for item in os.listdir('app/services'):
            print(f"  {item}")
    
    # 检查 templates 目录
    if os.path.exists('app/templates'):
        print("\napp/templates 目录内容:")
        for item in os.listdir('app/templates'):
            print(f"  {item}")

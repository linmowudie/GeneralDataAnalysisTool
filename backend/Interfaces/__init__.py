"""
backend.Interfaces：接口层（controllers / web / sdk）

依赖方向：Interfaces -> Services -> Cores -> Models -> Infrastructures。
注意：本包 __init__ 不主动导入 web 子包，保证 sdk 在无 fastapi 环境可用。
"""

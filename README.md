# First Seed

## 依赖包安装
```python
conda create -n first_seed python=3.12.2 

pip install langchain langchain_core langserve fastapi langchain_openai sse_starlette faiss-cpu loguru mypy pandas openpyxl overrides Jinja2
```

## 注意点
- Agent运行的设备需要挂代理；

## 严格模式检查
- mypy --strict main.py

## 运行步骤
1. 进入`first_seed/budding_world/`文件夹，运行`python gen_budding_world.py`,输入世界名(budding_world.xlsx内的创建世界的sheet页名),输入版本号:`ewan`(目前builder的解析版本是ewan).
2. 运行`first_seed/budding_world/gen_agent`下面的全部agent，启动agents服务器;
3. 然后运行main.py进行对话,先输入第1步创建的世界名,然后可以输入`/run`推进世界进程。
4. 或者通过'/login'命令通过玩家身份登陆游戏游玩。

## 启动所有agents（方便复制粘贴）
```shell
pm2 start budding_world/gen_agent/coffin_of_the_silent_one_agent.py budding_world/gen_agent/gray_chapel_agent.py budding_world/gen_agent/nameless_resurrector_agent.py budding_world/gen_agent/rat_king_agent.py budding_world/gen_agent/elias_gray_agent.py budding_world/gen_agent/moore_dog_agent.py budding_world/gen_agent/papal_emissary_agent.py budding_world/gen_agent/the_incinerator_agent.py budding_world/gen_agent/gray_cemetery_agent.py budding_world/gen_agent/mr_lucky_agent.py budding_world/gen_agent/rancid_cellar_agent.py
```


## “系统输入环节”的可用的命令, [system input]
```shell
# 退出游戏
/quit 
# 创建游戏房间
/create
# 选择角色
/pickactor @无名的复活者
/pickactor @教廷密使
# 加入已经存在的房间
/join @127.0.0.1
```

## “玩家输入环节”的可用的命令
```shell
# 直接停掉整个游戏
/quit
# 攻击目标NPC, 名字为Name?
/attack ‘Name?’
# 离开当前场景，去往Name?的场景
/leave ‘Name?’
# 在当前场景内广播内容。场景内所有NPC都能听见
/broadcast ‘说的内容’
# 对当前场景内的目标说话
/speak ‘@对谁>说话内容’
# 对当前场景内的目标低语
/whisper ‘@对谁>说话内容’
# 在当前场景内搜索叫‘Name?’的道具
/search ‘Name?’
# 在不知道去往哪里的情况下，‘跳出’当前场景，如果当前场景没有连接场景则会失败。
/portalstep
# 感知当前场景内有哪些人？事？道具？
/perception
# 盗取对当前场景内的目标的道具
/steal ‘@对谁>盗取的道具名字’
# 将我身上的道具交给目标
/trade ‘@对谁>我的道具的名字’
# 查看我身上有哪些道具？
/checkstatus
# 对谁使用某个道具
/useprop @谁>xx
```

## 测试指令
```shell
# 退出游戏
/quit 
# 创建游戏房间
/create
# 选择角色
/pickactor @无名的复活者
/pickactor @教廷密使
# 加入已经存在的房间
/join @127.0.0.1
# 无名的复活者使用道具离开禁言铁棺
/useprop @禁言铁棺>腐朽的匕首
```

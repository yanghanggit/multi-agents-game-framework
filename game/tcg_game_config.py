from pathlib import Path


###########################################################################################################################################
# 生成log的目录
LOGS_DIR: Path = Path("logs")
LOGS_DIR.mkdir(parents=True, exist_ok=True)
assert LOGS_DIR.exists(), f"找不到目录: {LOGS_DIR}"

# 生成世界的目录
GEN_WORLD_DIR: Path = Path("gen_worlds")
GEN_WORLD_DIR.mkdir(parents=True, exist_ok=True)
assert GEN_WORLD_DIR.exists(), f"找不到目录: {GEN_WORLD_DIR}"

# 生成运行时的目录
GEN_RUNTIME_DIR: Path = Path("gen_runtimes")
GEN_RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
assert GEN_RUNTIME_DIR.exists(), f"找不到目录: {GEN_RUNTIME_DIR}"

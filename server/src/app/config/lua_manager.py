import asyncio
import os
from typing import Any, Dict, List

from redis.asyncio import Redis
from redis.exceptions import ResponseError

from server.src.app.logging.logger_setup import get_logger

logger = get_logger(__name__)

class LuaScriptManager:
    def __init__(self, redis: Redis, lua_dir: str):
        self.redis = redis
        self.lua_dir = lua_dir
        self.scripts: Dict[str, Dict[str, str]] = {}
        self._lock = asyncio.Lock()

    async def load_scripts(self):
        if not os.path.exists(self.lua_dir):
            logger.error(f"Lua directory not found: {self.lua_dir}")
            return

        for root, _, files in os.walk(self.lua_dir):
            for file in files:
                if file.endswith(".lua"):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.lua_dir)
                    script_name = rel_path.replace(os.sep, "/").rsplit(".", 1)[0]
                    
                    try:
                        content = await asyncio.to_thread(self.read_file, file_path)
                        sha = await self.redis.script_load(content)
                        
                        self.scripts[script_name] = {
                            "sha": sha,
                            "content": content
                        }
                        logger.info(f"Loaded Lua script: {script_name} ({sha})")
                    except Exception as e:
                        logger.error(f"Failed to load Lua script {script_name}: {e}")
                        raise RuntimeError(f"Critical failure: Lua script {script_name} failed to load.") from e

    def read_file(self, path: str) -> str:
        with open(path, "r") as f:
            return f.read()

    async def execute(self, script_name: str, keys: List[Any], args: List[Any]) -> Any:
        script_data = self.scripts.get(script_name)
        if not script_data:
            raise RuntimeError(f"Lua script not loaded: {script_name}")
        
        sha = script_data["sha"]
        
        try:
            return await self.redis.evalsha(sha, len(keys), *keys, *args)
        except ResponseError as e:
            if "NOSCRIPT" in str(e):
                async with self._lock:
                    sha = self.scripts[script_name]["sha"]
                    try:
                        return await self.redis.evalsha(sha, len(keys), *keys, *args)
                    except ResponseError as retry_e:
                        if "NOSCRIPT" not in str(retry_e):
                            raise
                        
                        logger.warning(f"NOSCRIPT error for {script_name}, re-loading from memory...")
                        new_sha = await self.redis.script_load(script_data["content"])
                        self.scripts[script_name]["sha"] = new_sha
                        
                        return await self.redis.evalsha(new_sha, len(keys), *keys, *args)
            raise

from pathlib import Path

from fastapi import FastAPI

from server.src.app.config.lua_manager import LuaScriptManager
from server.src.app.logging.logger_setup import get_logger

logger = get_logger(__name__)

async def initialize_lua(app: FastAPI):
    base_dir = Path(__file__).resolve().parents[2]
    lua_dir = base_dir / "store" / "cache" / "lua"

    if not lua_dir.exists():
        error_msg = f"Lua directory does not exist at expected path: {lua_dir}"
        logger.fatal(error_msg)
        raise RuntimeError(error_msg)

    lua_manager = LuaScriptManager(app.state.redis, str(lua_dir))
    await lua_manager.load_scripts()
    
    app.state.lua_manager = lua_manager
    
    logger.info("Lua scripting layer initialized successfully.")

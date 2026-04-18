local user_key = KEYS[1]
local session_token_hashes = redis.call("SMEMBERS", user_key)

for _, session_token_hash in ipairs(session_token_hashes) do
    local session_key = "session:" .. session_token_hash
    local device_id = redis.call("HGET", session_key, "device_id")

    redis.call("DEL", session_key)

    if device_id and device_id ~= "" then
        redis.call("SREM", "device_sessions:" .. device_id, session_token_hash)
    end
end

redis.call("DEL", user_key)

return 1

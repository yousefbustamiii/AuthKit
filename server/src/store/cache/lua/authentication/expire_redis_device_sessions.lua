local total = 0

for i = 1, #KEYS do
    local device_key = KEYS[i]
    local session_token_hashes = redis.call("SMEMBERS", device_key)

    for _, session_token_hash in ipairs(session_token_hashes) do
        local session_key = "session:" .. session_token_hash
        local user_id = redis.call("HGET", session_key, "user_id")

        redis.call("DEL", session_key)

        if user_id and user_id ~= "" then
            redis.call("SREM", "user_sessions:" .. user_id, session_token_hash)
        end

        total = total + 1
    end

    redis.call("DEL", device_key)
end

return total

local session_token_hash = ARGV[1]
local session_key = "session:" .. session_token_hash
local session_data = redis.call("HGETALL", session_key)

if #session_data == 0 then
    return 1
end

local user_id, device_id
for i = 1, #session_data, 2 do
    if session_data[i] == "user_id" then
        user_id = session_data[i+1]
    elseif session_data[i] == "device_id" then
        device_id = session_data[i+1]
    end
end

redis.call("DEL", session_key)

if user_id and user_id ~= "" then
    redis.call("SREM", "user_sessions:" .. user_id, session_token_hash)
end

if device_id and device_id ~= "" then
    redis.call("SREM", "device_sessions:" .. device_id, session_token_hash)
end

return 1

local keys = KEYS
local num_keys = #KEYS

local SCALE = 1000000
local time = redis.call("TIME")
local current_time = tonumber(time[1]) * 1000 + math.floor(tonumber(time[2]) / 1000)

local buckets = {}

for i = 1, num_keys do
    local key = keys[i]
    local max_hits = tonumber(ARGV[(i - 1) * 2 + 1])
    local window = tonumber(ARGV[(i - 1) * 2 + 2])

    local max_tokens_scaled = max_hits * SCALE
    local window_ms = window * 1000

    local bucket = redis.call("HMGET", key, "tokens_scaled", "last_update")
    local tokens_scaled = tonumber(bucket[1])
    local last_update = tonumber(bucket[2])

    if tokens_scaled ~= nil then
        local delta_ms = current_time - last_update
        local added = math.floor((delta_ms * max_tokens_scaled) / window_ms)
        tokens_scaled = math.min(max_tokens_scaled, tokens_scaled + added)

        if tokens_scaled < SCALE then
            local needed = SCALE - tokens_scaled
            local retry_after_s = math.ceil((needed * window_ms) / (max_tokens_scaled * 1000))
            return {0, retry_after_s, key}
        end
    end

    buckets[i] = tokens_scaled
end

for i = 1, num_keys do
    local key = keys[i]
    local max_hits = tonumber(ARGV[(i - 1) * 2 + 1])
    local window = tonumber(ARGV[(i - 1) * 2 + 2])

    local max_tokens_scaled = max_hits * SCALE
    local window_ms = window * 1000

    local tokens_scaled = buckets[i]

    if tokens_scaled == nil then
        tokens_scaled = max_tokens_scaled - SCALE
    else
        tokens_scaled = tokens_scaled - SCALE
    end

    redis.call("HSET", key, "tokens_scaled", math.floor(tokens_scaled), "last_update", current_time)
    redis.call("PEXPIRE", key, window_ms)
end

return {1, 0, ""}

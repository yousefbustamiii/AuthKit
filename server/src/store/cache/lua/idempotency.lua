if redis.call("SET", KEYS[1], ARGV[1], "NX", "EX", 300) then
    return 0
else
    return redis.call("GET", KEYS[1])
end

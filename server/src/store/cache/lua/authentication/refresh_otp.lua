if redis.call("EXISTS", KEYS[1]) == 0 then
    return nil
end
redis.call("SET", KEYS[1], ARGV[2], "EX", ARGV[1])
return 1

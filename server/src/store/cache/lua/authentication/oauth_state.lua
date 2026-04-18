local val = redis.call('GET', KEYS[1])
if val then
    redis.call('DEL', KEYS[1])
    return 1
end
return 0

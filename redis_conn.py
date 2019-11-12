import redis

redis_cli=redis.StrictRedis()
res=list(redis_cli.smembers(b'search_keywords_set'))

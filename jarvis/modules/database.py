from jarvis import redis


def strb(redis_string):
    return str(redis_string)[2:-1]


async def is_afk():
    to_check = redis.get('is_afk')
    if to_check:
        return True
    else:
        return False


async def afk(reason):
    redis.set('is_afk', reason)


async def afk_reason():
    return strb(redis.get('is_afk'))


async def not_afk():
    redis.delete('is_afk')

# -*- coding: utf-8 -*- 

import redis, time
from config import *

g_cache = redis.StrictRedis(unix_socket_path=UNIX_DOMAIN_REDIS, db=0)
g_cache.ping()

IP_HASH_NAME = "tracker:ip"


def markip(ip):
    return g_cache.hset(IP_HASH_NAME, ip, str(int(time.time())))


def is_visit(ip):
    return bool(g_cache.hget(IP_HASH_NAME, ip))

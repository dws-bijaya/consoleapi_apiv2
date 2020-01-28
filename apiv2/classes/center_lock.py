"""
Distributed locks with Redis
Redis doc: http://redis.io/topics/distlock
"""
from __future__ import division
import random
import time
import uuid
import signal, os
import redis

try:
    from time import monotonic
except ImportError:
    # Python 2.7
    from time import time as monotonic


DEFAULT_RETRY_TIMES = 3
DEFAULT_RETRY_DELAY = 200
DEFAULT_TTL = 100000
CLOCK_DRIFT_FACTOR = 0.01

# Reference:  http://redis.io/topics/distlock
# Section Correct implementation with a single instance
RELEASE_LUA_SCRIPT = """
    if redis.call("get",KEYS[1]) == ARGV[1] then
        return redis.call("del",KEYS[1])
    else
        return 0
    end
"""


class RedLockError(Exception):
    pass


class RedLockFactory(object):
    """
    A Factory class that helps reuse multiple Redis connections.
    """

    def __init__(self, connection_details):
        """
        """
        self.redis_nodes = []

        for conn in connection_details:
            if isinstance(conn, (redis.StrictRedis, redis.Redis)):
                node = conn
            elif 'url' in conn:
                url = conn.pop('url')
                node = redis.StrictRedis.from_url(url, **conn)
            else:
                node = redis.StrictRedis(**conn)
            node._release_script = node.register_script(RELEASE_LUA_SCRIPT)
            self.redis_nodes.append(node)
            self.quorum = len(self.redis_nodes) // 2 + 1

    def create_lock(self, resource, **kwargs):
        """
        Create a new RedLock object and reuse stored Redis clients.
        All the kwargs it received would be passed to the RedLock's __init__
        function.
        """
        lock = RedLock(resource=resource, created_by_factory=True, **kwargs)
        lock.redis_nodes = self.redis_nodes
        lock.quorum = self.quorum
        lock.factory = self
        return lock


class RedLock(object):
    _locked = {}
    """
    A distributed lock implementation based on Redis.
    It shares a similar API with the `threading.Lock` class in the
    Python Standard Library.
    """
    def signal_handler(self, signum, frame):
        self.release()

    def init_sig(self):
        signal.signal(signal.SIGINT, self.signal_handler)

    def __init__(self, resource, uuid, connection_details=None,
                 retry_times=DEFAULT_RETRY_TIMES,
                 retry_delay=DEFAULT_RETRY_DELAY,
                 ttl=DEFAULT_TTL,
                 created_by_factory=False):

        # lock_key should be random and unique
        self.lock_key = uuid #uuid.uuid4().hex
        self._released = False
        self.init_sig()
        self.resource = resource
        self.retry_times = retry_times
        self.retry_delay = retry_delay
        self.ttl = ttl
        if created_by_factory:
            self.factory = None
            return

        self.redis_nodes = []
        # If the connection_details parameter is not provided,
        # use redis://127.0.0.1:6379/0
        if connection_details is None:
            connection_details = [{
                'host': 'localhost',
                'port': 6379,
                'db': 0,
            }]

        for conn in connection_details:
            if isinstance(conn, redis.StrictRedis):
                node = conn
            elif 'url' in conn:
                url = conn.pop('url')
                node = redis.StrictRedis.from_url(url, **conn)
            else:
                node = redis.StrictRedis(**conn)
            node._release_script = node.register_script(RELEASE_LUA_SCRIPT)
            self.redis_nodes.append(node)
        self.quorum = len(self.redis_nodes) // 2 + 1

    def __enter__(self):
        acquired, validity = self.acquire_with_validity()
        if not acquired:
            raise RedLockError('failed to acquire lock')
        return validity

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()

    def locked(self):
        for node in self.redis_nodes:
            if node.get(self.resource):
                return True
        return False

    def acquire_node(self, node):
        """
        acquire a single redis node
        """
        try:
            ret = node.set(self.resource, self.lock_key, nx=True, px=self.ttl)
            if not ret and node.get(self.resource) == self.lock_key and not self.resource in RedLock._locked:
                ret = True
            return ret
        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError):
            return False

    def release_node(self, node):
        """
        release a single redis node
        """
        # use the lua script to release the lock in a safe way
        try:
            node._release_script(keys=[self.resource], args=[self.lock_key])
        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError):
            pass

    def acquire(self):
        acquired, validity = self._acquire()
        return acquired

    def acquire_with_validity(self):
        return self._acquire()


    def _acquire(self):
        for retry in range(self.retry_times + 1):
            acquired_node_count = 0
            start_time = monotonic()

            # acquire the lock in all the redis instances sequentially
            for node in self.redis_nodes:
                if self.acquire_node(node):
                    acquired_node_count += 1

            end_time = monotonic()
            elapsed_milliseconds = (end_time - start_time) * 10**3
            # Add 2 milliseconds to the drift to account for Redis expires
            # precision, which is 1 milliescond, plus 1 millisecond min drift
            # for small TTLs.
            drift = (self.ttl * CLOCK_DRIFT_FACTOR) + 2
            validity = self.ttl - (elapsed_milliseconds + drift)
            if acquired_node_count >= self.quorum and validity > 0:
                self._released = False
                RedLock._locked[self.resource] = self.lock_key
                return True, validity
            else:
                for node in self.redis_nodes:
                    self.release_node(node)
                time.sleep(random.randint(0, self.retry_delay) / 1000)
        return False, 0

    def release(self):
        if self._released :
            return False
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        for node in self.redis_nodes:
            self.release_node(node)
            if self.resource in RedLock._locked:
                del RedLock._locked[self.resource]
        self._released = True
        return self._released

class ReentrantRedLock(RedLock):
    def __init__(self, *args, **kwargs):
        super(ReentrantRedLock, self).__init__(*args, **kwargs)
        self._acquired = 0

    def acquire(self):
        if self._acquired == 0:
            result = super(ReentrantRedLock, self).acquire()
            if result:
                self._acquired += 1
            return result
        else:
            self._acquired += 1
            return True

    def release(self):
        if self._acquired > 0:
            self._acquired -= 1
            if self._acquired == 0:
                return super(ReentrantRedLock, self).release()
            return True
        return False




class DistLock(object):
    """
    A distributed lock implementation based on Hazelcast.
    It shares a similar API with the `threading.Lock` class in the
    Python Standard Library.
    """
    hz_lock = None
    lock_name = None
    timeout = -1
    _locked  = False
    def __init__(self, hz_client, lockname, timeout = -1):

        try:
            self.hz_lock   = hz_client.get_lock(lockname).blocking()
        except Exception as e:
            print  e
            exit()

        self.timeout   = timeout

    def lock(self):
        if not self.hz_lock:
            return False

        if self._locked:
            return True

        locked = False
        try:
            if self.hz_lock.is_locked_by_current_thread() == True :
                hz_lock.unlock()
            locked =  not self.hz_lock.is_locked()
            #print "is_locked" , not locked
            if locked:
                self.hz_lock.lock()
                locked = self.hz_lock.is_locked()
        except Exception as e:
            print e
            exit()

        self._locked = locked
        return locked

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            is_locked_by_current_thread = self.hz_lock.is_locked_by_current_thread()
            if self.hz_lock and is_locked_by_current_thread:
                self.hz_lock.unlock()
        except Exception as e:
            print e
            exit()


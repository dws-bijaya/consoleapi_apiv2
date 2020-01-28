#coding=utf8
import redis
import time
import json
#import mysql.connector
#from mysql.connector import conversion
#from pymongo import MongoClient
from django.conf import settings
class _Bloom_Filter:
	_redis_conn = None
	_redis_pool = None
	_logger      = None
	def test_case(self):
		oConn = SAConnections()
		_redis3_conn , errno, errmsg = oConn.redis3_conn()
		print(_redis3_conn[1].bloomfilter_create("test", 11, 0.001))
		print(_redis3_conn[1].bloomfilter_add("test", "bijaya"))
		print(_redis3_conn[1].bloomfilter_exists("test", "bijaya"))


	def __init__(self, _redis_conn, _redis_pool, _logger):
		self.redis_conn = _redis_conn
		self._redis_pool = _redis_pool
		self._logger    = _logger

	def _bloomfilter_execute(self, command, raw = False):
		if not self.redis_conn:
			return None
		try:
			response = self.redis_conn.execute_command(command.encode("utf-8"))
			if raw:
				return  response
			return response == 'OK' or int(response) == 1
		except Exception as e:
			self._logger.error("Error Occured while executing Bloom command {command}, Native Error ={error}".format(command=command, error=repr(e)))
			return None

	def bloomfilter_keys(self, regex):
		if not self.redis_conn:
			return None
		result = self.redis_conn.keys(regex)
		return result

	def bloomfilter_delete(self, keys):
		if not self.redis_conn:
			return False
		keys = [keys] if isinstance(keys, str) or isinstance(keys, basestring)  else keys
		result = (self.redis_conn.delete(*keys) if len(keys) else None)

	def bloomfilter_create(self, key, capacity, error_rate):
		if not capacity:
			return False
		if not error_rate:
			return False
		command = "BF.RESERVE {key} {error_rate} {capacity}".format(key=key, capacity=capacity, error_rate=error_rate)
		result = self._bloomfilter_execute(command)
		return False if result is None else result

	def bloomfilter_exists(self, key, data):
		command = "BF.EXISTS {key} {data}".format(key=key, data=data)
		result = self._bloomfilter_execute(command)
		return True if result is None else result

	def bloomfilter_mexists(self, key, data):
		data   = " ".join(data)
		command = "BF.MEXISTS {key} {data}".format(key=key, data=data)
		result = self._bloomfilter_execute(command, raw = True)
		return False    if result is None else result

	def bloomfilter_add(self, key, data):
		command = "BF.ADD {key} {data}".format(key=key, data=data)
		result = self._bloomfilter_execute(command)
		return False    if result is None else result

	def close(self):
		try:
			self.conn.close();
			self.context.term();
		except Exception as e:
			print(e)


class _Oracle_NoSQL_Db:
	conn = None
	context = None

	def __init__(self, _conn, _context):
		self.conn = _conn
		self.context = _context

	def close(self):
		try:
			self.conn.close();
			self.context.term();
		except Exception as e:
			print(e)

	def exec_query(self, qry):
		if not self.conn:
			return (False, 1, '-OK')

		try:
			self.conn.send(qry.encode())
			ret  = self.conn.recv()
			res  =  json.loads(ret)
			if  'errno' in res and 'errmsg' in res and res['errno']:
				return (False, res['errno'], res['errmsg'])
			return (res, 0, "+OK")
		except Exception as e:
			print(e)
			return (False, e.code if 'code' in e else e.errno if 'errno' in e else None, repr(e))

class CSAPI_Connections:
	redis_conn = None
	data_conn = None
	report_conn = None
	redis_pool  = None
	redis2_conn = None
	redis2_pool = None
	cassandra_conn = None
	hazelcast_conn = None
	_ocl_nosqldb_conn = None
	_rabitmq_conn = None

	_redis3_conn = None
	_redis3_pool = None

	_rabitmq2_conn = None

	def redis3_conn(self, db=0):
		if self._redis3_conn :
			return (self._redis3_conn, 0, '+OK');
		if not self._redis3_pool :
			self._redis3_pool = redis.ConnectionPool(host=settings['REDIS3_HOST'], port=settings['REDIS3_PORT'], db=db, password=settings['REDIS3_PASSWORD'])
		lsterr = {}
		for _ in range(2):
			try:
				self._redis3_conn = redis.Redis(connection_pool=self._redis3_pool)
				try:
					self._redis3_conn.info()
					bf = _Bloom_Filter(self._redis3_conn, self._redis3_pool, self.logger)
					self._redis3_conn = (self._redis3_conn, bf,)
					lsterr = {}
					break
				except Exception as  e:
					self.logger.error("Bloom Filter connection error, Native Error= {error}".format(error=repr(e)))
					lsterr = { "errno":  e.errno if 'errno' in e else 1, "errmsg": str(e)}
			except Exception as  e:
				lsterr = { "errno":  e.errno if 'errno' in e else 1, "errmsg": str(e)}
				pass
			time.sleep(0.5)
		else:
			self._redis3_conn = None
		return (self._redis3_conn, 0, '') if self._redis3_conn else (None, lsterr['errno'], lsterr['errmsg'])

	def rabitmq_conn(self):
		if self._rabitmq_conn:
			return (self._rabitmq_conn, 0, '+OK')

		import pika
		credentials = pika.PlainCredentials(settings['RABITMQ_SERVER_USER'], settings['RABITMQ_SERVER_PASSWORD'])
		lsterr = None
		for _ in range(5):
			try:
				connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings['RABITMQ_SERVER_HOST'], port=settings['RABITMQ_SERVER_PORT'], virtual_host=settings['RABITMQ_SERVER_VHOST'],  heartbeat_interval= 0, credentials=credentials, connection_attempts=5, retry_delay=1))
				channel = connection.channel()
				properties=pika.BasicProperties(content_type='application/json', delivery_mode= 2)
				# Turn on delivery confirmations
				channel.confirm_delivery()
				lsterr = None
				self._rabitmq_conn = (connection, channel, properties)
				break
			except Exception as e:
				self.logger.error("connection fialed, erorr = {}".format(repr(e)))
				lsterr = { "errno": e.errno if 'errno' in e else 1, "errmsg": repr(e)}
				time.sleep(1)

		return (self._rabitmq_conn, 0, '+OK', ) if lsterr is None else (self._rabitmq_conn, lsterr['errno'], lsterr['errmsg'], )

	def rabitmq2_conn(self):
		if self._rabitmq2_conn:
			return (self._rabitmq2_conn, 0, '+OK')

		from pyrabbit.api import Client
		lsterr = None
		for _ in range(5):
			try:
				client = Client('{host}:{port}'.format(host=settings['MSGQUEUE_SERVER_HOST'], port=settings['MSGQUEUE_SERVER_API_PORT']), settings['MSGQUEUE_SERVER_USER'], settings['MSGQUEUE_SERVER_PASSWORD'], timeout=settings['MSGQUEUE_SERVER_TIMEOUT'])
				self._rabitmq2_conn = client
				lsterr = None
				break
			except Exception as e:
				print(e)
				self.logger.error("connection fialed, erorr = {}".format(repr(e)))
				lsterr = { "errno": e.errno if 'errno' in e else 1, "errmsg": repr(e)}
				time.sleep(1)
		return (self._rabitmq2_conn, 0, '+OK', ) if lsterr is None else (self._rabitmq2_conn, lsterr['errno'], lsterr['errmsg'], )

	def ocl_nosqldb_conn(self):
		if self._ocl_nosqldb_conn:
			return (self._ocl_nosqldb_conn, 0, '+OK')

		import zmq
		context = zmq.Context.instance()
		socket = context.socket(zmq.REQ)
		socket.connect ("tcp://%s:%s" % (settings['ORACLE_NOSQLDB_HOST'], settings['ORACLE_NOSQLDB_PORT']))
		socket.setsockopt(zmq.RCVTIMEO, settings['ORACLE_NOSQLDB_RCVTIMEO'])

		lsterr = None
		try:
			socket.send("PING")
			pong = socket.recv()
			if "PONG" in pong:
				self._ocl_nosqldb_conn = _Oracle_NoSQL_Db(socket, context)
		except Exception as e:
			print (e, "2414124")
			lsterr = { "errno": e.errno if 'errno' in e else 1, "errmsg": repr(e)}

		return (self._ocl_nosqldb_conn, 0, '+OK', ) if lsterr is None else (self._ocl_nosqldb_conn, lsterr['errno'], lsterr['errmsg'], )

	def _hazelcast_conn(self):
		if self.hazelcast_conn:
			return (self.hazelcast_conn, 0, '+OK')

		import hazelcast
		config = hazelcast.ClientConfig()
		config.logger_config.level = 100  if settings['LOG_ENABLED'] == False  else (settings['HAZELCAST_LOGGER_LEVELS'][settings['LOG_LEVEL']] if settings['LOG_LEVEL'] in settings['HAZELCAST_LOGGER_LEVELS'] else settings['HAZELCAST_LOGGER_LEVELS']['NOTSET'] )
		[config.network_config.addresses.append(host) for host in settings['HAZELCAST_HOSTS'] ]
		lsterr = None
		for _ in range(2):
			try:
				client = hazelcast.HazelcastClient(config)
				self.hazelcast_conn = client
				lsterr = None
				break
			except Exception as e:
				lsterr = { "errno": e.errno if 'errno' in e else 1, "errmsg": repr(e)}
			time.sleep(0.5)



		return (self.hazelcast_conn, 0, '+OK', ) if lsterr is None else (self.hazelcast_conn, lsterr['errno'], lsterr['errmsg'], )

	def _cassandra_conn(self, db = None):
		from cassandra.cluster import Cluster
		db = db if db is not None else settings['CASSANDRA_DBS'][0]
		if self.cassandra_conn:
			self.cassandra_conn[1].set_keyspace(db)
			return self.cassandra_conn


		for _ in range(2):
			try:
				cluster = Cluster(settings['CASSANDRA_HOSTS'], port = settings['CASSANDRA_PORT'])
				session = cluster.connect()
				session.set_keyspace(db)
				self.cassandra_conn = [(cluster, session), 0, '']
				return	self.cassandra_conn
			except Exception as e:
				self.cassandra_conn = [(None,None), e.errno if 'errno' in e else 1,  repr(e)]
				#print(e)
			time.sleep(0.5)

		return self.cassandra_conn

	def _localmysql_conn(self, db = None):
		db = db if db is not None else settings['LOCALMYSQL_DBS'][0]
		if self.localmysql_conn:
			curs = None
			try:
				curs = self.localmysql_conn.cursor()
				curs.execute("USE {db};".format(db=db))
				self.localmysql_conn.commit()
			except Exception as e:
				pass
			return ( [curs, self.localmysql_conn]  , 0, '')


		lsterr = {}
		for _ in range(2):
			try:
				self.localmysql_conn = mysql.connector.connect(user=settings['LOCALMYSQL_USER'], password=settings['LOCALMYSQL_PASSWORD'], host=settings['LOCALMYSQL_HOST'], port=settings['LOCALMYSQL_PORT'], database=settings['LOCALMYSQL_DBS'][0])
				break
			except Exception as e:
				lsterr = { "errno": e.errno, "errmsg": str(e)}
				time.sleep(0.5)
		curs = None
		if self.localmysql_conn:
			try:
				curs = self.localmysql_conn.cursor()
				curs.execute("USE {db};".format(db=db))
				self.localmysql_conn.commit()
			except Exception as e:
				pass
		return ( [curs, self.localmysql_conn]  , 0, '') if curs else (None, lsterr['errno'], lsterr['errmsg'])

	def _remotemysql_conn(self, db = None):
		db = db if db is not None else settings['REMOTEMYSQL_DBS'][0]
		if self.remotemysql_conn:
			curs = None
			try:
				curs = self.remotemysql_conn.cursor()
				curs.execute("USE {db};".format(db=db))
				self.remotemysql_conn.commit()
			except Exception as e:
				pass
			return ( [curs, self.remotemysql_conn]  , 0, '')


		lsterr = {}
		for _ in range(2):
			try:
				self.remotemysql_conn = mysql.connector.connect(user=settings['REMOTEMYSQL_USER'], password=settings['REMOTEMYSQL_PASSWORD'], host=settings['REMOTEMYSQL_HOST'], port=settings['REMOTEMYSQL_PORT'], database=settings['REMOTEMYSQL_DBS'][0])
				break
			except Exception as e:
				lsterr = { "errno": e.errno, "errmsg": str(e)}
				time.sleep(0.5)

		curs = None
		if self.remotemysql_conn:
			try:
				curs = self.remotemysql_conn.cursor()
				curs.execute("USE {db};".format(db=db))
				self.remotemysql_conn.commit()
			except Exception as e:
				pass
		return ( [curs, self.remotemysql_conn]  , 0, '') if curs else (None, lsterr['errno'], lsterr['errmsg'])

	def _report_conn(self, db):
		if self.report_conn:
			return (self.report_conn[db], 0, '');

		lsterr = {}
		for _ in range(2):
			try:
				self.report_conn = MongoClient("{host}:{port}".format(host=settings['MONGO_REPORT_HOST'], port=settings['MONGO_REPORT_PORT']))
				lsterr = {}
				break
			except Exception as e:
				lsterr = { "errno":  e.errno if 'errno' in e else 1, "errmsg": str(e)}
			time.sleep(0.5)
		return (self.report_conn[db], 0, '') if self.report_conn else (None, lsterr['errno'], lsterr['errmsg'])

	nfs_conn = None
	def __del__(self):

		self._nfs_conn_close()
		if self.cassandra_conn:
			try:
				self.cassandra_conn[0][0].shutdown()
				time.sleep(1)
			except Exception as e:
				print(e)

		if self.hazelcast_conn:
			try:
				self.hazelcast_conn.shutdown()
			except Exception as e:
				print(e)

		if self._ocl_nosqldb_conn:
			self._ocl_nosqldb_conn.close()


	def _nfs_conn_close(self):
		if self.nfs_conn:
			self.nfs_conn[0].close()
			self.nfs_conn[1].term()
			self.nfs_conn =None

	def _nfs_conn(self, reset = False, close = False):
		import zmq

		if close:
			self._nfs_conn_close()
			return (self.nfs_conn, 0, '+OK');

		if self.nfs_conn and not reset:
			return (self.nfs_conn, 0, '+OK');

		if reset:
			self._nfs_conn_close()


		context = zmq.Context()
		socket = context.socket(zmq.REQ)
		socket.connect('tcp://{NFS_HOST}:{NFS_PORT}'.format(NFS_HOST=settings['NFS_HOST'], NFS_PORT=settings['NFS_PORT']))

		socket.setsockopt(zmq.RCVTIMEO, 1000)
		socket.setsockopt(zmq.SNDTIMEO, 1000)  # milliseconds
		socket.setsockopt(zmq.RECONNECT_IVL_MAX, 1000)
		socket.setsockopt(zmq.RECONNECT_IVL, 100)
		socket.setsockopt(zmq.LINGER, 0)
		self.nfs_conn = [socket, context, 0, 0]
		return (self.nfs_conn, 0, '+OK');


	def _redis_conn(self, db=0):
		if self.redis_conn:
			return (self.redis_conn, 0, '+OK');

		if not self.redis_pool :
			self.redis_pool = redis.ConnectionPool(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=db, password=settings.REDIS_PASSWORD)
		lsterr = {}
		for _ in range(2):
			try:
				self.redis_conn = redis.Redis(connection_pool=self.redis_pool)
				try:
					self.redis_conn.info()
					lsterr = {}
					break
				except redis.exceptions.ConnectionError as e:
					pass
					lsterr = { "errno":  e.errno if 'errno' in e else 1, "errmsg": str(e)}
			except Exception as e:
				lsterr = { "errno":  e.errno if 'errno' in e else 1, "errmsg": str(e)}
				pass
			time.sleep(0.5)
		else:
			self.redis_conn = None
		return (self.redis_conn, 0, '') if self.redis_conn else (None, lsterr['errno'], lsterr['errmsg'])


	def _redis2_conn(self, db=0):
		if self.redis2_conn :
			return (self.redis2_conn, 0, '+OK');
		if not self.redis2_pool :
			self.redis2_pool = redis.ConnectionPool(host=settings['REDIS2_HOST'], port=settings['REDIS2_PORT'], db=db, password=settings['REDIS2_PASSWORD'])
		lsterr = {}
		for _ in range(2):
			try:
				self.redis2_conn = redis.Redis(connection_pool=self.redis2_pool)
				try:
					self.redis2_conn.info()
					lsterr = {}
					break
				except Exception as e:
					self.logger.error("Bloom Filter connection error, Native Error= {error}".format(error=repr(e)))
					lsterr = { "errno":  e.errno if 'errno' in e else 1, "errmsg": str(e)}
			except Exception as e:
				lsterr = { "errno":  e.errno if 'errno' in e else 1, "errmsg": str(e)}
				pass
			time.sleep(0.5)
		else:
			self.redis2_conn = None
		return (self.redis2_conn, 0, '') if self.redis2_conn else (None, lsterr['errno'], lsterr['errmsg'])


	def _data_conn(self, db):
		if self.data_conn:
			return (self.data_conn[db], 0, '');

		lsterr = {}
		for _ in range(2):
			try:
				self.data_conn = MongoClient("{host}:{port}".format(host=settings['MONGO_DATA_HOST'], port=settings['MONGO_DATA_PORT']))
				lsterr = {}
				break
			except Exception as e:
				lsterr = { "errno":  e.errno if 'errno' in e else 1, "errmsg": str(e)}
			time.sleep(0.5)
		return (self.data_conn[db], 0, '') if self.data_conn else (None, lsterr['errno'], lsterr['errmsg'])


	def _mongo_conn(self, db):
		if self.mongo_conn:
			return (self.mongo_conn[db], 0, '');

		lsterr = {}
		for _ in range(2):
			try:
				self.mongo_conn = MongoClient("{host}:{port}".format(host=settings['MONGO_MASTER_HOST'], port=settings['MONGO_MASTER_PORT']))
				lsterr = {}
				break
			except Exception as e:
				lsterr = { "errno":  e.errno if 'errno' in e else 1, "errmsg": str(e)}
			time.sleep(0.5)
		return (self.mongo_conn[db], 0, '') if self.mongo_conn else (None, lsterr['errno'], lsterr['errmsg'])



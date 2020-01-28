from apiv2 import _redisconn
from django.http.response import JsonResponse, HttpResponse
import time
import re
import json
from django.conf import settings
import uuid
from urllib.parse import urlparse
import os
import subprocess
class ConsoleAPI(object):
	_start_time = None
	"""docstring for ConsoleAPI"""
	def __init__(self, arg):
		super(ConsoleAPI, self).__init__()
		self.arg = arg

	@classmethod
	def _apikey_keys(cls, apikey):
		return "{appname}:{apikey}:apikeys".format(appname=settings.APP_ID, apikey=apikey)

	@classmethod
	def _x_rate_limits_keys(cls, apikey):
		return "{appname}:{apikey}:x_rate_limits".format(appname=settings.APP_ID, apikey=apikey)


	@classmethod
	def xratelimit_validate(cls, apikey):
		if not _redisconn:
			return (False, settings.DEFAULT_X_LIMITS, 0, int(time.time()) + settings.DEFAULT_X_LIMITS_WINDOW)

		x_rate_limits_key = cls._x_rate_limits_keys(apikey)
		return cls._test_hits(x_rate_limits_key, settings.DEFAULT_X_LIMITS_WINDOW, settings.DEFAULT_X_LIMITS)

	@staticmethod
	def SSL_Response(url):
		Security = []
		domain = url['domain'] if 'domain' in url else None
		port = url['port'] if 'port' in url else None
		ssl = url['ssl'] if 'ssl' in url else None
		sslcert = None
		#
		if domain and port and ssl:
			ssl_cache = settings.SSL_CACHE_DIR + ("/%s:%s" %(domain, port)) + '.cache'				
			if os.path.isfile(ssl_cache):
				try:
					with open(ssl_cache, 'r') as sptr:
						sslcert = json.loads(sptr.read())
						sslcert['execution_time'] = 0.0
						return sslcert
				except Exception as e:
					print(e)

			cmd = settings.SSL_BIN_COMMAND.format(host=domain, port=port, servername=domain, timeout=1)			
			out = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]			
			try:
				sslcert = json.loads(out)
			except Exception as e:
				print(e)

		return sslcert


	@classmethod
	def Filter_Request_Url(cls, url):
		
		#
		if not url:
			return {"url":"", "method":"GET", "ssl": False, "port":80}

		method = None
		_method = re.match(r'^([A-Z]{3,})\s(.*)', url)
		if _method:
			req_val = { 'method': _method.group(1), 'url': _method.group(2)}
		else:
			url = "http://%s" % url if url.startswith("//") or not url.startswith('http') else url
		req_val = { 'method':'GET', 'url': url}
		req_val['domain'] = None
		req_val['ssl']    = False
		req_val['port']    = None			
		domain, ssl, port = cls.Find_Domain_SSL_Port(req_val['url'])
		#print(domain, ssl, port)
		req_val['ssl']    = ssl
		req_val['port']   = port
		req_val['domain'] = domain	

		return req_val

	@staticmethod
	def Find_Domain_SSL_Port(url):
		domain = None;  ssl = None ; port = None;
		try:
			up = urlparse(url)
			if up.scheme == 'https':
				ssl = True

			netlocs  = up.netloc.lower().rsplit("@")[-1].rsplit(":")			
			domain = netlocs[0]				
			if len(netlocs)>1:
				try:
					port = int(netlocs[1])
				except Exception as e:
					pass
			if  port is None:
				port = 433 if ssl else 80
		except Exception as e:
			print (e)
			pass
		return (domain, ssl, port)

	@staticmethod
	def new_response_General(Request_URL, Request_Method, Remote_Address, Status_Code, Error_Code, Version, Content_Length, Content_Type, Referrer_Policy):
		return {
			'Request_URL':Request_URL,
			'Request_Method':Request_Method,
			'Remote_Address':Remote_Address,
			'Status_Code':Status_Code,
			'Error_Code':Error_Code,
			'Version':Version,
			'Content_Length':Content_Length,
			'Content_Type':Content_Type,
			'Referrer_Policy':Referrer_Policy
		};		

	@staticmethod
	def new_response(General, Headers, Params, Cookies, Timings, Security):


		"""
			['General'] = [ 'Request_URL': 'givenurl', 'Request_Method': 'POST', 'Remote_Address' : '139.99.89.89:443', 'Status_Code': '503 Service Unavailable', 'Version': 'HTTP/2.0', 'Content_Length': 0, 'Content-Type': '', 'Referrer-Policy': ]
			['Headers'] = [ 'Response': [ 'Size': 100, "headers":[] ], 'Request': ['Size': 100, "headers":[] ] ]
			['Params']  = [ 'Query_String':[ 'Size': 10, 'Params':[]], 'Post_Data':['Szie':0, 'Params':[]]]
			['Cookies'] = [ 'Request_Cookie':[ 'Size': 10, 'Cookies':[]], 'Response':['Szie':0, 'Cookies':[]]]
			['Timings'] = [ 'Blocked': 0, 'DNS_Resolution':0, 'Connecting':0, 'TLS_Setup':0, 'Sending': 0, 'Waiting': 0, 'Receiving':0 ]
			['Security']= [ 'Connection': ['Protocol version': 'TLSv1.2', 'Cipher suite': 'TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256', 'Key Exchange Group':	x25519, 'Signature Scheme':	'RSA-PSS-SHA256' 'Certificate': ['Issued To':['Common Name (CN)':consoleapi.com, 'Organization (O)':<Not Available>, 'Organizational Unit (OU)':<Not Available>], 'Issued By' : ['Common Name (CN)':Let's Encrypt Authority X3',  'Organization (O)':'Let's Encrypt', 'Organizational Unit (OU)':<Not Available>] , 'Period of Validity':['Begins On':	Wednesday, December 18, 2019, 'Expires On':	Tuesday, March 17, 2020,], 'Fingerprints':['SHA-256 Fingerprint':27:3F:C8:9F:88:1C:80:25:23:1D:…A4:FD:B3:E9:57:14:C8:EE:BE:01, 'SHA1 Fingerprint':	49:31:5D:AA:5D:D9:96:07:22:9A:DE:BF:B1:3B:F2:30:E5:BE:9F:6A],'Transparency':[<Not Available>] ]]
		"""




	@staticmethod
	def _test_hits(x_rate_limits_key, window, xlimit):
		hits = None
		curr_time = None
		try:
			curr_time = _redisconn[0].time()
			expires   = curr_time[0] - window
			with _redisconn[0].pipeline() as pipe:
				pipe.watch(x_rate_limits_key)  # ---- LOCK
				pipe.multi()
				pipe.zremrangebyscore(x_rate_limits_key, '-inf', expires)
				pipe.zcard(x_rate_limits_key)
				v1, hits = pipe.execute()
				print(v1, hits)
				if hits>=xlimit:
					return (False, settings.DEFAULT_X_LIMITS, settings.DEFAULT_X_LIMITS - hits, curr_time[0] + settings.DEFAULT_X_LIMITS_WINDOW)

				pair = {'%s' % str(uuid.uuid4()) :curr_time[0] + window}
				pipe.multi()
				pipe.zadd(x_rate_limits_key, pair)
				pipe.execute()
				return (True, settings.DEFAULT_X_LIMITS, settings.DEFAULT_X_LIMITS - (hits+1), curr_time[0] + settings.DEFAULT_X_LIMITS_WINDOW)
		except Exception as e:
			print(e)

		return (False, settings.DEFAULT_X_LIMITS, 0 if hits is None else settings.DEFAULT_X_LIMITS - hits, curr_time[0] if curr_time is not None else int(time.time()) + settings.DEFAULT_X_LIMITS_WINDOW)








	@classmethod
	def key_is_valid(cls, apikey):
		if not _redisconn:
			return False
		#_redisconn[0].hset('ConsoleAPI:jaymi-0910-saymi-0512:apikeys', 'status', 1)
		try:
			return _redisconn[0].exists(cls._apikey_keys(apikey))
		except Exception as e:
			raise e
		return False

	@staticmethod
	def time_start(ret=False):
		if not ret:
			ConsoleAPI._start_time = time.time()

		return ConsoleAPI._start_time
	@staticmethod
	def time_end():
		elapsed_time = time.time() - ConsoleAPI.time_start(True)
		print (elapsed_time)

		return "%.2f (s)" %(elapsed_time) # time.strftime("%H:%M:%S", time.gmtime(elapsed_time))

	@staticmethod
	def json_base_response(errno, errmsg):
		return {
			'errno':errno,
			'errmsg':errmsg,
			'about':{
				'copyrights' : '2020 (c) ConsoleAPI.com.',
				'tooks' : ConsoleAPI.time_end(),
			},
			'data' : None
		}

	@staticmethod
	def json_response_options(options):
		response =  HttpResponse("", content_type="application/json")
		response.status_code = 200
		response["Access-Control-Allow-Methods"] = options
		return response

	@staticmethod
	def json_response(errno, data, pretty =False, xlimits =[]):
		json_data = ConsoleAPI.json_base_response(errno['ERRNO'], errno['ERRMSG'])
		json_data['data'] = data
		json_pretty = ConsoleAPI._pretty_json(json_data)
		response =  HttpResponse(json_pretty, content_type="application/json")
		response.status_code = errno['HTTP_CODE']
		if xlimits:
			response['X-RateLimit-Limit'] = xlimits[1]
			response['X-RateLimit-Remaining'] = xlimits[2]
			response['X-RateLimit-Reset'] = xlimits[3]
		return response

	@staticmethod
	def _pretty_json(jsondict, pretty = False, xlimits =[]):
		json_pretty = json.dumps(jsondict, sort_keys=True, indent=4, ensure_ascii=False) if pretty else json.dumps(jsondict, ensure_ascii=False)
		try:
			json_pretty = json_pretty.encode('utf8')
		except Exception as e:
			print(e)



		return json_pretty

	@staticmethod
	def throw_error(errno, pretty =False, xlimits =[]):
		print(errno)
		json_pretty = ConsoleAPI.json_base_response(errno['ERRNO'], errno['ERRMSG'])
		json_pretty = json.dumps(json_pretty, sort_keys=True, indent=4) if pretty else json.dumps(json_pretty)
		response =  HttpResponse(json_pretty, content_type="application/json")
		response.status_code = errno['HTTP_CODE']
		if xlimits:
			response['X-RateLimit-Limit'] = xlimits[1]
			response['X-RateLimit-Remaining'] = xlimits[2]
			response['X-RateLimit-Reset'] = xlimits[3]
		return response
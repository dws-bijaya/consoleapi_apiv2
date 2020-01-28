from apiv2.classes.consoleapi import ConsoleAPI
from django.http.response import JsonResponse
from apiv2.classes.constants import *
from  django.views.generic.base import View
import time
#from django.http import HttpJsonResponse
class PingPong(View):
	"""docstring for PingPong"""
	def __init__(self, arg):
		super(PingPong, self).__init__()
		self.arg = arg

	@staticmethod
	def pong(request, apikey=None):
		pass


	@staticmethod
	def test(request, apikey=None):
		# https://curl.haxx.se/docs/caextract.html
		# echo | openssl s_client -connect stackoverflow.com:443 |& openssl x509  -fingerprint  -sha256  -noout -nocert -sha1
		# echo -n | openssl s_client -connect torproject.org:443 -CAfile /usr/share/ca-certificates/mozilla/DigiCert_Assured_ID_Root_CA.crt | sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' > ./torproject.pem
		pretty = request.META['HTTP_X_CSAPI_PRETTY']
		debug = request.META['HTTP_X_CSAPI_DEBUG']
		#print (ERR_CODE.HTTP_401)
		if not ConsoleAPI.key_is_valid(apikey):
			return ConsoleAPI.throw_error(ERR_CODE.HTTP_401, pretty)
		
		xlimits =  ConsoleAPI.xratelimit_validate(apikey)
		if xlimits[0] is False:
			return ConsoleAPI.throw_error(ERR_CODE.HTTP_429, pretty, xlimits = xlimits)


		requrl = request.META['HTTP_X_CSAPI_REQUEST_URL'] if 'HTTP_X_CSAPI_REQUEST_URL' in request.META else None
		Ssl_Response = ConsoleAPI.SSL_Response(requrl)
		#print(Ssl_Response)
		#
		#return ConsoleAPI.json_response(ERR_CODE.HTTP_200, "PONG", pretty, xlimits)
		#return ConsoleAPI.throw_error(ERR_CODE.HTTP_429, pretty, xlimits = xlimits)

		method = requrl['method'] if 'method' in requrl else 'GET'
		url    = requrl['url'] if 'url' in requrl else ""

		#
		_http_version = request.META['HTTP_X_CSAPI_HTTP_VERSION']
		http_version  = "--http1.0" if _http_version == 1.0 else "--http1.1" if _http_version == 1.1 else  "--http2" if _http_version == 2.0 else "--http2-prior-knowledge" if _http_version == "2P" else "--http1.0" 
		dns_servers="--dns-servers 8.8.8.8, 8.8.4.4, 208.67.222.222, 208.67.220.220, 209.244.0.3, 209.244.0.4"

		_ipv6 = request.META['HTTP_X_CSAPI_IPV6']
		ipv6  = '--ipv4' if _ipv6 == 4 else '--ipv6'


		include = '--include --fail --fail-early 
		pbar  = '-s'
		no_keepalive ="--no-keepalive"
		trace_time = '--trace-time'

		retry  = '--retry 0 --retry-delay 1 --retry-max-time 1'

		_timeout = request.META['HTTP_X_CSAPI_TIMEOUT']
		timeout  = '--max-time '+_timeout



		_sslverify = request.META['HTTP_X_CSAPI_SSL_VERIFIER']		
		sslverify  = '--k' if _sslverify else ""

		






		print(http_version)
		return ConsoleAPI.json_response(ERR_CODE.HTTP_200, "PONG", pretty, xlimits)



		#if not url:

			


		"""
			['General'] = [ 'Request_URL': 'givenurl', 'Request_Method': 'POST', 'Remote_Address' : '139.99.89.89:443', 'Status Code': '503 Service Unavailable', 'Version': 'HTTP/2.0', 'Content_Length': 0, 'Content-Type': '', 'Referrer-Policy': ]
			['Headers'] = [ 'Response': [ 'Size': 100, "headers":[] ], 'Request': ['Size': 100, "headers":[] ] ]
			['Params']  = [ 'Query_String':[ 'Size': 10, 'Params':[]], 'Post_Data':['Szie':0, 'Params':[]]]
			['Cookies'] = [ 'Request_Cookie':[ 'Size': 10, 'Cookies':[]], 'Response':['Szie':0, 'Cookies':[]]]
			['Timings'] = [ 'Blocked': 0, 'DNS_Resolution':0, 'Connecting':0, 'TLS_Setup':0, 'Sending': 0, 'Waiting': 0, 'Receiving':0 ]
			['Security']= [ 'Connection': ['Protocol version': 'TLSv1.2', 'Cipher suite': 'TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256', 'Key Exchange Group':	x25519, 'Signature Scheme':	'RSA-PSS-SHA256' 'Certificate': ['Issued To':['Common Name (CN)':consoleapi.com, 'Organization (O)':<Not Available>, 'Organizational Unit (OU)':<Not Available>], 'Issued By' : ['Common Name (CN)':Let's Encrypt Authority X3',  'Organization (O)':'Let's Encrypt', 'Organizational Unit (OU)':<Not Available>] , 'Period of Validity':['Begins On':	Wednesday, December 18, 2019, 'Expires On':	Tuesday, March 17, 2020,], 'Fingerprints':['SHA-256 Fingerprint':27:3F:C8:9F:88:1C:80:25:23:1D:…A4:FD:B3:E9:57:14:C8:EE:BE:01, 'SHA1 Fingerprint':	49:31:5D:AA:5D:D9:96:07:22:9A:DE:BF:B1:3B:F2:30:E5:BE:9F:6A],'Transparency':[<Not Available>] ]]


		HTTP/2.0 503 Service Unavailable
		date: Thu, 02 Jan 2020 13:58:10 GMT
		server: Apache/2.4.29 (Ubuntu)
		content-length: 386
		content-type: text/html; charset=iso-8859-1
		X-Firefox-Spdy: h2
		"""







		

		'''
		from django.conf import settings
		from apiv2 import _redisconn
		print (_redisconn)
		return None
		print(apikey)
		print(settings.REDIS_PASSWORD)
		'''

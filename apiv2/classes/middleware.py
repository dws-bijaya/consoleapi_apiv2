from django.utils.deprecation import MiddlewareMixin
from django.utils.cache import patch_vary_headers
from apiv2.classes.consoleapi import ConsoleAPI
from django.http.response import JsonResponse, HttpResponse
import time
from django.urls import resolve
from django.conf import settings
from corsheaders.conf import conf
from corsheaders.signals import check_request_enabled
import re
from urllib.parse import urlparse

ACCESS_CONTROL_ALLOW_ORIGIN = "Access-Control-Allow-Origin"
ACCESS_CONTROL_EXPOSE_HEADERS = "Access-Control-Expose-Headers"
ACCESS_CONTROL_ALLOW_CREDENTIALS = "Access-Control-Allow-Credentials"
ACCESS_CONTROL_ALLOW_HEADERS = "Access-Control-Allow-Headers"
ACCESS_CONTROL_ALLOW_METHODS = "Access-Control-Allow-Methods"
ACCESS_CONTROL_MAX_AGE = "Access-Control-Max-Age"

from corsheaders.middleware import CorsMiddleware

class RequestStartedMiddleware(MiddlewareMixin):

	def process_request(self, request):
		pretty = True if 'HTTP_X_CSAPI_PRETTY' in request.META and request.META['HTTP_X_CSAPI_PRETTY'].lower() in ['true', 'on', '1' ] else False
		request.META = request.META.copy()
		request.META['HTTP_X_CSAPI_PRETTY'] = pretty
		
		try:		
			view_func = resolve(request.META['PATH_INFO'])[0]
			app_label = view_func.__module__.rsplit('.', 1)[1]
			view_name = view_func.__name__
			methods = settings.ALLOW_EXPOSE_CORS_DATA[app_label][view_name]['METHODS']
			if methods:
				if getattr(request, "_CorsMiddleware", False) is False:
					self._CorsMiddleware = CorsMiddleware()

				response = self._CorsMiddleware.process_request(request)
				if response and request.method == "OPTIONS":
					response = self._CorsMiddleware.process_response(request, response)
					response[ACCESS_CONTROL_ALLOW_METHODS] = ", ".join(methods)
					try:
						headers = settings.ALLOW_EXPOSE_CORS_DATA[app_label][view_name]['EXPOSE_HEADERS']						
						if headers:
							response[ACCESS_CONTROL_EXPOSE_HEADERS] =  ", ".join(headers)
					except Exception as e:
						raise e


					try:
						headers = settings.ALLOW_EXPOSE_CORS_DATA[app_label][view_name]['ALLOW_HEADERS']						
						if headers:
							response[ACCESS_CONTROL_ALLOW_HEADERS] =  ", ".join(headers)
					except Exception as e:
						raise e
					response[ACCESS_CONTROL_ALLOW_HEADERS] = '*'
					response[ACCESS_CONTROL_EXPOSE_HEADERS] = []
					setattr(request, "_cors_enabled", False)
					return response
		except Exception as e:
			raise e
		

		
		request.META['_time'] = time.time()
		""" """
		req_key = 'HTTP_X_CSAPI_REQUEST_URL'
		req_val = None
		url     = request.META[req_key] if req_key in request.META else None
		req_val = ConsoleAPI.Filter_Request_Url(url)

		request.META[req_key] = req_val

		#
		req_key = 'HTTP_X_CSAPI_AUTHORIZATION'
		req_val     = request.META[req_key] if req_key in request.META else None
		if req_val:
			req_val = str(req_val)
		request.META[req_key] = req_val

		
		#
		req_key = 'HTTP_X_CSAPI_COOKIE'
		req_val     = request.META[req_key] if req_key in request.META else None
		if req_val:
			req_val = str(req_val)
		request.META[req_key] = req_val


		#
		req_key = 'HTTP_X_CSAPI_DEBUG'
		req_val     = request.META[req_key] if req_key in request.META else None
		req_val = True if req_val in ['true', 'on', '1', 'yes' ] else False
		request.META[req_key] = req_val

		#
		req_key = 'HTTP_X_CSAPI_FOLLOW_REDIRECTION'
		req_val     = request.META[req_key] if req_key in request.META else None
		req_val = True if req_val in ['true', 'on', '1', 'yes' ] else False
		request.META[req_key] = req_val

		#
		req_key = 'HTTP_X_CSAPI_HTTP_VERSION'
		req_val     = request.META[req_key] if req_key in request.META else None
		req_val = 1.0 if req_val in ['1', '1.0'] else ( 1.1 if req_val in ['1.1'] else 2.0 if req_val in ['2', '2.0'] else "2P" if  req_val in ['2p', '2P'] else 1.1)
		request.META[req_key] = req_val

		#
		req_key = 'HTTP_X_CSAPI_IPV6'
		req_val     = request.META[req_key] if req_key in request.META else None
		req_val = 6 if req_val in ['6'] else 4
		request.META[req_key] = req_val

		#
		req_key = 'HTTP_X_CSAPI_PRETTY'
		req_val     = request.META[req_key] if req_key in request.META else None
		req_val = True if req_val in ['true', 'on', '1', 'yes' ] else False
		request.META[req_key] = req_val

		
		#
		req_key = 'HTTP_X_CSAPI_REFERER'
		req_val     = request.META[req_key] if req_key in request.META else None		
		request.META[req_key] = req_val


		#
		req_key = 'HTTP_X_CSAPI_PROXY'
		req_val     = request.META[req_key] if req_key in request.META else None
		if req_val:
			pu = urlparse(req_val)
			scheme = pu.scheme
			netloc = pu.netloc
			if not netloc:
				req_val = None
			else:
				scheme   = 'https' if 'https' in scheme else ('http1.0' if 'http1.0' in scheme else ('http' if 'http' in scheme else ('socks4a' if 'socks4a' in scheme else ('socks4' if 'socks4' in scheme else ('socks5' if 'socks5' in scheme else 'socks5_hostname' if 'socks5_hostname' in scheme else 'http')))))
				netlocs  =  netloc.rsplit("@")
				userpass = netlocs[0] if len(netlocs)>1 else None
				netloc   = netlocs[1] if len(netlocs)>1 else netlocs[0]
				netlocs  = netloc.rsplit(":")
				netloc   = netlocs[0] 
				port     = netlocs[1] if len(netlocs)>1 else None
				username = None
				password = None
				if userpass:
					userpasss = userpass.split(":")
					username  = userpasss[0]
					password  = userpasss[1] if len(userpasss[0])>1 else None

				req_val = {'ip':netloc, 'port':port, 'scheme':scheme, 'username':username, 'password':password}
			request.META[req_key] = req_val
		

		#
		req_key = 'HTTP_X_CSAPI_SSL_VERIFIER'
		req_val     = request.META[req_key] if req_key in request.META else None		
		req_val = True if req_val in ['true', 'on', '1', 'yes' ] else False
		request.META[req_key] = req_val

		#
		req_key = 'HTTP_X_CSAPI_USER_AGENT'
		req_val     = request.META[req_key] if req_key in request.META else None		
		request.META[req_key] = req_val


		#
		req_key = 'HTTP_X_CSAPI_ACCEPT_LANGUAGE'
		req_val     = request.META[req_key] if req_key in request.META else None		
		request.META[req_key] = req_val

		#
		req_key = 'HTTP_X_CSAPI_ACCEPT_ENCODING'
		req_val     = request.META[req_key] if req_key in request.META else None		
		request.META[req_key] = req_val
		

		
		#
		req_key = 'HTTP_X_CSAPI_ACCEPT'
		req_val     = request.META[req_key] if req_key in request.META else None		
		request.META[req_key] = req_val
		


		#
		req_key = 'HTTP_X_CSAPI_TIMEOUT'
		req_val     = request.META[req_key] if req_key in request.META else None
		if req_val:
			try:
				req_val = int(req_val)
				req_val = 60 if req_val >60 else req_val
			except Exception as e:
				req_val = 60
		request.META[req_key] = req_val

		"""  Extra Headers """
		req_key = 'HTTP_X_CSAPI_XHEADERS'
		req_val = []
		for meta in request.META:
			xmatch = re.match(r'^(HTTP_X_CSAPI_(.*))', meta)
			if xmatch:
				xmkey = xmatch.group(2)				
				if xmkey not in ['XHEADERS', 'TIMEOUT', 'SSL_VERIFIER', 'USER_AGENT', 'REQUEST_URL', 'PROXY', 'REFERER', 'PRETTY', 'IPV6', 'HTTP_VERSION', 'FOLLOW_REDIRECTION', 'DEBUG', 'ACCEPT', 'ACCEPT_ENCODING', 'ACCEPT_LANGUAGE']:
					req_val.append({ xmkey.lower().replace('_', '-').title() :request.META[ xmatch.group(0)]})


		request.META[req_key] = req_val
		print(request.META['HTTP_X_CSAPI_XHEADERS'])
		print(request.META['HTTP_X_CSAPI_TIMEOUT'])
		print(request.META['HTTP_X_CSAPI_SSL_VERIFIER'])
		print(request.META['HTTP_X_CSAPI_PROXY'])
		print(request.META['HTTP_X_CSAPI_PRETTY'])
		print(request.META['HTTP_X_CSAPI_IPV6'])
		print(request.META['HTTP_X_CSAPI_HTTP_VERSION'])
		print(request.META['HTTP_X_CSAPI_DEBUG'])
		print(request.META['HTTP_X_CSAPI_FOLLOW_REDIRECTION'])
		print(request.META['HTTP_X_CSAPI_COOKIE'])
		print(request.META['HTTP_X_CSAPI_AUTHORIZATION'])
		print(request.META['HTTP_X_CSAPI_COOKIE'])
		print(request.META['HTTP_X_CSAPI_REQUEST_URL'])
		print(request.META['HTTP_X_CSAPI_USER_AGENT'])
		print(request.META['HTTP_X_CSAPI_ACCEPT_LANGUAGE'])
		print(request.META['HTTP_X_CSAPI_ACCEPT_ENCODING'])
		print(request.META['HTTP_X_CSAPI_ACCEPT'])
		return None

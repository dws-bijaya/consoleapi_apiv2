#!/bin/bash
# curl --tlsv1.3 https://enabled.tls13.com/
#https://www.howsmyssl.com/a/check
tmpdir=/home/consoleapi/public_html/apiv2/tmp
curlbin=/home/consoleapi/curl/bin/curl
domain=$1
port=$2
get=$3
url=$4
sllverify=$5
sslversion=$6
followlocation=$7
headers=@$tmpdir/$8.hdrs
postdata=@$tmpdir/$8.post
postredir=$9
h100_continue="--expect100-timeout ${10}"
if [[ "$sslversion" == "tlsv1.3" ]]; then
	curlbin=/usr/bin/curl
fi

if [[ "$sslversion" != "" ]]; then
	sslversion="--${sslversion}"
fi

if [[ "$followlocation" != "0" ]]; then
	followlocation=" -L --max-redirs $followlocation"
else
	followlocation=""
fi

tracefile=${tmpdir}/${domain}:${port}.trace
outputfile=${tmpdir}/${domain}:${port}.out
dumpheaderfile=${tmpdir}/${domain}:${port}.headers
errfile=${tmpdir}/${domain}:${port}.error
summaryfile=${tmpdir}/${domain}:${port}.summary
maxtimeout=100
debug=1

if [[ "POST PUT" == *$get* ]]; then
  echo '' 1> /dev/null
  postdata=" --data ${postdata}"
else
  postdata=""
fi



if [[ $postredir != "" ]]; then 
	export IFS=";"	
	postredirs=$postredir
	postredir=
	for dircode in $postredirs; do
  		postredir="$postredir ---post30${dircode}"
	done	
fi
#echo $followlocation  $get $postredir
#exit 1

if [[ $get == 'HEAD' ]]
then
	get='--head'
	maxtimeout=5
else
	get="-X ${get}"
fi

if [[ "$sllverify" == "1" ]]; then
	 sllverify='-k'
fi

if [[ $debug -eq 1 ]]; then 
	echo $sllverify
fi


tr_encoding="--tr-encoding"
options="$get ${url} -sv --tcp-fastopen --tcp-nodelay --trace-time --trace-ascii ${tracefile} --output ${outputfile} --stderr $errfile --show-error --max-time ${maxtimeout} --retry-max-time 1 --connect-timeout 1 --expect100-timeout 1  --max-filesize 5551024000  --dump-header ${dumpheaderfile} --no-keepalive --no-buffer --no-sessionid  --proto =http,https"
options2="--write-out \"time_total=||%{time_total}||\ncontent_type=||%{content_type}||\nurl_effective=||%{url_effective}||\ntime_starttransfer=||%{time_starttransfer}||\ntime_redirect=||%{time_redirect}||\ntime_pretransfer=||%{time_pretransfer}||\ntime_namelookup=||%{time_namelookup}||\ntime_connect=||%{time_connect}||\ntime_appconnect=||%{time_appconnect}||\nssl_verify_result=||%{ssl_verify_result}||\nsize_upload=||%{size_upload}||\nsize_request=||%{size_request}||\nsize_header=||%{size_header}||\nsize_download=||%{size_download}||\nscheme=||%{scheme}||\nremote_ip=||%{remote_ip}||\nremote_port=||%{remote_port}||\nredirect_url=||%{redirect_url}||\nlocal_port=||%{local_port}||\nlocal_ip=||%{local_ip}||\nhttp_version=||%{http_version}||\nhttp_connect=||%{http_connect}||\nhttp_code=||%{http_code}||\n\" "
#--post301 --post302 --post303


curlcmd="${curlbin}  $options --header $headers $postdata -L --ssl $sllverify $sslversion --limit-rate 1M $options2 $h100_continue 1>$summaryfile  2>/dev/null"

if [[ $debug -eq 1 ]]; then 
	echo $curlcmd;
fi
#postdata="-F user=user1&password"
#echo "$curlbin $options"
su - root -s /bin/sh -c "${curlcmd}"
#-F 'data=@/home/consoleapi/openssl-1.0.2o.tar.gz'
errno=$(($? + 0))
#echo $erno
#exit 1
#erno=0

declare -A CURLERRORS
CURLERRORS[-1]=CURLE_UNKONWN
CURLERRORS[0]=CURLE_OK
CURLERRORS[1]=CURLE_UNSUPPORTED_PROTOCOL
CURLERRORS[2]=CURLE_FAILED_INIT 
CURLERRORS[3]=CURLE_URL_MALFORMAT
CURLERRORS[4]=CURLE_NOT_BUILT_IN 
CURLERRORS[5]=CURLE_COULDNT_RESOLVE_PROXY
CURLERRORS[6]=CURLE_COULDNT_RESOLVE_HOST  
CURLERRORS[7]=CURLE_COULDNT_CONNECT  
CURLERRORS[8]=CURLE_WEIRD_SERVER_REPLY  
CURLERRORS[10]=CURLE_FTP_ACCEPT_FAILED  
CURLERRORS[11]=CURLE_FTP_WEIRD_PASS_REPLY  
CURLERRORS[12]=CURLE_FTP_ACCEPT_TIMEOUT  
CURLERRORS[13]=CURLE_FTP_WEIRD_PASV_REPLY  
CURLERRORS[14]=CURLE_FTP_WEIRD_227_FORMAT  
CURLERRORS[15]=CURLE_FTP_CANT_GET_HOST  
CURLERRORS[16]=CURLE_HTTP2  
CURLERRORS[17]=CURLE_FTP_COULDNT_SET_TYPE  
CURLERRORS[18]=CURLE_PARTIAL_FILE  
CURLERRORS[19]=CURLE_FTP_COULDNT_RETR_FILE
CURLERRORS[20]=
CURLERRORS[21]=CURLE_QUOTE_ERROR
CURLERRORS[22]=CURLE_HTTP_RETURNED_ERROR
CURLERRORS[23]=CURLE_WRITE_ERROR
CURLERRORS[24]=
CURLERRORS[25]=CURLE_UPLOAD_FAILED
CURLERRORS[26]=CURLE_READ_ERROR
CURLERRORS[27]=CURLE_OUT_OF_MEMORY
CURLERRORS[28]=CURLE_OPERATION_TIMEDOUT
CURLERRORS[29]=
CURLERRORS[30]=CURLE_FTP_PORT_FAILED
CURLERRORS[31]=CURLE_FTP_COULDNT_USE_REST
CURLERRORS[32]=
CURLERRORS[33]=CURLE_RANGE_ERROR
CURLERRORS[34]=URLE_HTTP_POST_ERROR
CURLERRORS[35]=CURLE_SSL_CONNECT_ERROR
CURLERRORS[36]=CURLE_BAD_DOWNLOAD_RESUME
CURLERRORS[37]=CURLE_FILE_COULDNT_READ_FILE
CURLERRORS[38]=CURLE_LDAP_CANNOT_BIND
CURLERRORS[39]=CURLE_LDAP_SEARCH_FAILED
CURLERRORS[40]=
CURLERRORS[41]=CURLE_FUNCTION_NOT_FOUND
CURLERRORS[42]=CURLE_ABORTED_BY_CALLBACK
CURLERRORS[43]=CURLE_BAD_FUNCTION_ARGUMENT
CURLERRORS[44]=
CURLERRORS[45]=CURLE_INTERFACE_FAILED
CURLERRORS[46]=
CURLERRORS[47]=CURLE_TOO_MANY_REDIRECTS
CURLERRORS[48]=CURLE_UNKNOWN_OPTION
CURLERRORS[49]=CURLE_TELNET_OPTION_SYNTAX
CURLERRORS[50]=
CURLERRORS[51]=
CURLERRORS[52]=CURLE_GOT_NOTHING
CURLERRORS[53]=CURLE_SSL_ENGINE_NOTFOUND
CURLERRORS[54]=CURLE_SSL_ENGINE_SETFAILED
CURLERRORS[55]=CURLE_SEND_ERROR
CURLERRORS[56]=CURLE_RECV_ERROR
CURLERRORS[57]=
CURLERRORS[58]=CURLE_SSL_CERTPROBLEM
CURLERRORS[59]=CURLE_SSL_CIPHER
CURLERRORS[60]=CURLE_PEER_FAILED_VERIFICATION
CURLERRORS[61]=CURLE_BAD_CONTENT_ENCODING
CURLERRORS[62]=CURLE_LDAP_INVALID_URL
CURLERRORS[63]=CURLE_FILESIZE_EXCEEDED
CURLERRORS[64]=CURLE_USE_SSL_FAILED
CURLERRORS[65]=CURLE_SEND_FAIL_REWIND
CURLERRORS[66]=CURLE_SSL_ENGINE_INITFAILED
CURLERRORS[67]=CURLE_LOGIN_DENIED
CURLERRORS[68]=CURLE_TFTP_NOTFOUND
CURLERRORS[69]=CURLE_TFTP_PERM
CURLERRORS[70]=CURLE_REMOTE_DISK_FULL
CURLERRORS[71]=CURLE_TFTP_ILLEGAL
CURLERRORS[72]=CURLE_TFTP_UNKNOWNID
CURLERRORS[73]=CURLE_REMOTE_FILE_EXISTS
CURLERRORS[74]=CURLE_TFTP_NOSUCHUSER
CURLERRORS[75]=CURLE_CONV_FAILED
CURLERRORS[76]=CURLE_CONV_REQD
CURLERRORS[77]=CURLE_SSL_CACERT_BADFILE
CURLERRORS[78]=CURLE_REMOTE_FILE_NOT_FOUND
CURLERRORS[79]=CURLE_SSH
CURLERRORS[80]=CURLE_SSL_SHUTDOWN_FAILED
CURLERRORS[81]=CURLE_AGAIN
CURLERRORS[82]=CURLE_SSL_CRL_BADFILE
CURLERRORS[83]=CURLE_SSL_ISSUER_ERROR
CURLERRORS[84]=CURLE_FTP_PRET_FAILED
CURLERRORS[85]=CURLE_RTSP_CSEQ_ERROR
CURLERRORS[86]=CURLE_RTSP_SESSION_ERROR
CURLERRORS[87]=CURLE_FTP_BAD_FILE_LIST
CURLERRORS[88]=CURLE_CHUNK_FAILED
CURLERRORS[89]=CURLE_NO_CONNECTION_AVAILABLE
CURLERRORS[90]=CURLE_SSL_PINNEDPUBKEYNOTMATCH
CURLERRORS[91]=CURLE_SSL_INVALIDCERTSTATUS
CURLERRORS[92]=CURLE_HTTP2_STREAM
CURLERRORS[93]=CURLE_RECURSIVE_API_CALL
CURLERRORS[94]=CURLE_AUTH_ERROR
CURLERRORS[95]=CURLE_HTTP3
if [[ $errno -ne 0  ]]
then
	regex='curl: \(([[:digit:]]+)\) (.[^:]*): (.*)'
	errcode=-1
	errsmsg="Uknown"
	errlmsg="Uknown"
	errcmsg="Uknown"
	errcurl=$(cat $errfile 2>/dev/null)
	if [[ $errcurl =~ $regex ]]; then
		errcode=${BASH_REMATCH[1]}
		errsmsg=${BASH_REMATCH[2]}
		errlmsg=${BASH_REMATCH[3]}
	else
		regex='curl: \(([[:digit:]]+)\) (.*)'
		if [[  $errcurl =~ $regex ]]; then 
			errcode=${BASH_REMATCH[1]}
			errsmsg=${BASH_REMATCH[2]}
			errlmsg=${BASH_REMATCH[2]}
		fi
	fi
	errcurl=
	errcmsg=${CURLERRORS[$errcode]}	

	errlmsg=${errlmsg//\\/\\\\} # \ 
	errlmsg=${errlmsg//\//\\\/} # / 
	errlmsg=${errlmsg//\'/\\\'} # ' (not strictly needed ?)
	errlmsg=${errlmsg//\"/\\\"} # " 
	errlmsg=${errlmsg//   /\\t} # \t (tab)
	errlmsg=${errlmsg///\\\n} # \n (newline)
	errlmsg=${errlmsg//^M/\\\r} # \r (carriage return)
	errlmsg=${errlmsg//^L/\\\f} # \f (form feed)
	errlmsg=${errlmsg//^H/\\\b} # \b (backspace)
	echo \{\"errcode\":${errcode},\"errsmsg\":\"$errsmsg\",\"errlmsg\":\"$errlmsg\",\"errcmsg\":\"$errcmsg\"\}
	exit 1
fi

#https://netbeez.net/blog/http-transaction-timing-breakdown-with-curl/
summarydata=$(cat $summaryfile 2>/dev/null)

#tracedata=$(sed -e  '/^[[:xdigit:]][[:xdigit:]][[:xdigit:]][[:xdigit:]]: /d' < $tracefile)
##########[find time sending]=====================
time_receive=0.000000

s1=$(cat $tracefile 2>/dev/null | grep -zoP  "Recv header,(.*)\n0000: \n\d+:\d+:\d+.\d+ <= Recv (SSL )?data,"  2>/dev/null | tail -1  2>/dev/null |awk '{print $1}'  2>/dev/null)
s2=$(cat $tracefile 2>/dev/null | grep -oP  "\d+:\d+:\d+.\d+ <= Recv (SSL )?data,"  2>/dev/null | tail -1  2>/dev/null | awk '{print $1}'  2>/dev/null)
#s1=08:27:22.018146
#s2=13:28:35.036769
#s1=13:28:29.967425
#echo $s1 $s2
regex='^([[:digit:]]+):([[:digit:]]+):([[:digit:]]+)\.([[:digit:]]+)$'
if [[ $s1 =~ $regex ]]; then
	s1_h=$(echo ${BASH_REMATCH[1]} 2>/dev/null | sed -e 's/^[0]*//' 2>/dev/null)
	s1_m=$(echo ${BASH_REMATCH[2]} 2>/dev/null | sed -e 's/^[0]*//' 2>/dev/null)
	s1_s=$(echo ${BASH_REMATCH[3]} 2>/dev/null | sed -e 's/^[0]*//' 2>/dev/null)
	s1_p=${BASH_REMATCH[4]}
	#echo $s1 $s1_h $s1_m $s1_s $s1_p
	let "s1_h=$s1_h * 60 * 60"
	let "s1_m=$s1_m * 60"
	let "s1_s=$s1_s"
	s1_seconds=$(bc <<< "scale=6; $s1_h + $s1_m + $s1_s  + $s1_p / 1000000" 2>/dev/null | sed -e 's/^\./0\./' 2>/dev/null)
	#echo $s1_seconds matched
	if [[ $s2 =~ $regex ]]; then
		s2_h=$(echo ${BASH_REMATCH[1]} 2>/dev/null | sed -e 's/^[0]*//' 2>/dev/null)
		s2_m=$(echo ${BASH_REMATCH[2]} 2>/dev/null | sed -e 's/^[0]*//' 2>/dev/null)
		s2_s=$(echo ${BASH_REMATCH[3]} 2>/dev/null | sed -e 's/^[0]*//' 2>/dev/null)
		s2_p=${BASH_REMATCH[4]}
		let "s2_h=$s2_h * 60 * 60"
		let "s2_m=$s2_m * 60"
		let "s2_s=$s2_s"
		s2_seconds=$(bc 2> /dev/null <<< "scale=6; $s2_h + $s2_m + $s2_s  + $s2_p / 1000000 " 2>/dev/null)
		#echo $s2_seconds
		time_receive=$(bc 2> /dev/null <<< "scale=6; $s2_seconds - $s1_seconds " 2>/dev/null  | sed -e 's/^\./0\./' 2>/dev/null | sed -e 's/^0/0\.0000000/' 2>/dev/null | grep -xE '[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?' | head -1)
		if [[ $time_receive == "" ]]; then
			time_receive=0.0000000
		fi
	fi
fi
#========================================


time_namelookup=0.000000
time_connect=0.000000
time_appconnect=0.000000
time_pretransfer=0.000000
time_redirect=0.000000
time_starttransfer=0.000000
time_total=0.000000

regex='time_namelookup=\|\|(.[^\|]*)\|\|'
if [[ $summarydata =~ $regex ]]; then
	time_namelookup="${BASH_REMATCH[1]}"
fi

regex='time_connect=\|\|(.[^\|]*)\|\|'
if [[ $summarydata =~ $regex ]]; then
	time_connect="${BASH_REMATCH[1]}"
fi


regex='time_appconnect=\|\|(.[^\|]*)\|\|'
if [[ $summarydata =~ $regex ]]; then
	time_appconnect="${BASH_REMATCH[1]}"
fi


regex='time_pretransfer=\|\|(.[^\|]*)\|\|'
if [[ $summarydata =~ $regex ]]; then
	time_pretransfer="${BASH_REMATCH[1]}"
fi


regex='time_redirect=\|\|(.[^\|]*)\|\|'
if [[ $summarydata =~ $regex ]]; then
	time_redirect="${BASH_REMATCH[1]}"
fi


regex='time_starttransfer=\|\|(.[^\|]*)\|\|'
if [[ $summarydata =~ $regex ]]; then
	time_starttransfer="${BASH_REMATCH[1]}"
fi

regex='time_total=\|\|(.[^\|]*)\|\|'
if [[ $summarydata =~ $regex ]]; then
	time_total="${BASH_REMATCH[1]}"
fi

time_receive=$(bc <<< "scale=6; $time_total - $time_starttransfer" 2>/dev/null)
time_sending=$(bc <<< "scale=6; $time_total - ($time_namelookup + $time_connect + $time_appconnect + $time_redirect + $time_pretransfer + $time_starttransfer)" 2>/dev/null)


remote_ip=null
regex='remote_ip=\|\|(.[^\|]*)\|\|'
if [[ $summarydata =~ $regex ]]; then
	remote_ip="${BASH_REMATCH[1]}"
fi

remote_port=null
regex='remote_port=\|\|(.[^\|]*)\|\|'
if [[ $summarydata =~ $regex ]]; then
	remote_port=\"${BASH_REMATCH[1]}\"
fi

local_ip=null
regex='local_ip=\|\|(.[^\|]*)\|\|'
if [[ $summarydata =~ $regex ]]; then
	local_ip=\"${BASH_REMATCH[1]}\"
fi
local_port=null
regex='local_port=\|\|(.[^\|]*)\|\|'
if [[ $summarydata =~ $regex ]]; then
	local_port="${BASH_REMATCH[1]}"
fi


scheme=null
regex='scheme=\|\|(.[^\|]*)\|\|'
if [[ $summarydata =~ $regex ]]; then
	scheme="${BASH_REMATCH[1]}"
fi


http_version=null
regex='http_version=\|\|(.[^\|]*)\|\|'
if [[ $summarydata =~ $regex ]]; then
	http_version="${BASH_REMATCH[1]}"
fi



http_code=null
regex='http_code=\|\|(.[^\|]*)\|\|'
if [[ $summarydata =~ $regex ]]; then
	http_code="${BASH_REMATCH[1]}"
fi



content_type=null
regex='content_type=\|\|(.[^\|]*)\|\|'
if [[ $summarydata =~ $regex ]]; then
	content_type="${BASH_REMATCH[1]}"
fi


ssl_verify_result=null
regex='ssl_verify_result=\|\|(.[^\|]*)\|\|'
if [[ $summarydata =~ $regex ]]; then
	ssl_verify_result="${BASH_REMATCH[1]}"
fi


if [[ $debug -eq 1 ]]; then 
	echo "ssl_verify_result=$ssl_verify_result,"
	echo "time_receive=$time_receive, time_sending=$time_sending, time_namelookup=$time_namelookup, time_connect=$time_connect, time_appconnect=$time_appconnect, time_pretransfer=$time_pretransfer,  time_starttransfer=$time_starttransfer, time_redirect=$time_redirect,  time_total=$time_total"
	echo "Local IP=$local_ip, Local PORT=$local_port, Remote IP=$remote_ip, Remote PORT=$remote_port, "
	echo "Sheme IP=$scheme,"
	echo "HTTp Version=$http_version,"	
	echo "HTTp Code=$http_code,"
	echo "Content Type=$content_type,"
fi


cat $outputfile 2> /dev/null
exit 1







# Find HTTP Status & Status Message i,e 200 OK







echo $erno
#/home/consoleapi/curl/bin/curl  -X GET --url http://consoleapi.com -sv --tr-encoding --compressed  --raw -L --tcp-fastopen --suppress-connect-headers --stderr  --show-error --max-time 10 --retry-max-time 1 --connect-timeout 1 --expect100-timeout 1 --max-time 10 --trace-ascii /home/consoleapi/public_html/apiv2/tmp/consoleapi.com:443.trace --output /home/consoleapi/public_html/apiv2/tmp/consoleapi.com:443.out --max-filesize 1024000 --max-redirs 5 --dump-header /home/consoleapi/public_html/apiv2/tmp/consoleapi.com:443.headers --no-keepalive --no-buffer --no-sessionid --post301 --post302 --post303 --proto =http,https
#/home/consoleapi/curl/bin/curl  --url https://api.ipify.org -s --show-error --max-time 10 --retry-max-time 0 --connect-timeout 1 --expect100-timeout 1 --max-time 10 --trace-ascii /home/consoleapi/public_html/apiv2/tmp/api.ipify.org:443.trace --output hB --max-filesize 1024000 --max-redirs 5 --dump-header /home/consoleapi/public_html/apiv2/tmp/api.ipify.org:443.headers --ignore-content-length --verbose --no-keepalive --no-buffer --no-sessionid --post301 --post302 --post303 --proto =http,https
#http://ifconfig.me
#http://www.icanhazip.com
#http://ipecho.net/plain
#http://indent.me
#http://bot.whatismyipaddress.com
#https://diagnostic.opendns.com/myip
#http://checkip.amazonaws.com

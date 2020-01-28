#!/usr/bin/env bash -e
pem=/home/consoleapi/public_html/apiv2/tmp/cache/$3:$2.pem
cert=/home/consoleapi/public_html/apiv2/cacert.pem
cache=/home/consoleapi/public_html/apiv2/tmp/cache/ssl/$3:$2.cache
openssl=/home/consoleapi/openssl/bin/openssl
start=$(date +%s.%N)
/usr/bin/timeout $4 $openssl s_client -connect $1:$2 -servername $3 -CAfile $cert 2> /dev/null 1>$pem  < /dev/null
errno=$?
duration=$(echo "$(date +%s.%N) - $start" | bc)
execution_time=`printf "%.3f" $duration`
if [[ $errno == 0 ]]
then
	sha256=$($openssl x509 -noout -in $pem   -fingerprint  -sha256  -noout)
	if [[ $sha256 =~ "SHA256 Fingerprint=" ]]
	then
		sha1=$($openssl x509 -noout -in $pem   -fingerprint  -sha1  -noout)
		pinmd5=$($openssl x509 -noout -in $pem  -pubkey -pubkey -noout | $openssl pkey -pubin -outform der | $openssl dgst -sha256 -binary | $openssl enc -base64)
		subject=$($openssl x509 -noout -in $pem   -subject  -noout)
		issuer=$($openssl x509 -noout -in $pem   -issuer  -noout)
		startdate=$($openssl x509 -noout -in $pem   -startdate  -noout)
		enddate=$($openssl x509 -noout -in $pem   -enddate  -noout)	
		cert=$(cat $pem)
		#
		rm -rf $pem 2 > /dev/null 1> /dev/null

		sha1="\"${sha1/SHA1 Fingerprint=/}\""
		sha256="\"${sha256/SHA256 Fingerprint=/}\""
		startdate="\"${startdate/notBefore=/}\""
		enddate="\"${enddate/notAfter=/}\""
		regex='OU=(.[^/]*)'
		sub_ou="null"
		if [[ $subject =~ $regex ]]; then
	  		sub_ou="\"${BASH_REMATCH[1]}\""
		fi
		sub_o="null"
		regex='O=(.[^/]*)'
		if [[ $subject =~ $regex ]]; then
	  		sub_o="\"${BASH_REMATCH[1]}\""
		fi
		sub_cn="null"
		regex='CN=(.[^/]*)'
		if [[ $subject =~ $regex ]]; then
	  		sub_cn="\"${BASH_REMATCH[1]}\""
		fi


		regex='OU=(.[^/]*)'
		iss_ou="null"
		if [[ $issuer =~ $regex ]]; then
	  		iss_ou="\"${BASH_REMATCH[1]}\""
		fi
		iss_o="null"
		regex='O=(.[^/]*)'
		if [[ $issuer =~ $regex ]]; then
	  		iss_o="\"${BASH_REMATCH[1]}\""
		fi
		iss_cn="null"
		regex='CN=(.[^/]*)'
		if [[ $issuer =~ $regex ]]; then
	  		iss_cn="\"${BASH_REMATCH[1]}\""
		fi
		pinmd5="\"$pinmd5\""
		Protocolversion="null"
		Ciphersuite="null"
		regex=' (.[^,]*), Cipher is ([A-Z0-9-]+)'
		
		if [[ $cert =~ $regex ]]; then
	  		Protocolversion="\"${BASH_REMATCH[1]}\""
	  		Ciphersuite="\"${BASH_REMATCH[2]}\""
	  		#echo "eeeeeeeeeeee" $iss_cn
		fi
		#TLSv1.2, Cipher is ECDHE-RSA-AES128-GCM-SHA256
		json="{\"execution_time\":$execution_time, \"PinnedMD5\":$pinmd5, \"Connection\":{\"Protocol_version\":$Protocolversion,\"Cipher_suite\":$Ciphersuite,\"Key_Exchange_Group\":null,\"Signature Scheme\":null},\"Certificate\":{\"Issued_To\":{\"cn\":${sub_cn},\"ou\":${sub_ou},\"o\":${sub_o}}, \"Issued_By\":{\"cn\":${iss_cn},\"ou\":${iss_ou},\"o\":${iss_o}}}, \"Period_of_Validity\":{\"Begins_On\":$startdate,\"Expires_On\":$enddate}, \"Transparency\":null, \"Fingerprints\":{\"SHA-256_Fingerprint\":$sha256,\"SHA1_Fingerprint\":$sha1}, \"Host\":{\"HTTP_Strict_Transport_Security\":false, \"Public_Key_Pinning\":false}}"
		echo $json > $cache
		echo $json
		exit 0

	fi
fi
json="{}"
echo $json
exit 1
#echo $sha1 $sha256 $pinmd5 $subject $issuer $startdate $enddate $execution_time
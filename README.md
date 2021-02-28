# How to make request in localhost with curl

## GET

curl -X GET "http://httpbin.org/get" -H "accept: application/json" --proxy 127.0.0.1:8888

curl -X GET "http://go.com" --proxy 127.0.0.1:8888

curl -X GET "http://google.com" --proxy 127.0.0.1:8888

curl -X GET "/" -H "Host: google.com" --proxy 127.0.0.1:8888


## Conditional GET
curl -v GET "http://go.com" -H "If-Modified-Since: Sun, 28 Feb 2021 19:41:00 GMT" --proxy 127.0.0.1:8888

curl -v GET "http://go.com" -H "If-Modified-Since: Sat, 27 Feb 2021 19:41:00 GMT" --proxy 127.0.0.1:8888

## POST

curl -X POST "http://httpbin.org/post" -H "accept: application/json" --proxy 127.0.0.1:8888

# Sample codes
echo_client.py

echo_server.py
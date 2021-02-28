#!/bin/bash

# Google.com
cat google.txt | netcat -N google.com 80 > google.com.html

# Example.com
cat example.txt | netcat -N example.com 80 > example.com.html

# httpbin
cat httpbin.txt | netcat -N httpbin.org 80 > httpbin.org.html

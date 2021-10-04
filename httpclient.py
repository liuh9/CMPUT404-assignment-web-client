#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):
    def get_url_info(self, url):
        url_info = urllib.parse.urlparse(url)
        url_info_list = ["", "", ""]

        # host
        url_info_list[0] = url_info.hostname

        # port
        url_info_list[1] = url_info.port

        if url_info_list[1] == None:
            if url_info.scheme == "https":
                url_info_list[1] = 443
            else:  # http
                url_info_list[1] = 80
           
        # path
        url_info_list[2] = url_info.path

        if url_info_list[2] == "":
            url_info_list[2] = "/"

        return url_info_list

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return self.socket

    def get_code(self, data):
        split_data = data.split(" ")
        if len(split_data) >= 2:
            status_code = int(split_data[1])
            return status_code
        return None

    def get_headers(self,data):
        split_data = data.split("\r\n")
        header = split_data[0]
        hearder_list = header.split("\n")
        return hearder_list

    def get_body(self, data):
        split_data = data.split("\r\n\r\n")
        if len(split_data) >= 2:
            body = split_data[1]
            return body
        return None
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""

        # get host, port, path
        returned_url_info = self.get_url_info(url)
        host = returned_url_info[0]
        port = returned_url_info[1]
        path = returned_url_info[2]

        # connect
        sock = self.connect(host, port)

        request = "GET " + path + " HTTP/1.1\r\nHost: " + host + "\r\nConnection: close\r\n\r\n"
        self.sendall(request)

        # receive
        response = self.recvall(sock)

        code = self.get_code(response)
        headers = self.get_headers(response)
        body = self.get_body(response)

        # close
        self.close()

        # print the info to stdout
        print(code)
        print("--------")
        print(headers)
        print("--------")
        print(body)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""

        # get host, port, path
        returned_url_info = self.get_url_info(url)
        host = returned_url_info[0]
        port = returned_url_info[1]
        path = returned_url_info[2]

        # connect
        sock = self.connect(host, port)

        if args == None:  # no query string
            request = "POST " + path + " HTTP/1.1\r\nHost: " + host + "\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: " + str(0) + "\r\n\r\n"
        else:             # have query string
            request = "POST " + path + " HTTP/1.1\r\nHost: " + host + "\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: " + str(len(urllib.parse.urlencode(args))) + "\r\n\r\n" + urllib.parse.urlencode(args)
        
        self.sendall(request)

        # receive
        response = self.recvall(sock)

        code = self.get_code(response)
        headers = self.get_headers(response)
        body = self.get_body(response)

        # close
        self.close()

        # print the info to stdout
        print(code)
        print("--------")
        print(headers)
        print("--------")
        print(body)

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))

#!/usr/bin/python

import os
import subprocess
import fabric 

import socket
import libssh2

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('ubuntu@10.0.0.3', 22))

session = libssh2.Session()
session.startup(sock)
#session.userauth_password('john', '******')

channel = session.channel()
channel.execute('ls -l')


#!/usr/bin/python

import grpc
import json
import os

import srv6_explicit_path_pb2_grpc
import srv6_explicit_path_pb2

# Define wheter to use SSL or not
SECURE = False
# SSL cerificate for server validation
CERTIFICATE = 'cert_client.pem'
stubs = {}
# Build a grpc stub
def get_grpc_session(ip_address, port, secure):
  # If secure we need to establish a channel with the secure endpoint
  if secure:
    # Open the certificate file
    with open(CERTIFICATE) as f:
      certificate = f.read()
    # Then create the SSL credentials and establish the channel
    grpc_client_credentials = grpc.ssl_channel_credentials(certificate)
    channel = grpc.secure_channel("%s:%s" %(ip_address, port), grpc_client_credentials)
  else:
    channel = grpc.insecure_channel("%s:%s" %(ip_address, port))
  return srv6_explicit_path_pb2_grpc.SRv6ExplicitPathStub(channel), channel


def add_srv6_route(request):
    try_remove_srv6_route(request)
    global stubs
    # try:
    try:    
        response = stubs[request.src].Create(request)
        print("add srv6 route OK:")
        # print("\t"+src+"->"+dst+"\t:"+str(segs))
    except Exception,e:
        print("add srv6 route ERROR:")
        # print("\t"+src+"->"+dst+"\t:"+str(segs))
        print(str(e))

def create_path_request(src,dst,segs,encapmode):
  path_request = srv6_explicit_path_pb2.SRv6EPRequest()
  path = path_request.path.add()
  path.destination = dst
  path.device = 'eth1'
  path.encapmode = encapmode
  path_request.src = src
  for seg in segs:
    srv6_segment = path.sr_path.add()
    srv6_segment.segment = seg
  return path_request

def try_remove_srv6_route(request):
  global stubs
  try:    
    response = stubs[request.src].Remove(request)
  except:
    None

def remove_srv6_route(request): 
  global stubs
  try:    
    response = stubs[request.src].Remove(request)
    print("remove srv6 route OK:")
  except Exception,e:
    print("remove srv6 route ERROR:")
    # print("\t"+src+"->"+dst+"\t")
    # print(e.message)
    print(str(e))

stubs['2000::1'],channel = get_grpc_session("[2000::1]", 8000, SECURE)
stubs['2000::2'],channel = get_grpc_session("[2000::2]", 8000, SECURE)
print("start:")
request = create_path_request('2000::1','fdff::2/128',['fdff::3'],'inline')
remove_srv6_route(request)
request = create_path_request('2000::2','fdff::1/128',['fdff::3'],'inline')
remove_srv6_route(request)
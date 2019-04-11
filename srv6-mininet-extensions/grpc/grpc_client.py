#!/usr/bin/python

import grpc
import json

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


def add_srv6_route(src,segs,dst,encapmode):
    global stubs

    path_request = srv6_explicit_path_pb2.SRv6EPRequest()
    path = path_request.path.add()
    path.destination = dst
    path.device = 'eth1'
    path.encapmode = encapmode
    for seg in segs:
        srv6_segment = path.sr_path.add()
        srv6_segment.segment = seg
    response = stubs[src].Create(path_request)
    print(response)
stubs['2000::1'],channel = get_grpc_session("[2000::1]", 8080, SECURE)
print("channel started")
add_srv6_route('2000::1',['2000::3'],'2000::2/128','inline')


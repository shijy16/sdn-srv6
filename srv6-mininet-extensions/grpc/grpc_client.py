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

class srv6_path_manager:
  stubs = {}
  srv6_path = {}
  def __init__(self,num = -1,adresses=[]):
    if(len(adresses) > 0):
      for address in adresses:
        self.stubs[address],channel = self.get_grpc_session("[" + address + "]", 8000, SECURE)
    elif num > -1:
      for i in range(1,num + 1):
        addr = '2000::' + str(eval('hex(' + str(i) + ')'))[2:]
        self.stubs[addr],channel = self.get_grpc_session("[" + addr + "]", 8000, SECURE)
    else:
      print('ERROR: NO SERVER')
  
  def get_key(self,src,dst):
    return src+"->"+dst

  def add_path(self,src,dst,segs,encapmode):
    print("+++++++++++++++++++add begin++++++++++++++++++++++++++")
    if self.srv6_path.has_key(self.get_key(src,dst)):
      print("exist,remove")
      self.remove_srv6_path(src,dst)
    request = self.create_path_request(src,dst,segs,encapmode)
    if(self.send_add_srv6_path(request)):
      self.srv6_path[self.get_key(src,dst)] = request
      return True
    else:
      if self.send_replace_srv6_path(request):
        self.srv6_path[self.get_key(src,dst)] = request
        return True
    return False
  def send_add_srv6_path(self,request):
    try:    
      response = self.stubs[request.src].Create(request)
      print("add srv6 route OK")
      print("\t"+request.src+"->"+request.dst+"\t" + str(request.sr_path))
      return True
    except Exception,e:
      print("add srv6 route ERROR")
      print("\t"+request.src+"->"+request.dst+"\t" + str(request.sr_path))
      print(str(e))
      return False

  def send_replace_srv6_path(self,request):
    try:    
      response = self.stubs[request.src].Replace(request)
      print("replace srv6 route OK")
      print("\t"+request.src+"->"+request.dst+"\t" + str(request.sr_path))
      return True
    except Exception,e:
      print("replace srv6 route ERROR")
      print("\t"+request.src+"->"+request.dst+"\t" + str(request.sr_path))
      print(str(e))
      return False

  def remove_srv6_path(self,src,dst,segs=[],encapmode='encap'):
    print("-------------------remove begin---------------")
    if(self.srv6_path.has_key(self.get_key(src,dst))):
      return self.send_remove_srv6_path(self.srv6_path.pop(self.get_key(src,dst)))
    else:
      request = self.create_path_request(src,dst,segs,encapmode)
      return self.send_remove_srv6_path(request)


  def send_remove_srv6_path(self,request): 
    try:    
      response = self.stubs[request.src].Remove(request)
      print("remove srv6 route OK")
      print(response)
      print("\t"+request.src+"->"+request.dst+"\t" + str(request.sr_path))
      return True
    except Exception,e:
      print("remove srv6 route ERROR")
      print("\t"+request.src+"->"+request.dst+"\t" + str(request.sr_path))
      print(str(e))
      return False

  staticmethod
  def create_path_request(self,src,dst,segs,encapmode):
    path_request = srv6_explicit_path_pb2.SRv6EPRequest()

    path_request.device = 'eth1'
    path_request.encapmode = encapmode
    path_request.src = src
    path_request.dst = dst
    for seg in segs:
      srv6_segment = path_request.sr_path.add()
      srv6_segment.segment = seg
    return path_request

  # Build a grpc stub
  staticmethod
  def get_grpc_session(self,ip_address, port, secure):
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

  def clear_all(self):
    print("\n**************************\n"
        + "*         clear all      *\n"
        + "**************************\n")
    for k,request in self.srv6_path.items():
      self.remove_srv6_path(request.src,request.dst)
    self.srv6_path.clear()


manager = srv6_path_manager(adresses=['2000::6','2000::1','2000::9'])
# manager.add_path('2000::1','fdf0:0:0:2::2/128',['fdf0:0:0:2::1'],'inline')
# manager.add_path('2000::1','fdf0:0:0:3::2/128',['fdff::2'],'inline')
manager.add_path('2000::6','fdff::1/128',['fdff::9'],'encap')
# manager.add_path('2000::1','fdff::5/128',['fdff::2'],'inline')
# manager.add_path('2000::1','fdff::6/128',['fdff::2'],'inline')
# manager.add_path('2000::1','fdff::7/128',['fdff::2'],'inline')
# manager.clear_all()
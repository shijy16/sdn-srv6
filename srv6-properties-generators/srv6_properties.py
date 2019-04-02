#!/usr/bin/python

##############################################################################################
# Copyright (C) 2018 Pier Luigi Ventre - (CNIT and University of Rome "Tor Vergata")
# Copyright (C) 2018 Stefano Salsano - (CNIT and University of Rome "Tor Vergata")
# www.uniroma2.it/netgroup - www.cnit.it
#
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Properties for Segment Routing IPv6
#
# @author Pier Luigi Ventre <pierventre@hotmail.com>
# @author Stefano Salsano <stefano.salsano@uniroma2.it>

# Store an OSPF network
class OSPFNetwork(object):
 
  def __init__(self, name, net, cost=1, hello_int=5, area="0.0.0.0"):

    self.net = net
    data = net.split("/")
    self.netbitOSPF = int(data[1])
    self.subnet = []
    self.cost = cost
    self.hello_int = hello_int
    self.area = area
    self.name = name

  def serialize(self):
    return "declare -a %s=(%s %s)\n" %(self.name, self.net, self.area)
  
  def __str__(self):
    return "{'name':'%s', 'net':'%s', 'area':'%s'}" %(self.name, self.net, self.area)

 # Encapsulate router properties
class RouterProperties(object):
  
  def __init__(self, loopback, routerid):
    self.loopback = loopback
    self.routerid = routerid

  def __str__(self):
    return "{'loopback':'%s/128', 'routerid': '%s'}" %(self.loopback, self.routerid)

# Encapsulate link properties used to build the testbed object in softfire-tiesr-deployer
class LinkProperties(object):

  def __init__(self, iplhs, iprhs, net):
    self.iplhs = iplhs
    self.iprhs = iprhs
    self.net = net

  def __str__(self):
    return "{'iplhs':'%s', 'iprhs':'%s', net':'%s'}" %(self.iplhs, self.iprhs, self.net)
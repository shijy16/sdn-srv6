#!/usr/bin/python

##############################################################################################
# Copyright (C) 2017 Pier Luigi Ventre - (CNIT and University of Rome "Tor Vergata")
# Copyright (C) 2017 Stefano Salsano - (CNIT and University of Rome "Tor Vergata")
# Copyright (C) 2017 Francesco Lombardo - (CNIT)
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
# Topology Parser for SoftFire
#
# @author Pier Luigi Ventre <pierventre@hotmail.com>
# @author Stefano Salsano <stefano.salsano@uniroma2.it>
# @author Francesco Lombardo <franclombardo@gmail.com>

import os
import json
import sys
import re
from srv6_topo_parser import SRv6TopoParser

class SoftFireTopoParser(SRv6TopoParser):
    path = ""

    """
    Init Function, load json_data from topo and ob (if provided)
    """
    def __init__(self, topo, ob, verbose=False):
        super(SRv6TopoParser, self).__init__(topo, verbose)
        self.servers = []
        self.servers_properties = []
        self.routers = []
        self.routers_properties = []
        self.routers_dict = {}
        self.edge_links = []
        self.edge_links_properties = []
        self.core_links = []
        self.core_links_properties = []
        self.vnf_term_dict = {}
        self.ip_addr_map = {}
        self.vims = []
        self.parsed = False

        if self.verbose:
            print "*** __init__: version topology format:", self.version
        topo = self.path + topo
        if os.path.exists(topo) == False:
            print "Error Topo File %s Not Found" % topo
            sys.exit(-2)
        topo_json_file = open(topo)
        self.topo_json_data = json.load(topo_json_file)
        topo_json_file.close()
        if self.verbose:
            print "*** topo data loaded:"
            print json.dumps(self.topo_json_data, sort_keys=True, indent=4)

        self.ob_json_data = {}
        ob = self.path + ob
        if os.path.exists(ob) == False:
            print "Openbaton Json File %s Not Found" % ob
        else:
            ob_json_file = open(ob)
            self.ob_json_data = json.load(ob_json_file)
            ob_json_file.close()
        if self.verbose:
            print "*** ob data loaded:"
            print json.dumps(self.ob_json_data, sort_keys=True, indent=4)

    """
    Parse Function, firstly it retrieves the vertices from json data,
    then it retrieves the links from json data
    """
    def parse_data(self):
        SRv6TopoParser.parse_data(self)
        self.load_vnfs_and_terms()
        self.load_vm_testbeds()
        self.load_openbaton()

    """
    Function used for retrieving vnf and term dictionary for each vertex
    """
    def getVNFandTERMdict(self, id):
        if self.parsed == False:
            self.parse_data()
        return self.routers_dict[id]['vnfs_and_terms']

    """
    Function used for retrieving tunneling
    """
    def getTunneling(self):
        if self.parsed == False:
            self.parse_data()
        return self.tunneling

    """
    Function used for retrieving vm-mapping
    """
    def getVMMapping(self):
        if self.parsed == False:
            self.parse_data()
        return self.ip_addr_map

    """
    Parses topology advanced options
    """
    def load_advanced(self):
        advanced_options = self.json_data['graph_parameters'] if 'graph_parameters' in self.json_data else []
        if 'tunneling' not in advanced_options:
            print "Error No Tunneling Data"
            sys.exit(-2)
        self.tunneling = advanced_options['tunneling']
        if self.tunneling == "":
            self.tunneling = "VXLAN"
        if 'testbed' not in advanced_options:
            print "Error No Testbed Data"
            sys.exit(-2)
        testbeds_types = ["SOFTFIRE"]
        testbed = advanced_options['testbed']
        if testbed not in testbeds_types:
            print "%s Not Supported" % testbed
            sys.exit(-2)
        self.testbed = testbed

    """
    Parses vertex from json_data, renames the node in 'vertices' and in 'edges'
    """
    def load_vertex(self):
        if self.verbose:
            print "*** Retrieve Vertex"
        vertices = self.json_data['vertices']
        for vertex in vertices:
            curvtype = vertex['info']['type']
            #curvproperty = vertex['info']['property']
            curvproperty = vertex['info'].get('property', {})
            if 'VM' in curvtype:
                self.routers.append(str(vertex['id']))
                self.routers_properties.append(curvproperty)
                self.routers_dict[str(vertex['id'])]=curvproperty
            elif 'Testbed' in curvtype:
                self.vims.append(str(vertex['id']))
            elif 'ovnf_netns' in curvtype:
                self.vnf_term_dict[str(vertex['id'])]=curvproperty
                self.vnf_term_dict[str(vertex['id'])]['type']='ovnf_netns'
            elif 'ovnf_lxdcont' in curvtype:
                self.vnf_term_dict[str(vertex['id'])]=curvproperty
                self.vnf_term_dict[str(vertex['id'])]['type']='ovnf_lxdcont'
            elif 'term_netns' in curvtype:
                self.vnf_term_dict[str(vertex['id'])]=curvproperty
                self.vnf_term_dict[str(vertex['id'])]['type']='term_netns'
            elif 'term_lxdcont' in curvtype:
                self.vnf_term_dict[str(vertex['id'])]=curvproperty
                self.vnf_term_dict[str(vertex['id'])]['type']='term_lxdcont'
        if self.verbose:
            print "*** Routers:", self.routers
            print "*** Routers dict:", self.routers_dict
            print "*** vnf_term_dict:", self.vnf_term_dict

    """
    Parses vnfs and terms from json_data
    needs to be called after load_vertex

    the routers_dict[myrouter]['vnfs_and_terms'] has the following structure:
    {'vnf1': {'type': TYPE, 'key1':'value1'}}
    """
    def load_vnfs_and_terms(self):
        if self.verbose:
            print "*** Retrieve Vnfs and Terms"
        edges = self.json_data['edges']
        for edge in edges:
            myrouter = ""
            myvnf_ter = ""
            if (edge['source'] in self.routers and edge['target'] in self.vnf_term_dict):
                myrouter = str(edge['source'])
                myvnf_ter = str(edge['target'])
            if (edge['target'] in self.routers and edge['source'] in self.vnf_term_dict) :
                myrouter = str(edge['target'])
                myvnf_ter = str(edge['source'])
            if myrouter != "" :  
                if 'vnfs_and_terms' in self.routers_dict[myrouter] :
                    self.routers_dict[myrouter]['vnfs_and_terms'][myvnf_ter]=self.vnf_term_dict[myvnf_ter]
                else :
                    self.routers_dict[myrouter].update({'vnfs_and_terms':{myvnf_ter:self.vnf_term_dict[myvnf_ter]}})
        if self.verbose:
            print "*** Routers dict updated:", self.routers_dict

    """
    Parses ob information
    """
    def load_openbaton(self):
        if self.ob_json_data != {} :
            for myvnf in self.ob_json_data ['payload']['vnfr']:
                ip_dict = {}
                ip_dict.update({'internal_ip':str(myvnf['vdu'][0]['vnfc_instance'][0]['ips'][0]['ip'])})
                ip_dict.update({'floating_ip':str(myvnf['vdu'][0]['vnfc_instance'][0]['floatingIps'][0]['ip'])})
                self.ip_addr_map[str(myvnf['name'])]=ip_dict
        if self.verbose:
            print "*** IP address map: \n", self.ip_addr_map

    """
    Parses vm-to-testbeds information
    """
    def load_vm_testbeds(self):
        if self.verbose:
            print "*** Retrieve VM to tesbed map"
        edges = self.json_data['edges']
        for edge in edges:
            myrouter = ""
            mytestbed = ""
            if (edge['source'] in self.routers and edge['target'] in self.vims):
                myrouter = str(edge['source'])
                mytestbed = str(edge['target'])
            if (edge['target'] in self.routers and edge['source'] in self.vims) :
                myrouter = str(edge['target'])
                mytestbed = str(edge['source'])
            if myrouter != "" :  
                self.routers_dict[myrouter].update({'vim':mytestbed})
        if self.verbose:
            print "*** VM to tesbed map:", self.routers_dict
      
if __name__ == '__main__':
    parser = SoftFireTopoParser(topo="example/example_softfire_topology.json",
        ob="example/example_openbaton_notification", verbose=False)
    parser.parse_data()
    print "*** Nodes:"
    for router, router_property in zip(parser.getRouters(), parser.getRoutersProperties()):
        print "*** Router: %s - Property: %s" % (router, router_property)
    print "*** Core Links"
    for core_link, core_link_property in zip(parser.getCoreLinks(), parser.getCoreLinksProperties()):
        print "*** Core Link: %s - Property: %s" % (core_link, core_link_property)
    print "*** Tunneling", parser.tunneling
    print "*** Testbed", parser.testbed

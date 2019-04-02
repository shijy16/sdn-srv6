#!/usr/bin/python

##############################################################################################
# Copyright (C) 2017 Pier Luigi Ventre - (CNIT and University of Rome "Tor Vergata")
# Copyright (C) 2017 Stefano Salsano - (CNIT and University of Rome "Tor Vergata")
# Copyright (C) 2017 Alessandro Masci - (University of Rome "Tor Vergata")
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
# Topology Parser for Segment Routing IPv6
#
# @author Pier Luigi Ventre <pierventre@hotmail.com>
# @author Stefano Salsano <stefano.salsano@uniroma2.it>
# @author Alessandro Masci <mascialessandro89@gmail.com>

import os
import json
import sys
import re
from topo_parser import TopoParser

class SRv6TopoParser(TopoParser):
    path = ""

    """
    Init Function, load json_data from topo and ob (if provided)
    """
    def __init__(self, topo, verbose=False):
        self.verbose = verbose
        self.routers = []
        self.routers_properties = []
        self.edge_links = []
        self.edge_links_properties = []
        self.core_links = []
        self.core_links_properties = []
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

    """
    Parse Function, firstly retrieves the vertices from json data,
    then retrieves the links from json data
    """
    def parse_data(self):
        self.load_advanced()
        self.load_vertex()
        self.load_core_links()
        self.parsed = True

    """
    Function used for retrieving routers from json data
    """
    def getRouters(self):
        if self.parsed == False:
            self.parse_data()
        return self.routers

    """
    Function used for retrieving routers properties from json data
    """
    def getRoutersProperties(self):
        if self.parsed == False:
            self.parse_data()
        return self.routers_properties

    """
    Function used for retrieving core links from json data
    """
    def getCoreLinks(self):
        if self.parsed == False:
            self.parse_data()
        return self.core_links

    """
    Function used for retrieving core links properties from json data
    """
    def getCoreLinksProperties(self):
        if self.parsed == False:
            self.parse_data()
        return self.core_links_properties

    """
    Parses topology advanced options
    """
    def load_advanced(self):
        if self.verbose:
            print "*** Retrieve Advanced Option"
        advanced_options = self.topo_json_data['graph_parameters'] if 'graph_parameters' in self.topo_json_data else []
        if 'testbed' not in advanced_options:
            print "Error No Testbed Data"
            sys.exit(-2)
        testbeds_types = ["MININET"]
        testbed = advanced_options['testbed']
        if testbed not in testbeds_types:
            print "%s Not Supported" % testbed
            sys.exit(-2)
        self.testbed = testbed

    """
    Parses vertex from topo_json_data, renames the node in 'vertices' and in 'edges'
    """
    def load_vertex(self):
        if self.verbose:
            print "*** Retrieve Vertex"
        vertices = self.topo_json_data['vertices']
        for vertex in vertices:
            curvtype = vertex['info']['type']
            curvproperty = vertex['info']['property']
            if 'Router' in curvtype:
                self.routers.append(str(vertex['id']))
                self.routers_properties.append(curvproperty)
        if self.verbose:
            print "*** Routers:", self.routers

    # Parses core_links from topo_json_data
    def load_core_links(self):
        if self.verbose:
            print "*** Retrieve Core Links"
        edges = self.topo_json_data['edges']
        for edge in edges:
            edge_property = edge['info']['property']
            if edge['source'] in self.routers and edge['target'] in self.routers:
                self.core_links.append((str(edge['source']), str(edge['target'])))
                self.core_links_properties.append(edge_property)
        if self.verbose:
            print "*** Corelinks:", self.core_links
      
if __name__ == '__main__':
    parser = SRv6TopoParser(topo="example/example_srv6_topology.json", verbose=False)
    parser.parse_data()
    print "*** Nodes:"
    for router, router_property in zip(parser.getRouters(), parser.getRoutersProperties()):
        print "*** Router: %s - Property: %s" % (router, router_property)
    print "*** Core Links"
    for core_link, core_link_property in zip(parser.getCoreLinks(), parser.getCoreLinksProperties()):
        print "*** Core Link: %s - Property: %s" % (core_link, core_link_property)
    print "*** Testbed", parser.testbed

#!/usr/bin/python

##############################################################################################
# Copyright (C) 2014 Pier Luigi Ventre - (Consortium GARR and University of Rome "Tor Vergata")
# Copyright (C) 2014 Giuseppe Siracusano, Stefano Salsano - (CNIT and University of Rome "Tor Vergata")
# www.garr.it - www.uniroma2.it/netgroup - www.cnit.it
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
# Topology Parser.
#
# @author Pier Luigi Ventre <pierventre@hotmail.com>
# @author Giuseppe Siracusano <a_siracusano@tin.it>
# @author Stefano Salsano <stefano.salsano@uniroma2.it>

import os
import json
import sys
from topo_parser_utils import Subnet
import re

class TopoParser(object):
    path = ""

    """
    Init Function, load json_data from path_json
    """
    def __init__(self, path_json, verbose=False, version=1):
        self.verbose = verbose
        self.version = int(version)
        self.cr_oshis = []
        self.cr_oshis_properties = []
        self.pe_oshis = []
        self.pe_oshis_properties = []
        self.cers = []
        self.cers_properties = []
        self.ctrls = []
        self.ctrls_properties = []
        self.vlls = []
        self.pws = []
        self.vss = []
        self.l2vss = []
        self.pplinks = []
        self.ppsubnets = []
        self.subnetclass = Subnet
        self.generated = False
        self.parsed = False
        self.testbed = None
        self.mapped = False
        self.vlan = None

        if self.verbose:
            print "*** __init__: version topology format:", self.version
        path_json = self.path + path_json
        if os.path.exists(path_json) == False:
            print "Error Topo File %s Not Found" % path_json
            sys.exit(-2)
        json_file = open(path_json)
        self.json_data = json.load(json_file)
        json_file.close()
        if self.verbose:
            print "*** JSON Data Loaded:"
            print json.dumps(self.json_data, sort_keys=True, indent=4)

    """
    Parse Function, firstly it retrieves the vertices from json data,
    then retrieves the links from json data, finally create the PPsubnet
    """
    def parse_data(self):
        self.load_advanced()
        self.load_vertex()
        self.load_links()
        self.load_vss()
        self.create_subnet()
        self.parsed = True

    def getsubnets(self):
        if self.parsed == False:
            self.parse_data()
        return self.ppsubnets  # , self.l2subnets)

    def getVLLs(self):
        if self.parsed == False:
            self.parse_data()
        return self.vlls

    def getPWs(self):
        if self.parsed == False:
            self.parse_data()
        return self.pws

    def getVSs(self):
        if self.parsed == False:
            self.parse_data()
        return self.vss

    def load_advanced(self):
        if self.verbose:
            print "*** Retrieve Advanced Option"
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
        testbeds = ["OFELIA", "GOFF", "GTS", "MININET", "SOFTFIRE"]
        testbed = advanced_options['testbed']
        if testbed not in testbeds:
            print "%s Not Supported" % testbed
            sys.exit(-2)
        self.testbed = testbed
        if 'mapped' not in advanced_options:
            print "Error No Mapped Data"
            sys.exit(-2)
        self.mapped = advanced_options['mapped']
        if 'generated' not in advanced_options:
            print "Error No Generated Data"
            sys.exit(-2)
        self.generated = advanced_options['generated']
        if 'vlan' not in advanced_options:
            print "Error No VLAN Data"
            sys.exit(-2)
        vlan = advanced_options['vlan']
        try:
            self.vlan = int(vlan)
        except ValueError:
            print "Error VLAN Data"
        if self.mapped == True and self.vlan <= 0 and self.testbed != "MININET":
            print "Invalid VLAN Data"
            sys.exit(-2)

    """
    Parses vertex from json_data, renames the node in 'vertices' and in 'edges',
    and divides them in: cr - oshi (Core Oshi), pe - oshi (Access Oshi) 
    and cers (Customer Edge Router).
    """
    def load_vertex(self):
        if self.version == 2:
            return self.load_vertex_v2()
        if self.verbose:
            print "*** Retrieve Vertex"
        vertices = self.json_data['vertices']
        for vertex in vertices:

            curvtype = vertices[vertex]['info']['type']
            curvproperty = vertices[vertex]['info']['property']

            if 'OSHI-CR' in curvtype:
                number = map(int, re.findall(r'\d+', vertex))
                self.cr_oshis.append('cro%s' % number[0])
                self.cr_oshis_properties.append(curvproperty)
            elif 'OSHI-PE' in curvtype:
                number = map(int, re.findall(r'\d+', vertex))
                self.pe_oshis.append('peo%s' % number[0])
                self.pe_oshis_properties.append(curvproperty)
            elif 'CE' in curvtype:
                number = map(int, re.findall(r'\d+', vertex))
                self.cers.append('cer%s' % number[0])
                self.cers_properties.append(curvproperty)
            elif 'OF Controller' in curvtype:
                number = map(int, re.findall(r'\d+', vertex))
                self.ctrls.append('ctr%s' % number[0])
                self.ctrls_properties.append(curvproperty)
            elif 'VS' in curvtype:
                number = map(int, re.findall(r'\d+', vertex))
                self.l2vss.append('vs%s' % number[0])

        if self.verbose:
            print "*** CROSHI:", self.cr_oshis
            print "*** PEOSHI:", self.pe_oshis
            print "*** CER:", self.cers
            print "*** CTRL:", self.ctrls
            print "*** VS:", self.l2vss

    def load_vertex_v2(self):
        if self.verbose:
            print "*** Retrieve Vertex"
        vertices = self.json_data['vertices']

        for vertex in vertices:
            curvtype = vertex['info']['type']
            curvproperty = vertex['info']['property']
            if 'OSHI-CR' in curvtype:
                self.cr_oshis.append(str(vertex['id']))
                self.cr_oshis_properties.append(curvproperty)
            elif 'OSHI-PE' in curvtype:
                self.pe_oshis.append(str(vertex['id']))
                self.pe_oshis_properties.append(curvproperty)
            elif 'CE' in curvtype:
                self.cers.append(str(vertex['id']))
                self.cers_properties.append(curvproperty)
            elif 'OF Controller' in curvtype:
                self.ctrls.append(str(vertex['id']))
                self.ctrls_properties.append(curvproperty)
            elif 'VS' in curvtype:
                self.l2vss.append(str(vertex['id']))

        if self.verbose:
            print "*** CROSHI:", self.cr_oshis
            print "*** PEOSHI:", self.pe_oshis
            print "*** CER:", self.cers
            print "*** CTRL:", self.ctrls
            print "*** VS:", self.l2vss

    def load_vss(self):
        if self.version == 2:
            return self.load_vss_v2()
        if self.verbose:
            print "*** Retrieve VSs"
        edges = self.json_data['edges']
        for l2vs in self.l2vss:
            vs = []
            for edge in edges:
                vertids = edge.split('&&')
                if l2vs in vertids[0] and vertids[1] not in vs:
                    vs.append(vertids[1])
                elif l2vs in vertids[1] and vertids[0] not in vs:
                    vs.append(vertids[0])
            self.vss.append(vs)

    def load_vss_v2(self):
        if self.verbose:
            print "*** Retrieve VSs"
        edges = self.json_data['edges']
        for l2vs in self.l2vss:
            vs = []
            for edge in edges:
                if l2vs == str(edge['source']) and str(edge['target']) not in vs:
                    vs.append(str(edge['target']))
                elif l2vs == str(edge['target']) and str(edge['source']) not in vs:
                    vs.append(str(edge['source']))
            self.vss.append(vs)

    def load_links(self):
        if self.version == 2:
            return self.load_links_v2()
        if self.verbose:
            print "*** Retrieve Links"
        edges = self.json_data['edges']
        for edge in edges:
            vertids = edge.split('&&')
            for link in edges[edge]['links']:
                if link['view'] == 'Vll':
                    self.vlls.append((vertids[0], vertids[1], link))
                elif link['view'] == 'PW':
                    self.pws.append((vertids[0], vertids[1], link))
                elif link['view'] == 'Data':
                    self.pplinks.append((vertids[0], vertids[1], link))

        if self.verbose:
            print "*** PPlinks:", self.pplinks
            print "*** VLLs:", self.vlls

    def load_links_v2(self):
        if self.verbose:
            print "*** Retrieve Links"
        edges = self.json_data['edges']
        for edge in edges:
            if edge['view'] == 'Vll':
                self.vlls.append((str(edge['source']), str(edge['target']), edge))
            elif edge['view'] == 'PW':
                self.pws.append((str(edge['source']), str(edge['target']), edge))
            elif edge['view'] == 'Data':
                self.pplinks.append((str(edge['source']), str(edge['target']), edge))

        if self.verbose:
            print "*** PPlinks:", self.pplinks
            print "*** VLLs:", self.vlls

    """
    From the parsed Links, creates the associates Subnet
    """
    def create_subnet(self):
        # Creates the ppsubnets
        for pplink in self.pplinks:
            s = self.subnetclass()
            s.appendLink(pplink)
            self.ppsubnets.append(s)
        # Eliminates all links
        self.pplinks = []
        if self.verbose:
            i = 0
            print "*** Subnets:"
            for subnet in self.ppsubnets:
                print "*** PP Subnet(%s): Nodes %s - Links %s" % (i + 1, subnet.nodes, subnet.links)
                i = i + 1

if __name__ == '__main__':
    parser = TopoParser("example/example_dreamer_topology.json", verbose=False, version=2)
    ppsubnets = parser.getsubnets()
    print "*** Nodes:"
    for cr, cr_property in zip(parser.cr_oshis, parser.cr_oshis_properties):
        print "*** CR: %s - Property: %s" % (cr, cr_property)
    for pe, pe_property in zip(parser.pe_oshis, parser.pe_oshis_properties):
        print "*** PE: %s - Property: %s" % (pe, pe_property)
    for cer, cer_property in zip(parser.cers, parser.cers_properties):
        print "*** CER: %s - Property: %s" % (cer, cer_property)
    for ctrl, ctrl_property in zip(parser.ctrls, parser.ctrls_properties):
        print "*** CTRL: %s - Property: %s" % (ctrl, ctrl_property)
    print "*** Networks Point To Point"
    for ppsubnet in ppsubnets:
        links = ppsubnet.links
        print "*** Subnet: Node %s - Links %s" % (ppsubnet.nodes, links)
    print "*** VLLs", parser.getVLLs()
    print "*** PWs", parser.getPWs()
    print "*** VSs", parser.getVSs()
    print "*** Tunneling", parser.tunneling
    print "*** Testbed", parser.testbed
    print "*** Mapped", parser.mapped
    print "*** Generated", parser.generated
    print "*** VLAN", parser.vlan

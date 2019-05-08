import json

class edge:
    def __init__(self,l,r,bw):
        self.node_l = l
        self.node_r = r
        self.band_width = bw

    def show(self):
        print(self.node_l,self.node_r,self.band_width)

def get_num_in_str(line):
    line = line.replace('\n','')
    words = line.split(' ')
    if('' in words):
        words.remove('')
    return list(map(int,words))

def read_topo():
    f = open('topo.txt','r')
    content = f.readlines()
    f.close()
    t_list = get_num_in_str(content[0])
    node_num = t_list[0]
    edge_num = t_list[1]
    edges = []
    for i in range(1,edge_num + 1):
        t_list = get_num_in_str(content[i])
        edges.append(edge(t_list[0],t_list[1],t_list[2]/1000exit))
    return node_num,edge_num,edges

def build_dict(node_num,edge_num,_edges):
    content = {}
    vertices = []
    edges = []
    content['graph_parameters'] = {"testbed":"MININET"}
    for i in range(0,node_num):
        vertice = {}
        info = {}
        info['type'] = 'Router'
        info['property'] = {}
        info['group'] = []
        vertice['info'] = info
        vertice['id'] = str(i + 1)
        vertices.append(vertice)
    content['vertices'] = vertices
    for i in range(0,edge_num):
        edge = {}
        edge['source'] = str(_edges[i].node_l + 1)
        edge['target'] = str(_edges[i].node_r + 1)
        edge['view'] = 'data'
        info = {}
        info_property = {}
        info_property['bw'] = _edges[i].band_width
        info_property['delay'] = 1000
        info['property'] = info_property
        info['group'] = ''
        edge['info'] = info
        edges.append(edge)
    content['edges'] = edges
    return content

def write_json(content):
    try:
        json_str = json.dumps(content, indent=4)
        with open('topo.json', 'w') as json_file:
            json_file.write(json_str)
        return True
    except:
        return False



node_num,edge_num,edges = read_topo()
write_json(build_dict(node_num,edge_num,edges))

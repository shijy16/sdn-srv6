def read_traffic(p):
    f = open(p)
    lines = f.readlines()
    path_matrix = [[ [] for j in range(12) ] for i in range(12)]
    for line in lines:
        line = line.replace('\n','')
        key_values = line.split('  ')
        st = 0
        ed = 0
        t_dict = {} 
        for key_value in key_values:
            key_value = key_value.split(' ')
            k = key_value[0]
            v = key_value[1]
            #handle segs
            if len(key_value) > 2:
                for i in range(2,len(key_value)):
                    v += key_value[i]
                v = v.replace('[','')
                v = v.replace(']','')
                v = v.split(',')
                t = []
                for vv in v:
                    t.append(int(vv) + 1)
                v = t
            if(k == 'st'):
                st = int(v)
            elif(k == 'ed'):
                ed = int(v)
            else:
                if(k.find('id') > -1):
                    v = int(v)
                elif(k.find('path') > 3):
                    v = float(v)
                elif(k.find('demand') > -1):
                    v = float(v)
                t_dict[k] = v
        path_matrix[st][ed].append(t_dict)
    return path_matrix

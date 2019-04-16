# sdn-srv6
attempt to use build a srv6 algorithm testbed in mininet.

> Based on `Dreamer-Topology-Parser`,`srv6-properties-generators`,`srv6-contoller` and `srv6-mininet-extensions` by [netgroup](<https://github.com/netgroup>)



## I. Startup

### 1. Get `srv6-mininet-extensions ` ready

see srv6-mininet-extensions/README.md

### 2.Get `grpc` southbound api ready

in folder `grpc`,we need to get two grpc packages `srv6_explicit_path_pb2_grpc and srv6_explicit_path_pb2` with the proto file `srv6_explicit_path.proto `.

##### install tools for grpc proto files

````
pip install protobuf
pip install grpcio
pip install grpcio-tools
````

##### get the grpc packages

````shell
python -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. srv6_explicit_path.proto
````

## II. Usage

> all in folder `srv6-mininet-extensions`

### 1.Run srv6-mininet topo

````shell
sudo python srv6_mininet_extension.py --topology topo/example_srv6_topology.json     
````

### 2.Enter devices' xterm

use the following command in mininet cli to enter ads1's terminal

````shell
xterm ads1
````

### 3. Run client and servers

run client in mgmt's or controller's xterm

```shell
python grpc/grpc_client.py
```

run server on router's xterm

````shell
python grpc/grpc_server.py
````

PS:Now the code is only ready for the connection between mgmt and ads1.You may need to change `grpc/grpc_server.py` to connect with other devices

## III. development date

#### 11st April

+  run through and add function `add_srv6_route(src,segs,dst,encapmode)`

+  **TODO**
  + [ ]  add auto startup funcs for each devices
    + [ ] still some bugs
  + [ ] add delete function(need to learn `grpc` programming I guess)
  + [ ] to see if it's possible to build grpc links between mgmt and all routers through  real time topology


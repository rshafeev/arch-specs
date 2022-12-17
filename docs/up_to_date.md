# Up-To-Date Support Policy
[[_TOC_]]

## Events and your actions
### Event: When the development of a new service started.
* __Responsible persons:__ 
  * Team Lead of dev-team
* __Action__:
You should add a specification for the new service in the file:
`/<product>/specifications/<service_module>.yaml` , service specification example:

```yaml
 ...
  some-service:
    src: <link to gitlab>
    desc: <service short description>
    status: *develop
    state: *stateful
    owner: Roman Shafeev
    dev_team: <dev team name>
    internal_storage:                 # [optional] a list of internal storages which the service uses. e.g.: rocksdb, lucene, lmdb, etc.
      - name: rocksdb                 # [required] internal storage name
        desc: some description        # [optional] description in markdown format
```
_see full example in [CRUD Specifications Policy](/docs/crud.md)_.

### Event: When we designed/implemented that the service produces a new kafka topic
* __Responsible persons:__ 
  * Team Lead of dev-team 
  * Service Owner
  * Developer   
* __Action__:
You should add a description about a new topic to the `kafka` store in the file:
`/<product>/specifications/<service_module>.yaml`
```yaml
kafka:
  name: kafka
  type: *kafka
  status: *ready
  owner: Roman Shafeev
  state: *stateful
  topics:
    ...
    sessions:
      # description, markdown format
      desc: User sessions.
      # protocol, markdown format
      protocol: '[ExtensionInfo.proto](<some link to proto file>)'
```


### Event: When we designed/implemented that the additional storage (e.g. cassandra) is used by the service 
* __Responsible persons:__ 
  * Team Lead of dev-team 
  *  Service Owner
  * Developer 
* __Action__:
You should add to 'connect_to' section of your service in the file:
`/<product>/specifications/<service_module>.yaml`
```yaml
  <your_service>:                     # service name.  
    ...   
    connect_to:                      
      # connect to database
      - name: postgresql              # [required] the service name to connect to
        transport: tcp                # [optional] network transport protocol. Available values: tcp, udp, etc.
        protocol: pg                  # [optional] application`s layer protocol. 
        data_direction: *rx           # [required] data direction: rx(read), tx(write), rx_tx(read and write)
        desc: some description        # [optional] description
      # connect to database(clickhouse)
      - name: clickhouse              # [required] the service name to connect to
        protocol: http                # [optional] application`s layer protocol. 
        data_direction: *rx           # [required] data direction: rx(read), tx(write), rx_tx(read and write)
        desc: some description        # [optional] description
      # connect to database(cassandra)
      - name: cassandra-singledc      # [required] the service name to connect to
        transport: tpc                # [optional] application`s layer protocol. 
        data_direction: *rx_tx        # [required] data direction: rx(read), tx(write), rx_tx(read and write)
        desc: some description        # [optional] description
```

> :information_source: Note! if the specification of the service which defined in `connect_to` 
>  section (property 'name') does not exist 
>  in any /<product>/specifications/*.yaml files
>  you should add it to the *.yaml specifications.

### Event:  When we designed/implemented the network communication with additional services (by http/grpc)"
* __Responsible persons:__ 
  * Team Lead of dev-team 
  * Service Owner
  * Developer  
* __Action__:
You should add to 'connect_to' section of your service in the file:
`/<product>/specifications/<service_module>.yaml`

```yaml
  <your_service>:                     # service name.  
    ...   
    connect_to:                      
      # connect to grpc service
      - name: external/service1       # [required] the service name to connect to
        protocol: grpc                # [required] network transport. Available values: tcp, udp, etc.
        desc: some description        # [optional] description

      # connect to http api service
      - name: api                      # [required] the service name to connect to
        protocol: http                # [required] network transport. Available values: tcp, udp, etc.
        data_direction: *rx           # [required] data direction: rx(read  - make GET requests only), 
                                      #                            tx(write - make POST/PUT/DELETE requests only), rx_tx(read and write)
        desc: some description        # [optional] description
      
      # connect to kafka (consume topics)
      - name: kafka                      # [required] the service name to connect to           
        data_direction: *kafka_consumer # [required] data direction: rx(consumer)
        desc: some description          # [optional] description
        offset_storage: rocksdb         # [optional] offset storage
        topics:                         # [optional] [only for kafka connection] a list of the topics which used by 
                                        #            the service. This list will be merged with topics from PRO Prometheus.
          sessions:                     # [required] topic name
        
      # connect to kafka (produce topics)
      - name: kafka                     # [required] the service name to connect to           
        data_direction: *kafka_producer # [required] data direction: tx(producer)
        desc: some description          # [optional] description
        topics:                         # [optional] [only for kafka connection] a list of the topics which used by 
                                        #            the service. This list will be merged with topics from PRO Prometheus.
          sessions:                  # [required] topic name
```  

> :information_source: Note! if the specification of the service which defined in `connect_to` 
>  section (property 'name') does not exist 
>  in any /<product>/specifications/*.yaml files
>  you should add it to the *.yaml specifications.

### Event: When we decommissioned the service from any PRO ENVs
* __Responsible persons:__ 
  * Service Owner
  * Ops Engineer
* __Action__:
You should change a service status to `decommission` in the file:
`/<product>/specifications/<service_module>.yaml`
```yaml
 ...
  <your_service>:           # service name.  
    ...
    status: *decommission   # service status.  
```

### Event: When The Engineer delegated services ownership to other eng.
* __Responsible persons:__ 
  * Engineering Manager
  * Service Owner  
* __Action__:
You should assign other engineers as owners of these services [property 'owner']. The file:
`/<product>/specifications/<service_module>.yaml`
```yaml
 ...
  <your_service>:           # service name.  
    ...
    owner: roman.shafeev
```

### Event: When you found a mistake in *.yaml specifications!
* __Action__:
Feel free to add fix and merge to the develop branch :)!

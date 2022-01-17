/* eslint-disable */
export const testData = {
    code: 200,
    msg: 'success',
    timestamp: 0,
    entityids: [
        'HOST_0001',
        'HOST_0002',
        'HOST_0003',
        'HOST_0004',
        'CONTAINER_1001',
        'CONTAINER_1002',
        'TASK_2001',
        'TASK_2002',
        'TASK_2003',
        'TASK_2004',
        'ENDPOINT_3001',
        'TCP_LINK_4001',
        'TCP_LINK_4002',
        'TCP_LINK_4003',
        'TCP_LINK_4004',
        'IPVS_LINK_5001'
    ],
    entities: [
        //  {
        //	"entityid": "",
        //	"type": "",
        //	"name": "",
        //	"level": "",
        //	"dependingitems": [
        //	  {
        //		"relation_id": "",
        //		"layer": "",
        //		"target": {
        //		  "type": "",
        //		  "entityid": ""
        //		}
        //	  },
        //	],
        //	"dependeditems": [
        //	  {
        //		"relation_id": "",
        //		"layer": "",
        //		"target": {
        //		  "type": "",
        //		  "entityid": ""
        //		}
        //	  }
        //	],
        //	"attrs": [
        //	  {
        //		"key": "",
        //		"value": "",
        //		"vtype": ""
        //	  }
        //	],
        //	"anomaly": {}
        //  },
        {
            entityid: 'HOST_0001',
            type: 'host',
            name: 'k8s-node1',
            level: 'HOST',
            dependingitems: [],
            dependeditems: [
                {
                    relation_id: 'runs_on',
                    layer: 'direct',
                    target: {
                        type: 'task',
                        entityid: 'TASK_2001'
                    }
                },
                {
                    relation_id: 'connect',
                    layer: 'indirect',
                    target: {
                        type: 'host',
                        entityid: 'HOST_0002'
                    }
                },
                {
                    relation_id: 'connect',
                    layer: 'indirect',
                    target: {
                        type: 'host',
                        entityid: 'HOST_0004'
                    }
                }
            ],
            attrs: [
                {
                    key: 'hostname',
                    value: 'k8s-node1',
                    vtype: 'string'
                }
            ],
            anomaly: {}
        },
        {
            entityid: 'HOST_0002',
            type: 'host',
            name: 'k8s-node2',
            level: 'HOST',
            dependingitems: [
                {
                    relation_id: 'connect',
                    layer: 'indirect',
                    target: {
                        type: 'host',
                        entityid: 'HOST_0001'
                    }
                }
            ],
            dependeditems: [
                {
                    relation_id: 'runs_on',
                    layer: 'direct',
                    target: {
                        type: 'task',
                        entityid: 'TASK_2002'
                    }
                }
            ],
            attrs: [
                {
                    key: 'hostname',
                    value: 'k8s-node2',
                    vtype: 'string'
                }
            ],
            anomaly: {}
        },
        {
            entityid: 'HOST_0003',
            type: 'host',
            name: 'k8s-node3',
            level: 'HOST',
            dependingitems: [],
            dependeditems: [
                {
                    relation_id: 'runs_on',
                    layer: 'direct',
                    target: {
                        type: 'container',
                        entityid: 'CONTAINER_1001'
                    }
                }
            ],
            attrs: [
                {
                    key: 'hostname',
                    value: 'k8s-node3',
                    vtype: 'string'
                }
            ],
            anomaly: {}
        },
        {
            entityid: 'HOST_0004',
            type: 'host',
            name: 'k8s-node4',
            level: 'HOST',
            dependingitems: [
                {
                    relation_id: 'connect',
                    layer: 'indirect',
                    target: {
                        type: 'host',
                        entityid: 'HOST_0001'
                    }
                }
            ],
            dependeditems: [
                {
                    relation_id: 'runs_on',
                    layer: 'direct',
                    target: {
                        type: 'container',
                        entityid: 'CONTAINER_1002'
                    }
                }
            ],
            attrs: [
                {
                    key: 'hostname',
                    value: 'k8s-node4',
                    vtype: 'string'
                }
            ],
            anomaly: {}
        },
        {
            entityid: 'CONTAINER_1001',
            type: 'container',
            name: 'container1',
            level: 'CONTAINER',
            dependingitems: [
                {
                    relation_id: 'runs_on',
                    layer: 'direct',
                    target: {
                        type: 'host',
                        entityid: 'HOST_0003'
                    }
                }
            ],
            dependeditems: [
                {
                    relation_id: 'runs_on',
                    layer: 'direct',
                    target: {
                        type: 'task',
                        entityid: 'TASK_2003'
                    }
                }
            ],
            attrs: [
                {
                    key: 'container_name',
                    value: 'container1',
                    vtype: 'string'
                }
            ],
            anomaly: {}
        },
        {
            entityid: 'CONTAINER_1002',
            type: 'container',
            name: 'container2',
            level: 'CONTAINER',
            dependingitems: [
                {
                    relation_id: 'runs_on',
                    layer: 'direct',
                    target: {
                        type: 'host',
                        entityid: 'HOST_0004'
                    }
                }
            ],
            dependeditems: [
                {
                    relation_id: 'runs_on',
                    layer: 'direct',
                    target: {
                        type: 'task',
                        entityid: 'TASK_2004'
                    }
                }
            ],
            attrs: [
                {
                    key: 'container_name',
                    value: 'container2',
                    vtype: 'string'
                }
            ],
            anomaly: {}
        },
        {
            entityid: 'TASK_2001',
            type: 'task',
            name: 'python3_server1',
            level: 'PROCESS',
            dependingitems: [
                {
                    relation_id: 'runs_on',
                    layer: 'direct',
                    target: {
                        type: 'host',
                        entityid: 'HOST_0001'
                    }
                }
            ],
            dependeditems: [
                {
                    relation_id: 'belongs_to',
                    layer: 'direct',
                    target: {
                        type: 'endpoint',
                        entityid: 'ENDPOINT_3001'
                    }
                },
                {
                    relation_id: 'belongs_to',
                    layer: 'direct',
                    target: {
                        type: 'tcp_link',
                        entityid: 'TCP_LINK_4001'
                    }
                },
                {
                    relation_id: 'belongs_to',
                    layer: 'direct',
                    target: {
                        type: 'tcp_link',
                        entityid: 'TCP_LINK_4003'
                    }
                },
                {
                    relation_id: 'connect',
                    layer: 'indirect',
                    target: {
                        type: 'task',
                        entityid: 'TASK_2002'
                    }
                },
                {
                    relation_id: 'connect',
                    layer: 'indirect',
                    target: {
                        type: 'task',
                        entityid: 'TASK_2004'
                    }
                }
            ],
            attrs: [
                {
                    key: 'task_name',
                    value: 'python3_server1',
                    vtype: 'string'
                }
            ],
            anomaly: {}
        },
        {
            entityid: 'TASK_2002',
            type: 'task',
            name: 'python3_client1',
            level: 'PROCESS',
            dependingitems: [
                {
                    relation_id: 'runs_on',
                    layer: 'direct',
                    target: {
                        type: 'host',
                        entityid: 'HOST_0002'
                    }
                },
                {
                    relation_id: 'connect',
                    layer: 'indirect',
                    target: {
                        type: 'task',
                        entityid: 'TASK_2001'
                    }
                }
            ],
            dependeditems: [
                {
                    relation_id: 'belongs_to',
                    layer: 'direct',
                    target: {
                        type: 'tcp_link',
                        entityid: 'TCP_LINK_4002'
                    }
                }
            ],
            attrs: [
                {
                    key: 'task_name',
                    value: 'python3_client1',
                    vtype: 'string'
                }
            ],
            anomaly: {}
        },
        {
            entityid: 'TASK_2003',
            type: 'task',
            name: 'ipvs_lb',
            level: 'PROCESS',
            dependingitems: [
                {
                    relation_id: 'runs_on',
                    layer: 'direct',
                    target: {
                        type: 'container',
                        entityid: 'CONTAINER_1001'
                    }
                }
            ],
            dependeditems: [
                {
                    relation_id: 'belongs_to',
                    layer: 'direct',
                    target: {
                        type: 'ipvs_link',
                        entityid: 'IPVS_LINK_5001'
                    }
                }
            ],
            attrs: [
                {
                    key: 'task_name',
                    value: 'ipvs_lb',
                    vtype: 'string'
                }
            ],
            anomaly: {}
        },
        {
            entityid: 'TASK_2004',
            type: 'task',
            name: 'python3_client2',
            level: 'PROCESS',
            dependingitems: [
                {
                    relation_id: 'runs_on',
                    layer: 'direct',
                    target: {
                        type: 'container',
                        entityid: 'CONTAINER_1002'
                    }
                },
                {
                    relation_id: 'connect',
                    layer: 'indirect',
                    target: {
                        type: 'task',
                        entityid: 'TASK_2001'
                    }
                }
            ],
            dependeditems: [
                {
                    relation_id: 'belongs_to',
                    layer: 'direct',
                    target: {
                        type: 'tcp_link',
                        entityid: 'TCP_LINK_4004'
                    }
                }
            ],
            attrs: [
                {
                    key: 'task_name',
                    value: 'python3_client2',
                    vtype: 'string'
                }
            ],
            anomaly: {}
        },
        {
            entityid: 'TCP_LINK_4001',
            type: 'tcp_link',
            name: 'tcp_link1',
            level: 'RPC',
            dependingitems: [
                {
                    relation_id: 'belongs_to',
                    layer: 'direct',
                    target: {
                        type: 'task',
                        entityid: 'TASK_2001'
                    }
                },
                {
                    relation_id: 'is_peer',
                    layer: 'direct',
                    target: {
                        type: 'tcp_link',
                        entityid: 'TCP_LINK_4002'
                    }
                }
            ],
            dependeditems: [
                {
                    relation_id: 'is_peer',
                    layer: 'direct',
                    target: {
                        type: 'tcp_link',
                        entityid: 'TCP_LINK_4002'
                    }
                }
            ],
            attrs: [
                {
                    key: 'link_name',
                    value: 'tcp_link1',
                    vtype: 'string'
                }
            ],
            anomaly: {}
        },
        {
            entityid: 'TCP_LINK_4002',
            type: 'tcp_link',
            name: 'tcp_link2',
            level: 'RPC',
            dependingitems: [
                {
                    relation_id: 'belongs_to',
                    layer: 'direct',
                    target: {
                        type: 'task',
                        entityid: 'TASK_2002'
                    }
                },
                {
                    relation_id: 'is_peer',
                    layer: 'direct',
                    target: {
                        type: 'tcp_link',
                        entityid: 'TCP_LINK_4001'
                    }
                }
            ],
            dependeditems: [
                {
                    relation_id: 'is_peer',
                    layer: 'direct',
                    target: {
                        type: 'tcp_link',
                        entityid: 'TCP_LINK_4001'
                    }
                }
            ],
            attrs: [
                {
                    key: 'link_name',
                    value: 'tcp_link2',
                    vtype: 'string'
                }
            ],
            anomaly: {}
        },
        {
            entityid: 'TCP_LINK_4003',
            type: 'tcp_link',
            name: 'tcp_link3',
            level: 'RPC',
            dependingitems: [
                {
                    relation_id: 'belongs_to',
                    layer: 'direct',
                    target: {
                        type: 'task',
                        entityid: 'TASK_2001'
                    }
                },
                {
                    relation_id: 'is_server',
                    layer: 'direct',
                    target: {
                        type: 'ipvs_link',
                        entityid: 'IPVS_LINK_5001'
                    }
                }
            ],
            dependeditems: [],
            attrs: [
                {
                    key: 'link_name',
                    value: 'tcp_link3',
                    vtype: 'string'
                }
            ],
            anomaly: {}
        },
        {
            entityid: 'TCP_LINK_4004',
            type: 'tcp_link',
            name: 'tcp_link4',
            level: 'RPC',
            dependingitems: [
                {
                    relation_id: 'belongs_to',
                    layer: 'direct',
                    target: {
                        type: 'task',
                        entityid: 'TASK_2004'
                    }
                },
                {
                    relation_id: 'is_client',
                    layer: 'direct',
                    target: {
                        type: 'ipvs_link',
                        entityid: 'IPVS_LINK_5001'
                    }
                }
            ],
            dependeditems: [],
            attrs: [
                {
                    key: 'link_name',
                    value: 'tcp_link4',
                    vtype: 'string'
                }
            ],
            anomaly: {}
        },
        {
            entityid: 'IPVS_LINK_5001',
            type: 'ipvs_link',
            name: 'ipvs_link1',
            level: 'LB',
            dependingitems: [
                {
                    relation_id: 'belongs_to',
                    layer: 'direct',
                    target: {
                        type: 'task',
                        entityid: 'TASK_2003'
                    }
                }
            ],
            dependeditems: [
                {
                    relation_id: 'is_client',
                    layer: 'direct',
                    target: {
                        type: 'tcp_link',
                        entityid: 'TCP_LINK_4004'
                    }
                },
                {
                    relation_id: 'is_server',
                    layer: 'direct',
                    target: {
                        type: 'tcp_link',
                        entityid: 'TCP_LINK_4003'
                    }
                }
            ],
            attrs: [
                {
                    key: 'link_name',
                    value: 'ipvs_link1',
                    vtype: 'string'
                }
            ],
            anomaly: {}
        }
    ]
};

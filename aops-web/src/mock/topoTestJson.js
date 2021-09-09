/* eslint-disable */
export const testJson = {
  "nodes": [
    {"id": "0", "label": "n0", "class": "c0","x": 1000, "y": -100 },
    {"id": "1", "label": "n1", "class": "c0","x": 300, "y": -10 },
    {"id": "2", "label": "n2", "class": "c0","x": 10, "y": 10 },
    {"id": "3", "label": "n3", "class": "c0","x": 320, "y": -100 },
    {"id": "4", "label": "n4", "class": "c0","x": 100, "y": 900 },
    {"id": "5", "label": "n5", "class": "c0","x": 120, "y": 213 },
    {"id": "6", "label": "n6", "class": "c1","x": 543, "y": 12 },
    {"id": "7", "label": "n7", "class": "c1","x": 543, "y": -100 },
    {"id": "8", "label": "n8", "class": "c1","x": 1, "y": 0 },
    {"id": "9", "label": "n9", "class": "c1","x": 0, "y": -222 },
    {"id": "10", "label": "n10", "class": "c1","x": 435, "y": 69 },
    {"id": "11", "label": "n11", "class": "c1","x": 23, "y": 10 },
    {"id": "12", "label": "n12", "class": "c1","x": -129, "y": 39 },
    {"id": "13", "label": "n13", "class": "c2","x": 234, "y": 843 },
    {"id": "14", "label": "n14", "class": "c2","x": -301, "y": 129 },
    {"id": "15", "label": "n15", "class": "c2","x": -20, "y": -76 },
    {"id": "16", "label": "n16", "class": "c2","x": 1220, "y": -34 },
    {"id": "17", "label": "n17", "class": "c2","x": -10, "y": 954 },
    {"id": "18", "label": "n18", "class": "c2","x": 492, "y": 123 },
    {"id": "19", "label": "n19", "class": "c2","x": 123, "y": -241 }
  ],
  "edges": [
    {"source": "0", "target": "1", "label": "e0-1", "weight": 1 },
    {"source": "0", "target": "2", "label": "e0-2", "weight": 2 },
    {"source": "0", "target": "3", "label": "e0-3", "weight": 3 },
    {"source": "0", "target": "4", "label": "e0-4", "weight": 1.4 },
    {"source": "0", "target": "5", "label": "e0-5", "weight": 2 },
    {"source": "0", "target": "7", "label": "e0-7", "weight": 2 },
    {"source": "0", "target": "8", "label": "e0-8", "weight": 2 },
    {"source": "0", "target": "9", "label": "e0-9", "weight": 1.3 },
    {"source": "0", "target": "10", "label": "e0-10", "weight": 1.5 },
    {"source": "0", "target": "11", "label": "e0-11", "weight": 1 },
    {"source": "0", "target": "13", "label": "e0-13", "weight": 10 },
    {"source": "0", "target": "14", "label": "e0-14", "weight": 2 },
    {"source": "0", "target": "15", "label": "e0-15", "weight": 0.5 },
    {"source": "0", "target": "16", "label": "e0-16", "weight": 0.8 },
    {"source": "2", "target": "3", "label": "e2-3", "weight": 1 },
    {"source": "4", "target": "5", "label": "e4-5", "weight": 1.4 },
    {"source": "4", "target": "6", "label": "e4-6", "weight": 2.1 },
    {"source": "5", "target": "6", "label": "e5-6", "weight": 1.9 },
    {"source": "7", "target": "13", "label": "e7-13", "weight": 0.5 },
    {"source": "8", "target": "14", "label": "e8-14", "weight": 0.8 },
    {"source": "9", "target": "10", "label": "e9-10", "weight": 0.2 },
    {"source": "10", "target": "14", "label": "e10-14", "weight": 1 },
    {"source": "10", "target": "12", "label": "e10-12", "weight": 1.2 },
    {"source": "11", "target": "14", "label": "e11-14", "weight": 1.2 },
    {"source": "12", "target": "13", "label": "e12-13", "weight": 2.1 },
    {"source": "16", "target": "17", "label": "e16-17", "weight": 2.5 },
    {"source": "16", "target": "18", "label": "e16-18", "weight": 3 },
    {"source": "17", "target": "18", "label": "e17-18", "weight": 2.6 },
    {"source": "18", "target": "19", "label": "e18-19", "weight": 1.6 }
  ]
}

export const topoSimple = {
  "code": 200,
  "entities": [
    {
      "attrs": [
        {
          "key": "link_count",
          "value": "1",
          "vtype": "string"
        },
        {
          "key": "rx_bytes",
          "value": "3613",
          "vtype": "string"
        },
        {
          "key": "tx_bytes",
          "value": "1590412",
          "vtype": "string"
        },
        {
          "key": "packets_out",
          "value": "1452",
          "vtype": "string"
        },
        {
          "key": "packets_in",
          "value": "655",
          "vtype": "string"
        },
        {
          "key": "retran_packets",
          "value": "6",
          "vtype": "string"
        },
        {
          "key": "lost_packets",
          "value": "0",
          "vtype": "string"
        },
        {
          "key": "rtt",
          "value": "172",
          "vtype": "string"
        }
      ],
      "dependeditems": {
        "calls": {
          "id": "exe.ffmpeg",
          "type": "PROCESS"
        }
      },
      "dependingitems": {
        "calls": {
          "id": "ipvs-fnat.ipvs",
          "type": "PROCESS"
        }
      },
      "entityid": "exe.ffmpeg.ipvs-fnat.ipvs.tcp_link",
      "name": "exe.ffmpeg.ipvs-fnat.ipvs.tcp_link",
      "type": "TCP-LINK"
    },
    {
      "attrs": [
        {
          "key": "link_count",
          "value": "1",
          "vtype": "string"
        },
        {
          "key": "rx_bytes",
          "value": "1737381",
          "vtype": "string"
        },
        {
          "key": "tx_bytes",
          "value": "142",
          "vtype": "string"
        },
        {
          "key": "packets_out",
          "value": "326",
          "vtype": "string"
        },
        {
          "key": "packets_in",
          "value": "365",
          "vtype": "string"
        },
        {
          "key": "retran_packets",
          "value": "0",
          "vtype": "string"
        },
        {
          "key": "lost_packets",
          "value": "0",
          "vtype": "string"
        },
        {
          "key": "rtt",
          "value": "114",
          "vtype": "string"
        }
      ],
      "dependeditems": {
        "calls": {
          "id": "haproxy1.haproxy",
          "type": "PROCESS"
        }
      },
      "dependingitems": {
        "calls": {
          "id": "vlb-origin.nginx",
          "type": "PROCESS"
        }
      },
      "entityid": "haproxy1.haproxy.vlb-origin.nginx.tcp_link",
      "name": "haproxy1.haproxy.vlb-origin.nginx.tcp_link",
      "type": "TCP-LINK"
    },
    {
      "attrs": [
        {
          "key": "link_count",
          "value": "1",
          "vtype": "string"
        },
        {
          "key": "rx_bytes",
          "value": "1737381",
          "vtype": "string"
        },
        {
          "key": "tx_bytes",
          "value": "91",
          "vtype": "string"
        },
        {
          "key": "packets_out",
          "value": "336",
          "vtype": "string"
        },
        {
          "key": "packets_in",
          "value": "386",
          "vtype": "string"
        },
        {
          "key": "retran_packets",
          "value": "0",
          "vtype": "string"
        },
        {
          "key": "lost_packets",
          "value": "0",
          "vtype": "string"
        },
        {
          "key": "rtt",
          "value": "5413",
          "vtype": "string"
        }
      ],
      "dependeditems": {
        "calls": {
          "id": "exe.curl",
          "type": "PROCESS"
        }
      },
      "dependingitems": {
        "calls": {
          "id": "ipvs-fnat.ipvs",
          "type": "PROCESS"
        }
      },
      "entityid": "exe.curl.ipvs-fnat.ipvs.tcp_link",
      "name": "exe.curl.ipvs-fnat.ipvs.tcp_link",
      "type": "TCP-LINK"
    },
    {
      "attrs": [
        {
          "key": "link_count",
          "value": "1",
          "vtype": "string"
        },
        {
          "key": "rx_bytes",
          "value": "3613",
          "vtype": "string"
        },
        {
          "key": "tx_bytes",
          "value": "1590415",
          "vtype": "string"
        },
        {
          "key": "packets_out",
          "value": "1446",
          "vtype": "string"
        },
        {
          "key": "packets_in",
          "value": "614",
          "vtype": "string"
        },
        {
          "key": "retran_packets",
          "value": "0",
          "vtype": "string"
        },
        {
          "key": "lost_packets",
          "value": "0",
          "vtype": "string"
        },
        {
          "key": "rtt",
          "value": "151",
          "vtype": "string"
        }
      ],
      "dependeditems": {
        "calls": {
          "id": "exe.ffmpeg",
          "type": "PROCESS"
        }
      },
      "dependingitems": {
        "calls": {
          "id": "ipvs-fnat.ipvs",
          "type": "PROCESS"
        }
      },
      "entityid": "exe.ffmpeg.ipvs-fnat.ipvs.tcp_link",
      "name": "exe.ffmpeg.ipvs-fnat.ipvs.tcp_link",
      "type": "TCP-LINK"
    },
    {
      "attrs": [
        {
          "key": "link_count",
          "value": "1",
          "vtype": "string"
        },
        {
          "key": "rx_bytes",
          "value": "1599435",
          "vtype": "string"
        },
        {
          "key": "tx_bytes",
          "value": "94",
          "vtype": "string"
        },
        {
          "key": "packets_out",
          "value": "253",
          "vtype": "string"
        },
        {
          "key": "packets_in",
          "value": "283",
          "vtype": "string"
        },
        {
          "key": "retran_packets",
          "value": "0",
          "vtype": "string"
        },
        {
          "key": "lost_packets",
          "value": "0",
          "vtype": "string"
        },
        {
          "key": "rtt",
          "value": "409",
          "vtype": "string"
        }
      ],
      "dependeditems": {
        "calls": {
          "id": "exe.curl",
          "type": "PROCESS"
        }
      },
      "dependingitems": {
        "calls": {
          "id": "ipvs-fnat.ipvs",
          "type": "PROCESS"
        }
      },
      "entityid": "exe.curl.ipvs-fnat.ipvs.tcp_link",
      "name": "exe.curl.ipvs-fnat.ipvs.tcp_link",
      "type": "TCP-LINK"
    },
    {
      "attrs": [
        {
          "key": "link_count",
          "value": "1",
          "vtype": "string"
        },
        {
          "key": "rx_bytes",
          "value": "1598608",
          "vtype": "string"
        },
        {
          "key": "tx_bytes",
          "value": "113",
          "vtype": "string"
        },
        {
          "key": "packets_out",
          "value": "327",
          "vtype": "string"
        },
        {
          "key": "packets_in",
          "value": "366",
          "vtype": "string"
        },
        {
          "key": "retran_packets",
          "value": "0",
          "vtype": "string"
        },
        {
          "key": "lost_packets",
          "value": "0",
          "vtype": "string"
        },
        {
          "key": "rtt",
          "value": "114",
          "vtype": "string"
        }
      ],
      "dependeditems": {
        "calls": {
          "id": "nginx1.nginx",
          "type": "PROCESS"
        }
      },
      "dependingitems": {
        "calls": {
          "id": "vlb-origin.nginx",
          "type": "PROCESS"
        }
      },
      "entityid": "nginx1.nginx.vlb-origin.nginx.tcp_link",
      "name": "nginx1.nginx.vlb-origin.nginx.tcp_link",
      "type": "TCP-LINK"
    },
    {
      "attrs": [
        {
          "key": "link_count",
          "value": "1",
          "vtype": "string"
        },
        {
          "key": "rx_bytes",
          "value": "0",
          "vtype": "string"
        },
        {
          "key": "tx_bytes",
          "value": "1537",
          "vtype": "string"
        },
        {
          "key": "packets_out",
          "value": "3",
          "vtype": "string"
        },
        {
          "key": "packets_in",
          "value": "1",
          "vtype": "string"
        },
        {
          "key": "retran_packets",
          "value": "0",
          "vtype": "string"
        },
        {
          "key": "lost_packets",
          "value": "0",
          "vtype": "string"
        },
        {
          "key": "rtt",
          "value": "247",
          "vtype": "string"
        }
      ],
      "dependeditems": {
        "calls": {
          "id": "ipvs-fnat.ipvs",
          "type": "PROCESS"
        }
      },
      "dependingitems": {
        "calls": {
          "id": "vlb-origin.nginx",
          "type": "PROCESS"
        }
      },
      "entityid": "ipvs-fnat.ipvs.vlb-origin.nginx.tcp_link",
      "name": "ipvs-fnat.ipvs.vlb-origin.nginx.tcp_link",
      "type": "TCP-LINK"
    },
    {
      "attrs": [
        {
          "key": "link_count",
          "value": "1",
          "vtype": "string"
        },
        {
          "key": "rx_bytes",
          "value": "0",
          "vtype": "string"
        },
        {
          "key": "tx_bytes",
          "value": "90",
          "vtype": "string"
        },
        {
          "key": "packets_out",
          "value": "3",
          "vtype": "string"
        },
        {
          "key": "packets_in",
          "value": "0",
          "vtype": "string"
        },
        {
          "key": "retran_packets",
          "value": "0",
          "vtype": "string"
        },
        {
          "key": "lost_packets",
          "value": "0",
          "vtype": "string"
        },
        {
          "key": "rtt",
          "value": "220",
          "vtype": "string"
        }
      ],
      "dependeditems": {
        "calls": {
          "id": "ipvs-fnat.ipvs",
          "type": "PROCESS"
        }
      },
      "dependingitems": {
        "calls": {
          "id": "haproxy1.haproxy",
          "type": "PROCESS"
        }
      },
      "entityid": "ipvs-fnat.ipvs.haproxy1.haproxy.tcp_link",
      "name": "ipvs-fnat.ipvs.haproxy1.haproxy.tcp_link",
      "type": "TCP-LINK"
    },
    {
      "attrs": [
        {
          "key": "link_count",
          "value": "1",
          "vtype": "string"
        },
        {
          "key": "rx_bytes",
          "value": "0",
          "vtype": "string"
        },
        {
          "key": "tx_bytes",
          "value": "93",
          "vtype": "string"
        },
        {
          "key": "packets_out",
          "value": "3",
          "vtype": "string"
        },
        {
          "key": "packets_in",
          "value": "1",
          "vtype": "string"
        },
        {
          "key": "retran_packets",
          "value": "0",
          "vtype": "string"
        },
        {
          "key": "lost_packets",
          "value": "0",
          "vtype": "string"
        },
        {
          "key": "rtt",
          "value": "266",
          "vtype": "string"
        }
      ],
      "dependeditems": {
        "calls": {
          "id": "ipvs-fnat.ipvs",
          "type": "PROCESS"
        }
      },
      "dependingitems": {
        "calls": {
          "id": "nginx1.nginx",
          "type": "PROCESS"
        }
      },
      "entityid": "ipvs-fnat.ipvs.nginx1.nginx.tcp_link",
      "name": "ipvs-fnat.ipvs.nginx1.nginx.tcp_link",
      "type": "TCP-LINK"
    },
    {
      "attrs": [
        {
          "key": "example",
          "value": "0xabcd",
          "vtype": "int"
        }
      ],
      "dependeditems": {
        "calls": [],
        "runOns": []
      },
      "dependingitems": {
        "calls": [
          {
            "id": "exe.ffmpeg.ipvs-fnat.ipvs.tcp_link",
            "type": "TCP_LINK"
          },
          {
            "id": "exe.ffmpeg.ipvs-fnat.ipvs.tcp_link",
            "type": "TCP_LINK"
          }
        ],
        "runOns": {
          "id": "exe",
          "type": "VM"
        }
      },
      "entityid": "exe.ffmpeg",
      "name": "exe.ffmpeg",
      "type": "PROCESS"
    },
    {
      "attrs": [
        {
          "key": "example",
          "value": "0xabcd",
          "vtype": "int"
        }
      ],
      "dependeditems": {
        "calls": [
          {
            "id": "exe.curl.ipvs-fnat.ipvs.tcp_link",
            "type": "TCP_LINK"
          },
          {
            "id": "exe.ffmpeg.ipvs-fnat.ipvs.tcp_link",
            "type": "TCP_LINK"
          },
          {
            "id": "exe.curl.ipvs-fnat.ipvs.tcp_link",
            "type": "TCP_LINK"
          },
          {
            "id": "exe.ffmpeg.ipvs-fnat.ipvs.tcp_link",
            "type": "TCP_LINK"
          }
        ],
        "runOns": []
      },
      "dependingitems": {
        "calls": [
          {
            "id": "ipvs-fnat.ipvs.nginx1.nginx.tcp_link",
            "type": "TCP_LINK"
          },
          {
            "id": "ipvs-fnat.ipvs.haproxy1.haproxy.tcp_link",
            "type": "TCP_LINK"
          },
          {
            "id": "ipvs-fnat.ipvs.vlb-origin.nginx.tcp_link",
            "type": "TCP_LINK"
          }
        ],
        "runOns": {
          "id": "ipvs-fnat",
          "type": "VM"
        }
      },
      "entityid": "ipvs-fnat.ipvs",
      "name": "ipvs-fnat.ipvs",
      "type": "PROCESS"
    },
    {
      "attrs": [
        {
          "key": "example",
          "value": "0xabcd",
          "vtype": "int"
        }
      ],
      "dependeditems": {
        "calls": [
          {
            "id": "ipvs-fnat.ipvs.haproxy1.haproxy.tcp_link",
            "type": "TCP_LINK"
          }
        ],
        "runOns": []
      },
      "dependingitems": {
        "calls": [
          {
            "id": "haproxy1.haproxy.vlb-origin.nginx.tcp_link",
            "type": "TCP_LINK"
          }
        ],
        "runOns": {
          "id": "haproxy1",
          "type": "VM"
        }
      },
      "entityid": "haproxy1.haproxy",
      "name": "haproxy1.haproxy",
      "type": "PROCESS"
    },
    {
      "attrs": [
        {
          "key": "example",
          "value": "0xabcd",
          "vtype": "int"
        }
      ],
      "dependeditems": {
        "calls": [
          {
            "id": "ipvs-fnat.ipvs.vlb-origin.nginx.tcp_link",
            "type": "TCP_LINK"
          },
          {
            "id": "nginx1.nginx.vlb-origin.nginx.tcp_link",
            "type": "TCP_LINK"
          },
          {
            "id": "haproxy1.haproxy.vlb-origin.nginx.tcp_link",
            "type": "TCP_LINK"
          }
        ],
        "runOns": []
      },
      "dependingitems": {
        "calls": [],
        "runOns": {
          "id": "vlb-origin",
          "type": "VM"
        }
      },
      "entityid": "vlb-origin.nginx",
      "name": "vlb-origin.nginx",
      "type": "PROCESS"
    },
    {
      "attrs": [
        {
          "key": "example",
          "value": "0xabcd",
          "vtype": "int"
        }
      ],
      "dependeditems": {
        "calls": [],
        "runOns": []
      },
      "dependingitems": {
        "calls": [
          {
            "id": "exe.curl.ipvs-fnat.ipvs.tcp_link",
            "type": "TCP_LINK"
          },
          {
            "id": "exe.curl.ipvs-fnat.ipvs.tcp_link",
            "type": "TCP_LINK"
          }
        ],
        "runOns": {
          "id": "exe",
          "type": "VM"
        }
      },
      "entityid": "exe.curl",
      "name": "exe.curl",
      "type": "PROCESS"
    },
    {
      "attrs": [
        {
          "key": "example",
          "value": "0xabcd",
          "vtype": "int"
        }
      ],
      "dependeditems": {
        "calls": [
          {
            "id": "ipvs-fnat.ipvs.nginx1.nginx.tcp_link",
            "type": "TCP_LINK"
          }
        ],
        "runOns": [
          {
            "id": "ipvs-fnat.ipvs.vlb-origin.nginx.nginx_link",
            "type": "NGINX-LINK"
          }
        ]
      },
      "dependingitems": {
        "calls": [
          {
            "id": "nginx1.nginx.vlb-origin.nginx.tcp_link",
            "type": "TCP_LINK"
          }
        ],
        "runOns": {
          "id": "nginx1",
          "type": "VM"
        }
      },
      "entityid": "nginx1.nginx",
      "name": "nginx1.nginx",
      "type": "PROCESS"
    },
    {
      "dependeditems": {
        "calls": {
          "id": "ipvs-fnat.ipvs",
          "type": "PROCESS"
        }
      },
      "dependingitems": {
        "calls": {
          "id": "vlb-origin.nginx",
          "type": "PROCESS"
        },
        "runOns": {
          "id": "nginx1.nginx",
          "type": "PROCESS"
        }
      },
      "entityid": "ipvs-fnat.ipvs.vlb-origin.nginx.nginx_link",
      "name": "ipvs-fnat.ipvs.vlb-origin.nginx.nginx_link",
      "type": "NGINX-LINK"
    }
  ],
  "msg": "Successful",
  "timestamp": 12345678
}


export const treeTestData = {
  "label":"重启类故障树（简）",
  "node_id": 'n1',
  "value":null,
  "condition":"硬件问题 || 软件问题 || 内核问题",
  "description":"",
  "advice":"",
  "children":[
      {
          "label":"硬件问题",
          "node_id": 'n1-n1',
          "value":null,
          "condition":"硬件问题1 &amp;&amp; 硬件问题2",
          "description":"出现硬件问题",
          "advice":"ccc ddd",
          "children":[
              {
                  "label":"硬件问题1",
                  "node_id": 'n1-n1-n1',
                  "value":null,
                  "condition":"检查项1 || 硬件子问题1",
                  "description":"",
                  "advice":"",
                  "children":[
                      {
                          "label":"检查项1",
                          "node_id": 'n1-n1-n1-n1',
                          "value":null,
                          "check item":"check_item1"
                      },
                      {
                          "label":"硬件子问题1",
                          "node_id": 'n1-n1-n1-n2',
                          "value":null,
                          "condition":"检查项2 &amp;&amp; 检查项3",
                          "description":"",
                          "advice":"",
                          "children":[
                              {
                                  "label":"检查项2",
                                  "node_id": 'n1-n1-n1-n2-n1',
                                  "value":null,
                                  "check item":"check_item2"
                              },
                              {
                                  "label":"检查项3",
                                  "node_id": 'n1-n1-n1-n2-n2',
                                  "value":null,
                                  "check item":"check_item3"
                              }
                          ]
                      }
                  ]
              },
              {
                  "label":"硬件问题2",
                  "node_id": 'n1-n1-n2',
                  "value":null,
                  "condition":"硬件子问题2 || 硬件子问题4",
                  "description":"",
                  "advice":"",
                  "children":[
                      {
                          "label":"硬件子问题2",
                          "node_id": 'n1-n1-n2-n1',
                          "value":null,
                          "condition":"硬件子问题3",
                          "description":"",
                          "advice":"",
                          "children":[
                              {
                                  "label":"硬件子问题3",
                                  "node_id": 'n1-n1-n2-n1-n1',
                                  "value":null,
                                  "condition":"检查项3 &amp;&amp; 检查项4",
                                  "description":"",
                                  "advice":"",
                                  "children":[
                                      {
                                          "label":"检查项3",
                                          "node_id": 'n1-n1-n2-n1-n1-n1',
                                          "value":null,
                                          "check item":"check_item3"
                                      },
                                      {
                                          "label":"检查项4",
                                          "node_id": 'n1-n1-n2-n1-n1-n2',
                                          "value":null,
                                          "check item":"check_item4"
                                      }
                                  ]
                              }
                          ]
                      },
                      {
                          "label":"硬件子问题4",
                          "node_id": 'n1-n1-n2-n2',
                          "value":null,
                          "condition":"检查项5 || 检查项6",
                          "description":"aaa bbb",
                          "advice":"",
                          "children":[
                              {
                                  "label":"检查项5",
                                  "node_id": 'n1-n1-n2-n2-n1',
                                  "value":null,
                                  "check item":"check_item5"
                              },
                              {
                                  "label":"检查项6",
                                  "node_id": 'n1-n1-n2-n2-n2',
                                  "value":null,
                                  "check item":"check_item6"
                              }
                          ]
                      }
                  ]
              }
          ]
      },
      {
          "label":"软件问题",
          "node_id": 'n1-n2',
          "value":null,
          "condition":"软件问题1",
          "description":"",
          "advice":"",
          "children":[
              {
                  "label":"软件问题1",
                  "node_id": 'n1-n2-n1',
                  "value":null,
                  "condition":"软件子问题1",
                  "description":"",
                  "advice":"",
                  "children":[
                      {
                          "label":"软件子问题1",
                          "node_id": 'n1-n2-n1-n1',
                          "value":null,
                          "condition":"软件子问题2",
                          "description":"",
                          "advice":"",
                          "children":[
                              {
                                  "label":"软件子问题2",
                                  "node_id": 'n1-n2-n1-n1-n1',
                                  "value":null,
                                  "condition":"检查项7",
                                  "description":"",
                                  "advice":"",
                                  "children":[
                                      {
                                          "label":"检查项7",
                                          "node_id": 'n1-n2-n1-n1-n1-n1',
                                          "value":null,
                                          "check item":"check_item7"
                                      }
                                  ]
                              }
                          ]
                      }
                  ]
              }
          ]
      },
      {
          "label":"内核问题",
          "node_id": 'n1-n3',
          "value":null,
          "condition":"检查项8 &amp;&amp; 检查项9",
          "description":"",
          "advice":"",
          "children":[
              {
                  "label":"检查项8",
                  "node_id": 'n1-n3-n1',
                  "value":null,
                  "check item":"check_item8"
              },
              {
                  "label":"检查项9",
                  "node_id": 'n1-n3-n2',
                  "value":null,
                  "check item":"check_item9"
              }
          ]
      }
  ]
}
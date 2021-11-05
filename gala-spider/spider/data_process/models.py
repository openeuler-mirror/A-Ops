from dataclasses import dataclass
from dataclasses import field


@dataclass
class Node:
    def node_id(self) -> str:
        pass


@dataclass
class HostNode(Node):
    host_name: str
    processes: list = field(default_factory=list)

    def node_id(self) -> str:
        return self.host_name

    def __eq__(self, o: object) -> bool:
        if isinstance(o, HostNode):
            return self.host_name == o.host_name
        return False

    def __hash__(self) -> int:
        return hash(self.host_name)


@dataclass
class ProcessNode(Node):
    host: HostNode
    process_name: str
    r_edges: list = field(default_factory=list)
    l_edges: list = field(default_factory=list)
    lb_edges: list = field(default_factory=list)

    def node_id(self) -> str:
        return self.host.node_id() + "." + self.process_name

    def __eq__(self, o: object) -> bool:
        if isinstance(o, ProcessNode):
            return self.host == o.host and self.process_name == o.process_name
        return False

    def __hash__(self) -> int:
        return hash((self.host, self.process_name))


@dataclass
class TcpLinkKey:
    s_ip: str
    s_port: str
    c_ip: str
    c_process: ProcessNode

    def c_node_id(self) -> str:
        return self.c_process.node_id() if self.c_process else ""

    def __hash__(self) -> int:
        return hash((self.s_ip, self.s_port, self.c_ip, self.c_process))

    def __eq__(self, o: object) -> bool:
        if isinstance(o, TcpLinkKey):
            return self.s_ip == o.s_ip and self.s_port == o.s_port and \
                   self.c_ip == o.c_ip and self.c_process == o.c_process
        return False


@dataclass
class LbLinkKey:
    s_ip: str
    s_port: str
    v_ip: str
    v_port: str
    l_ip: str
    c_ip: str

    def __hash__(self) -> int:
        return hash((self.s_ip, self.s_port, self.v_ip, self.v_port,
                     self.l_ip, self.c_ip))

    def __eq__(self, o: object) -> bool:
        if isinstance(o, LbLinkKey):
            return self.s_ip == o.s_ip and self.s_port == o.s_port and \
                   self.v_ip == o.v_ip and self.v_port == o.v_port and \
                   self.l_ip == o.l_ip and self.c_ip == o.c_ip
        return False


@dataclass
class TcpLinkMetric:
    rx_bytes: str = ""
    tx_bytes: str = ""
    packets_out: str = ""
    packets_in: str = ""
    retran_packets: str = ""
    lost_packets: str = ""
    rtt: str = ""
    link_count: str = ""


@dataclass
class TcpLinkInfo:
    key: TcpLinkKey
    s_process: ProcessNode = None
    link_metric: TcpLinkMetric = None
    link_type: str = ""
    status: int = 1     # default status, 1 represents normal status

    def __hash__(self) -> int:
        return hash(self.key)

    def __eq__(self, o: object) -> bool:
        if isinstance(o, TcpLinkInfo):
            return self.key == o.key
        return False

    def s_node_id(self) -> str:
        return self.s_process.node_id() if self.s_process else ""

    def c_node_id(self) -> str:
        return self.key.c_node_id() if self.key else ""

    def link_id(self) -> str:
        if self.c_node_id() and self.s_node_id() and self.link_type:
            return self.c_node_id() + "." + self.s_node_id() + "."\
                   + self.link_type
        return ""


@dataclass
class LbLinkInfo:
    key: LbLinkKey
    lb_process: ProcessNode = None
    c_process: ProcessNode = None
    s_process: ProcessNode = None
    link_type: str = ""

    def __hash__(self) -> int:
        return hash(self.key)

    def __eq__(self, o: object) -> bool:
        if isinstance(o, LbLinkInfo):
            return self.key == o.key
        return False

    def s_node_id(self) -> str:
        return self.s_process.node_id() if self.s_process else ""

    def c_node_id(self) -> str:
        return self.c_process.node_id() if self.c_process else ""

    def lb_node_id(self) -> str:
        return self.lb_process.node_id() if self.lb_process else ""

    def link_id(self) -> str:
        if self.c_process and self.s_process and self.link_type:
            return self.c_process.node_id() + "." + self.s_process.node_id()\
                   + "." + self.link_type

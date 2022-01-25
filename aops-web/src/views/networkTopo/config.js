/**
 * @file 配置信息文件
 */

export const levelOrders = [
    {type: 'HOST', text: '主机', src: '/主机.png'},
    {type: 'CONTAINER', text: '容器', src: '/容器.png'},
    {type: 'PROCESS', text: '进程', show: true, src: '/进程.png'},
    {type: 'RPC', text: 'RPC', src: '/TCP连接.png'},
    {type: 'LB', text: 'LB', src: '/IPVS连接.png'}
];

export const relationTypes = {
    runsOn: 'runs_on',
    belongsTo: 'belongs_to',
    connect: 'connect',
    peer: 'is_peer'
};

export const entitiesInEachLevel = {
    HOST: {
        entities: ['host']
    },
    CONTAINER: {
        entities: ['container']
    },
    PROCESS: {
        entities: ['task']
    },
    RPC: {
        entities: ['tcp_link']
    },
    LB: {
        entities: ['ipvs_link']
    }
};

export const linkTypeInEachLevel = {
    host: {
        types: []
    },
    container: {
        types: []
    },
    process: {
        types: []
    },
    RPC: {
        types: ['tcp_link']
    },
    LB: {
        types: ['ipvs_link']
    }
};

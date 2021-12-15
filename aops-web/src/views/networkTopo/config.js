/**
 * @file 配置信息文件
 */

export const levelOrders = [
    {type: 'HOST', text: '主机'},
    {type: 'CONTAINER', text: '容器'},
    {type: 'PROCESS', text: '进程', show: true},
    {type: 'RPC', text: 'RPC'},
    {type: 'LB', text: 'LB'}
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

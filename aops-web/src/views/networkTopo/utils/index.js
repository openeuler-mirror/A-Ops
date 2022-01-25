/**
 * @file 绘图工具方法
 */

import {relationTypes} from '../config';

/**
 * 获取当前节点的父级Id
 * @param {Object} entity 当前节点引用对象
 * @returns 当前节点的父级Id
 */

export function getParentId(entity) {
    if (!entity.dependingitems) {
        return null;
    }
    let tempId = null;
    entity.dependingitems.forEach(function (item) {
        if (tempId) {
            return;
        }
        // node runs on parent node
        if (item.relation_id === relationTypes.runsOn) {
            tempId = item.target && item.target.entityid;
        }
        // tcp link belongs to parent node
        if (item.relation_id === relationTypes.belongsTo) {
            tempId = item.target && item.target.entityid;
        }
    });
    return tempId;
}

/**
 * 获取到当前节点的子节点id列表
 * @param {Object} entity 当前节点引用对象
 * @returns 当前节点的子节点id列表
 */

export function gerChildrenIds(entity) {
    if (!entity.dependeditems) {
        return [];
    }
    const tempArr = [];
    entity.dependeditems.forEach(function (item) {
        // node runs on parent node
        if (item.relation_id === relationTypes.runsOn) {
            item.target && tempArr.push(item.target.entityid);
        }
        // tcp link belongs to parent node
        if (item.relation_id === relationTypes.belongsTo) {
            item.target && tempArr.push(item.target.entityid);
        }
    });
    return tempArr;
}

/**
 * 获取当前节点关联的边对象列表
 * @param {Object} entity 当前节点引用对象
 * @returns 当前节点关联的边对象列表
 */

export function getRelatedEdges(entity) {
    if (!entity.dependingitems && !entity.dependeditems) {
        return [];
    }
    const tempArr = [];
    // 从当前节点触发的边
    entity.dependingitems
        && entity.dependingitems.forEach(function (item) {
            if (item.relation_id === relationTypes.connect) {
                item.target
                    && tempArr.push({
                        ...item,
                        refTarget: item.target,
                        // id、source、target是绘图工具需要的参数。
                        id: `connect$${entity.entityid}$${item.target.entityid}`,
                        source: entity.entityid,
                        target: item.target.entityid
                    });
            }
            if (item.relation_id === relationTypes.peer) {
                item.target
                    && tempArr.push({
                        ...item,
                        refTarget: item.target,
                        id: `peer$${entity.entityid}$${item.target.entityid}`,
                        source: entity.entityid,
                        target: item.target.entityid,
                        style: {endArrow: false}
                    });
            }
        });
    // 到达当前节点的边
    entity.dependeditems
        && entity.dependeditems.forEach(function (item) {
            if (item.relation_id === relationTypes.connect) {
                item.target
                    && tempArr.push({
                        ...item,
                        refTarget: item.target,
                        id: `connect$${item.target.entityid}$${entity.entityid}`,
                        source: item.target.entityid,
                        target: entity.entityid
                    });
            }
        });

    return tempArr;
}

/**
 * 获取和当前节点链接的node id列表
 * @param {Array} startOfLinks 从节点发出的连接
 * @param {Array} endOfLinks 到达节点的连接
 * @param {Object} linkMap 全量连接的hash表
 * @returns 当前节点链接的node id列表
 */

export function getRemoteNodeIds(
    startOfLinks = [],
    endOfLinks = [],
    linkMap = {}
) {
    const outputArr = [];
    startOfLinks.forEach(linkId => {
        linkMap[linkId] && outputArr.push(linkMap[linkId].target);
        // 针对peer类型链接的特殊处理。因为peer类型是双向的，但是只会绘制一个链接。即只有一个id，
        // 那么反向查询时，需要反向配置id名称
        if (linkId.indexOf('peer$') === 0) {
            const idArr = linkId.split('$');
            if (!linkMap[linkId] && linkMap[`peer$${idArr[2]}$${idArr[1]}`]) {
                outputArr.push(linkMap[`peer$${idArr[2]}$${idArr[1]}`].source);
            }
        }
    });
    endOfLinks.forEach(linkId => {
        linkMap[linkId] && outputArr.push(linkMap[linkId].source);
    });
    return outputArr;
}

/**
 * 递归查询当前节点的根节点
 * @param {Object} entity 当前节点引用对象
 * @param {Objct} nodeMap 全量节点hash表
 * @returns 根节点引用
 */

export function getRoot(entity, nodeMap) {
    if (!entity.parentId) {
        return entity;
    }
    return getRoot(nodeMap[entity.parentId], nodeMap);
}

/**
 * 根据当前节点，创建树形数据结构。供绘制垂直图
 * @param {Object} rawTreeData 树的根节点。节点需包含子节点信息，存储在children属性中。
 * @returns 树形数据结构
 */

export function getTreeData(rawTreeData) {
    const tempNode = {
        id: rawTreeData.id,
        name: rawTreeData.name,
        label: undefined,
        type: rawTreeData.type,
        icon: {
            show: true,
            img:
               rawTreeData.type === 'host'
               ? '/主机.png'
               : rawTreeData.type === 'container'
               ? '/容器.png'
               : rawTreeData.type === 'task'
               ? '/进程.png'
               : rawTreeData.type === 'tcp_link'
               ? '/TCP连接.png'
               : '/IPVS连接.png',
            width: 40,
            height: 40
        },
        attrs: rawTreeData.attrs
    };
    if (rawTreeData.children) {
        tempNode.children = rawTreeData.children.map(child => {
            return getTreeData(child);
        });
    }
    return tempNode;
}

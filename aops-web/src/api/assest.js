import request from '@/vendor/ant-design-pro/utils/request';

const api = {
  hostList: '/manage/host/get', // 全量接口待确认
  hostCount: '/manage/host/count', // 全量接口待确认
  hostInfo: '/manage/host/info/query',
  addHost: '/manage/host/add',
  editHost: '/manage/host/edit_host', // 未提供
  deleteHost: '/manage/host/delete',
  hostGroupList: '/manage/host/group/get',
  addHostGroup: '/manage/host/group/add',
  deleteHostGroup: '/manage/host/group/delete',
  transcationDomainConfigList: '/manage/config/get_transcation_domain_config',
  deleteTranscationDomainConfig: '/manage/config/delete_transcation_domain_config',

  // host detail plugin control
  sceneGet: '/manage/host/scene/get',
  pluginInfoGet: '/manage/agent/plugin/info',
  pluginSet: '/manage/agent/plugin/set',
  metricSet: '/manage/agent/metric/set',
  getHostDetail: '/manage/host/info/query'
};

export default api;

const directionMap = {'ascend': 'asc',
  'descend': 'desc'};
const managementMap = {'true': true,
  'false': false};

// 主机管理
export function hostList({tableInfo, ...parameter}) {
  const management = tableInfo.filters.management
  ? managementMap[tableInfo.filters.management[0]] // 将字符串true false转换成boolean
  : undefined;
  return request({
    url: api.hostList,
    method: 'post',
    data: {
      ...parameter,
      host_group_list: tableInfo.filters.host_group_name || [],
      management,
      sort: tableInfo.sorter.field,
      direction: directionMap[tableInfo.sorter.order],
      page: tableInfo.pagination.current,
      per_page: tableInfo.pagination.pageSize
    }
  });
};
// 主机统计
export function hostCount() {
  return request({
    url: api.hostCount,
    method: 'post',
    data: {}
  });
};

export function hostInfo(parameter) {
  return request({
    url: api.hostInfo,
    method: 'post',
    data: {
      ...parameter,
      host_list: parameter.host_list
    }
  });
};
// 获取指定主机的基本信息，并以map形式返回。需要特别的代码结构配合使用;
export function hostBasicInfo(list, key) {
  var hostList = [];
  list.forEach(function (item) {
    hostList.push(item[key || 'host_id']);
  });
  return request({
    url: api.hostInfo,
    method: 'post',
    data: {
      host_list: hostList,
      basic: true
    }
  }).then(function (data) {
    var map = {};
    data.host_infos.forEach(function (host) {
      map[host.host_id] = host;
    });
    return map;
  });
};

export function addHost(parameter) {
  return request({
    url: api.addHost,
    method: 'post',
    data: {
      host_list: [{
        host_name: parameter.host_name,
        host_group_name: parameter.host_group_name,
        public_ip: parameter.public_ip,
        ssh_port: parameter.ssh_port,
        management: parameter.management,
        username: parameter.username,
        password: parameter.password,
        sudo_password: parameter.sudo_password
      }],
      key: parameter.key
    }
  });
};

export function deleteHost({hostList, parameter}) {
  return request({
    url: api.deleteHost,
    method: 'delete',
    data: {
      host_list: hostList,
      ...parameter
    }
  });
};

// 主机组管理
export function hostGroupList({tableInfo, ...parameter}) {
  return request({
    url: api.hostGroupList,
    method: 'post',
    data: {
      ...parameter,
      sort: tableInfo.sorter.field,
      direction: directionMap[tableInfo.sorter.order],
      page: tableInfo.pagination.current,
      per_page: tableInfo.pagination.pageSize
    }
  });
};

export function addHostGroup({name, description, ...parameter}) {
  return request({
    url: api.addHostGroup,
    method: 'post',
    data: {
      ...parameter,
      host_group_name: name,
      description
    }
  });
};

export function deleteHostGroup({hostGroupList, parameter}) {
  return request({
    url: api.deleteHostGroup,
    method: 'delete',
    data: {
      host_group_list: hostGroupList,
      ...parameter
    }
  });
};

// host detail plugin control
export function sceneGet({hostId}) {
  return request({
    url: api.sceneGet,
    method: 'get',
    params: {
      host_id: hostId
    }
  });
};

export function pluginInfoGet({hostId}) {
  return request({
    url: api.pluginInfoGet,
    method: 'get',
    params: {
      host_id: hostId
    }
  });
};

export function metricSet({metricStatus, parameter}) {
  return request({
    url: api.metricSet,
    method: 'post',
    data: {
      host_id: metricStatus.hostId,
      plugins: metricStatus.plugins,
      ...parameter
    }
  });
};

export function pluginSet({pluginStatus, parameter}) {
  return request({
    url: api.pluginSet,
    method: 'post',
    data: {
      host_id: pluginStatus.hostId,
      plugins: pluginStatus.plugins,
      ...parameter
    }
  });
};

/*
*  isBasicInfo: 值为true时，获取主机的基本信息（主机名、ip地址等）；
*               值为false时，获取主机下详细的资源信息（缓存、Cpu信息等）。
*/
export function getHostDetail(hostId, isBasicInfo = false) {
  return request({
    url: api.getHostDetail,
    method: 'post',
    data: {
      host_list: [hostId],
      basic: isBasicInfo
    }
  });
};

/**
 * @file: 缺陷管理模块-配置信息文件。主要是模块中各种状态的英文值对应的中文和颜色的配置信息。
 */

export const statusList = [
    {
        text: '未关注',
        value: 'not reviewed'
    },
    {
        text: '关注中',
        value: 'in review'
    },
    {
        text: '挂起',
        value: 'on-hold'
    },
    {
        text: '已解决',
        value: 'resolved'
    },
    {
        text: '已忽略',
        value: 'no action'
    }
];

export const statusMap = {
    'not reviewed': '未关注',
    'in review': '关注中',
    'on-hold': '挂起',
    resolved: '已解决',
    'no action': '已忽略'
};

export const severityMap = {
    critical: '严重',
    high: '高风险',
    medium: '中风险',
    low: '低风险',
    unknown: '未知'
};

export const severityColorMap = {
    critical: '#f62f2f',
    high: '#fda72c',
    medium: '#fde92c',
    low: '#3bd065',
    unknown: '#ccc'
};

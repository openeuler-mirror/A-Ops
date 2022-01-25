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
    Critical: '严重',
    High: '高风险',
    Medium: '中风险',
    Low: '低风险',
    Unknown: '未知'
};

export const severityColorMap = {
    Critical: '#f62f2f',
    High: '#fda72c',
    Medium: '#fde92c',
    Low: '#3bd065',
    Unknown: '#ccc'
};

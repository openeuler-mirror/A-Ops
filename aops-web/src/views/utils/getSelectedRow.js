/**
 * @file: 翻页时，获取已选择行的完整数据列表
 * @param {Array} selectedRowKeys 已选择行的id列表
 * @param {Array} selectedRowsAll 上一次已选择行的完整数据列表
 * @param {Array} pageTableData 当前表格的数据
 * @param {String} selectKeyName 用来匹配数据id的键名
 * @returns 本次已选择行的完整数据列表
 */

export function getSelectedRow(
    selectedRowKeys,
    selectedRowsAll,
    pageTableData,
    selectKeyName
) {
    const newselectedRowsAll = [];
    selectedRowKeys.forEach(key => {
        const filteredItem = selectedRowsAll.filter(
            row => row[selectKeyName] === key
        );
        if (filteredItem.length > 0) {
            newselectedRowsAll.push(filteredItem[0]);
        } else {
            newselectedRowsAll.push(
                pageTableData.filter(row => row[selectKeyName] === key)[0]
            );
        }
    });
    return newselectedRowsAll;
}

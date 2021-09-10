export function getSelectedRow (selectedRowKeys, selectedRowsAll, pageTableData) {
  const newselectedRowsAll = []
  selectedRowKeys.forEach(key => {
    const filteredItem = selectedRowsAll.filter(row => row.host_group_name === key)
    if (filteredItem.length > 0) {
      newselectedRowsAll.push(filteredItem[0])
    } else {
      newselectedRowsAll.push(pageTableData.filter(row => row.host_group_name === key)[0])
    }
  })
  return newselectedRowsAll
}

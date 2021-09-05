export const STATUS_ENUM = {
  sync: 'SYNCHRONIZED',
  notSync: 'NOT SYNCHRONIZE',
  notFound: 'NOT FOUND'
}
// return a sync status from a status list and a number of hosts which are not in sync status.
// return 'SYNCHRONISED' only if all status in list are 'SYNCHRONISED'.
export function getStatusInfoFromAllConfs (statusList) {
  const resultObj = { count: 0 }
  if (statusList.length === 0) {
    resultObj.syncStatus = STATUS_ENUM.notFound
    return resultObj
  }

  for (let i = 0; i < statusList.length; i++) {
    if (statusList[i].isSynced !== STATUS_ENUM.sync) {
      resultObj.count++
    }
  }
  if (resultObj.count > 0) {
    resultObj.syncStatus = STATUS_ENUM.notSync
  } else {
    resultObj.syncStatus = STATUS_ENUM.sync
  }
  return resultObj
}

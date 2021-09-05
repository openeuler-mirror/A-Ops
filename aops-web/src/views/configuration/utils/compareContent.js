export function checkIsDiff (diffResult) {
  for (let i = 0; i < diffResult.length; i++) {
    if (diffResult[i].added || diffResult[i].removed) {
      return true
    }
  }
  return false
}

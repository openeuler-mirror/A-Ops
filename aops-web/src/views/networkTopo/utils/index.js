export function getEdgeLabel (edgeAttrs) {
  const labelList = edgeAttrs.map(attr => {
    return `${attr.key}: ${attr.value}`
  })

  return labelList.join(';')
}

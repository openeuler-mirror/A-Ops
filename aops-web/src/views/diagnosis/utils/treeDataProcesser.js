// this tool is abandoned
export function treeDataProcesser(rawTreeData, id = '0') {
  if (!rawTreeData['node name']) { return null; };
  const {children, ...params} = rawTreeData;
  const nodeTemp = {
    ...params,
    label: rawTreeData['node name'],
    id
  };
  if (rawTreeData.children) {
    const childsArrayTemp = [];
    rawTreeData.children.forEach((node, idx) => {
      childsArrayTemp.push(treeDataProcesser(node, `${id}-${idx}`));
    });
    nodeTemp.children = childsArrayTemp;
  };

  return nodeTemp;
};

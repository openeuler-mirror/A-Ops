#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN 'AS IS' BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
"""
Description: Basic data structure and methods of diagnose tree
Class: NodeData, DiagTree
"""

import abc
import collections
from sys import getsizeof
from adoctor_diag_executor.function.diag_exception import ExpressionError
from adoctor_diag_executor.function.calculation import calculate

__all__ = ["DiagTree"]


class TreeNode(abc.ABC):
    """
    Base class of Diagnose tree's node
    """
    def __init__(self, data):
        """
        Init node of the diagnose tree, cannot be instantiated.
        Args:
            data (dict): node's dict
        """
        self._dict = data
        self.name = data["node name"]
        self.value = data["value"]

    @abc.abstractmethod
    def to_dict(self):
        """
        Transfer node to dict
        Returns:

        """
        pass

    def is_leaf(self):
        return isinstance(self, LeafNode)

    def is_branch(self):
        return isinstance(self, BranchNode)


class BranchNode(TreeNode):
    """
    class of branch node in diagnose tree
    """
    def __init__(self, data):
        """
        Init a middle node
        Args:
            data: e.g.
                {
                    "node name": ""
                    "value": bool,
                    "condition": "",
                    "description": "",
                    "advice": "",
                    "children": [
                        {
                            "node name": "",
                            "value": bool,
                            "condition": "",
                            "description": "",
                            "advice": "",
                            "children": [
                                {
                                    "node name": "",
                                    "value": bool,
                                    "check item": ""
                                }]
                        },
                        {
                            "node name": "",
                            "value": bool,
                            "check item": ""
                        }]
                }
        """
        TreeNode.__init__(self, data)
        self.children = []
        self.condition = data["condition"]

    def to_dict(self):
        """
        convert node to dict

        Returns:
            dict: node's dict
        """
        self._dict["value"] = self.value

        children_dict = []
        for child in self.children:
            children_dict.append(child.to_dict())

        self._dict["children"] = children_dict
        return self._dict


class LeafNode(TreeNode):
    """
    class of leaf node of diagnose tree
    """
    def __init__(self, data):
        """
        Init leaf node
        Args:
            data: e.g.
                {
                    "node name": "",
                    "value": bool,
                    "check item": ""
                }

        """
        TreeNode.__init__(self, data)
        self.check_item = data["check item"]
        self.msg = ""

    def to_dict(self):
        """
        covert node to dict
        Returns:
            dict: node's dict
        """
        self._dict["value"] = self.value
        self._dict["msg"] = self.msg
        return self._dict


class DiagTree:
    """
    Diag tree sheet
    """
    def __init__(self, tree_dict):
        """
        Init DiagTree object
        Args:
            tree_dict (dict): dict of whole tree
        """
        self.root = BranchNode(tree_dict)
        self.check_items = set()
        self.__generate_tree(tree_dict["children"])

    def create_node(self, node_dict, parent_node):
        """
        Create a new node
        Args:
            node_dict (dict): dict of node's description, condition, advice, check list,
            parent_node (BranchNode): parent node of the new node

        """
        def is_leaf(data_dict):
            if "check item" in data_dict:
                return True
            return False

        if is_leaf(node_dict):
            new_node = LeafNode(node_dict)
            self.check_items.add(new_node.check_item)
        else:
            new_node = BranchNode(node_dict)

        parent_node.children.append(new_node)
        return new_node

    def __generate_tree(self, tree_children):
        """
        create diagnose tree by combining nodes
        """

        def dfs_create(children_list, parent):

            for child_dict in children_list:
                new_node = self.create_node(child_dict, parent)
                # if the node is a branch node, continue create
                if new_node.is_branch():
                    dfs_create(child_dict["children"], new_node)

        dfs_create(tree_children, self.root)

    def to_dict(self):
        """
        Transfer diag tree to dict

        Returns:
            dict: dict of the diag tree
        """
        return self.root.to_dict()

    def diagnose(self, check_item_dict):
        """
        Execute diagnose of single diagnostic tree with the abnormal leaves from check process.
        Args:
            check_item_dict (dict): checked items' status.
                e.g.
                    {
                        "abnormal": abnormal_set,
                        "no data": no_data_set,
                        "internal error": internal_error_set
                    }

        Returns:
            dict
        """
        abnormal_set = check_item_dict["abnormal"]
        no_data_set = check_item_dict["no data"]
        internal_err_set = check_item_dict["internal error"]

        def dfs_diagnose(parent):
            expression = parent.condition
            children = parent.children
            leaves_dict = {}

            for child in children:
                if child.is_leaf():
                    check_item = child.check_item

                    if check_item in abnormal_set:
                        leaves_dict[child.name] = True
                        child.value = True

                    elif check_item in no_data_set:
                        leaves_dict[child.name] = False
                        child.value = None
                        child.msg = "No data"
                    # internal error
                    elif check_item in internal_err_set:
                        leaves_dict[child.name] = False
                        child.value = None
                        child.msg = "Internal error"
                    # node is normal or not checked during the time range
                    # (which is bad, will fix in the future)
                    else:
                        leaves_dict[child.name] = False
                        child.value = False

                else:
                    leaves_dict[child.name] = dfs_diagnose(child)
            try:
                value = calculate(expression, leaves_dict)
            except ExpressionError as error:
                raise ExpressionError("Expression '%s' of node '%s' has error."
                                      % (expression, parent.name)) from error
            parent.value = value

            return value

        dfs_diagnose(self.root)
        res = self.root.to_dict()
        return res

    @property
    def total_size(self):
        """
        Get the tree's total size.
        Returns:
            str: diagnose tree's total size
        """
        size = 0
        seen = set()

        def dfs_size(obj):
            nonlocal size
            nonlocal seen

            if id(obj) in seen:
                return
            seen.add(id(obj))
            size += getsizeof(obj)
            if isinstance(obj, collections.Mapping):
                for key, value in obj.items():
                    dfs_size(key)
                    dfs_size(value)
            else:
                obj_dict = getattr(obj, '__dict__', None)
                if obj_dict:
                    dfs_size(obj_dict)

        dfs_size(self)
        return str(size / 1024 / 1024) + ' MB'

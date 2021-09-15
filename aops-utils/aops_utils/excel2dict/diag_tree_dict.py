#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
"""
A tool to transfer diagnostic tree's info from excel to dict
Needed files: xxxx.xlsx exported from MindMaster
"""

import xlrd


CONDITION_PRE = "condition:"
ADVICE_PRE = "advice:"
DESCRIPTION_PRE = "description:"


class PaintingRuleError(Exception):
    """
    Self-defined Exception class
    """
    def __init__(self, error_info=''):
        """
        Init PaintingRuleError exception.

        args:
            error_info (str): Exception's error info
        """
        Exception.__init__(self)
        self.message = error_info

    def __str__(self):
        """
        string of the exception

        Returns:
            str
        """
        return self.message


class DiagBook:
    """
    Class of diag excel workbook which contains multiple sheets
    """
    def __init__(self, tree_excel_path):
        """
        Init DiagBook object

        Args:
            tree_excel_path (str): diagnose tree excel's path
        """
        self.tree_workbook = xlrd.open_workbook(tree_excel_path)
        self.diag_table = self.get_diag_table()

    def get_diag_table(self):
        """
        Check the workbooks meets the standard or not

        Returns:
            xlrd.sheet.Sheet: diag sheet
        """
        if "diag" not in self.tree_workbook.sheet_names():
            raise PaintingRuleError("'diag' sheet is not in the Mind master's diag tree excel.")
        return self.tree_workbook.sheet_by_name("diag")


class DiagNode:
    """
    Node in diagnostic tree
    """
    def __init__(self, name):
        """
        Init DiagNode object

        Args:
            name (str): node's name
        """
        self.name = name
        self.diag_condition = ""
        self.diag_description = ""
        self.diag_advice = ""
        self.check_item = ""
        self.is_leaf = self._is_leaf()
        # children
        self.children = {}
        self.dict = {}

    def _is_leaf(self):
        """
        The node is a leaf or not

        Returns:
            bool
        """
        if '|' in self.name:
            return True
        return False

    def children_all_leaves(self):
        """
        If the node's children all leaves

        Returns:
            bool
        """
        for child_node in self.children.values():
            if not child_node.is_leaf:
                return False
        return True

    def children_all_trees(self):
        """
        If the node's children are all subtrees

        Returns:
            bool
        """
        for child_node in self.children.values():
            if child_node.is_leaf:
                return False
        return True

    def to_dict(self):
        """
        Transfer Diag node to dict

        Returns:
            dict
        Raises:
            PaintingRuleError
        """
        if self.is_leaf:
            self.dict["node name"] = self.name
            self.dict["value"] = None
            self.dict["check item"] = self.check_item
            self.dict["msg"] = ""
            return self.dict

        self.dict["node name"] = self.name
        self.dict["value"] = None

        # create children's dict first for function children_all_leaves/trees
        children = []
        for child_node in self.children.values():
            children.append(child_node.to_dict())

        # If diag condition is not defined in the graph
        if not self.diag_condition:
            # Default relationship between leaves is "and"
            if self.children_all_leaves():
                self.diag_condition = " && ".join(self.children.keys())
            # Default relationship between middle nodes is "or"
            elif self.children_all_trees():
                self.diag_condition = " || ".join(self.children.keys())
            else:
                raise PaintingRuleError("Node which have both leaves and subtrees as children, "
                                        "must define diag condition in Mind Master")

        self.dict["condition"] = self.diag_condition
        self.dict["description"] = self.diag_description
        self.dict["advice"] = self.diag_advice
        self.dict["children"] = children

        return self.dict


class DiagTree:
    """
    Diag tree sheet
    """
    def __init__(self, diag_table):
        """
        Init DiagTree object

        Args:
            diag_table (xlrd.sheet.Sheet): diag sheet of the excel exported from MindMaster
        """
        self.table = diag_table
        self.name = self.get_tree_name()
        self.root = DiagNode(self.name)
        # Check items' name dictionary
        self.eng2cn_dict = {}
        self.cn2eng_dict = {}
        self.__generate_tree()

    def get_tree_name(self):
        """
        Get tree's name.

        Returns:
            str
        """
        return self.table.cell_value(0, 0)

    def check_one2one(self, eng_name, cn_name):
        """
        Check abnormal items' English name match only one Chinese name, vice versa.
        Args:
            eng_name (str): Check abnormal items' English name
            cn_name (str): Check abnormal items' Chinese name

        Raises: PaintingRuleError

        """
        if eng_name in self.eng2cn_dict and self.eng2cn_dict[eng_name] != cn_name:
            raise PaintingRuleError("Check item's English name '%s' mapped to two Chinese "
                                    "name: '%s', '%s'" %
                                    (eng_name, self.eng2cn_dict[eng_name], cn_name))
        if cn_name in self.cn2eng_dict and self.cn2eng_dict[cn_name] != eng_name:
            raise PaintingRuleError("Check item's Chinese name '%s' mapped to two English "
                                    "name: '%s', '%s'" %
                                    (cn_name, self.cn2eng_dict[cn_name], eng_name))

    def create_node(self, name, parent_node):
        """
        Create a new node
        Args:
            name (str): node's name
            parent_node (DiagNode): node's parent node

        Returns:
            DiagNode
        """
        new_node = DiagNode(name)

        # if the new_node is a subtree
        if new_node.is_leaf:
            name_list = name.split('|')
            cn_name = name_list[0].strip()
            eng_name = name_list[1].strip()

            # Check if check item (in English) mapped with only one Chinese name, vice versa.
            self.check_one2one(eng_name, cn_name)
            self.eng2cn_dict[eng_name] = cn_name
            self.cn2eng_dict[cn_name] = eng_name

            new_node.name = cn_name
            new_node.check_item = eng_name

            parent_node.children[cn_name] = new_node
        else:
            parent_node.children[name] = new_node

        return new_node

    def __generate_tree(self):
        """
        create diagnose tree by combining nodes
        """
        row_num = self.table.nrows
        # 7 columns of the excel are useless
        col_num = self.table.ncols - 7

        parent_node = self.root
        parent_stack = [self.root]
        current_deep = 0

        for row in range(2, row_num):
            for col in range(0, col_num):
                if not self.table.cell_value(row, col):
                    continue
                value = self.table.cell_value(row, col).strip()
                # find parent node and switch column
                if current_deep == col and parent_stack:
                    parent_node = parent_stack.pop()
                elif current_deep < col:
                    current_deep = col
                else:
                    for _ in range(current_deep - col + 1):
                        parent_node = parent_stack.pop()
                    current_deep = col

                if value.startswith(CONDITION_PRE):
                    parent_node.diag_condition = value[len(CONDITION_PRE):].strip()
                    parent_stack.append(parent_node)
                elif value.startswith(DESCRIPTION_PRE):
                    parent_node.diag_description = value[len(DESCRIPTION_PRE):].strip()
                    parent_stack.append(parent_node)
                elif value.startswith(ADVICE_PRE):
                    parent_node.diag_advice = value[len(ADVICE_PRE):].strip()
                    parent_stack.append(parent_node)
                else:
                    new_node = self.create_node(value, parent_node)
                    parent_stack.append(parent_node)
                    parent_node = new_node
                break

    def to_dict(self, node=None):
        """
        Transfer diag tree to dict
        Args:
            node (DiagNode): node of the diagnose tree
        Returns:
            dict: dict of the tree/subtree expanded from specified node
        """
        if not node:
            return self.root.to_dict()
        return node.to_dict()


def generate_tree_dict(excel_path):
    """
    Entrance of diagnostic tree's excel to dict
    Args:
        excel_path (str): excel file's path

    Returns
        dict
    """
    diag_book = DiagBook(excel_path)
    diag_tree = DiagTree(diag_book.diag_table)

    return diag_tree.to_dict()

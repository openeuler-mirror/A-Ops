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
Time:
Author:
Description: Elasticsearch index related mappings
"""
from aops_database.conf.constant import DIAG_REPORT_INDEX, DIAG_TREE_INDEX,\
    TASK_INDEX, TEMPLATE_INDEX, CHECK_RESULT_INDEX, CHECK_RULE_INDEX, DIAG_TASK_INDEX

MAPPINGS = {
    TASK_INDEX: {
        "mappings": {
            "properties": {
                "task_id": {
                    "type": "keyword",
                    "ignore_above": 256
                },
                "task_name": {
                    "type": "keyword",
                    "ignore_above": 256
                },
                "description": {
                    "type": "text"
                },
                "username": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        }
    },
    TEMPLATE_INDEX: {
        "mappings": {
            "properties": {
                "template_name": {
                    "type": "keyword",
                    "ignore_above": 256
                },
                "template_content": {
                    "type": "text"
                },
                "description": {
                    "type": "text"
                },
                "username": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        }
    },
    DIAG_TREE_INDEX: {
        "mappings": {
            "properties": {
                "tree_name": {
                    "type": "keyword",
                    "ignore_above": 256
                },
                "tree_content": {
                    "type": "text"
                },
                "description": {
                    "type": "text"
                },
                "username": {
                    "type": "keyword",
                    "ignore_above": 256
                }
            }
        }
    },
    DIAG_REPORT_INDEX: {
        "mappings": {
            "properties": {
                "tree_name": {
                    "type": "keyword",
                    "ignore_above": 256
                },
                "host_id": {
                    "type": "keyword",
                    "ignore_above": 256
                },
                "task_id": {
                    "type": "keyword",
                    "ignore_above": 256
                },
                "report_id": {
                    "type": "keyword",
                    "ignore_above": 256
                },
                "start": {
                    "type": "long"
                },
                "end": {
                    "type": "long"
                },
                "username": {
                    "type": "keyword",
                    "ignore_above": 256
                },
                "report": {
                    "type": "text"
                }
            }
        }
    },
    DIAG_TASK_INDEX: {
        "mappings": {
            "properties": {
                "task_id": {
                    "type": "keyword",
                    "ignore_above": 256
                },
                "username": {
                    "type": "keyword",
                    "ignore_above": 256
                },
                "time": {
                    "type": "long"
                },
                "expected_report_num": {
                    "type": "long"
                }
            }
        }
    },
    CHECK_RULE_INDEX: {
        "mappings": {
            "properties": {
                "username": {
                    "type": "keyword",
                    "ignore_above": 256
                },
                "check_item": {
                    "type": "keyword",
                    "ignore_above": 256
                },
                "condition": {
                    "type": "text"
                },
                "description": {
                    "type": "text"
                },
                "data_list": {
                    "type": "nested",
                    "properties": {
                        "name": {
                            "type": "text"
                        },
                        "type": {
                            "type": "text"
                        },
                        "label": {
                            "type": "object"
                        }
                    }
                }
            }
        }
    },
    CHECK_RESULT_INDEX: {
        "mappings": {
            "properties": {
                "username": {
                    "type": "keyword",
                    "ignore_above": 256
                },
                "host_id": {
                    "type": "keyword",
                    "ignore_above": 256
                },
                "start": {
                    "type": "long"
                },
                "end": {
                    "type": "long"
                },
                "check_item": {
                    "type": "keyword",
                    "ignore_above": 256
                },
                "condition": {
                    "type": "text"
                },
                "value": {
                    "type": "text"
                },
                "data_list": {
                    "type": "nested",
                    "properties": {
                        "name": {
                            "type": "text"
                        },
                        "type": {
                            "type": "text"
                        },
                        "label": {
                            "type": "object"
                        }
                    }
                }
            }
        }
    }
}

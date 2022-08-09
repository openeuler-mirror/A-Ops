#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2022-2022. All rights reserved.
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
Description:
"""
from typing import Dict, Tuple, List
from collections import defaultdict

APP_SCENE_MAP = {
    "hadoop": {
        "big_data": 0.5
    },
    "mysql": {
        "big_data": 0.2
    },
    "zookeeper": {
        "big_data": 0.5
    },
    "kafka": {
        "big_data": 0.3
    },
    "nginx": {
        "web": 0.7
    },
    "spark": {
        "big_data": 0.3
    },
    "redis": {
        "big_data": 0.2
    },
    "flink": {
        "big_data": 0.2
    },
    "kubeedge": {
        "edge": 0.7
    },
    "kubernetes": {
        "cloud": 0.5
    }
}

SCENE_COLLECT_MAP = {
    "big_data": {
        "gala-gopher": ["system_infos"]
    },
    "web": {
        "gala-gopher": ["system_infos", "nginx"]
    },
    "edge": {
        "gala-gopher": ["system_infos"]
    },
    "cloud": {
        "gala-gopher": ["system_infos"]
    },
    "unknown": {
        "gala-gopher": ["system_infos"]
    }
}


class PackageWeightIdentify:
    """
    Identify host's scene by mapping application with scene
    """
    __slots__ = ["__application", "__support_collect_items", "__app_scene_map", "__scene_collect_map"]
    PluginsCollectItems = Dict[str, List[str]]

    def __init__(self, applications: list, collect_items: PluginsCollectItems, app_scene_map: dict = None,
                 scene_collect_map: Dict[str, PluginsCollectItems] = None):
        """
        init class
        Args:
            applications: application result
            collect_items: plugins' support collect items
            app_scene_map: app and scene's matching relationship
            scene_collect_map: scene and collect items' matching relationship
        """
        self.__application = applications
        self.__support_collect_items = collect_items
        self.__app_scene_map = app_scene_map or APP_SCENE_MAP
        self.__scene_collect_map = scene_collect_map or SCENE_COLLECT_MAP

        if "unknown" not in self.__scene_collect_map:
            raise ValueError("An 'unknown' scene should be given in case of no scene matches.")

    def get_scene(self) -> Tuple[str, PluginsCollectItems]:
        """
        Get scene and relative collect items.
        """
        scene_score = defaultdict(int)
        for app in self.__application:
            if app not in self.__app_scene_map:
                continue
            for scene in self.__app_scene_map[app]:
                scene_score[scene] += self.__app_scene_map[app][scene]

        if not scene_score:
            recommend_scene = "unknown"
        else:
            # for now, if two scene have same value, choose the first one
            sorted_scene = sorted(scene_score, key=lambda x: x[1])
            recommend_scene = sorted_scene[0]

        scene_collect_item = self.__scene_collect_map[recommend_scene]
        recommend_collect_item = self.__get_reco_collect_items(self.__support_collect_items,
                                                               scene_collect_item)
        return recommend_scene, recommend_collect_item

    @staticmethod
    def __get_reco_collect_items(support_collect_item: PluginsCollectItems,
                                 scene_collect_item: PluginsCollectItems) -> PluginsCollectItems:
        """
        get recommended collect items of a host
        """
        reco_collect_items = {}
        for plugin in scene_collect_item:
            if plugin not in support_collect_item:
                continue
            collect_items = list(set(support_collect_item[plugin]) & set(scene_collect_item[plugin]))
            if collect_items:
                reco_collect_items[plugin] = collect_items
        return reco_collect_items

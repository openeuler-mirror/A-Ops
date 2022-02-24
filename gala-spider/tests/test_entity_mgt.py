from spider.conf.observe_meta import ObserveMetaMgt, DirectRelationMeta
from spider.entity_mgt import ObserveEntityCreator, DirectRelationCreator, IndirectRelationCreator
from .common import gen_host_entity, gen_task_entity, gen_tcp_link_entity, gen_ipvs_link_entity
from .common import gen_app_instance_entity
from .common import init_spider_config, init_observe_meta_mgt


def setup_module():
    init_spider_config()
    init_observe_meta_mgt()


class TestObserveEntityCreator:
    def test_create_observe_entity(self):
        entity_type = 'task'
        entity_attrs = {
            'fork_count': 1,
            'timestamp': 0,
            'comm': 'task0',
            'pid': 1,
            'machine_id': '123',
        }
        observe_meta_mgt = ObserveMetaMgt()
        entity_meta = observe_meta_mgt.get_observe_meta(entity_type)

        entity = ObserveEntityCreator.create_observe_entity(entity_type, entity_attrs, entity_meta)
        assert entity is not None
        assert entity.id == '{}_{}_{}'.format(entity_type.upper(), entity_attrs.get('machine_id'),
                                              entity_attrs.get('pid'))
        assert entity.type == entity_type
        assert entity.name == entity_attrs.get('comm')
        assert entity.level == entity_meta.level
        assert entity.timestamp == entity_attrs.get('timestamp')
        assert entity.attrs
        assert len(entity.attrs) == 4
        # keys
        assert entity.attrs.get('pid') == entity_attrs.get('pid')
        assert entity.attrs.get('machine_id') == entity_attrs.get('machine_id')
        # labels
        assert entity.attrs.get('comm') == entity_attrs.get('comm')
        # metrics
        assert entity.attrs.get('fork_count') == entity_attrs.get('fork_count')

        del entity_attrs['pid']
        entity = ObserveEntityCreator.create_observe_entity(entity_type, entity_attrs, entity_meta)
        assert entity is None

        entity_attrs.setdefault('pid', 1)
        del entity_attrs['comm']
        entity = ObserveEntityCreator.create_observe_entity(entity_type, entity_attrs, entity_meta)
        assert entity is not None
        assert entity.name is None

    def test__create_app_instance_observe_entities(self):
        observe_meta_mgt = ObserveMetaMgt()
        task_meta = observe_meta_mgt.get_observe_meta('task')

        task1 = gen_task_entity(task_meta, pid=1, machine_id='1', exe_file='/usr/bin/redis')
        task2 = gen_task_entity(task_meta, pid=2, machine_id='1', exe_file='/usr/bin/redis')

        res = ObserveEntityCreator._create_app_instance_observe_entities([task1, task2])
        assert len(res) == 1
        assert res[0].type == 'appinstance'
        assert res[0].name == ''
        assert res[0].level == 'APPLICATION'
        assert res[0].timestamp == task1.timestamp
        assert res[0].attrs.get('pgid') == task1.attrs.get('pgid')
        assert res[0].attrs.get('machine_id') == task1.attrs.get('machine_id')
        assert res[0].attrs.get('exe_file') == task1.attrs.get('exe_file')
        assert res[0].attrs.get('exec_file') == task1.attrs.get('exec_file')
        assert len(res[0].attrs.get('tasks')) == 2
        assert res[0].attrs.get('tasks')[0] == task1.id
        assert res[0].attrs.get('tasks')[1] == task2.id
        assert res[0].id == 'APPINSTANCE_1_0'

    def test_create_logical_observe_entities(self):
        observe_meta_mgt = ObserveMetaMgt()
        task_meta = observe_meta_mgt.get_observe_meta('task')

        task1 = gen_task_entity(task_meta, pid=1, machine_id='1', pgid=0, exe_file='/usr/bin/redis')
        task2 = gen_task_entity(task_meta, pid=2, machine_id='1', pgid=0, exe_file='/usr/bin/redis')
        task3 = gen_task_entity(task_meta, pid=3, machine_id='1', pgid=1, exe_file='/usr/bin/redis')
        task4 = gen_task_entity(task_meta, pid=4, machine_id='1', pgid=2, exe_file='/usr/bin/go')
        task5 = gen_task_entity(task_meta, pid=1, machine_id='2', pgid=0, exe_file='/usr/bin/redis')

        res = ObserveEntityCreator.create_logical_observe_entities([task1, task2, task3, task4, task5])
        # expect: generate 4 app instances
        assert len(res) == 4


class TestDirectRelationCreator:
    def test_create_relation(self):
        observe_meta_mgt = ObserveMetaMgt()
        sub_entity = gen_app_instance_entity(observe_meta_mgt.get_observe_meta('appinstance'))
        obj_entity = gen_host_entity(observe_meta_mgt.get_observe_meta('host'))
        relation_meta = DirectRelationMeta('runs_on', 'direct', 'appinstance', 'host', [])
        for item in observe_meta_mgt.relation_meta_set:
            if relation_meta == item:
                relation_meta = item
                break
        relation = DirectRelationCreator.create_relation(sub_entity, obj_entity, relation_meta)
        assert relation is not None
        assert relation.id == '{}_{}_{}'.format('runs_on', sub_entity.id, obj_entity.id)
        assert relation.type == 'runs_on'
        assert relation.layer == 'direct'
        assert relation.sub_entity is sub_entity
        assert relation.obj_entity is obj_entity

        sub_entity = gen_app_instance_entity(observe_meta_mgt.get_observe_meta('appinstance'), machine_id='123')
        obj_entity = gen_host_entity(observe_meta_mgt.get_observe_meta('host'), machine_id='456')
        relation = DirectRelationCreator.create_relation(sub_entity, obj_entity, relation_meta)
        assert relation is None

        sub_entity = gen_app_instance_entity(observe_meta_mgt.get_observe_meta('appinstance'), container_id='1')
        obj_entity = gen_host_entity(observe_meta_mgt.get_observe_meta('host'))
        relation = DirectRelationCreator.create_relation(sub_entity, obj_entity, relation_meta)
        assert relation is None

        sub_entity = gen_app_instance_entity(observe_meta_mgt.get_observe_meta('appinstance'))
        obj_entity = gen_host_entity(observe_meta_mgt.get_observe_meta('host'))
        relation_meta1 = DirectRelationMeta('runs_on', 'direct', 'appinstance', 'container',
                                            relation_meta.matches, relation_meta.requires)
        relation = DirectRelationCreator.create_relation(sub_entity, obj_entity, relation_meta1)
        assert relation is None

    def test_create_relations(self):
        observe_meta_mgt = ObserveMetaMgt()

        observe_entities = []
        relations = DirectRelationCreator.create_relations(observe_entities)
        assert len(relations) == 0

        app_inst1 = gen_app_instance_entity(observe_meta_mgt.get_observe_meta('appinstance'), machine_id='123')
        task1 = gen_task_entity(observe_meta_mgt.get_observe_meta('task'), pid=1, machine_id='123')
        observe_entities = [app_inst1, task1]
        relations = DirectRelationCreator.create_relations(observe_entities)
        assert len(relations) == 1

        tcp_link1 = gen_tcp_link_entity(observe_meta_mgt.get_observe_meta('tcp_link'), pid=1, machine_id='123')
        observe_entities = [app_inst1, task1, tcp_link1]
        relations = DirectRelationCreator.create_relations(observe_entities)
        assert len(relations) == 2

        app_inst2 = gen_app_instance_entity(observe_meta_mgt.get_observe_meta('appinstance'), machine_id='456')
        task2 = gen_task_entity(observe_meta_mgt.get_observe_meta('task'), pid=1, machine_id='456')
        tcp_link2 = gen_tcp_link_entity(observe_meta_mgt.get_observe_meta('tcp_link'), pid=1, machine_id='456')
        observe_entities = [app_inst1, task1, tcp_link1, app_inst2, task2, tcp_link2]
        relations = DirectRelationCreator.create_relations(observe_entities)
        assert len(relations) == 6


class TestIndirectRelationCreator:
    def test_create_connect_relation(self):
        observe_meta_mgt = ObserveMetaMgt()

        # create success
        sub_entity = gen_task_entity(observe_meta_mgt.get_observe_meta('task'), pid=1, machine_id='123')
        obj_entity = gen_task_entity(observe_meta_mgt.get_observe_meta('task'), pid=1, machine_id='234')
        relation = IndirectRelationCreator.create_connect_relation(sub_entity, obj_entity)
        assert relation is not None

        # object entity is subject entity
        obj_entity = gen_task_entity(observe_meta_mgt.get_observe_meta('task'), pid=1, machine_id='123')
        relation = IndirectRelationCreator.create_connect_relation(sub_entity, obj_entity)
        assert relation is None

        # relation meta not match
        obj_entity = gen_host_entity(observe_meta_mgt.get_observe_meta('host'), machine_id='123')
        relation = IndirectRelationCreator.create_connect_relation(sub_entity, obj_entity)
        assert relation is None

    def test_create_connect_relations(self):
        observe_meta_mgt = ObserveMetaMgt()

        observe_entities = []
        direct_relations = DirectRelationCreator.create_relations(observe_entities)
        connect_relations = IndirectRelationCreator.create_connect_relations(observe_entities, direct_relations)
        assert len(connect_relations) == 0

        # case: is_peer -> connect
        task1 = gen_task_entity(observe_meta_mgt.get_observe_meta('task'), pid=1, machine_id='123')
        tcp_link1 = gen_tcp_link_entity(observe_meta_mgt.get_observe_meta('tcp_link'), pid=1, machine_id='123')
        task2 = gen_task_entity(observe_meta_mgt.get_observe_meta('task'), pid=1, machine_id='456')
        tcp_link2 = gen_tcp_link_entity(observe_meta_mgt.get_observe_meta('tcp_link'), pid=1, machine_id='456')
        observe_entities = [task1, tcp_link1, task2, tcp_link2]
        direct_relations = DirectRelationCreator.create_relations(observe_entities)
        assert len(direct_relations) == 4
        connect_relations = IndirectRelationCreator.create_connect_relations(observe_entities, direct_relations)
        assert len(connect_relations) == 2

        # case: is_server & is_client -> connect
        tcp_link1 = gen_tcp_link_entity(observe_meta_mgt.get_observe_meta('tcp_link'),
                                        server_ip='0.0.0.0', server_port='80',
                                        pid=1, machine_id='123', role=0)
        tcp_link2 = gen_tcp_link_entity(observe_meta_mgt.get_observe_meta('tcp_link'),
                                        server_ip='1.1.1.1', server_port='80', client_ip='2.2.2.2',
                                        pid=1, machine_id='456', role=1)
        ipvs_link = gen_ipvs_link_entity(observe_meta_mgt.get_observe_meta('ipvs_link'),
                                         server_ip='0.0.0.0', server_port='80', virtual_ip='1.1.1.1', virtual_port='80',
                                         local_ip='3.3.3.3', client_ip='2.2.2.2',
                                         machine_id='789')
        observe_entities = [task1, tcp_link1, task2, tcp_link2, ipvs_link]
        direct_relations = DirectRelationCreator.create_relations(observe_entities)
        assert len(direct_relations) == 4
        connect_relations = IndirectRelationCreator.create_connect_relations(observe_entities, direct_relations)
        print(connect_relations)
        assert len(connect_relations) == 1

    def test_create_relations(self):
        observe_meta_mgt = ObserveMetaMgt()

        task1 = gen_task_entity(observe_meta_mgt.get_observe_meta('task'), pid=1, machine_id='123')
        tcp_link1 = gen_tcp_link_entity(observe_meta_mgt.get_observe_meta('tcp_link'), pid=1, machine_id='123')
        task2 = gen_task_entity(observe_meta_mgt.get_observe_meta('task'), pid=1, machine_id='456')
        tcp_link2 = gen_tcp_link_entity(observe_meta_mgt.get_observe_meta('tcp_link'), pid=1, machine_id='456')
        observe_entities = [task1, tcp_link1, task2, tcp_link2]
        direct_relations = DirectRelationCreator.create_relations(observe_entities)
        assert len(direct_relations) == 4
        connect_relations = IndirectRelationCreator.create_relations(observe_entities, direct_relations)
        assert len(connect_relations) == 2

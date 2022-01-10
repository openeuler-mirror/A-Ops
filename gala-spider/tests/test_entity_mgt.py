from spider.conf.observe_meta import ObserveMetaMgt, DirectRelationMeta
from spider.entity_mgt import ObserveEntityCreator, DirectRelationCreator, IndirectRelationCreator
from .common import gen_host_entity, gen_task_entity, gen_tcp_link_entity, gen_ipvs_link_entity
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
            'task_name': 'task0',
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
        assert entity.name == entity_attrs.get('task_name')
        assert entity.level == entity_meta.level
        assert entity.timestamp == entity_attrs.get('timestamp')
        assert entity.attrs
        assert len(entity.attrs) == 4
        # keys
        assert entity.attrs.get('pid') == entity_attrs.get('pid')
        assert entity.attrs.get('machine_id') == entity_attrs.get('machine_id')
        # labels
        assert entity.attrs.get('task_name') == entity_attrs.get('task_name')
        # metrics
        assert entity.attrs.get('fork_count') == entity_attrs.get('fork_count')

        del entity_attrs['pid']
        entity = ObserveEntityCreator.create_observe_entity(entity_type, entity_attrs, entity_meta)
        assert entity is None

        entity_attrs.setdefault('pid', 1)
        del entity_attrs['task_name']
        entity = ObserveEntityCreator.create_observe_entity(entity_type, entity_attrs, entity_meta)
        assert entity is not None
        assert entity.name is None


class TestDirectRelationCreator:
    def test_create_relation(self):
        observe_meta_mgt = ObserveMetaMgt()
        sub_entity = gen_task_entity(observe_meta_mgt.get_observe_meta('task'))
        obj_entity = gen_host_entity(observe_meta_mgt.get_observe_meta('host'))
        relation_meta = DirectRelationMeta('runs_on', 'direct', 'task', 'host', [])
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

        sub_entity = gen_task_entity(observe_meta_mgt.get_observe_meta('task'), machine_id='123')
        obj_entity = gen_host_entity(observe_meta_mgt.get_observe_meta('host'), machine_id='456')
        relation = DirectRelationCreator.create_relation(sub_entity, obj_entity, relation_meta)
        assert relation is None

        sub_entity = gen_task_entity(observe_meta_mgt.get_observe_meta('task'), container_id='1')
        obj_entity = gen_host_entity(observe_meta_mgt.get_observe_meta('host'))
        relation = DirectRelationCreator.create_relation(sub_entity, obj_entity, relation_meta)
        assert relation is None

        sub_entity = gen_task_entity(observe_meta_mgt.get_observe_meta('task'))
        obj_entity = gen_host_entity(observe_meta_mgt.get_observe_meta('host'))
        relation_meta1 = DirectRelationMeta('runs_on', 'direct', 'task', 'container',
                                            relation_meta.matches, relation_meta.requires)
        relation = DirectRelationCreator.create_relation(sub_entity, obj_entity, relation_meta1)
        assert relation is None

    def test_create_relations(self):
        observe_meta_mgt = ObserveMetaMgt()

        observe_entities = []
        relations = DirectRelationCreator.create_relations(observe_entities)
        assert len(relations) == 0

        host1 = gen_host_entity(observe_meta_mgt.get_observe_meta('host'), machine_id='123')
        task1 = gen_task_entity(observe_meta_mgt.get_observe_meta('task'), pid=1, machine_id='123')
        observe_entities = [host1, task1]
        relations = DirectRelationCreator.create_relations(observe_entities)
        assert len(relations) == 1

        tcp_link1 = gen_tcp_link_entity(observe_meta_mgt.get_observe_meta('tcp_link'), pid=1, machine_id='123')
        observe_entities = [host1, task1, tcp_link1]
        relations = DirectRelationCreator.create_relations(observe_entities)
        assert len(relations) == 2

        host2 = gen_host_entity(observe_meta_mgt.get_observe_meta('host'), machine_id='456')
        task2 = gen_task_entity(observe_meta_mgt.get_observe_meta('task'), pid=1, machine_id='456')
        tcp_link2 = gen_tcp_link_entity(observe_meta_mgt.get_observe_meta('tcp_link'), pid=1, machine_id='456')
        observe_entities = [host1, task1, tcp_link1, host2, task2, tcp_link2]
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
        host1 = gen_host_entity(observe_meta_mgt.get_observe_meta('host'), machine_id='123')
        task1 = gen_task_entity(observe_meta_mgt.get_observe_meta('task'), pid=1, machine_id='123')
        tcp_link1 = gen_tcp_link_entity(observe_meta_mgt.get_observe_meta('tcp_link'), pid=1, machine_id='123')
        host2 = gen_host_entity(observe_meta_mgt.get_observe_meta('host'), machine_id='456')
        task2 = gen_task_entity(observe_meta_mgt.get_observe_meta('task'), pid=1, machine_id='456')
        tcp_link2 = gen_tcp_link_entity(observe_meta_mgt.get_observe_meta('tcp_link'), pid=1, machine_id='456')
        observe_entities = [host1, task1, tcp_link1, host2, task2, tcp_link2]
        direct_relations = DirectRelationCreator.create_relations(observe_entities)
        assert len(direct_relations) == 6
        connect_relations = IndirectRelationCreator.create_connect_relations(observe_entities, direct_relations)
        assert len(connect_relations) == 4

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
        observe_entities = [host1, task1, tcp_link1, host2, task2, tcp_link2, ipvs_link]
        direct_relations = DirectRelationCreator.create_relations(observe_entities)
        assert len(direct_relations) == 6
        connect_relations = IndirectRelationCreator.create_connect_relations(observe_entities, direct_relations)
        print(connect_relations)
        assert len(connect_relations) == 2

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

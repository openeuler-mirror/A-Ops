from spider.data_process.prometheus_processor import g_prometheus_processor
from spider.conf.observe_meta import ObserveMetaMgt, g_observe_meta_mgt
from spider.controllers.gala_spider import get_observed_entity_list
from spider.util import conf
from tests.common import gen_task_entity, gen_tcp_link_entity


class TestController:
    def _mock_context(self, mocker, observe_meta_mgt: ObserveMetaMgt):
        mocker.patch.object(conf, 'db_agent', 'prometheus')

        mocker.patch.object(g_observe_meta_mgt, 'data_agent', observe_meta_mgt.data_agent)
        mocker.patch.object(g_observe_meta_mgt, 'observe_meta_map', observe_meta_mgt.observe_meta_map)
        mocker.patch.object(g_observe_meta_mgt, 'relation_meta_set', observe_meta_mgt.relation_meta_set)

    def _mock_get_observe_entities(self, mocker, observe_entities):
        mocker.patch.object(g_prometheus_processor, 'get_observe_entities', return_value=observe_entities)

    def test_get_observed_entity_list(self, mocker, observe_meta_mgt: ObserveMetaMgt):
        self._mock_context(mocker, observe_meta_mgt)

        self._mock_get_observe_entities(mocker, [])
        resp, code = get_observed_entity_list(0)
        assert code == 200
        assert resp.code == 500
        assert resp.msg == 'Empty'

        task1 = gen_task_entity(observe_meta_mgt.get_observe_meta('task'), pid=1, machine_id='123')
        tcp_link1 = gen_tcp_link_entity(observe_meta_mgt.get_observe_meta('tcp_link'), pid=1, machine_id='123')
        task2 = gen_task_entity(observe_meta_mgt.get_observe_meta('task'), pid=1, machine_id='456')
        tcp_link2 = gen_tcp_link_entity(observe_meta_mgt.get_observe_meta('tcp_link'), pid=1, machine_id='456')
        observe_entities = [task1, tcp_link1, task2, tcp_link2]

        self._mock_get_observe_entities(mocker, observe_entities)
        resp, code = get_observed_entity_list(0)
        print(resp)
        assert code == 200
        assert resp.code == 200
        assert resp.msg == 'Successful'
        assert resp.timestamp == 0
        assert len(resp.entityids) == 4
        assert len(resp.entities) == 4
        task1_resp = None

        for entity in resp.entities:
            if entity.entityid == task1.id:
                task1_resp = entity
                break
        assert task1_resp is not None
        assert task1_resp.entityid == task1.id
        assert task1_resp.type == 'task'
        assert task1_resp.level == 'PROCESS'
        assert len(task1_resp.attrs) == 5
        assert len(task1_resp.dependingitems) == 1
        assert len(task1_resp.dependeditems) == 2



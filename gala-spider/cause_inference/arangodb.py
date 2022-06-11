from pyArango.connection import Connection
from pyArango.database import Database
from pyArango.theExceptions import AQLQueryError

from cause_inference.exceptions import DBException

_TIMESTAMP_COLL_NAME = 'Timestamps'
_OBSERVE_ENTITY_COLL_PREFIX = 'ObserveEntities'


def _get_collection_name(collection_type, ts_sec):
    return '{}_{}'.format(collection_type, ts_sec)


def connect_to_arangodb(arango_url, db_name):
    try:
        conn: Connection = Connection(arangoURL=arango_url)
    except ConnectionError as ex:
        raise DBException('Connect to arangodb error because {}'.format(ex)) from ex
    if not conn.hasDatabase(db_name):
        raise DBException('Arango database {} not found, please check!'.format(db_name))
    return conn.databases[db_name]


def query_recent_topo_ts(db: Database, ts):
    bind_vars = {'@collection': _TIMESTAMP_COLL_NAME, 'ts': ts}
    aql_query = '''
    FOR t IN @@collection
      FILTER TO_NUMBER(t._key) <= @ts
      SORT t._key DESC
      LIMIT 1
      RETURN t._key
    '''
    try:
        query_res = db.AQLQuery(aql_query, bindVars=bind_vars, rawResults=True).response
    except AQLQueryError as ex:
        raise DBException(ex) from ex
    if query_res.get('error') or not query_res.get('result'):
        raise DBException('Can not find topological graph at the abnormal timestamp {}'.format(ts))
    last_ts = query_res.get('result')[0]
    return int(last_ts)


def query_topo_entities(db: Database, ts, query_options=None):
    if not query_options:
        query_options = {}

    entity_coll_name = _get_collection_name(_OBSERVE_ENTITY_COLL_PREFIX, ts)
    bind_vars = {'@collection': entity_coll_name}
    bind_vars.update(query_options)
    filter_options = ['v.{} == @{}'.format(k, k) for k in query_options]
    filter_str = ' and '.join(filter_options)
    aql_query = '''
    FOR v IN @@collection
      FILTER {}
      return v
    '''.format(filter_str)
    try:
        query_res = db.AQLQuery(aql_query, bindVars=bind_vars, rawResults=True).response
    except AQLQueryError as ex:
        raise DBException(ex) from ex
    if query_res.get('error') or not query_res.get('result'):
        raise DBException('Can not find observe entities satisfied.')
    return query_res.get('result')


def query_subgraph(db, ts, start_node_id, edge_collection, depth=1):
    if not edge_collection:
        return {}, False

    entity_coll_name = _get_collection_name(_OBSERVE_ENTITY_COLL_PREFIX, ts)
    bind_vars = {
        '@collection': entity_coll_name,
        'depth': depth,
        'start_v': start_node_id,
    }
    edge_coll_str = ', '.join(edge_collection)
    aql_query = '''
    WITH @@collection
    FOR v, e IN 1..@depth ANY @start_v
      {}
      return {{"vertex": v, "edge": e}}
    '''.format(edge_coll_str)
    try:
        query_res = db.AQLQuery(aql_query, bindVars=bind_vars, rawResults=True).response
    except AQLQueryError as ex:
        raise DBException(ex) from ex
    vertices = {}
    edges = {}
    for item in query_res.get('result'):
        vertex = item.get('vertex')
        edge = item.get('edge')
        vertices.setdefault(vertex.get('_id'), vertex)
        edges.setdefault(edge.get('_id'), edge)
    return {
        'vertices': vertices,
        'edges': edges,
    }

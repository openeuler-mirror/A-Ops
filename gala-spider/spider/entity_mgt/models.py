from dataclasses import dataclass, field, InitVar

from spider.conf.observe_meta import ObserveMeta

ENTITYID_CONCATE_SIGN = '_'
RELATIONID_CONCATE_SIGN = '_'


@dataclass
class ObserveEntity:
    id: str = field(init=False)
    type: str
    name: str
    level: str
    timestamp: float
    attrs: dict = field(init=False)
    observe_data: InitVar[dict]
    observe_meta: InitVar[ObserveMeta]

    def __post_init__(self, observe_data: dict, observe_meta: ObserveMeta):
        if not observe_data or not observe_meta:
            return

        self.attrs = {}
        for key in observe_meta.keys:
            if key in observe_data:
                self.attrs[key] = observe_data.get(key)
        for label in observe_meta.labels:
            if label in observe_data:
                self.attrs[label] = observe_data.get(label)
        for metric in observe_meta.metrics:
            if metric in observe_data:
                self.attrs[metric] = observe_data.get(metric)

        self.id = ''
        if not self.type or not self.attrs:
            return
        ids = [self.type.upper()]
        for key in observe_meta.keys:
            if key not in self.attrs:
                print("which key not exist: {}".format(key))
                return
            ids.append(str(self.attrs.get(key)))

        self.id = ENTITYID_CONCATE_SIGN.join(ids)


@dataclass
class Relation:
    id: str = field(init=False)
    type: str
    layer: str
    sub_entity: ObserveEntity
    obj_entity: ObserveEntity

    def __post_init__(self):
        self.id = ''
        if not self.type or self.sub_entity is None or self.obj_entity is None:
            return
        self.id = RELATIONID_CONCATE_SIGN.join([self.type, self.sub_entity.id, self.obj_entity.id])

MACHINE_ID_NAME = 'machine_id'
ENTITYID_CONCATE_SIGN = '_'
ALLOWED_PUNC_CHARS = {'_', '-', ':', '.', '@', '(', ')', '+', ',', '=', ';', '$', '$', '!', '*', '\'', '%'}
SUBSTI_CHAR_OF_ENTITYID = ':'
MAX_LEN_OF_ENTITYID = 254


def concate_entity_id(entity_type: str, labels: dict, keys: list) -> str:
    if not entity_type or not labels.get(MACHINE_ID_NAME):
        return ''
    ids = [labels.get(MACHINE_ID_NAME), entity_type]
    for key in keys:
        if key not in labels:
            return ''
        if key == MACHINE_ID_NAME:
            continue
        ids.append(str(labels.get(key)))
    return ENTITYID_CONCATE_SIGN.join(ids)


def escape_entity_id(entity_id: str) -> str:
    entity_id = entity_id[:MAX_LEN_OF_ENTITYID]
    ids = list(entity_id)
    escaped = False
    for i, c in enumerate(ids):
        if 'a' <= c <= 'z' or 'A' <= c <= 'Z':
            continue
        if '0' <= c <= '9':
            continue
        if c in ALLOWED_PUNC_CHARS:
            continue
        ids[i] = SUBSTI_CHAR_OF_ENTITYID
        escaped = True
    if not escaped:
        return entity_id
    return ''.join(ids)

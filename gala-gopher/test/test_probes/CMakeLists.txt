CMAKE_MINIMUM_REQUIRED(VERSION 3.12.1)
PROJECT(gala-gopher-test)

MESSAGE("ENV PROBES_LIST:\n"  ${PROBES_LIST})
MESSAGE("ENV PROBES_C_LIST:\n"  ${PROBES_C_LIST})
MESSAGE("ENV PROBES_META_LIST:\n"  ${PROBES_META_LIST})

SET(EXECUTABLE_OUTPUT_PATH ../../)
SET(EXECUTABLE_TARGET probes_test)

SET(SRC_DIR         ../../src)
SET(BASE_DIR        ${SRC_DIR}/lib)
SET(RESOURCE_DIR    ${SRC_DIR}/resource)
SET(CONFIG_DIR      ${SRC_DIR}/lib/config)
SET(EGRESS_DIR      ${SRC_DIR}/egress)
SET(INGRESS_DIR     ${SRC_DIR}/ingress)
SET(FIFO_DIR        ${SRC_DIR}/lib/fifo)
SET(META_DIR        ${SRC_DIR}/lib/meta)
SET(KAFKA_DIR       ${SRC_DIR}/lib/kafka)
SET(TAOSDATA_DIR    ${SRC_DIR}/lib/taosdata)
SET(PROBE_DIR       ${SRC_DIR}/lib/probe)

SET(LIBRDKAFKA_DIR /usr/include/librdkafka)

SET(CMAKE_C_FLAGS "-rdynamic -g -fno-builtin-fprintf -Wl,--wrap=fprintf   \
    -DPROBES_LIST=\"${PROBES_LIST}\"                        \
    -DPROBES_META_LIST=\"${PROBES_META_LIST}\" "
)

SET(SOURCES main.c test_probes.c 
    ${RESOURCE_DIR}/resource.c
    ${CONFIG_DIR}/config.c
    ${EGRESS_DIR}/egress.c
    ${INGRESS_DIR}/ingress.c

    ${FIFO_DIR}/fifo.c
    ${META_DIR}/meta.c
    ${KAFKA_DIR}/kafka.c
    ${TAOSDATA_DIR}/taosdata.c

    ${PROBE_DIR}/probe.c
)

FOREACH(FILE ${PROBES_C_LIST})
    SET(SOURCES ${SOURCES} ${FILE})
ENDFOREACH()
MESSAGE("SOURCES:\n" ${SOURCES})

ADD_EXECUTABLE(${EXECUTABLE_TARGET} ${SOURCES})
TARGET_INCLUDE_DIRECTORIES(${EXECUTABLE_TARGET} PRIVATE 
    ${BASE_DIR}
    ${RESOURCE_DIR}
    ${CONFIG_DIR}
    ${EGRESS_DIR}
    ${INGRESS_DIR}

    ${FIFO_DIR}
    ${META_DIR}
    ${KAFKA_DIR}
    ${TAOSDATA_DIR}

    ${PROBE_DIR}
    ${LIBRDKAFKA_DIR}
)

TARGET_LINK_LIBRARIES(${EXECUTABLE_TARGET} PRIVATE config dl rdkafka taos cunit)


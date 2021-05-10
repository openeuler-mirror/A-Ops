CMAKE_MINIMUM_REQUIRED(VERSION 3.12.1)
PROJECT(gala-gopher-test)

SET(EXECUTABLE_OUTPUT_PATH ../../)
SET(EXECUTABLE_TARGET submodule_test)

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
SET(IMDB_DIR        ${SRC_DIR}/lib/imdb)

SET(LIBRDKAFKA_DIR /usr/include/librdkafka)

SET(CMAKE_C_FLAGS "-g")

ADD_EXECUTABLE(${EXECUTABLE_TARGET}
    main.c
    test_fifo.c
    test_kafka.c
    test_meta.c
    test_probe.c
    test_taosdata.c
    test_imdb.c

    ${RESOURCE_DIR}/resource.c
    ${CONFIG_DIR}/config.c
    ${EGRESS_DIR}/egress.c
    ${INGRESS_DIR}/ingress.c
    ${FIFO_DIR}/fifo.c
    ${META_DIR}/meta.c
    ${KAFKA_DIR}/kafka.c
    ${TAOSDATA_DIR}/taosdata.c
    ${PROBE_DIR}/probe.c
    ${IMDB_DIR}/imdb.c
)

TARGET_INCLUDE_DIRECTORIES(${EXECUTABLE_TARGET} PRIVATE ${BASE_DIR}
    ${RESOURCE_DIR}
    ${CONFIG_DIR}
    ${EGRESS_DIR}
    ${INGRESS_DIR}
    ${FIFO_DIR}
    ${META_DIR}
    ${KAFKA_DIR}
    ${TAOSDATA_DIR}
    ${PROBE_DIR}
    ${IMDB_DIR}
    ${LIBRDKAFKA_DIR}
)

TARGET_LINK_LIBRARIES(${EXECUTABLE_TARGET} PRIVATE config dl rdkafka taos cunit)


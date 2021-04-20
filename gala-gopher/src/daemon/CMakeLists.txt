CMAKE_MINIMUM_REQUIRED(VERSION 3.12.1)
PROJECT(gala-gopher)

MESSAGE("ENV PROBES_LIST:\n"  ${PROBES_LIST})
MESSAGE("ENV PROBES_C_LIST:\n"  ${PROBES_C_LIST})
MESSAGE("ENV PROBES_META_LIST:\n"  ${PROBES_META_LIST})

SET(EXECUTABLE_OUTPUT_PATH ../../../)

SET(BASE_DIR ../lib)
SET(CONFIG_DIR ../config)
SET(EGRESS_DIR ../egress)
SET(INGRESS_DIR ../ingress)
SET(FIFO_DIR ../lib/fifo)
SET(META_DIR ../lib/meta)
SET(KAFKA_DIR ../lib/kafka)
SET(TAOSDATA_DIR ../lib/taosdata)
SET(PROBE_DIR ../lib/probe)

SET(LIBRDKAFKA_DIR /usr/include/librdkafka)

SET(CMAKE_C_FLAGS "-rdynamic -g -fno-builtin-fprintf -Wl,--wrap=fprintf   \
    -DPROBES_LIST=\"${PROBES_LIST}\"                        \
    -DPROBES_META_LIST=\"${PROBES_META_LIST}\" "
)

SET(SOURCES main.c daemon.c
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

ADD_EXECUTABLE(gala-gopher ${SOURCES})
TARGET_INCLUDE_DIRECTORIES(gala-gopher PRIVATE 
	${BASE_DIR}
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

TARGET_LINK_LIBRARIES(gala-gopher PRIVATE config pthread dl rdkafka taos)


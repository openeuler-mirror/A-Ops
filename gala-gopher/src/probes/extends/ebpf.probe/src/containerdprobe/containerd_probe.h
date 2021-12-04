#ifndef __TRACE_CONTAINERD__H
#define __TRACE_CONTAINERD__H

#define TASK_COMM_LEN             16
#define CONTAINER_MAX_ENTRIES   1000
#define CONTAINER_ID_LEN          64
#define NAMESPACE_LEN             64

struct go_containerd_t {
    // Arguments of runtime/v1/linux.(*Task).Start.
    int task_Start_t_offset;                // 8

    // Arguments of runtime/v1/linux.(*Task).Delete.
    int task_Delete_t_offset;               // 8
    int task_Delete_resp_offset;            // 24

    // Members of /runtime.Exit
    int runtime_Exit_Pid_offset;            // 0
    int runtime_Exit_Status_offset;         // 4
    int runtime_Exit_Timestamp_offset;      // 8

    // Members of /runtime/v1/linux.Task
    int linux_Task_id_offset;               // 8
    int linux_Task_pid_offset;              // 24
    int linux_Task_namespace_offset;        // 40
    int linux_Task_cg_offset;               // 56

};

struct container_key {
    char container_id[CONTAINER_ID_LEN];
};

struct container_value {
    char namespace[NAMESPACE_LEN];
    __u32 task_pid;
    __u32 containerd_pid;
    __u32 status;
    char comm[16];
};

#endif /* __TRACE_CONTAINERD__H */
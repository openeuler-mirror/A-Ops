# 根因定位接口文档

## 根因定位结果输出格式

根因定位的结果会作为一条 json 格式的消息发送到 kafka ，它的格式如下：

```json
{
    "Timestamp": 0, 
    "event_id": "",
    "Atrributes": {
        "event_id": ""
    }, 
    "Resource": {
        "abnormal_kpi": {
            "metric_id": "",
            "entity_id": "",
            "timestamp": 0, 
            "metric_labels": {}
        }, 
        "cause_metrics": [
            {
                "metric_id": "",
                "entity_id": "",
                "metric_labels": {},
                "timestamp": 0,
                "path": [
                    {
                        "metric_id": "",
                        "entity_id": "",
                        "metric_labels": {},
                        "timestamp": 0
                    },
                    {
                        "metric_id": "",
                        "entity_id": "",
                        "metric_labels": {},
                        "timestamp": 0
                    }
                ]
            }
        ]
    }, 
    "SeverityText": "WARN", 
    "SeverityNumber": 13, 
    "Body": "A cause inferring event for an abnormal event"
}
```

字段说明：

- Timestamp ：此次根因定位对应的异常 KPI 事件发生的时间
- event_id ：异常事件 ID
- Atrributes ：事件属性信息，包括：
  - event_id ：异常事件 ID
- Resource ：包含根因定位的输出结果信息
  - abnormal_kpi ：此次根因定位对应的异常 KPI 的信息，包括：
    - metric_id ：异常 KPI 的名称
    - entity_id ：异常 KPI 对应的观测实例ID
    - timestamp ：异常 KPI 发生的时间
    - metric_labels ：异常 KPI 的标签信息
  - cause_metrics ：此次根因定位输出的 topK 根因指标信息，它是一个对象列表，每个元素内容包括：
    - metric_id ：根因指标的名称
    - entity_id ：根因指标对应的观测实例ID
    - timestamp ：根因指标发生异常的时间
    - metric_labels ：根因指标的标签信息
    - path ：根因传播路径，它是一个对象列表，从根因指标到异常KPI指标经过的异常指标传播路径按顺序存入该列表。每个元素内容包括：
      - metric_id ：路径中指标的名称
      - entity_id ：路径中指标对应的观测实例ID
      - timestamp ：路径中指标发生异常的时间
      - metric_labels ：路径中指标的标签信息
- SeverityText ：根因定位事件的严重等级
- SeverityNumber ：根因定位事件的严重等级编号
- Body ：根因定位事件的描述信息
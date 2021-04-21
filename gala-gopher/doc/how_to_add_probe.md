如何开发探针
============
## 探针参考
```
example.probe
```

## 探针技术规范
### 1、定义探针的main函数
探针main函数要以`int main()`形式，不支持使用`int main(int argc, char *argv[])`作为main函数<br>
参考:
```c
int main()
{
    example_collect_data();
    return 0;
}
```
### 2、定义探针的meta文件

```conf
version = "1.0.0"                # meta文件版本

measurements:                    # 探针数据表list，可以在一个探针中配置多张数据表
(
    {                            #--> 探针数据表
        name: "example",         #--> 数据表名称（唯一）
        fields:                  #--> 数据字段
        (
            "cpu_usage",         #--> 数据字段名称
            "memory_usage",
            "tcp_connection_num",
        )
    }
)
```

### 3、输出探针指标
探针采集的数据要以通过`fprintf`打印的方式<br>
打印的第一个字符串是数据表名称<br>
而后的每个字符串和数据字段一一对应<br>
每个字段数据按照 `|` 分隔 <br>
如这里和example表中的数据对应：<br>
`cpu_usage:high`<br>
`memory_usage:low`<br>
`tcp_connection_num:15`<br>

```c
void example_collect_data()
{
    fprintf(stdout, "|%s|%s|%s|%s|\n",
        "example",
        "high",
        "low",
        "15"
    );
}
```

## 总结
按照上面的方式开发好探针后，就可以被框架自动集成了：）

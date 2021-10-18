#!/usr/bin/env python3

import ast
import multiprocessing
from spider.db_agent.db_process import db_process_agent
from spider.ui_agent.show_process import ui_neo4j_agent
from spider.util.conf import db_agent
from spider.util.conf import neo4j_timer

def main():
    record = []
    process = multiprocessing.Process(target=db_process_agent, args=(ast.literal_eval(db_agent),))
    process.start()
    record.append(process)
    process = multiprocessing.Process(target=ui_neo4j_agent, args=(int(neo4j_timer),))
    process.start()
    record.append(process)
    for process in record:
        process.join()

if __name__ == '__main__':
    main()

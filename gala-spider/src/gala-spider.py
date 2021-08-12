import configparser
import multiprocessing
import time
from db_agent import db_process
from ui_agent import show_process

if __name__ == '__main__':
    # Obtain Conf
    cf = configparser.ConfigParser()
    cf.read("../config/gala-spider.conf", encoding="utf-8")
    db_agent = cf.get("global", "data_source")
    ui_agent = cf.get("global", "ui_source")

    # Multi-process
    record = []
    process = multiprocessing.Process(target=db_process.main, args = (eval(db_agent),))
    process.start()
    record.append(process)
    process = multiprocessing.Process(target=show_process.main, args=(eval(ui_agent), 5,))
    process.start()
    record.append(process)
    for process in record:
        process.join()
#!/usr/bin/env python3

import connexion
import multiprocessing
from spider import encoder
from spider.db_agent.db_process import db_process_agent
from spider.util.conf import db_agent

def main():
    #record = []
    #process = multiprocessing.Process(target=db_process_agent, args=(eval(db_agent),))
    #process.start()
    #record.append(process)
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'Topo Graph Engine Service'})
    app.run(port=11115)


if __name__ == '__main__':
    main()

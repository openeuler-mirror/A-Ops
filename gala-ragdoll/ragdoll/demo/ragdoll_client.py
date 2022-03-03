import argparse

from ragdoll.demo.domain import DomainManage
from ragdoll.demo.host import HostManage
from ragdoll.demo.conf_manage import ConfManage
from ragdoll.demo.conf_sync import ConfSync

def parse_commands():
    domain_manage = DomainManage()
    host_manage =HostManage()
    conf_manages = ConfManage()
    conf_syncs = ConfSync()

    ragdoll_cli = argparse.ArgumentParser(prog="ragdoll_cli")
    sub_parser = ragdoll_cli.add_subparsers(dest="sub_parser", title="ragdoll_cli")

    # 1 ragdoll > domian
    domain = sub_parser.add_parser("domain", help="Configuring Domain Management.")
    domain = domain.add_subparsers(dest="sub_sub_parser", title="domian")
    
    # ragdoll > domian > create
    domain_create = domain.add_parser("create", help="create configuring domain")
    domain_create.add_argument("--domainName", dest="domain_name", type=str, action="append", required=True, help="domain name")
    domain_create.add_argument("--priority", dest="priority", type=int, action="append", required=True, help="domain priority")
    domain_create.set_defaults(func=domain_manage.domain_create)
    
    # ragdoll > domian > delete
    domain_delete = domain.add_parser("delete", help="delete configuring domain")
    domain_delete.add_argument("--domainName", dest="domain_name", type=str, action="append", required=True, help="domain name")
    domain_delete.set_defaults(func=domain_manage.domain_delete)
    
    # ragdoll > domian > query
    domain_query = domain.add_parser("query", help="query configuring domain")
    domain_query.set_defaults(func=domain_manage.domain_query)

    # 2 ragdoll > host
    host = sub_parser.add_parser("host", help="Configuring Host Management in a Domain.")
    host = host.add_subparsers(dest="sub_sub_parser", title="host")
    
    # ragdoll > host > add
    host_add = host.add_parser("add", help="add a host to a configuration domain")
    host_add.add_argument("--domainName", dest="domain_name", type=str, required=True, help="domain name")
    host_add.add_argument("--ipv6", dest="ipv6", type=str, action="append", required=True, help="ipv6 address")
    host_add.add_argument("--ip", dest="ip", type=str, action="append", required=True, help="ip address")
    host_add.add_argument("--hostId", dest="host_id", type=str, action="append", required=True, help="host id")
    host_add.set_defaults(func=host_manage.host_add)
    
    # ragdoll > host > query
    host_query = host.add_parser("query", help="query host info in a configuration domain")
    host_query.add_argument("--domainName", dest="domain_name", type=str, required=True, help="domain name")
    host_query.set_defaults(func=host_manage.host_query)

    # ragdoll > host > delete
    host_delete = host.add_parser("delete", help="delete a host from a configuration domain")
    host_delete.add_argument("--domainName", dest="domain_name", type=str, required=True, help="domain name")
    host_delete.add_argument("--ipv6", dest="ipv6", type=str, action="append", required=True, help="ipv6 address")
    host_delete.add_argument("--ip", dest="ip", type=str, action="append", required=True, help="ip address")
    host_delete.add_argument("--hostId", dest="host_id", type=str, action="append", required=True, help="host id")
    host_delete.set_defaults(func=host_manage.host_delete)

    # 3 ragdoll > conf_manage
    conf_manage = sub_parser.add_parser("confManage", help="Expected Configuration Management.")
    conf_manage = conf_manage.add_subparsers(dest="sub_sub_parser", title="conf_manage")

    # ragdoll > conf_manage > add
    conf_add = conf_manage.add_parser("add", help="add expected configurations to a configuration domain")
    conf_add.add_argument("--domainName", dest="domain_name", type=str, required=True, help="domain name")
    conf_add.add_argument("--confPath", dest="file_path", type=str, action="append", required=True, help="configuration path")
    conf_add.add_argument("--confInfo", dest="contents", type=str, action="append", help="configuration contents")
    conf_add.add_argument("--hostId", dest="host_id", type=str, action="append", help="host id. You should choose at least one of --confInfo and --hostId.")
    conf_add.set_defaults(func=conf_manages.conf_add)
    
    # ragdoll > conf_manage > query
    conf_query = conf_manage.add_parser("query", help="query the managed configurations in the configuration domain.")
    conf_query.add_argument("--domainName", dest="domain_name", type=str, required=True, help="domain name")
    conf_query.set_defaults(func=conf_manages.conf_query)

    # ragdoll > conf_manage > delete
    conf_delete = conf_manage.add_parser("delete", help="delete the managed configuration in the configuration domain.")
    conf_delete.add_argument("--domainName", dest="domain_name", type=str, required=True, help="domain name")
    conf_delete.add_argument("--confPath", dest="file_path", type=str, action="append", required=True, help="configuration path")
    conf_delete.set_defaults(func=conf_manages.conf_delete)

    # ragdoll > conf_manage > changelog
    conf_changelog = conf_manage.add_parser("changelog", help="query the changelog of expected configurations in a configuration domain")
    conf_changelog.add_argument("--domainName", dest="domain_name", type=str, required=True, help="domain name")
    conf_changelog.add_argument("--confPath", dest="file_path", type=str, action="append", required=True, help="configuration path")
    conf_changelog.set_defaults(func=conf_manages.conf_changelog)

    # 4 ragdoll > conf_sync
    conf_sync = sub_parser.add_parser("confSync", help="Configuration Synchronization Management.")
    conf_sync = conf_sync.add_subparsers(dest="sub_sub_parser", title="conf_manage")

    # ragdoll > conf_sync > realConf
    query_real_conf = conf_sync.add_parser("queryRealConf", help="querying the real configuration of a host in the configuration domain")
    query_real_conf.add_argument("--domainName", dest="domain_name", type=str, required=True, help="domain name")
    query_real_conf.add_argument("--hostId", dest="host_id", type=str, required=True, action="append", help="host id")
    query_real_conf.set_defaults(func=conf_syncs.query_real_conf)

    # ragdoll > conf_sync > sync
    sync_conf = conf_sync.add_parser("sync", help="sync configurations to hosts")
    sync_conf.add_argument("--domainName", dest="domain_name", type=str, required=True, help="domain name")
    sync_conf.add_argument("--hostId", dest="host_id", type=str, required=True, action="append", help="host id")
    sync_conf.set_defaults(func=conf_syncs.sync_conf)

    # ragdoll > conf_sync > syncStatus
    sync_status = conf_sync.add_parser("syncStatus", help="query the sync status of configurations in a configuration domain")
    sync_status.add_argument("--domainName", dest="domain_name", type=str, required=True, help="domain name")
    sync_status.set_defaults(func=conf_syncs.sync_status)

    # ragdoll > conf_sync > expectedConfs
    expected_conf = conf_sync.add_parser("expectedConfs", help="query the management configuration")
    expected_conf.set_defaults(func=conf_syncs.query_expected_conf)

    args = ragdoll_cli.parse_args()

    if not args.sub_parser:
        ragdoll_cli.print_help()
    elif not args.sub_sub_parser:
        sub_parser.choices[args.sub_parser].print_help()
    else:
        args.func(args)

if __name__ == "__main__":
    parse_commands()
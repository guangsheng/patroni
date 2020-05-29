### 一些入口函数
- patroni 入口函数 patroni/__init__.py: def main():
- patroni_ctl 入口函数 patroni/ctl.py: def ctl(ctx, config_file, dcs, insecure):

- patroni restapi接口: patroni/api.py
- postgresql相关操作: 
	- patroni/ha.py self.state_handler = patroni.postgresql
	- patroni/postgresql/__init__.py 

### 如何抢leader

### patroni主函数-ha._run_cycle
```
#实体
    self.patroni = patroni
    self.state_handler = patroni.postgresql
    self.watchdog = patroni.watchdog
    self.dcs = patroni.dcs
    self.cluster = None
    self.old_cluster = None
    self._async_executor = AsyncExecutor(self.state_handler.cancellable, self.wakeup)
    self._rewind = Rewind(self.state_handler)
#属性
    self._is_leader = False
    self._leader_access_is_restricted = False
    self._was_paused = False
    self._leader_timeline = None
    self.recovering = False
    self._post_bootstrap_task = None
    self._crash_recovery_executed = False
    self._start_timeout = None
    self._disable_sync = 0
#锁
    self._is_leader_lock = RLock()
    self._member_state_lock = RLock()
    
    

cluster = Cluster(initialize, config, leader, last_leader_operation, members, failover, sync, history)

```


### 一些默认的环境变量
CONFIG_DIR_PATH = click.get_app_dir('patroni')
CONFIG_FILE_PATH = os.path.join(CONFIG_DIR_PATH, 'patronictl.yaml')
DCS_DEFAULTS = {'zookeeper': {'port': 2181, 'template': "zookeeper:\n hosts: ['{host}:{port}']"},
                'exhibitor': {'port': 8181, 'template': "exhibitor:\n hosts: [{host}]\n port: {port}"},
                'consul': {'port': 8500, 'template': "consul:\n host: '{host}:{port}'"},
                'etcd': {'port': 2379, 'template': "etcd:\n host: '{host}:{port}'"}}

### 命令执行时可以使用到的几个环境变量
```
-c :PATRONICTL_CONFIG_FILE
-d :DCS
log level : LOGLEVEL/PATRONI_LOGLEVEL/PATRONI_LOG_LEVEL
```


### 一些命令
```
#查看
/opt/patroni-1.6.5/patronictl.py -c /opt/patroni-1.6.5/postgres0.yml list -e
/opt/patroni-1.6.5/patronictl.py --dcs etcd://10.111.29.70:2379 list pro_hello_everest -e
#修改配置
./patronictl.py -c postgres0.yml edit-config
#重启
./patronictl.py -c postgres0.yml restart pro_hello_everest
#查看历史
./patronictl.py -c postgres0.yml history
#从新加载配置
/opt/patroni-1.6.5/patronictl.py -c /opt/patroni-1.6.5/postgres0.yml reload pro_hello_everest
#倒换
/opt/patroni-1.6.5/patronictl.py --dcs etcd://10.111.29.70:2379 switchover pro_hello_everest --master postgresql2 --candidate postgresql1 —force
#重建
/opt/patroni-1.6.5/patronictl.py -c /opt/patroni-1.6.5/postgres.yml reinit pro_hello_everest postgresql2 —force
#查询
/opt/patroni-1.6.5/patronictl.py --dcs etcd://10.111.29.70:2379 query pro_hello_everest -U postgres -d postgres -m postgresql0 -c "select * from t_test" --password

$ /opt/patroni-1.6.5/patronictl.py --help
Usage: patronictl.py [OPTIONS] COMMAND [ARGS]...


Options:
  -c, --config-file TEXT  Configuration file
  -d, --dcs TEXT          Use this DCS
  -k, --insecure          Allow connections to SSL sites without certs
  --help                  Show this message and exit.


Commands:
  configure    Create configuration file
  dsn          Generate a dsn for the provided member, defaults to a dsn of…   #返回值类似host=10.111.29.70 port=3433
  edit-config  Edit cluster configuration
  failover     Failover to a replica
  flush        Discard scheduled events (restarts only currently)
  history      Show the history of failovers/switchovers
  list         List the Patroni members for a given Patroni
  pause        Disable auto failover
  query        Query a Patroni PostgreSQL member                                ## 到某个节点执行SQL语句
  reinit       Reinitialize cluster member                                      ## leader节点不能执行，没有leader不能执行; 使用immediate方式停止数据库然后重建指定member（使用pg_basebackup） 要在对应节点所在机器上执行
  reload       Reload cluster member configuration                              ## 重新加载指定节点的参数（PostgreSQL/log/watchdog/restapi)
  remove       Remove cluster from DCS                                          ## 从DCS中删除掉指定的patroni管理的集群
  restart      Restart cluster member                                           ## 重启指定的PostgreSQL
  resume       Resume auto failover
  scaffold     Create a structure for the cluster in DCS
  show-config  Show cluster configuration
  switchover   Switchover to a replica
  version      Output version of patronictl command or a running Patroni...
```
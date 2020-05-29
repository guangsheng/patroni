import click
import os
import time


def check_postgresql_status(bindir, pg_data, role):
    print "check_postgresql_status"
    check_command = "{0}/pg_controldata -D {1} |grep 'Database cluster state'".format(
        bindir, pg_data.replace('\n', '').replace('\r', ''))
    try:
        c_pipeline = os.popen(check_command)
        cluster_status = c_pipeline.read()
        cluster_status = cluster_status.split(":")[1].strip()
        print cluster_status
        if (role == 'None' and cluster_status == 'in archive recovery') or \
                (role == 'Leader' and cluster_status == 'in production'):
            return True
    except Exception, e:
        print e.message()
        return False
    return False


def process_fail(master_member, slave_member, role, bindir, pg_data, dcs, cluster_name):
    print "process_fail"
    if role == 'Leader':
        print "switchover"
        c_command = '{0} --dcs {1} switchover {2} --master {3} --candidate {4} --force'.\
            format(G_PATRONI_CTL, dcs, cluster_name, master_member, slave_member)
        print c_command
        pipeline = os.popen(c_command)
        print pipeline.read()
        time.sleep(30)
        if not check_postgresql_status(bindir, pg_data, role):
            print "failover!"
            c_command = '{0} --dcs {1} failover {2} --master {3} --candidate {4} --force'.\
                format(G_PATRONI_CTL, dcs, cluster_name, master_member, slave_member)
            os.popen(c_command)

        print "leader failed deal"
    elif role == 'None':
        print 'Slave failed deal'
    else:
        print 'role is wrong-{0}'.format(role)


@click.command()
@click.option('--cluster_name', '-c', help='postgresql cluster name', required=True)
@click.option('--member_name', '-m', help='postgresql cluster member name', required=True)
@click.option('--loop_wait', '-m', help='loop wait seconds', required=False, default=10)
@click.option('--max_error_loop', '-me', help='max error loop', required=False, default=10)
@click.option('--dcs', '-d', help='max error loop', required=True)
@click.option('--bindir', '-b', help='postgresql bin directory', required=True)
def monitor(cluster_name, member_name, loop_wait, max_error_loop, dcs, bindir):
    v_error_count = 0
    time.sleep(300)
    while True:
        config_command = '{0} --dcs {1} show-config {2} |grep data_directory'.format(G_PATRONI_CTL, dcs, cluster_name)
        c_pipeline = os.popen(config_command)
        pg_data = c_pipeline.read()
        if pg_data is None or pg_data == '':
            pass #todo
        pg_data = pg_data.split(':')[1]
        list_command = "{0} --dcs {1} list {2} -f json".format(G_PATRONI_CTL, dcs, cluster_name)
        c_pipeline=os.popen(list_command)
        try:
            s_output=eval(c_pipeline.read())
            v_get_member = False
            v_get_leader = False
            v_master_memeber = 'None'
            v_slave_member = 'None'
            v_local_role = 'None'
            for v_item in s_output:
                v_role = v_item['Role'] if v_item.has_key('Role') else 'None'
                v_memeber = v_item['Member'] if v_item.has_key('Member') else 'None'
                if v_memeber == member_name:
                    v_get_member = True
                    v_local_role = v_role
                    if not check_postgresql_status(bindir, pg_data, v_role):
                        v_error_count += 1
                    else:
                        v_error_count = 0

                if v_role == 'Leader':
                    v_get_leader = True
                    v_master_memeber = v_memeber
                else:
                    v_slave_member = v_memeber

            if v_error_count >= max_error_loop:
                process_fail(v_master_memeber, v_slave_member, v_local_role, bindir, pg_data, dcs, cluster_name)
                pass  # todo
            if not v_get_member:
                print "cannot fine {0}".format(member_name)
                pass  # todo
            if not v_get_leader:
                print "cannot get leader"
                pass  # todo
        except Exception, e:
            print e.message()

        time.sleep(loop_wait)


G_PATRONI_CTL = '/opt/patroni-1.6.5/patronictl.py'
if __name__ == '__main__':
    monitor()
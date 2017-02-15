# -*- coding: utf8 -*-
import os
import ssl
import time
import json
import requests
import ConfigParser
from api import models
from celery import shared_task
from pysphere import VIServer, VIProperty, VITask
from pysphere.resources import VimService_services as VI 

# config info
cf = ConfigParser.ConfigParser()
config = {}
cf.read('/opt/app/autosetup/api/config.ini')
config['vcenter_server1_host'] = cf.get('vcenter_server1', 'host')
config['vcenter_server1_user'] = cf.get('vcenter_server1', 'user')
config['vcenter_server1_passwd'] = cf.get('vcenter_server1', 'passwd')
config['vcenter_server2_host'] = cf.get('vcenter_server2', 'host')
config['vcenter_server2_user'] = cf.get('vcenter_server2', 'user')
config['vcenter_server2_passwd'] = cf.get('vcenter_server2', 'passwd')
config['vcenter_server3_host'] = cf.get('vcenter_server3', 'host')
config['vcenter_server3_user'] = cf.get('vcenter_server3', 'user')
config['vcenter_server3_passwd'] = cf.get('vcenter_server3', 'passwd')
config['linux_user'] = cf.get('linux', 'user')
config['linux_passwd'] = cf.get('linux', 'passwd')
config['linux_guiqiao_passwd'] = cf.get('linux', 'passwd-guiqiao')
config['windows_user'] = cf.get('windows', 'user')
config['windows_passwd'] = cf.get('windows', 'passwd')
config['cmdb_url'] = cf.get('cmdb', 'url')
config['cmdb_user'] = cf.get('cmdb', 'user')
config['cmdb_passwd'] = cf.get('cmdb', 'passwd')
config['autosetup_url'] = cf.get('autosetup', 'url')
config['autosetup_user'] = cf.get('autosetup', 'user')
config['autosetup_passwd'] = cf.get('autosetup', 'passwd')
config['control_url'] = cf.get('control', 'url')
config['control_user'] = cf.get('control', 'user')
config['control_passwd'] = cf.get('control', 'passwd')
config['control_token_path'] = cf.get('control', 'token_path')
config['control_accept_path'] = cf.get('control', 'accept_path')
config['control_delete_path'] = cf.get('control', 'delete_path')
config['control_init_path'] = cf.get('control', 'init_path')

def connect_vcenter_server(name):
    vcenter_server = VIServer()
    try:
        # close ssl authentication
        ssl._create_default_https_context = ssl._create_unverified_context
        if name == config.get('vcenter_server1_host'):
            vcenter_server.connect(host=config.get('vcenter_server1_host'), user=config.get('vcenter_server1_user'), password=config.get('vcenter_server1_passwd'))
        elif name == config.get('vcenter_server2_host'):
            vcenter_server.connect(host=config.get('vcenter_server2_host'), user=config.get('vcenter_server2_user'), password=config.get('vcenter_server2_passwd'))
        elif name == config.get('vcenter_server3_host'):
            vcenter_server.connect(host=config.get('vcenter_server3_host'), user=config.get('vcenter_server3_user'), password=config.get('vcenter_server3_passwd'))
        else:
            raise Exception('vcenter_server %s does not exist' %name)
        return vcenter_server
    except Exception as e:
        raise e

def get_host_by_name(vcenter_server, name):
    mor = None
    for host_mor, host_name in vcenter_server.get_hosts().items():
        if host_name == name: mor = host_mor; break 
    return mor

def get_resource_pool_by_property(vcenter_server, prop, value):
    mor = None
    for rp_mor, rp_path in vcenter_server.get_resource_pools().items():
        p = vcenter_server._get_object_properties(rp_mor, [prop])
        if p.PropSet[0].Val == value: mor = rp_mor; break 
    return mor

def get_datastore_by_name(vcenter_server, name):
    mor = None
    for ds_mor, ds_name in vcenter_server.get_datastores().items():
        if ds_name == name: mor = ds_mor; break 
    return mor

def login_guest(sleep_time, vm, user, password):
    for i in range(10):
        try:
            time.sleep(sleep_time)
            vm.login_in_guest(user, password)
            return 0
        except:
            continue

def check_ip(sleep_time, ip):
    for i in range(10):
        ret = os.system('ping -c 5 {}'.format(ip))
        if ret == 0:
            return 0
        time.sleep(sleep_time)
            
def get_ip(sleep_time, vm):
    for i in range(10):
        ip = vm.get_property('ip_address', from_cache=False)
        if ip != None:
            return ip
        time.sleep(sleep_time)

def myclone(vcenter_server, item, copy=None, power_on=True):
    print item
    if item.cloned_vm_name:
        # copy from vm
        vm = vcenter_server.get_vm_by_name("{}".format(item.cloned_vm_name)) 
    else:
        # copy from template copy
        print 1
        vm = vcenter_server.get_vm_by_name("{}".format(copy)) 
    print 2
    host_mor = get_host_by_name(vcenter_server, item.host_ips)   
    print 3
    prop = vcenter_server._get_object_properties(host_mor, ['parent'])  
    print 4
    parent = prop.PropSet[0].Val
    print 5
    rp_mor = get_resource_pool_by_property(vcenter_server,'parent', parent)   
    print 6
    props = VIProperty(vcenter_server, host_mor)
    print 7
    ds_name = props.datastore[0].info.name
    print 8
    ds_mor = get_datastore_by_name(vcenter_server, ds_name)   
    print 9
    vm.clone(item.name, resourcepool=rp_mor, datastore=ds_mor, host=host_mor, power_on=power_on) 
    print 10

def update_cmdb(name, status=None, description=None, data=None):
    cmdb_url = config.get('cmdb_url')
    r = requests.post(url='{0}/api/cmdb/token/'.format(cmdb_url), data={'username': config.get('cmdb_user'), 'password': config.get('cmdb_passwd')})
    headers = {'Authorization': 'token {0}'.format(json.loads(r.text)['token'])}
    r = requests.get('{0}/api/cmdb/devices/virtualmachine'.format(cmdb_url), params={'name': name}, headers=headers)
    url = json.loads(r.text)['results'][0]['url']
    if status:
        r = requests.patch(url=url, data={'status': status}, headers=headers)
    elif description or description == '':
        r = requests.patch(url=url, data={'description': description}, headers=headers)
    elif data:
        virtual_cpu = data['virtual_cpu']
        virtual_memory = data['virtual_memory']
        virtual_storage = data['virtual_storage']
        r = requests.patch(url=url, data={'virtual_cpu': virtual_cpu, 'virtual_memory': virtual_memory, 'virtual_storage': virtual_storage}, headers=headers)

def call_api(url, data):
    r = requests.post('{0}/api/token/'.format(config['autosetup_url']), data={'username': config['autosetup_user'], 'password': config['autosetup_passwd']})
    headers = {'Authorization': 'token {0}'.format(json.loads(r.text)['token'])}
    requests.post(url=url, data=data, headers=headers)

def get_vm_info(vcenter_server, name): 
    vm = vcenter_server.get_vm_by_name(name)
    virtual_cpu = vm.get_property(name='num_cpu')
    if vm.get_property(name='memory_mb'):
        virtual_memory = vm.get_property(name='memory_mb') / 1024
    else:
        virtual_memory = 0
    if vm.get_property(name='disks'):
        virtual_storage = vm.get_property(name='disks')[0]['capacity'] / 1024 / 1024
    else:
        datastore = 0
    return {'virtual_cpu': virtual_cpu, 'virtual_memory': virtual_memory, 'virtual_storage': virtual_storage}

def check_vm(vcenter_server, vcenter_server_name, name, ipaddresses):
    ''' confirm that if the online application is not using the vm and latest installed fail, then delete the vm first'''
    r = requests.post('{0}/api/cmdb/token/'.format(config.get('cmdb_url')), data={'username': config.get('cmdb_user'),'password': config.get('cmdb_passwd')})
    headers = {'Authorization': 'token {0}'.format(json.loads(r.text)['token'])}
    r = requests.get('{0}/api/cmdb/applications/applicationgroup'.format(config.get('cmdb_url')), params={'ipaddresses':ipaddresses}, headers=headers) 
    # count is the number of online applications use
    count = json.loads(r.text)['count']
    if models.VmClone.objects.filter(name=name) and models.VmClone.objects.filter(name=name)[0].exit_code != 0 and count == 0:
        try:
            vm = vcenter_server.get_vm_by_name(name)
        except:
            return
        url = '{0}/api/vmdelete'.format(config.get('autosetup_url'))
        data = {'vcenter_server': vcenter_server_name, 'name': name}
        call_api(url=url, data=data)
        while True:
            time.sleep(5)
            if models.VmDelete.objects.filter(name=name) and models.VmDelete.objects.filter(name=name)[0].exit_code == 0:
                break

@shared_task
def vm_clone(item):
    try:
        copy = None
        vcenter_server = connect_vcenter_server(item.vcenter_server)
        
        #existingItems = models.VmClone.objects.filter(name = item.name).exclude(pk = item.pk)
        #if existingItems:
        #    for existingItem in existingItems:
        #        if existingItem.exit_code is None:
        #            vmCloneItem = models.VmClone.objects.filter(pk = item.pk)
        #            raise Exception('该对象已加入克隆队列，无法新建克隆任务。')
        
        vmCloneItem = models.VmClone.objects.filter(pk = item.pk)
        vmCloneItem.update(comment = '正在克隆')
        # step 1 检查
        update_cmdb(name = item.name, description = '1')
        ret = os.system('ping -c 5 {}'.format(item.ipaddresses))
        if ret == 0:
            vmCloneItem.update(comment = 'IP已被使用', exit_code = 1)
            update_cmdb(name = item.name, status = '2')
            update_cmdb(name = item.name, description = 'IP已被使用')
            raise Exception('IP已被使用')
        # copy from vm
        if item.cloned_vm_name:
            # step 2 正在克隆
            update_cmdb(name = item.name, description = '2')
            myclone(vcenter_server, item)
        # copy from template copy, a template copy clone a vm once, the status of template copy is None default
        else:
            vm_template = models.Template.objects.get(name = item.vm_template)
            copies = vm_template.copy_set.all()
            for i in copies:
                if not i.status:
                    copy = i
                    break
            if copy:
                copy.status = True
                copy.save()
                # step 2 正在克隆
                update_cmdb(name = item.name, description = '2')
                if item.remark == 'onlyclone':
                    myclone(vcenter_server, item, copy.name, power_on=False)
                    vmCloneItem.update(comment = '虚拟机模板克隆完成', exit_code = 2)
                    copy.status = False
                    copy.save()
                    return 
                else:
                    myclone(vcenter_server, item, copy.name)
                    copy.status = False
                    copy.save()
            else:
                while True:
                    time.sleep(20)
                    vm_template = models.Template.objects.get(name = item.vm_template)
                    copies = vm_template.copy_set.all()
                    copy = None
                    for i in copies:
                        if not i.status:
                            copy = i
                            break
                    if copy:
                        copy.status = True
                        copy.save()
                        # step 2 正在克隆
                        update_cmdb(name = item.name, description = '2')
                        if item.remark == 'onlyclone':
                            myclone(vcenter_server, item, copy.name, power_on=False)
                            vmCloneItem.update(comment = '虚拟机模板克隆完成', exit_code = 2)
                            copy.status = False
                            copy.save()
                            return 
                        else:
                            myclone(vcenter_server, item, copy.name)
                            copy.status = False
                            copy.save()
                            break
        # step 3 网络设置
        update_cmdb(name = item.name, description = '3')
        vlan_set(vcenter_server, item)
        ip_set(vcenter_server, item)
        result = check_ip(10, item.ipaddresses)
        if result != 0:
            vmCloneItem.update(comment = 'ip设置失败', exit_code = 1)
            update_cmdb(name = item.name, status = '2')
            update_cmdb(name = item.name, description = 'ip设置失败')
        else:
            # step 4 软件安装
            update_cmdb(name = item.name, description = '4')
            software_install(vcenter_server, item)
            vmCloneItem.update(comment = '克隆完成', exit_code = 0)
            data = []
            for i in range(3):
                try:
                    time.sleep(5)
                    data = get_vm_info(vcenter_server, item.name)
                except:
                    continue
            if not data:
                raise Exception('get vm info failed')
            update_cmdb(name = item.name, status = '3')
            update_cmdb(name = item.name, data = data)
            update_cmdb(name = item.name, description = '')
    except Exception as e:
        vmCloneItem.update(comment = e.message, exit_code = 1)
        update_cmdb(name = item.name, status='2')
        update_cmdb(name = item.name, description = e.message)
        data = []
        for i in range(3):
            try:
                time.sleep(5)
                data = get_vm_info(vcenter_server, item.name)
            except:
                continue
        if data:
            update_cmdb(name = item.name, data = data)
        if not item.cloned_vm_name and copy:
            copy.status = False
            copy.save()
        raise e
    finally:
        vcenter_server.disconnect()

@shared_task
def vm_relocate(item):
    try:
        vcenter_server = connect_vcenter_server(item.vcenter_server)
        
        existingItems = models.VmRelocate.objects.filter(name = item.name).exclude(pk = item.pk)
        if existingItems:
            for existingItem in existingItems:
                if existingItem.exit_code is None:
                    vmRelocateItem = models.VmRelocate.objects.filter(pk = item.pk)
                    raise Exception('该对象已加入迁移队列，无法新建迁移任务。')

        vmRelocateItem = models.VmRelocate.objects.filter(pk = item.pk)
        vmRelocateItem.update(comment = '正在迁移，请稍后刷新')

        vm = vcenter_server.get_vm_by_name(item.name)
        if vm.is_powered_on():
            vm.power_off()
        host_mor = get_host_by_name(vcenter_server,item.host_ips)   
        prop = vcenter_server._get_object_properties(host_mor, ['parent'])  
        parent = prop.PropSet[0].Val
        rp_mor = get_resource_pool_by_property(vcenter_server,'parent', parent)   
        props = VIProperty(vcenter_server, host_mor)
        ds_name = props.datastore[0].info.name
        ds_mor = get_datastore_by_name(vcenter_server, ds_name)   
        vm.relocate(datastore=ds_mor, resource_pool=rp_mor, host=host_mor)
        vm = vcenter_server.get_vm_by_name(item.name)
        vm.power_on()
        vlan_set(vcenter_server, item)
        ipaddresses = get_ip(10, vm)
        if ipaddresses:
            result = check_ip(10, ipaddresses)
            if result != 0:
                vmRelocateItem.update(comment = 'ip设置失败', exit_code = 1)
            else:
                vmRelocateItem.update(comment = '迁移完成', exit_code = 0)
        else:
            vmRelocateItem.update(comment = 'ip设置失败', exit_code = 1)
    except Exception as e:
        vmRelocateItem.update(comment = e.message, exit_code = 1)
        raise e
    finally:
        vcenter_server.disconnect()

@shared_task
def vm_delete(item):
    try:
        vcenter_server = connect_vcenter_server(item.vcenter_server)
        
        existingItems = models.VmDelete.objects.filter(name = item.name).exclude(pk = item.pk)
        if existingItems:
            for existingItem in existingItems:
                if existingItem.exit_code is None:
                    vmDeleteItem = models.VmDelete.objects.filter(pk=item.pk)
                    raise Exception('该对象已加入删除队列，无法新建删除任务。')

        vmDeleteItem = models.VmDelete.objects.filter(pk=item.pk)
        vmDeleteItem.update(comment = '正在删除，请稍后刷新')
        
        vm = vcenter_server.get_vm_by_name(item.name)
        if vm.is_powered_on():
            vm.power_off()
        request = VI.Destroy_TaskRequestMsg() 
        _this = request.new__this(vm._mor) 
        _this.set_attribute_type(vm._mor.get_attribute_type()) 
        request.set_element__this(_this) 
        ret = vcenter_server._proxy.Destroy_Task(request)._returnval 
        vmDeleteItem.update(comment = '删除完成', exit_code = 0)
    except Exception as e:
        vmDeleteItem.update(comment = e.message, exit_code = 1)
        raise e
    finally:
        vcenter_server.disconnect()

@shared_task
def batch_clone(item):
    try:
        cloned_vm_name = None
        cloneitem_pk_list = None
        vcenter_server = connect_vcenter_server(item.vcenter_server)
        
        batchCloneItem = models.BatchClone.objects.filter(pk=item.pk)
        batchCloneItem.update(comment = '正在克隆')
        
        vm_info = json.loads(item.vm_info)
        # the vm number of batch clone
        num = len(vm_info)
        if num == 1:
            vm_name = vm_info[0][0]
            ipaddresses = vm_info[0][1]
            check_vm(vcenter_server, item.vcenter_server, vm_name, ipaddresses)
            url = '{0}/api/vmclone'.format(config.get('autosetup_url'))
            data = {'vcenter_server': item.vcenter_server, 'host_ips': item.host_ips, 'name': vm_name, 'os': item.os, 'ipaddresses': ipaddresses, 'vlan_tags': item.vlan_tags, 'vm_template': item.vm_template}
            call_api(url=url, data=data)
            cloneitem_pk = models.VmClone.objects.filter(name = vm_name).get(exit_code = None).pk
            while True:
                time.sleep(20)
                cloneitem = models.VmClone.objects.get(pk = cloneitem_pk)
                if cloneitem.exit_code == 0:
                    batchCloneItem.update(comment = '批量克隆完成', exit_code = 0)
                    break
                elif cloneitem.exit_code == 1:
                    batchCloneItem.update(comment = '批量克隆失败', exit_code = 1)
                    break
        elif num > 1:
            cloned_vm_name = vm_info[0][0]
            cloned_ipaddresses = vm_info[0][1]
            check_vm(vcenter_server, item.vcenter_server, cloned_vm_name, cloned_ipaddresses)
            url = '{0}/api/vmclone'.format(config.get('autosetup_url'))
            data = {'vcenter_server': item.vcenter_server, 'host_ips': item.host_ips, 'name': cloned_vm_name, 'os': item.os, 'ipaddresses': cloned_ipaddresses, 'vlan_tags': item.vlan_tags, 'vm_template': item.vm_template, 'remark': 'onlyclone'}
            call_api(url=url, data=data)
            cloneitem_pk = models.VmClone.objects.filter(name = cloned_vm_name).get(exit_code = None).pk
            while True:
                time.sleep(20)
                cloneitem = models.VmClone.objects.get(pk = cloneitem_pk)
                if cloneitem.exit_code == 2:
                    batchCloneItem.update(comment = '模板虚拟机克隆完成')
                    break
                elif cloneitem.exit_code == 1:
                    batchCloneItem.update(comment = '批量克隆失败', exit_code = 1)
                    for i in range(1, num):
                        name = vm_info[i][0]
                        update_cmdb(name = name, status = '2')
                    return
            
            cloneitem_pk_list = []
            for i in range(1, num):
                name = vm_info[i][0]
                ipaddresses = vm_info[i][1]
                check_vm(vcenter_server, item.vcenter_server, name, ipaddresses)
                data = {'vcenter_server': item.vcenter_server, 'host_ips': item.host_ips, 'name': name, 'os': item.os, 'ipaddresses': ipaddresses, 'vlan_tags': item.vlan_tags, 'cloned_vm_name': cloned_vm_name, 'vm_template': item.vm_template}
                call_api(url=url, data=data)
                cloneitem_pk_list.append(models.VmClone.objects.filter(name = name).get(exit_code = None).pk)

            for i in range(len(cloneitem_pk_list)):
                while True:
                    time.sleep(20)
                    cloneitem = models.VmClone.objects.get(pk = cloneitem_pk_list[i])
                    if cloneitem.exit_code == 0:
                        cloneitem_pk_list[i] = 0
                        break
                    elif cloneitem.exit_code == 1:
                        cloneitem_pk_list[i] = 1
                        break
            if 1 in cloneitem_pk_list:
                batchCloneItem.update(comment = '批量克隆失败', exit_code = 1)
            else:
                batchCloneItem.update(comment = '虚拟机克隆完成')

            vm = vcenter_server.get_vm_by_name(cloned_vm_name)
            if vm.is_powered_off():
                vm.power_on()
            vmCloneItem = models.VmClone.objects.filter(pk = cloneitem_pk)
            
            # step 3 网络设置
            update_cmdb(name = cloned_vm_name, description = '3')
            vlan_set(vcenter_server, vmCloneItem[0])
            ip_set(vcenter_server, vmCloneItem[0])
            result = check_ip(10, vmCloneItem[0].ipaddresses)
            if result != 0:
                vmCloneItem.update(comment = 'ip设置失败', exit_code = 1)
                batchCloneItem.update(comment = '批量克隆失败', exit_code = 1)
                update_cmdb(name = cloned_vm_name, status = '2')
                update_cmdb(name = cloned_vm_name, description = 'ip设置失败')
            else:
                # step 4 软件安装
                update_cmdb(name = cloned_vm_name, description = '4')
                software_install(vcenter_server, vmCloneItem[0])
                vmCloneItem.update(comment = '克隆完成', exit_code = 0)
                data = []
                for i in range(3):
                    try:
                        time.sleep(5)
                        data = get_vm_info(vcenter_server, cloned_vm_name)
                    except:
                        continue
                if not data:
                    raise Exception('get vm info failed')
                update_cmdb(name = cloned_vm_name, status = '3')
                update_cmdb(name = cloned_vm_name, data = data)
                update_cmdb(name = cloned_vm_name, description = '')
                batchCloneItem.update(comment = '批量克隆成功', exit_code = 0)
        else:
            raise Exception('vm_info is empty')
    except Exception as e:
        batchCloneItem.update(comment = e.message, exit_code = 1)
        if e.message in ['get vm info failed', 'software install failed', 'salt key accept failed', 'salt key init failed']:
            vmCloneItem.update(comment = e.message, exit_code = 1)
            update_cmdb(name=cloned_vm_name, status='2')
            update_cmdb(name=cloned_vm_name, description=e.message)
            data = []
            for i in range(3):
                try:
                    time.sleep(5)
                    data = get_vm_info(vcenter_server, item.name)
                except:
                    continue
            if data:
                update_cmdb(name = item.name, data = data)
        if not cloned_vm_name and not cloneitem_pk_list:
            for i in range(num):
                name = vm_info[i][0]
                update_cmdb(name=name, status='2')
                update_cmdb(name=name, description=e.message)
        raise e

def ip_set(vcenter_server, item):
    vm = vcenter_server.get_vm_by_name(item.name)
    vc = item.vcenter_server
    if '.'.join(item.ipaddresses.split('.')[:-1]) in ['10.10.101', '10.11.101', '10.12.99', '10.12.100', '10.12.101']:
        env = 'stg' 
    else:   
        env = 'pro' 
    if item.os in ['CentOS 6.5']:
        if vc in ['10.10.15.101', '10.11.251.101']:
            ret = login_guest(10, vm, config.get('linux_user'), config.get('linux_passwd'))
        else:
            ret = login_guest(10, vm, config.get('linux_user'), config['linux_guiqiao_passwd'])
        if ret == 0:
            if vc in ['10.10.15.101', '10.11.251.101']:
                if env == 'pro':
                    vm.send_file('/opt/app/autosetup/api/scripts/ip_set_huaxin_pro.sh', '/root/ip_set.sh', overwrite=True)
                else:
                    vm.send_file('/opt/app/autosetup/api/scripts/ip_set_huaxin_stg.sh', '/root/ip_set.sh', overwrite=True)
            else:
                if env == 'pro':
                    if '.'.join(item.ipaddresses.split('.')[:-1]) in ['10.12.0', '10.12.1', '10.12.2', '10.12.3', '10.12.4', '10.12.5']:
                        vm.send_file('/opt/app/autosetup/api/scripts/ip_set_guiqiao_tmp_pro.sh', '/root/ip_set.sh', overwrite=True)
                    else:
                        vm.send_file('/opt/app/autosetup/api/scripts/ip_set_guiqiao_pro.sh', '/root/ip_set.sh', overwrite=True)
                else:
                    vm.send_file('/opt/app/autosetup/api/scripts/ip_set_guiqiao_stg.sh', '/root/ip_set.sh', overwrite=True)
            vm.start_process('/bin/rm', ['-f', '/etc/udev/rules.d/70-persistent-net.rules'])
            vm.start_process('/bin/bash', ['/root/ip_set.sh', item.ipaddresses])
            vm.start_process('/bin/rm', ['-f', '/root/ip_set.sh'])
            vm.start_process('/sbin/reboot')
        else:
            raise Exception('login failed')
    elif item.os in ['Windows Server 2008 R2', 'Windows Server 2008']:
        ret = login_guest(60, vm, config.get('windows_user'), config.get('windows_passwd'))
        if ret == 0:
            if vc in ['10.10.15.101', '10.11.251.101']:
                if env == 'pro':
                    vm.send_file('/opt/app/autosetup/api/scripts/ip_set_huaxin_pro.bat', 'C:\Users\Administrator\ip_set.bat', overwrite=True)
                else:
                    vm.send_file('/opt/app/autosetup/api/scripts/ip_set_huaxin_stg.bat', 'C:\Users\Administrator\ip_set.bat', overwrite=True)
                #vm.send_file('/opt/app/autosetup/api/scripts/domain_set.bat', 'C:\Users\Administrator\domain_set.bat', overwrite=True)
                gateway = '.'.join(item.ipaddresses.split('.')[:-1]) + '.254'
                name = '-'.join(item.name.split('.'))
                vm.start_process('C:\Users\Administrator\ip_set.bat', [item.ipaddresses, gateway, name])
                ret = login_guest(20, vm, config.get('windows_user'), config.get('windows_passwd'))
                if ret == 0:
                    #vm.start_process('C:\Users\Administrator\domain_set.bat')
                    vm.delete_file('C:\Users\Administrator\ip_set.bat')
                    #vm.delete_file('C:\Users\Administrator\domain_set.bat')
                else:
                    raise Exception('login failed')
            else:
                if env == 'pro':
                    if '.'.join(item.ipaddresses.split('.')[:-1]) in ['10.12.0', '10.12.1', '10.12.2', '10.12.3', '10.12.4', '10.12.5']:
                        vm.send_file('/opt/app/autosetup/api/scripts/ip_set_guiqiao_tmp_pro.bat', 'C:\Users\Administrator\ip_set.bat', overwrite=True)
                    else:
                        vm.send_file('/opt/app/autosetup/api/scripts/ip_set_guiqiao_pro.bat', 'C:\Users\Administrator\ip_set.bat', overwrite=True)
                else:
                    vm.send_file('/opt/app/autosetup/api/scripts/ip_set_guiqiao_stg.bat', 'C:\Users\Administrator\ip_set.bat', overwrite=True)
                #vm.send_file('/opt/app/autosetup/api/scripts/domain_set.bat', 'C:\Users\Administrator\domain_set.bat', overwrite=True)
                gateway = '.'.join(item.ipaddresses.split('.')[:-1]) + '.254'
                gateway = '.'.join(item.ipaddresses.split('.')[:-1]) + '.254'
                name = '-'.join(item.name.split('.'))
                vm.start_process('C:\Users\Administrator\ip_set.bat', [item.ipaddresses, gateway, name])
                ret = login_guest(20, vm, config.get('windows_user'), config.get('windows_passwd'))
                if ret == 0:
                    #vm.start_process('C:\Users\Administrator\domain_set.bat')
                    vm.delete_file('C:\Users\Administrator\ip_set.bat')
                    #vm.delete_file('C:\Users\Administrator\domain_set.bat')
                else:
                    raise Exception('login failed')
        else:
            raise Exception('login failed')
    else:
        raise Exception('os %s does not exist'.format(item.os))
        
def vlan_set(vcenter_server, item):
    vm = vcenter_server.get_vm_by_name(item.name)
    net_device = []
    for dev in vm.properties.config.hardware.device:
        if dev._type in ["VirtualE1000", "VirtualE1000e", "VirtualPCNet32", "VirtualVmxnet", "VirtualNmxnet2", "VirtualVmxnet3"]:
            net_device.append(dev)
    if len(net_device) == 0:
        raise Exception("The vm seems to lack a Virtual Nic")
    # Invoke ReconfigVM_Task
    request = VI.ReconfigVM_TaskRequestMsg()
    _this = request.new__this(vm._mor)
    _this.set_attribute_type(vm._mor.get_attribute_type())
    request.set_element__this(_this)
    # Build a list of device change spec objects
    devs_changed = []
    for dev in net_device:
        dev._obj.Backing.set_element_deviceName(item.vlan_tags)
        spec = request.new_spec()
        dev_change = spec.new_deviceChange()
        dev_change.set_element_device(dev._obj)
        dev_change.set_element_operation("edit")
        devs_changed.append(dev_change)
    # Submit the device change list
    spec.set_element_deviceChange(devs_changed)
    request.set_element_spec(spec)
    ret = vcenter_server._proxy.ReconfigVM_Task(request)._returnval
    # Wait for the task to finish
    task = VITask(ret, vcenter_server)
    status = task.wait_for_state([task.STATE_SUCCESS, task.STATE_ERROR])
    if status == task.STATE_ERROR:
        raise Exception("{0} vlan configurate error {1}".format(item.name, task.get_error_message()))

def software_install(vcenter_server, item):
    vm = vcenter_server.get_vm_by_name(item.name)
    vc = item.vcenter_server
    if '.'.join(item.ipaddresses.split('.')[:-1]) in ['10.10.101', '10.11.101', '10.12.99', '10.12.100', '10.12.101']:
        env = 'stg' 
    else:   
        env = 'pro' 
    if item.os in ['CentOS 6.5']:
        minion = ''.join(item.ipaddresses.split('.'))
        if vc in ['10.10.15.101', '10.11.251.101']:
            ret = login_guest(10, vm, config.get('linux_user'), config.get('linux_passwd'))
        else:
            ret = login_guest(10, vm, config.get('linux_user'), config['linux_guiqiao_passwd'])
        if ret == 0:
            try:    
                vm.start_process('/usr/bin/curl', ['http://10.11.251.8/shell/linux-init', '|', 'sh'])
            except: 
                raise Exception('software install failed')
        else:   
            raise Exception('login failed')
        try:
            vm.send_file('/opt/app/autosetup/api/scripts/sshd_config', '/etc/ssh/sshd_config', overwrite=True)
            vm.start_process('/sbin/service', ['sshd', 'restart'])
        except: 
            raise Exception('restart sshd error')
        try:
            vm.send_file('/opt/app/autosetup/api/scripts/salt-guard-cli', '/tmp/salt-guard-cli', overwrite=True)
            vm.start_process('/bin/chmod', ['755', '/tmp/salt-guard-cli'])
            vm.start_process('/tmp/salt-guard-cli', ['-logging', '/tmp/salt_init.log'])
        except:
            raise Exception('init salt error')
    elif item.os in ['Windows Server 2008 R2', 'Windows Server 2008']: 
        minion = 'WEB-' + ''.join(item.ipaddresses.split('.'))
        ret = login_guest(30, vm, config.get('windows_user'), config.get('windows_passwd'))
        if ret == 0:
            try:    
                if vc in ['10.10.15.101', '10.11.251.101']:
                    vm.start_process('D:\package\zabbix_agents_auto_installer.win.exe')
                    time.sleep(1)
                    vm.start_process('D:\package\ymatou_iis_healthcheck_module_stg_prod.exe')
                    time.sleep(1)
                    if env == 'pro':
                        vm.start_process('D:\package\salt_minion_webdeploy_prod.exe')
                    else:   
                        vm.start_process('D:\package\salt_minion_webdeploy_stg.exe')
                else:
                    vm.start_process('D:\package\zabbix_agent_install.exe')
                    time.sleep(1)
                    vm.start_process('D:\package\ymatou_iis_healthcheck_module_stg_prod.exe')
                    time.sleep(1)
                    if env == 'pro':
                        vm.start_process('D:\package\salt_minion_webdeploy_prod.exe')
                    else:   
                        vm.start_process('D:\package\salt_minion_webdeploy_stg.exe')
            except: 
                raise Exception('software install failed')
            try:
                vm.send_file('/opt/app/autosetup/api/scripts/salt-guard-cli.exe', 'D:\package\salt-guard-cli.exe')
                vm.start_process('D:\package\salt-guard-cli.exe', ['-logging', 'D:\salt_init.log'])
            except:
                raise Exception('init salt error')
        else:
            raise Exception('login failed')
    else:
        raise Exception('os {0} does not exist'.format(item.os))

@shared_task
def clone(item):
    try:
        info = {}
        datas = json.loads(item.data)
        for item in datas:
            if item.get('host_ips') and item.get('vm_template'):
                # The same host use the same template into a info processing
                if info.get((item['host_ips'], item['vm_template'])):
                    info[(item['host_ips'], item['vm_template'])].append(item)
                else:
                    info[(item['host_ips'], item['vm_template'])] = [item]
            else:
                raise Exception('host_ips or vm_template is empty')
        for k,v in info.items():
            host_ips = k[0] 
            vm_template = k[1]
            vcenter_server = v[0]['vcenter_server']
            vlan_tags = v[0]['vlan_tags']
            vm_os = v[0]['os']
            vm_info = [(i['name'],i['ipaddresses']) for i in v]
            vm_info = json.dumps(vm_info)
            url = '{0}/api/batchclone'.format(config.get('autosetup_url'))
            data = {'vcenter_server': vcenter_server, 'host_ips': host_ips, 'os': vm_os, 'vm_info': vm_info, 'vlan_tags': vlan_tags, 'vm_template': vm_template}
            call_api(url=url, data=data)
            time.sleep(1)
    except Exception as e:
        raise e

@shared_task
def relocate(item):
    try:
        datas = json.loads(item.data)
        for i in datas:
            vcenter_server = i['vcenter_server']
            name = i['name']
            host_ips = i['host_ips']
            vlan_tags = i['vlan_tags']
            url = '{0}/api/vmrelocate'.format(config.get('autosetup_url'))
            data={'vcenter_server': vcenter_server, 'name': name, 'host_ips': host_ips, 'vlan_tags': vlan_tags}
            call_api(url=url, data=data)
    except Exception as e:
        raise e

@shared_task
def delete(item):
    try:
        datas = json.loads(item.data)
        for i in datas:
            vcenter_server = i['vcenter_server']
            name = i['name']
            url = '{0}/api/vmdelete'.format(config.get('autosetup_url'))
            data = {'vcenter_server': vcenter_server, 'name': name}
            call_api(url=url, data=data)
    except Exception as e:
        raise e

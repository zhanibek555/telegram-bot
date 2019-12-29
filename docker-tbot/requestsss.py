# -*- coding: utf-8 -*-
# !/usr/bin/env python
import requests as r
from lxml import html
import datetime
import concurrent.futures
import paramiko
import json

r.packages.urllib3.disable_warnings()
errors = ''

def check_bs(target):
    global errors
    errors = ''
    if 'ast:' in target:
        BS = {'1': '1', '2': '10', '3': '16', '4': '17', '5': '19',
              '6': '21', '7': '22', '8': '26', '9': '27', '10': '28',
              '11': '29', '12': '30', '13': '32', '14': '33'}
        for i in BS:
            if i == target.replace(' ', '').split(':')[1]:
                return [BS[i], 'ast:']
    elif 'ukk:' in target:
        BS = {'1': '3', '2': '4', '3': '5'}
        for i in BS:
            if i == target.replace(' ', '').split(':')[1]:
                return [BS[i], 'ukk:']
    elif 'alm:' in target:
        BS = {'1': '2', '2': '3', '3': '4'}
        for i in BS:
            if i == target.replace(' ', '').split(':')[1]:
                return [BS[i], 'alm:']
    elif 'shym:' in target:
        BS = {'1': '2', '2': '3'}
        for i in BS:
            if i == target.replace(' ', '').split(':')[1]:
                return [BS[i], 'shym:']
    return False


def find_node_in_apk(Apk_location):
    url = 'http://registry.sergek.kz:8081/update'
    parsed_body = html.fromstring(r.get(url).text)
    found = ''
    text = parsed_body.xpath('//pre/text()')
    for i in text:
        pass
    Apk = json.loads(i)
    for Apk_node in Apk:
        for main in Apk[Apk_node]:
            if Apk_location in str(Apk[Apk_node][main]):
                found += Apk_node + ', '
    if found:
        return found[0:-2]
    else:
        return "Не найдено"


def restart_node(Ip, mess):
    try:
        host = Ip
        user = 'cvt'
        secret = 'cvt588'
        port = 22
        tim = 60
        banner = 60
        auth = 60

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, username=user, password=secret, port=port, timeout=tim, auth_timeout=auth,
                       banner_timeout=banner)
        if mess:
            if "ast:" in mess:
                stdin, stdout, stderr = client.exec_command(
                    'curl --fail "http://registry.sergek.kz:8081/balancer/ast/genyml4?version=1.2.3&target={}" > gpu.yml'.format(Ip), timeout=20)
                data = stdout.read() + stderr.read()

                stdin, stdout, stderr = client.exec_command(
                    'curl --fail "http://registry.sergek.kz:8081/balancer/ast/genconfig4?target={}" > config.json'.format(Ip), timeout=20)
                data = stdout.read() + stderr.read()
            elif "ukk:" in mess:
                stdin, stdout, stderr = client.exec_command(
                    'curl --fail "http://registry.sergek.kz:8084/genyml3?queuezmq=2.0.0&videoprocessor=4.5.28&recognizer=4.2.0&servermanager=3.2.26&target={}" > gpu.yml'.format(
                        Ip, datetime.date.today()), timeout=20)
                data = stdout.read() + stderr.read()
            elif "alm:" in mess:
                stdin, stdout, stderr = client.exec_command(
                    'curl --fail "http://registry.sergek.kz:8082/genyml3?queuezmq=2.0.0&videoprocessor=4.5.33&recognizer=4.2.0&servermanager=3.2.26&target={}" > gpu.yml'.format(
                        Ip, datetime.date.today()), timeout=20)
                data = stdout.read() + stderr.read()
            elif "shym:" in mess:
                stdin, stdout, stderr = client.exec_command(
                    'curl --fail "http://registry.sergek.kz:8083/genyml3?queuezmq=2.0.0&videoprocessor=4.5.28&recognizer=4.2.0&servermanager=3.2.26&target={}" > gpu.yml'.format(
                        Ip, datetime.date.today()), timeout=20)
                data = stdout.read() + stderr.read()

        stdin, stdout, stderr = client.exec_command('sudo docker rm -f $(sudo docker ps -aq)', timeout=20)
        data = stdout.read() + stderr.read()
        stdin, stdout, stderr = client.exec_command('sudo docker-compose -f gpu.yml up -d', timeout=90)
        data = stdout.read() + stderr.read()

    except Exception as e:
        if e.args:
            client.close()
            global errors
            print(f'\n{e.args} - {Ip}.\n')
            errors += f'Нет доступа до: {Ip}.\n'
    finally:
        client.close()


def vot_bi_zarabotalo(mess):    # If an error occurs, add c = None
    global errors
    errors = ''
    if "ukk:" in mess:
        url = "http://registry.sergek.kz:8084/reload"
        r1 = r.get("https://ukk.sergek.kz/station/", verify=False, timeout=5)
    elif "ast:" in mess:
        url = "http://registry.sergek.kz:8081/reload"
        r1 = r.get("https://ast.sergek.kz/station/", verify=False, timeout=5)
    elif "alm:" in mess:
        url = "http://registry.sergek.kz:8082/reload"
        r1 = r.get("https://alm.sergek.kz/station/", verify=False, timeout=5)
    elif "shym:" in mess:
        url = "http://registry.sergek.kz:8083/reload"
        r1 = r.get("https://shym.sergek.kz/station/", verify=False, timeout=5)
    else:
        url = ''
        r1 = ''

    bs = check_bs(mess)

    payload_tuples = [(bs[0], 'True')]
    result = r.post(url, data=payload_tuples)
    if r1.status_code == 200:
        conf = json.loads(r1.text)['rows']
        nodes = []
        for base_id in conf:
            if base_id == bs[0]:
                nodes.extend([n['ip_address'] for n in conf[base_id].get('nodes', []) if
                              n.get('is_active', True) is True])
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            for index in nodes:
                executor.submit(restart_node, index, bs[1])
        if errors:
            return errors
        else:
            return "Выполнено"
    else:
        return "error_connect"

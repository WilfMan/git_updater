#! -*- coding: utf-8 -*-
import tempfile
import os
import time
import subprocess
import sys

from logs import logger

pidFile = tempfile.gettempdir() + '/daemonGitPushNotify.pid'
info = tempfile.gettempdir() + '/.wathcher_info'
run = 'RUN'
stop = 'STOP'
speech_server = 'festival'
run_speech_server = 'festival --server'
command = '/usr/bin/python2 %s/my_notify.py' % os.path.split(os.path.abspath(__file__))[0]


def check_status(path):
    # logger.info('check status')
    if os.path.exists(path):
        with open(path, 'r') as ff:
            return ff.read()


def wr(path, data):
    with open(path, 'w') as ww:
        ww.write(data)


def get_pid(path):
    if os.path.exists(path):
        with open(path) as p:
            return int(p.read().strip())
    sys.exit(0)


def pid_exists(pid):
    process = subprocess.Popen(stdout=-1, args='ps x|grep %s|grep -v grep' % pid, shell=True)
    output, _ = process.communicate()
    process.poll()
    if output:
        return output.split()[0]


def proc_exist(name):
    try:
        process = subprocess.Popen(stdout=-1, args='ps x|grep %s|grep -v grep|grep -v Z' % name, shell=True)
        output, _ = process.communicate()
        process.poll()
        if output:
            return output.split()[0]
    except:
        return


def main():
    # subprocess.Popen(['export', 'DISPLAY=:0'])
    logger.info('check status')
    status = check_status(info)
    logger.info('status= %s' % status)

    logger.info('check %s server' % speech_server)
    f_stat = proc_exist(speech_server)
    if not f_stat:
        subprocess.Popen(run_speech_server.split(' '))

    if status == run:
        pid = get_pid(pidFile)
        logger.info('found watcher :%s' % pid)
        subprocess.Popen('kill %s' % pid, shell=True)
        wr(info, stop)
        sys.exit(0)
    else:
        wr(info, run)
    logger.info('run notifar')
    while check_status(info) != stop:
        if os.path.exists(pidFile):
            pid = get_pid(pidFile)

            if pid_exists(pid):
                time.sleep(1)
                # print 1
                continue

        logger.info('no tartget procces  try restart')
        logger.info(command)
        process = subprocess.Popen(command, shell=True)
        output, _ = process.communicate()
        logger.info('%s %s' % (output, _))
        print 'Fire!!!'
        time.sleep(1)


if __name__ == '__main__':
    main()

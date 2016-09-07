#! /usr/bin/python
# ! -*- coding: utf-8 -*-
import argparse
import datetime
import os
import subprocess
import sys
import time

import daemon


class Work_off(object):
    def __init__(self, parsed_args):
        self.parsed_args = parsed_args

    def work_off(self):
        if not os.path.exists('%s/.config/work_off/%s' % (os.path.expanduser('~'), self.parsed_args.file)):
            print 'no file %s/.config/work_off/%s' % (os.path.expanduser('~'), self.parsed_args.file)
            sys.exit(0)
        uptime = subprocess.check_output('uptime -s', shell=True)
        time_d = datetime.datetime.now() - datetime.datetime.strptime(uptime.strip(), '%Y-%m-%d %H:%M:%S')
        if time_d > datetime.timedelta(hours=8):
            subprocess.call('vlc file  --no-repeat -d %s vlc://quit' % self.parsed_args.file)
            sys.exit(0)

    def round_call(self):
        print 'run'
        while 1:
            self.work_off()
            time.sleep(self.parsed_args.period)


class Daemonn(daemon.Daemon):
    def run(self):
        Work_off(self.parsed_args).round_call()

    def parse(self):
        self.parsed_args = parse_argsself()
        getattr(self, self.parsed_args.command[0])()


def parse_argsself():
    parser = argparse.ArgumentParser(description=u'Play song on work off')
    parser.add_argument("-p", "--period", help=u"Период проверки времени (сек)", metavar='SECONDS',
                        dest='period',
                        default=60 * 10, type=int)
    parser.add_argument('command', nargs=1, choices=['start', 'stop', 'restart'],
                        help="run command ")
    parser.add_argument('-f', '--file', help='file to play', dest='file', type=str, default='bad_to_be_bone.mp3')
    parsed_args = parser.parse_args()
    return parsed_args


if __name__ == '__main__':
    daemon_ = Daemonn('/tmp/wop.pid')
    daemon_.parse()
    # Work_off(parse_argsself()).round_call()

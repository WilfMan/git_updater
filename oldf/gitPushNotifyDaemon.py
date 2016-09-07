#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

__author__ = 'Anton Fischer <a.fschr@gmail.com>'
__date__ = '$30.08.2011 23:33:33$'

import sys
import os
import time
import tempfile

import daemon
import gitPushNotify


class GitPushNotifyDaemon(daemon.Daemon):
    def run(self):
        c = gitPushNotify.GitPushNotify()
        c.run()


if __name__ == '__main__':
    pidFile = tempfile.gettempdir() + '/daemonGitPushNotify.pid'
    ff = tempfile.gettempdir() + '/gitPushNotify.log'
    daemon = GitPushNotifyDaemon(pidFile)
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            print 'Daemon starting..'
            daemon.start()
            print 'Daemon started!'
        elif 'stop' == sys.argv[1]:
            print 'Daemon stopping..'
            daemon.stop()
            print 'Daemon stopped!'
        elif 'restart' == sys.argv[1]:
            print 'Daemon restarting..'
            daemon.restart()
            print 'Daemon restarted!'
        else:
            print 'Unknown command'
            sys.exit(2)
        sys.exit(0)
    else:
        print 'usage: %s start|stop|restart' % sys.argv[0]
        sys.exit(2)
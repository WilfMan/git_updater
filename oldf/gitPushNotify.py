#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import threading
import subprocess
import os
import ConfigParser
import sys
from datetime import datetime
import traceback

import notify2

from pull_all import pull_all_branches
import gitParser
from sys_tray import Icon

# import gtk as gtk_
# import gobject
import Gtk as gtk_, GObject as gobject
gobject.threads_init()

dir_ = os.path.dirname(__file__)

from logs import logger as log_

rr = re.compile('\[(?:\w)+/([A-Za-z0-9\._]+): behind (\d+)\]')


def empty_cb(n):
    log_.info('closed notify msg')
    n.close()


class GitPushNotify(object):
    opt_repository = []
    opt_branch = []
    notif = []
    opt_timeout = 60  # sec

    def __init__(self):
        notify2.init('icon-summary-body', 'glib')
        self.log = log_

        self.log.info('\n\nDaemon start\n\n')

        config = ConfigParser.ConfigParser()
        configpath = os.path.join(*(list(os.path.split(os.path.dirname(__file__))) + ['config.cfg', ]))
        self.log.info('settings path: %s' % configpath)
        if os.path.exists(configpath):
            config.read(configpath)
        else:
            self.fire_notify('File "config.cfg" does not exist. Daemon stopped.')
            sys.exit(2)

        for section in config.sections():
            for option in config.options(section):
                '''@type option: str'''

                func = config.get
                if option.endswith('bool'):

                    func = config.getboolean
                elif option.endswith('int'):
                    func = config.getint

                if str(option).startswith('repository'):
                    data = getattr(self, 'opt_repository', [])
                    data.append(config.get(section, option))
                    setattr(self, 'opt_repository', data)

                else:
                    setattr(self, 'opt_%s' % option.split('_')[0], func(section, option))

        if not getattr(self, 'opt_repository'):
            message = 'Is not define repository path in "config.cfg". Daemon stopped.'
            self.fire_notify(message)
            self.log.error(message)
            sys.exit(2)
        self.fire_notify('start')

    def update_branches(self, path):
        try:
            pull_all_branches(path)
            self.log.info('call fire')
            self.fire_notify('pull ok: %s' % path, 'title')
            self.log.info('exit update')
        except Exception as e:
            self.fire_notify('error', 'title')
            self.log.error(e)

    def run_in_thread(self, target, *a, **k):
        try:
            join = False
            if 'join' in k:
                join = k.pop('join')
            self.log.info(str(k))
            tr = threading.Thread(target=target, args=a, kwargs=k)
            tr.start()
            self.log.info('join: %s' % join)
            if join:
                tr.join()
        except:
            self.log.info('err in thread: %s' % traceback.format_exc())
        else:
            self.log.info('thread done')

    def call_back_fire(self, *a):
        self.log.info('fire: %s' % str(a))
        self.run_in_thread(self.update_branches, a[2])
        self.log.info('end update exit callback')

    def call_back_menu(self, *a):
        self.log.info('menu: %s' % str(a))
        self.run_in_thread(self.update_branches, a[0])
        self.log.info('end update exit menu')

    def fire_notify(self, msg='', title='GitPushNotify', add_callback=None, path=None):
        # raise Exception(999)
        self.log.info('Called fireNotify()')
        try:
            n = notify2.Notification(title, msg, '')
            self.log.info('create n obj')
            if len(self.notif) > 40:
                self.notif = self.notif[-38:]
            self.notif.append(n)
            self.log.info('append data')
            n.set_urgency(notify2.URGENCY_LOW)
            self.log.info('set_urgency')
            if add_callback:

                self.log.info('add callback ')
                n.connect('closed', empty_cb)
                n.add_action(
                    "clicked",
                    " pull all branches ",
                    self.call_back_fire,
                    path)
            self.log.info('show')
            try:
                self.run_in_thread(n.show, join=True)
            except Exception as e:
                self.log.info('error while show: %s' % e)
            else:
                self.log.info('showed')
        except Exception as e:
            self.log.info('error in firenotify: %s' % e)
            traceback.print_exc()
        else:
            self.log.info('ok firenotify')

    @property
    def get_daemon_timeout(self):
        return self.opt_timeout

    def check_one(self, repository_path):
        subprocess.check_output(
            'cd ' + repository_path + ';'
            + ' git fetch',
            shell=True
        )
        try:
            s = subprocess.check_output(
                'cd ' + repository_path + ' && git branch -vv|grep behind', shell=True)
        except subprocess.CalledProcessError:
            self.log.info('no changes path: %s' % repository_path)
            return

        self.log.info('changes: %s', s)

        branches_list = s.split('\n')
        if self.opt_branch:
            branches_list = [i for i in s.split('\n') if self.opt_branch in i]

        self.log.info('branches_list: %s' % str(branches_list))

        count_commits = 0
        message = ''

        for br in branches_list:
            num = rr.search(br)
            if num is None:
                continue

            branch_ = str(num.group(1))
            count = str(num.group(2))
            watched = ('cd ' + repository_path + ' &&'
                       + ' git whatchanged ' + branch_
                       + ' -' + count
                       + ' --date=raw --date-order --pretty=format:"%H %n%cn %n%ce %n%ct %n%s"')
            src = '\n' + subprocess.check_output(
                watched,
                shell=True
            )
            parser = gitParser.GitParser(src)
            list_changes = parser.getChangesList()
            count_commits += len(list_changes)

            if list_changes:
                message += '*****\n %s\n' % branch_

            for item in list_changes[:7]:
                commit_time = datetime.fromtimestamp(int(item['time']))
                message += ('...\n'
                            + commit_time.strftime('%x %X') + '\n'
                            + item['author'] + ' &lt;' + item['email'] + '&gt;\n'
                            + item['message'] + '\n')

        if count_commits:
            message += '...\n%s new commit(s)\n\n' % count_commits
            self.fire_notify(message, add_callback=True, path=repository_path)

        self.log.info('Count commits: %s', count_commits)
        self.log.info('End check()')

    def check(self):
        self.log.info('Called check()')
        for repository_path in self.opt_repository:
            self.log.info('check repository: %s' % repository_path)
            self.run_in_thread(self.check_one, repository_path)

        gobject.timeout_add(self.get_daemon_timeout * 1000, self.check)

    def sys_icon(self):
        br = []
        for repo in self.opt_repository:
            br.append(['Check: %s' % repo.split('/')[-1], self.call_back_menu, repo])
        Icon(self.get_full_path('images4.png'), br).crearte_sys_tray_icon()

    @staticmethod
    def get_full_path(*args):
        return os.path.join(dir_, *args)

    def run(self):
        self.log.info('create menu')
        self.sys_icon()
        self.log.info('item to loop')
        gobject.timeout_add(10, self.check)
        self.log.info('start loop')
        gtk_.main()
        self.log.info('end run method')


if __name__ == '__main__':
    g = GitPushNotify()
    g.run()

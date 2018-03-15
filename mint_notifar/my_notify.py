#! -*- coding: utf-8 -*-
import ConfigParser
import json
import tempfile
import threading
import traceback
import datetime
from gi.repository import Gtk as gtk, Gdk, Notify
import os
import re
import time
import subprocess
import sys

import gitParser
from logs import logger
from pull_all import pull_all_branches
from sys_tray_menu import Icon


# import notify2
# notify2.init('icon-summary-body', 'glib')


class BaseApp(object):
    def __init__(self):
        logger.info('start init')

        self.icon = None
        self.log = logger
        self.rg = re.compile('\[(?:\w)+/([A-Za-z0-9\._]+): behind (\d+)\]')
        self.opt_repository = []
        self.opt_branch = []
        self.opt_timeout = 60
        self.log.info('\n\nDaemon start\n\n')
        self.img_path = None
        self._running = 1
        self.nn = []
        self.datata = []
        self.config_parse()
        self.fire_notify('start')

        # notify2.init('icon-summary-body')

    def config_parse(self):
        config = ConfigParser.ConfigParser()
        configpath = self.get_full_path('config.cfg')
        self.img_path = self.get_full_path('images4.png')
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
                    self.opt_repository.append(config.get(section, option))

                else:
                    setattr(self, 'opt_%s' % option.split('_')[0], func(section, option))

        if not getattr(self, 'opt_repository'):
            message = 'Is not define repository path in "config.cfg". Daemon stopped.'
            self.fire_notify(message)
            self.log.error(message)
            sys.exit(2)

    def run(self):
        while self._running:
            try:
                self.run_in_thread(self.updater, daemon='no')
                self.create_icon()
            except:
                self.log.info(traceback.format_exc())

    def updater(self):
        while self._running:
            self.log.info('run check in thread by timeout %s' % self.opt_timeout)
            self.check()
            if self.icon is not None:
                self.icon.count_down(self.opt_timeout, False)

    def update_branches(self, path):
        try:
            pull_all_branches(path)
            self.log.info('call fire')
            self.fire_notify('pull ok: %s' % path, 'title')
            self.log.info('exit update')
        except Exception as e:
            self.fire_notify('error', 'title')
            self.log.error(e)
        else:
            self.log.info('noerror in update')
        finally:
            self.log.info('exit from updater')

    @staticmethod
    def close(*a, **kwargs):
        logger.info('close in myapp')
        subprocess.call(['python', '%s/watcher.py' % os.path.split(os.path.abspath(__file__))[0]])

    def create_icon(self):
        br = []
        for repo in self.opt_repository:
            br.append(['Check: %s' % repo.split('/')[-1], self.call_back_menu, (repo, repo.split('/')[-1])])
        if os.path.exists(self.img_path):

            class I(Icon):
                def close_app(*args, **kwargs):
                    self.close()

            self.icon = I(self.img_path, br)
            self.icon.reload_command = 'kill %s' % os.getpid()
            self.icon.crearte_sys_tray_icon()
            self.icon.start_giu()
        else:
            self.log.error('no img path:%s' % self.img_path)
            raise Exception('no image')

    def run_in_thread(self, target, *a, **k):
        try:
            join = False
            if 'join' in k:
                join = k.pop('join')
            dd = 'y'
            if 'daemon' in k:
                dd = k.pop('daemon')
            self.log.info(str(k))
            tr = threading.Thread(target=target, args=a, kwargs=k)

            if dd == 'y':
                tr.setDaemon(1)
            tr.start()
            self.log.info('join: %s' % join)
            if join:
                tr.join()
        except:
            self.log.info('err in thread: %s' % traceback.format_exc())
        else:
            self.log.info('thread created')

    # @staticmethod
    def call_back_fire(self, _, action, data=None):
        self.log.info('callback %s,   %s' % (action, data))
        self.run_in_thread(pull_all_branches, data)
        self.fire_notify('check %s' % data)
        self.say(['say_en', '"git. pull. repo"'])

    def call_back_menu(self, a):
        self.log.info('menu: %s' % str(a))
        self.run_in_thread(self.update_branches, a[0])
        self.log.info('end update exit menu')
        self.say(['say_en', '"git. pull. repo. %s"' % a[1], ])

    def empty_cb(self, n):
        self.log.info('closed notify msg')
        n.close()

    def fire_notify(self, msg='', title='GitPushNotify', add_callback=None, path=None):
        # raise Exception(999)
        Notify.init("New commit")

        self.log.info('Called fireNotify()')
        try:
            # n = notify2.Notification(title, msg, '')
            n = Notify.Notification.new(title, msg)
            if len(self.nn) > 10:
                self.nn = []
            self.nn.append(n)

            self.log.info('append data')
            n.set_urgency(1)
            self.log.info('set_urgency')
            if add_callback:
                self.log.info('add callback ')
                n.connect('closed', self.empty_cb)
                n.add_action(
                    "clicked",
                    " pull all branches ",
                    self.call_back_fire,
                    path)
            self.log.info('show')
            try:
                n.show()
            except Exception as e:
                self.log.info('error while show: %s' % e)
            else:
                self.log.info('showed')
            finally:
                self.log.info('end show')
        except Exception as e:
            self.log.info('error in firenotify: %s' % e)
            traceback.print_exc()
        else:
            self.log.info('ok firenotify')

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

        self.log.info('branches_list: %s' % json.dumps(branches_list))

        count_commits = 0
        message = ''

        for br in branches_list:
            num = self.rg.search(br)
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
                commit_time = datetime.datetime.fromtimestamp(int(item['time']))
                message += ('...\n'
                            + commit_time.strftime('%x %X') + '\n'
                            + item['author'] + ' &lt;' + item['email'] + '&gt;\n'
                            + item['message'] + '\n')

        if count_commits:
            message += '...\n%s new commit(s)\n\n' % count_commits
            self.fire_notify(message, add_callback=True, path=repository_path)
            self.say(['say_en', '"get. new. commit"'])

        self.log.info('Count commits: %s', count_commits)
        self.log.info('End check()')

    def say(self, data):
        self.run_in_thread(self._say, data)

    @staticmethod
    def _say(data):
        try:
            ss = subprocess.Popen(data)
            ss.wait()
        except:
            logger.error(traceback.format_exc())

    def check(self, threaded=True):
        try:
            self.log.info('Called check()')
            for repository_path in self.opt_repository:
                self.log.info('check repository: %s' % repository_path)
                if threaded:
                    self.run_in_thread(self.check_one, repository_path)
                else:
                    self.check_one(repository_path)
        except:
            self.log.error(traceback.format_exc())

    @staticmethod
    def get_full_path(*args):
        return os.path.join(os.path.dirname(__file__), *args)


if __name__ == '__main__':
    def proc_exist(name):
        try:
            process = subprocess.Popen(stdout=-1, args='ps x|grep %s|grep -v grep|grep -v Z' % name, shell=True)
            output, _ = process.communicate()
            process.poll()
            if output:
                return set(i.split()[0] for i in output.rstrip('\n').split('\n'))
            return set()
        except:
            return set()

    ppe = proc_exist(__file__)
    pid = {str(os.getpid()), }
    if ppe - pid:
        logger.info('found %s process' % (ppe - pid))
        sys.exit(1)

    pidfile = tempfile.gettempdir() + '/daemonGitPushNotify.pid'
    pid = str(os.getpid())
    with open(pidfile, 'w') as pf:
        pf.write("%s" % pid)
    bapp = BaseApp()
    bapp.say(['say_en', '"start service"', ])
    bapp.run()

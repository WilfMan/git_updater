import subprocess
import re

from logs import logger as log_


class Stash(object):
    def __init__(self, status, project_path, new_branch):
        self.do_stash = 'modified' in status
        self.project_path = project_path
        self.cur_branch = status.split('\n')[0].split(' ')[-1:][0]
        self._need_checkout = self.cur_branch != new_branch

    def __enter__(self):
        if self.do_stash:
            log_.info('stashing  %s' % self.cur_branch)
            name = 'save stash in branch %s' % self.cur_branch
            subprocess.check_output(
                'cd %(project_dir)s && git stash save "%(msg)s"' % {
                    'project_dir': self.project_path, 'msg': name},
                shell=True)

    def __exit__(self, *_):
        if self._need_checkout:
            subprocess.check_output(
                'cd %(project_dir)s && git checkout %(branch)s' % {
                    'project_dir': self.project_path, 'branch': self.cur_branch},
                shell=True)
        if self.do_stash:
            subprocess.check_output(
                'cd %(project_dir)s && git stash pop' % {'project_dir': self.project_path, },
                shell=True)


def pull_all_branches(project_dir):
    log_.info('get task path: %s' % project_dir)
    try:
        raw_branches = subprocess.check_output(
            'cd %(project_dir)s && git fetch && git branch -vv|grep behind' % {'project_dir': project_dir}, shell=True)
        log_.info('raw_branches: %s' % raw_branches)
    except subprocess.CalledProcessError:
        raw_branches = ''
    if not raw_branches:
        log_.info('nothing pull dir:%s' % project_dir)
        return

    rr = re.compile('\[(?:\w)+/([A-Za-z0-9\._]+): behind (\d+)\]')

    branches = [rr.search(i).group(1) for i in raw_branches.split('\n') if rr.search(i)]
    if branches:
        log_.info('branches: %s' % branches)
        status = subprocess.check_output('cd %(project_dir)s && git status' % {'project_dir': project_dir},
                                         shell=True)
        log_.info('status: %s' % status)
        for branch in branches:
            with Stash(status, project_dir, branch):
                s = subprocess.check_output(
                    'cd %(project_dir)s && git checkout %(branch)s && git pull' % {
                        'project_dir': project_dir, 'branch': branch},
                    shell=True)
                log_.info('pull: %s' % s)
    else:
        log_.info('branches from regexp is none')


if __name__ == '__main__':
    pull_all_branches('/home/vilf/work/paymentgateway')

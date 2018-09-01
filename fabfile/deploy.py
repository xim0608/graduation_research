from fabric.api import run, abort, env, cd, local
from fabric.decorators import task


class RemoteHandler(object):
    env.use_ssh_config = True
    env.ssh_config_path = "~/.ssh/config"
    
    def pull(self):
        with cd(env.app_path):
            self.__check_no_diff()
            run('git checkout master')
            run("git pull origin master")

    def restart(self):
        self.__install_required_package()
        # TODO: restart server daemon

    def __install_required_package(self):
        with cd(env.app_path):
            run('pipenv install')

    def __check_no_diff(self):
        res = run('git ls-files -m')
        if res:
            abort('remote error: there are some diff on git supervised files')

@task
def deploy():
    rh = RemoteHandler()
    rh.pull()
    rh.restart()

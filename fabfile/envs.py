from fabric.api import env
from fabric.decorators import task

@task
def production():
    home_dir = '/home/gr_user'
    env.environment = "production"
    env.app_path = home_dir + '/graduation_research'
    env.daemon_name = 'graduation_research daemon'
    env.user = 'gr_user'
    env.hosts = ['worker01.idcf', 'worker02.idcf']

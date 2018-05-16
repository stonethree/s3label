from fabric.api import cd, local, run, sudo


def deploy_backend():
    site_folder = '/opt/s3_label/backend'
    with cd(site_folder):
        _update_virtualenv()


def deploy_frontend():
    site_folder = '/opt/s3_label/frontend/spa'
    with cd(site_folder):
        _update_node_modules()


def _update_virtualenv():
    run('./venv/bin/pip install -r requirements.txt')


def _update_node_modules():
    run('npm install')

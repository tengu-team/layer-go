#!/usr/bin/env python3
# Copyright (C) 2017  Ghent University
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import os
import shutil
import tarfile
import requests
from pwd import getpwnam
from grp import getgrnam
from jujubigdata import utils
from charmhelpers.core import hookenv
from charmhelpers.core.hookenv import status_set, log
from charms.reactive import when, when_not, set_state, remove_state


@when_not('go.installed')
def install_go():
    version = hookenv.config().get('version')
    if not version:
        status_set('blocked', 'Provide a Go version')
        return
    try:
        request = requests.get(version)
        if not request.status_code == 200:
            return
        file_path = '/tmp/' + version.split('/')[-1]
        with open(file_path, 'wb') as f:
            f.write(request.content)
    except requests.exceptions.RequestException as e:
        hookenv.log(e)
        return
    tar = tarfile.open(file_path, 'r:gz')
    tar.extractall('/tmp')
    tar.close()
    if not os.path.exists('/home/ubuntu/go'):
        shutil.move('/tmp/go', '/home/ubuntu')
    os.makedirs('/home/ubuntu/code/go/bin')
    chown_recursive('/home/ubuntu/go', 'ubuntu', 'ubuntu')
    chown_recursive('/home/ubuntu/code', 'ubuntu', 'ubuntu')
    with utils.environment_edit_in_place('/etc/environment') as env:
        env['GOROOT'] = '/home/ubuntu/go'
        env['GOPATH'] = '/home/ubuntu/code/go'
        env['PATH'] = env['PATH'] + ':/home/ubuntu/go/bin:/home/ubuntu/code/go/bin'

    # Install package manager
    r = requests.get('https://raw.githubusercontent.com/pote/gpm/v1.4.0/bin/gpm')
    with open('/usr/local/bin/gpm', 'wb') as f:
        f.write(r.content)
    os.chmod("/usr/local/bin/gpm", 0o755)

    status_set('active', 'go installed')
    set_state('go.installed')


def chown_recursive(path, user, group):
    user_id = getpwnam(user).pw_uid
    group_id = getgrnam(group).gr_gid
    for root, dirs, files in os.walk(path):
        for momo in dirs:
            os.chown(os.path.join(root, momo), user_id, group_id)
        for momo in files:
            os.chown(os.path.join(root, momo), user_id, group_id)
    os.chown(path, user_id, group_id)
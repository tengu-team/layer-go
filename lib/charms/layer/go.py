from charmhelpers.core import hookenv


def environment():
    """returns a dict containing the following environment variables:
    GOROOT
    GOPATH
    """
    version = hookenv.config().get('version')
    if not version:
        return None
    return {
        'GOROOT': '/home/ubuntu/go',
        'GOPATH': '/home/ubuntu/code/go'
    }
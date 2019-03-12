import subprocess


def push_and_compile(commit_message):
    """
    Executes shell script 'build.sh' from `git:frangitron-raspberry/scripts`
    """
    command = ['gnome-terminal', '-x', 'bash', '-c', './push.sh "{}"'.format(commit_message)]

    subprocess.Popen(
        command,
        cwd="/home/frangi/frangitron/frangitron-raspberry/scripts",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )


def upload_samples(address, user, source):
    """
    Uploads samples to pi's /var/frangitron/samples
    """
    command = ['gnome-terminal', '-x', 'bash', '-c', 'scp -r {} {}@{}:/var/frangitron/samples'.format(
        source,
        user,
        address
    )]

    subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )


def retrieve_recordings(address, user, destination):
    """
    Retieves recordings from pi's /var/frangitron
    """
    command = ['gnome-terminal', '-x', 'bash', '-c', 'scp -r {}@{}:/var/frangitron {}'.format(
        user,
        address,
        destination
    )]

    subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

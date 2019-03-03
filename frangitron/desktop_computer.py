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

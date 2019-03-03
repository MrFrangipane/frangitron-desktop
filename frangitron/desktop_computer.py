import subprocess


def push_and_compile(commit_message):
    """
    Executes shell script 'build.sh' from `git:frangitron-raspberry/scripts`
    """
    subprocess.Popen(
        ['gnome-terminal', '-x', 'bash', '-c', './push.sh', commit_message],
        cwd="/home/frangi/frangitron/frangitron-raspberry/scripts",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

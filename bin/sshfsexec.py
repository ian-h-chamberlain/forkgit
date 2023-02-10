#!/usr/bin/env python3

import errno
import json
import os
import pipes
import re
import sys
import stat

from pathlib import Path
from configparser import ConfigParser
from subprocess import run


EXIT_COMMAND_NOT_FOUND = 127
EXIT_SSHFS_HOST_MISMATCH = 1
SSH_BINARY = 'ssh'


def which(binary, path=os.environ.get('PATH', '')):
    """
    Return the absolute path of an executable with the basename defined by
    `binary.` If an absolute path is given for `binary`, then the value is
    `binary` is returned if it is executable. In the event that an
    executable binary cannot be found, None is returned. This command is
    analogous to the *nix command "which(1)."
    """
    if '/' in binary:
        if os.access(binary, os.X_OK):
            return binary
        return None

    for folder in path.split(':'):
        try:
            contents = os.listdir(folder)
        except Exception:
            continue

        if binary in contents:
            binarypath = os.path.abspath(os.path.join(folder, binary))
            if os.access(binarypath, os.X_OK):
                return binarypath

    return None


def listtoshc(arglist):
    """
    Convert a list of command line arguments to a string that can be
    executed by POSIX shells without interpolation of special characters.

    Example:
    >>> print(listtoshc(['cat', '.profile', '`rm -rf *`']))
    cat .profile '`rm -rf *`'
    """
    return ' '.join(map(pipes.quote, arglist))


def fake_section_heading(fp):
    yield '[fakesection]\n'
    yield from fp

    
def read_dotforkgit(path):
    dotforkgit = Path(path) / '.forkgit'
    if not dotforkgit.exists():
        return {}
    cp = ConfigParser()
    cp.read_file(fake_section_heading(dotforkgit.open()))
    return cp['fakesection']


def main(configcode=''):
    command, originalargs = os.path.basename(sys.argv[0]), sys.argv[1:]
    envpassthrough = dict()
    environment = dict(os.environ)
    stdin_is_pipe = stat.S_ISFIFO(os.fstat(0).st_mode)

    # Configuration defaults
    translate_all_arguments = False
    preserve_isatty = False
    coerce_remote_execution = False

    config = read_dotforkgit(os.getcwd())

    # Figure out where the current working directory is on the remote system.
    local_root = os.getcwd()
    remote_host = config.get('remote-host')
    if remote_host:
        remote_root = config['remote-root']
        sshlogin = remote_host
        remotepath = remote_root
        sshhost = sshlogin.split('@')[0] if '@' in sshlogin else sshlogin
    else:
        sshlogin = None

    # First execution of configuration code prior to processing arguments.
    pre_process_config = True
    exec(configcode)

    if sshlogin and command == 'git':
        preserve_isatty = True
        if originalargs in (['rev-parse', '--absolute-git-dir'],
                            ['rev-parse', '--show-toplevel']):
            print(os.getcwd())
            sys.exit()
        elif originalargs[0] == 'commit':
            for i, originalarg in enumerate(originalargs[1:], 1):
                if not originalarg.startswith('--file'):
                    continue
                arg, local_path = originalarg.split('=')
                remote_path = os.path.join('/tmp', os.path.basename(local_path))
                run(['scp', local_path, f'{sshlogin}:{remote_path}'], check=True)
                originalargs[i] = f'--file={remote_path}'

    remoteargs = list()
    for argument in originalargs:
        remoteargs.append(argument)

    # Second execution of configuration code after processing arguments.
    pre_process_config = False
    exec(configcode)

    if sshlogin:
        # If the command should be executed on a remote server, generate the
        # execution string to pass into the shell.
        executed = listtoshc([command] + remoteargs)

        # Prepend environment variable declarations
        for variable, value in envpassthrough.items():
            executed = '%s=%s %s' % (variable, pipes.quote(value), executed)

        if remote_root:
            # If the current working directory is inside an SSHFS mount, cd
            # into the corresponding remote directory first. Why the brackets?
            # When data is piped into cd without cd being in a command group,
            # cd will not work:
            #
            #   ~% echo example | cd / && pwd
            #   /home/jameseric
            #   ~% echo example | { cd / && pwd; }
            #   /
            #
            quotedremotecwd = pipes.quote(remote_root)
            sshcommand = '{ cd %s && %s; }' % (quotedremotecwd, executed)
        else:
            sshcommand = executed

        ttys = [fd.isatty() for fd in (sys.stdin, sys.stdout, sys.stderr)]
        if any(ttys):
            ttyoption = '-t'
            if not preserve_isatty:
                # Only create a tty if stdin and stdout are attached a tty.
                ttyoption = '-t' if all(ttys[0:2]) else '-T'

            elif not all(ttys):
                # Do some kludgey stuff to make isatty for the remote process
                # match the what sshfsexec sees.
                if not ttys[0]:
                    sshcommand = 'stty -echo; /bin/cat | ' + sshcommand
                    ttyoption = '-tt'
                if not ttys[1]:
                    sshcommand += ' | /bin/cat'
                if not ttys[2]:
                    sshcommand = ('exec 3>&1; %s 2>&1 >&3 3>&- | /bin/cat >&2'
                        % sshcommand)

        else:
            ttyoption = '-T'

        argv = [SSH_BINARY, '-o', 'LogLevel=QUIET']
        if ttyoption == '-T':
            argv += ['-e', 'none']

        argv += [sshlogin, ttyoption, sshcommand]

    else:
        # If the command does not interact with any SSHFS-mounted paths, run
        # the executable that the script replaced.
        path = os.environ.get('PATH', '')
        while path:
            replacedbinary = which(command, path)

            if replacedbinary:
                if os.path.samefile(__file__, replacedbinary):
                    if ':' in path:
                        _, path = path.split(':', 1)
                        continue
                else:
                    break

            print("sshfsexec: %s: command not found" % command)
            exit(EXIT_COMMAND_NOT_FOUND)

        argv = [replacedbinary] + originalargs

    os.execvpe(argv[0], argv, environment)


if __name__ == "__main__":
    defaultconfigpath = os.path.expanduser('~/.sshfsexec.conf')
    configpath = os.environ.get('SSHFSEXEC_CONFIG', defaultconfigpath)

    try:
        with open(configpath) as iostream:
            configcode = iostream.read()
    except IOError as e:
        if e.errno != errno.ENOENT:
            raise
        configcode = ''

    main(configcode)

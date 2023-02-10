sshgit
======

This is a fork of [sshfsexec](https://github.com/ericpruitt/sshfsexec) to allow
[Fork](https://fork.dev/) on macOS to interact with remote git checkouts over SSH.

Known issues:
- not thoroughly tested; expect trouble!
- the current branch and HEAD commit are not indicated properly
  (commits on the current branch are normally displayed in black and the HEAD
   commit should be displayed in bold text)
- removing untracked files doesn't work
- interactive rebase is not yet working
- you may need to refresh the Local Changes view explicitly (Cmd+R)
- not tested at all on Windows and thus unlikely to work there

See also https://github.com/fork-dev/Tracker/issues/929.


Usage
-----

1. Clone this repository.

2. For each git checkout on the remote server, create a directory locally and
   create a file `.gitfork` inside with these contents (replacing values within
   `<>`):
   ```
   remote-host = <remote machine's hostname>
   remote-root = <absolute path to git checkout on the remote machine>
   ```

4. In the Fork Git preferences, add this repository's `bin/git` as a custom git
   instance.

5. Open the directories that represent the git checkouts on the remote machine
   in Fork.


To speed up interaction with remote checkouts, you can configure SSH multiplexing
for the server. This involves setting _ControlPath_, _ControlMaster_ and _ControlPersist_
in your `~/.ssh/config` for the host you're connecting to. See the [OpenSSH Wikibook](https://en.wikibooks.org/wiki/OpenSSH/Cookbook/Multiplexing#Setting_Up_Multiplexing)
for more information.


See sshfsexec.md for more information on sshfsexec.

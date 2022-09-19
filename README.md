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

2. Locally, create empty directories corresponding to git checkout directories
   on the remote server.

3. Adjust checkouts.json to map these directories. The format is
   ```
   "<path to empty dir on local machine>":
       ["<server hostname>", "<path to git checkout dir on server>"]
   ```
   (remember to append a comma to all entries but the last)

4. In the Fork Git preferences, add this repository's `bin/git` as a custom git
   instance.

5. Open one of the empty directories that you mapped in checkouts.json


To speed up interaction with remote checkouts, you can configure SSH multiplexing
for the server. This involves setting _ControlPath_, _ControlMaster_ and _ControlPersist_
in your `~/.ssh/config` for the host you're connecting to. See the [OpenSSH Wikibook](https://en.wikibooks.org/wiki/OpenSSH/Cookbook/Multiplexing#Setting_Up_Multiplexing)
for more information.


See sshfsexec.md for more information on sshfsexec.

# py9tor

A Python orchestrator for shell processes.

`py9tor` is designed to apply various policies to start local or remote processes.

At the time of this writing, two policies are available:

1. a simple policy that limits concurrent instances of a process;
1. a `rsnapshot` specific policy that handles process priority to avoid overlapping instances (i.e. wait for `weekly` to end before starting `daily`).

Other can be created adding modules in the `py9tor/handlers` package.

## LICENSE

Copyright Ugo Paternostro 2025. Licensed under the EUPL-1.2 or later.

See [LICENSE](LICENSE.md) for license full text, or visit [European Commission Joinup site](https://joinup.ec.europa.eu/collection/eupl) for latest version.

## USAGE

Clone the repository somewhere (I'm using `/usr/local/py9tor` directory):

    git clone https://github.com/upaternostro/py9tor.git

Create a `config.json` configuration file (see below).

Launch the server:

    python main.py

Use the client to interact with the server: from another shell use

    python p9tor-client.py

specifying a target to launch (`-t` switch) or requesting current status (`-s` switch).

### Requirements

`py9tor` requires a Python v3 or above interpeter. At this moment, it does not use any external module or library.

### Daemon installation

Use the `systemd/py9tor.service` template to add `systemd` support. Copy it to `/etc/systemd/system`

    cp systemd/py9tor.service /etc/systemd/system

enable it

    systemctl enable py9tor.service

then reload `systemd` configuration

    systemctl daemon-reload

and finally start it

    systemctl start py9tor.service

Please note that `systemd/py9tor.service` is just a template: you have to edit it substituting your paths both for installation directory and for Python interpeter.

In this configuration, output from `py9tor` is captured by `systemd` and can be accessed via

    systemctl status py9tor.service

or

    journalctl -u py9tor.service

## CONFIGURATION

`py9tor` reads a single configuration file, named `config.json`, that should contain a JSON object containing the following keys:

1. `host`: the address to bind XMLRPC server to (default: `localhost`);
1. `port`: the port to bind XMLRPC server to (default: `8000`);
1. `targets`: an object containing targets, identified by the key value.

Each target is itself a JSON object containing at least the following keys:

1. `class`: the worker class that will run the target. Must be one of:
    * `py9tor.worker.DummyExecutor`: a dummy, do-nothing, executor;
    * `py9tor.worker.LocalExecutor`: a class that will spawn a local process;
    * `py9tor.worker.SSHExecutor`: a class that uses SSH to run a remote process.
1. `attrs`: an object containing specific keys based on the selected class.
1. `handler`: an optional module name that will manage target acceptance (i.e. decide if it has to be ran or not). At the moment, two modules are available:
    * `py9tor.handlers.cardinality`;
    * `py9tor.handlers.rsnapshot`.

    Please nothe tha handlers may require specific configuration adding keys in the JSON object (see below).

The following paragraphs will describe classes, attributes and handlers.

The same `config.json` is used by the `py9tor-client` to extract the connection URI (see below).

### Worker classes and their attributes

#### DummyExecutor

This class is used for test purposes: it does not start any process, but simply waits for a configurable amount of seconds.

It accepts a single attribute, named `time`, that must contain the amount of seconds to wait (integer number).

#### LocalExecutor

This class spawn a local process as configured in the `args` array attribute.

The first array entry (`args[0]`) must contain the process to launch (eventually with its full path).

Other entries will be passed to the process as parameters.

#### SSHExecutor

This class uses a local SSH client to start a process on a remote machine. It requires the following attributes:

* `key`: the identity file used to authenticate. Please note that the file must not be password protected;
* `user`: the user used for authentication;
* `host`: the remote host domain name or IP;
* `port`: the remote TCP port to connect to (defaults to 22);
* `cmds`: an array of commands to execute on the remote host, one per line (each line must contain its parameters too).

### Handler modules

#### cardinality

This handler limits the number of concurrent processes.

The maximum number of processes must be specified via the `instances` key.

#### rsnapshot

This is a `rsnapshot` specific handler, useful to queue running instances by priority.

As you can read in the `rsnapshot` documentation, you'll define a set of "backup intervals", for example `daily`, `weekly`, `monthly` and `yearly` in ascending order.

Those intervals are usually scheduled via a cron that, in the worst case, will start them in descending order (i.e. from `yearly` to `daily`), interleaving them with an appropiate delay (say: half an hour).

Well, if you system performance or its load are not optimal, it may happens that the second `rsnapshot` instance does not start as it detects that the first is still running.

This handler cares of this situation: if you configure the system to signal `py9tor` that a `rsnapshot` shoukd start, the handler will take care of delaying it till all the higher priorities `rsnapshot` completed.

### Logging configuration

`py9tor` can be tweaked modifing the `logging.conf` configuration file.

The default configuration outputs `INFO` and higher messages to `stdout`. This will be captured by `systemd` if the daemon is uner its control.

## CLIENT

`py9tor-client.py` is an interface to the running daemon that can start targets or query status.

Please invoke with the `-h` (or `--help`) parameter to see usage, as in:

    pyhton py9tor-client.py --help

Please note that it will read `config.json` file to extract host and port of the daemon.

## EXAMPLES

`config.json` example:

    {
        "host": "localhost",
        "port": 1234,
        "targets": {
            "dummyTarget": {
                "class": "py9tor.worker.DummyExecutor",
                "handler": "py9tor.handlers.cardinality",
                "instances": 1,
                "attrs": {
                    "time": 10
                }
            },
            "aLocal": {
                "class": "py9tor.worker.LocalExecutor",
                "attrs": {
                    "args": [
                        "ls",
                        "-l"
                    ]
                }
            },
            "aRemote": {
                "class": "py9tor.worker.SSHExecutor",
                "attrs": {
                    "key": "keyfile",
                    "user": "username",
                    "host": "host-fqdn",
                    "cmds": [
                        "ls -la"
                    ]
                }
            },
            "rsnap-hourly": {
                "class": "py9tor.worker.LocalExecutor",
                "handler": "py9tor.handlers.rsnapshot",
                "interval": "hourly",
                "attrs": {
                    "args": [
                        "/usr/bin/rsnapshot",
                        "hourly"
                    ]
                }
            },
            "rsnap-daily": {
                "class": "py9tor.worker.LocalExecutor",
                "handler": "py9tor.handlers.rsnapshot",
                "interval": "daily",
                "attrs": {
                    "args": [
                        "/usr/bin/rsnapshot",
                        "daily"
                    ]
                }
            },
            "rsnap-weekly": {
                "class": "py9tor.worker.LocalExecutor",
                "handler": "py9tor.handlers.rsnapshot",
                "interval": "weekly",
                "attrs": {
                    "args": [
                        "/usr/bin/rsnapshot",
                        "weekly"
                    ]
                }
            },
            "rsnap-monthly": {
                "class": "py9tor.worker.LocalExecutor",
                "handler": "py9tor.handlers.rsnapshot",
                "interval": "monthly",
                "attrs": {
                    "args": [
                        "/usr/bin/rsnapshot",
                        "monthly"
                    ]
                }
            },
            "rsnap-yearly": {
                "class": "py9tor.worker.LocalExecutor",
                "handler": "py9tor.handlers.rsnapshot",
                "interval": "yearly",
                "attrs": {
                    "args": [
                        "/usr/bin/rsnapshot",
                        "yearly"
                    ]
                }
            }
        }
    }

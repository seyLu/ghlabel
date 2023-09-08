# `ghlabel`

Setup Github Labels from a yaml/json config file.

**Usage**:

```console
$ ghlabel [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--version`, `-v`
Show version and exit.
* `--debug`, `-D`
Enable debug mode and show logs.
* `--help`, `-h`
Show this message and exit.

**Commands**:

* `dump`
Generate starter labels config files.
* `setup`
Add/Remove Github labels from config files.

## `ghlabel dump`

Generate starter labels config files.

**Usage**:

```console
$ ghlabel dump [OPTIONS]
```

**Options**:

* `--new`, `-n` / `--keep-old-labels`, `-N`: [default: new] Deletes all files in labels dir.
* `--dir TEXT`: [default: labels]
Specify the dir where to find labels.
* `--ext [json|yaml]`: [default: yaml]
Label file extension.
* `--app [app|game|web]`: [default: app]
App to determine label template.
* `--help`: Show this message and exit.

## `ghlabel setup`

Add/Remove Github labels from config files.

**Usage**:

```console
$ ghlabel setup [OPTIONS] TOKEN REPO_OWNER
```

**Arguments**:

* `TOKEN`: [required]
* `REPO_OWNER`: [required]

**Options**:

* `--repo-name TEXT`
* `--dir TEXT`: [default: labels]
* `--strict / --no-strict`: [default: strict]
* `--add-labels TEXT`
* `--remove-labels TEXT`
* `--remove-all [disable|enable|silent]`: [default: disable]
* `--help`: Show this message and exit.



## :red_circle: `ghlabel`

Setup Github Labels from a yaml/json config file.

### Usage:

```console
$ ghlabel [OPTIONS] COMMAND [ARGS]...
```

<br>

### :large_orange_diamond: Options:

#### `--version`, `-v`
Show version and exit.
#### `--debug`, `-D`
Enable debug mode and show logs.
#### `--help`, `-h`
Show this message and exit.

<br>

### Commands:

#### `dump`
Generate starter labels config files.
#### `setup`
Add/Remove Github labels from config files.

<br>

## :red_circle: `ghlabel dump`

Generate starter labels config files.

### Usage:

```console
$ ghlabel dump [OPTIONS]
```

<br>

### :large_orange_diamond: Options:

#### `--new`, `-n` / `--keep-old-labels`, `-N` [default: new]
Deletes all files in labels dir.
#### `--dir TEXT` [default: labels]
Specify the dir where to find labels.
#### `--ext [json|yaml]` [default: yaml]
Label file extension.
#### `--app [app|game|web]` [default: app]
App to determine label template.
#### `--help`
Show this message and exit.

<br>

## :red_circle: `ghlabel setup`

Add/Remove Github labels from config files.

### Usage:

```console
$ ghlabel setup [TOKEN] [REPO_OWNER] [REPO_NAME] [OPTIONS]
```

<br>

### :large_blue_diamond: Arguments:

#### `TOKEN` [optional]
#### `REPO_OWNER` [optional]
#### `REPO_NAME` [optional]

<br>

### :large_orange_diamond: Options:

#### `--dir TEXT` [default: labels]
Specify the dir where to find labels.
#### `--strict`, `-s` / `--no-strict`, `-S` [default: strict]
Strictly mirror Github labels from labels config.
#### `--add-labels TEXT`
Add more labels.
#### `--remove-labels TEXT`
Remove more labels.
#### `--remove-all [disable|enable|silent]` [default: disable]
Remove all Github labels.
#### `--help`: Show this message and exit.

<br>

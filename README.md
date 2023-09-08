<div align="center">
    <img height=100 src="https://github.com/seyLu/setup-issue-label-cli/blob/main/static/icons/labels.png" alt="Setup Github Label CLI Icon">
    <h1Github Label CLI</h1>
    <p>CLI tool to help setup Github Labels from a yaml/json config file.</p>
    <p>
        <a href="https://github.com/seyLu/setup-issue-label-cli/issues/new">Report Bug</a>
        ·
        <a href="https://github.com/seyLu/setup-issue-label-cli/issues/new">Request Feature</a>
        ·
        <a href="https://github.com/seyLu/setup-issue-label-cli/discussions">Ask Question</a>
    </p>
</div>

<br>

### Supported Python version

```bash
python==3.11
```

<br>

### Setup

#### 1. Clone the repo

```bash
git clone https://github.com/seyLu/setup-github-label-cli.git
```

#### 2. Install dependencies

##### Create a new virtual environment

```bash
python -m venv .venv
```

##### Activate the virtual environment

```bash
# Linux/Mac
. .venv/bin/activate

# Windows
.venv\Scripts\activate.bat
```

##### Install dependencies from requirements.txt

```bash
pip install -r requirements.txt
```

#### 3. Create `.env` and supply github credentials

```bash
cp .env.example .env
```

##### `.env.example` preview

```bash
GITHUB_PERSONAL_ACCESS_TOKEN=<your_github_personal_access_token>
GITHUB_REPO_OWNER=<target_github_repository_owner>
GITHUB_REPO_NAME=<target_github_repository_name>
```

<br>

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
#### `--help`
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
#### `--dir`, `-d TEXT` [default: labels]
Specify the dir where to find labels.
#### `--ext`, `-e [json|yaml]` [default: yaml]
Label file extension.
#### `--app`, `-a [app|game|web]` [default: app]
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

#### `--dir`, `-d TEXT` [default: labels]
Specify the dir where to find labels.
#### `--strict`, `-s` / `--no-strict`, `-S` [default: no-strict]
Strictly mirror Github labels from labels config.
#### `--add-labels`, `-a TEXT`
Add more labels.
#### `--remove-labels`, `-r TEXT`
Remove more labels.
#### `--remove-all`, `-R [disable|enable|silent]`  [default: disable]
Remove all Github labels.
#### `--help`
Show this message and exit.

<br>

### Example Usage

#### Overriding `.env` or Manually adding Environment Variables

```bash
REPO_NAME=medrec ghlabel setup
```

#### Removing more labels

```bash
# -r [comma-separated string]
# will be parsed as list[str]
ghlabel setup -r "Type: Feature Request, Type: Bug"
```

#### Adding more labels

```bash
# -a [valid json string]
# will be parsed as list[dict[str, str]]
ghlabel setup -a "[{'name': 'wontfix', 'color': '#ffffff'}, {'name': 'bug', 'color': '#d73a4a', 'description': 'Something isn't working'}]"
```

<br>

### Adding Custom Github Labels

#### valid values (yaml/json)

```yaml
# yaml
- name: <label_name>
  color: <label_color_hash>
  description: <label_description>
```
```yaml
# json
[
  {
    "name": <label_name>,
    "color": <label_color_hash>,
    "description": <label_description>
  }
]
```

#### labels/affects_labels.yaml
![Affects Labels Screenshot](static/images/affects_labels.png)

#### labels/close_labels.yaml
![Close Labels Screenshot](static/images/close_labels.png)

#### labels/default_labels.yaml
![Default Labels Screenshot](static/images/default_labels.png)

#### labels/needs_labels.yaml
![Needs Labels Screenshot](static/images/needs_labels.png)

#### labels/priority_labels.yaml
![Priority Labels Screenshot](static/images/priority_labels.png)

#### labels/state_labels.yaml
![State Labels Screenshot](static/images/state_labels.png)

#### labels/type_labels.yaml
![Type Labels Screenshot](static/images/type_labels.png)

### Removing labels

#### labels/_remove_labels.yaml
```yaml
- bug
- dependencies
- documentation
- duplicate
- enhancement
- github_actions
- help wanted
- invalid
- python
- question
- wontfix
```

### [Optional] Game Dev Additional Labels

#### labels/affects_labels.yaml
![Game Dev Affects Labels Screenshot](static/images/game_dev/affects_labels.png)

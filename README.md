<div align="center">
    <img height=100 src="https://github.com/seyLu/setup-issue-label-cli/blob/main/static/icons/labels.png" alt="Setup Issue Label CLI Icon">
    <h1>Setup Issue Label CLI</h1>
    <p>CLI tool to help setup Github Issue labels from a yaml/json config file.</p>
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

### Usage

#### 1. Clone the repo

```bash
git clone git@github.com:seyLu/setup-issue-label-cli.git
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
. .venv/Scripts/activate
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

#### 4. Run the CLI tool

```py
python scripts/setup_issue_label.py
```

<br>

### Adding Custom Issue Labels

> Currently only supports YAML config

#### valid values

```
- name: <label_name>
  color: <label_color_hash>
  description: <label_description>
```

#### `config/labels.yaml` preview

```yaml
- name: 'Type: Feature Request'
  color: '#e88a1a'
  description: Issue describes a feature or enhancement we'd like to implement.
- name: 'Type: Question'
  color: '#d876e3'
  description: This issue doesn't require code. A question needs an answer.
- name: 'Type: Refactor/Clean-up'
  color: '#a0855b'
  description: Issues related to reorganization/clean-up of data or code (e.g. for
    maintainability).
```

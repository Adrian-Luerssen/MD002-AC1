# MD002-AC1

## Setup for Ubuntu 24.04

### Install system libraries

```
sudo apt install curl
sudo apt install git
sudo apt install make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
```

### Install Pyenv to manage Python versions

```
curl https://pyenv.run | bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.profile
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.profile
echo 'eval "$(pyenv init -)"' >> ~/.profile
```

Restart the terminal after this step.

### Set the global Python version of the system

```
pyenv install 3.12.7
pyenv global 3.12.7
```

### Clone and run the app

```
git clone https://github.com/Adrian-Luerssen/MD002-AC1.git
cd MD002-AC1/
python main.py
```

To access the webserver go to `localhost:8080`.

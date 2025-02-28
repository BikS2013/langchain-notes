## wsl installation on windows
I'll guide you through installing WSL on Windows. Here's the step-by-step process:

1. **Easiest Method** - Using Windows PowerShell (Run as Administrator):
```powershell
wsl --install
```
This command:
- Enables required Windows features
- Downloads and installs Ubuntu by default
- Requires a system restart

2. **After Restart**:
- WSL will automatically start
- You'll need to create a UNIX username and password
- This doesn't have to match your Windows credentials

3. **Alternative Method** - Manual steps if the simple command doesn't work:

First, enable WSL:
```powershell
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
```

Then enable Virtual Machine Platform:
```powershell
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
```

4. **System Requirements**:
- Windows 10 version 2004 or higher (Build 19041 or higher)
- Windows 11

5. **To install a different Linux distribution**:
```powershell
# List available distributions
wsl --list --online

# Install a specific distribution
wsl --install -d <DistributionName>
# Example: wsl --install -d Debian
```

After installation, you can access WSL by:
- Opening Windows Terminal and clicking the dropdown for WSL
- Typing `wsl` in Command Prompt or PowerShell
- Searching for "Ubuntu" (or your chosen distro) in the Start menu

Let me know if you encounter any issues during the installation!


## install pyenv to manage multiple python distributions 

I'll help you install pyenv in WSL (Windows Subsystem for Linux). Here's the step-by-step process:

0. Check internet connectivity & DNS resolution
a) ping 8.8.8.8 to check internet connectivity
b) ping google.com to check DNS resolution
if either step a) or step b) is not succesful, do the following
sudo rm /etc/resolv.conf
sudo bash -c 'echo "nameserver 8.8.8.8" > /etc/resolv.conf'

1. Ιnstall the required dependencies:
```bash
sudo apt update
sudo apt install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev wget curl llvm libncursesw5-dev xz-utils \
tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev git
```

2. Clone the pyenv repository:
```bash
curl https://pyenv.run | bash
```

3. Add the following to your `~/.bashrc` (if using bash) or `~/.zshrc` (if using zsh):
a) First, let's find out which shell you're using
```bash
echo $SHELL
```
This will output something like /bin/bash or /bin/zsh
Based on your shell, you'll need to edit the correct configuration file:
For bash: ~/.bashrc
For zsh: ~/.zshrc
b) You can edit the file using any text editor like nano or vim. Let's use nano as it's simpler:
```bash
nano ~/.bashrc  # if using bash
# or
nano ~/.zshrc   # if using zsh
```
c) In the editor, scroll to the bottom and add these three lines:
```bash
export PYENV_ROOT="$HOME/.pyenv"
command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
```
d) Save the file:
If using nano: Press Ctrl + X, then Y to confirm, then Enter to save
If using vim: Press Esc, type :wq, then press Enter

4. Reload your shell configuration:
```bash
source ~/.bashrc  # or source ~/.zshrc if using zsh
```

5. Verify the installation:
```bash
pyenv --version
```

Now you can install Python versions using:
```bash
pyenv install 3.12.0  # or any version you want
pyenv install 3.13.0  # or any version you want
pyenv global 3.12.0   # to set it as default
```

If you encounter any issues during installation, make sure all dependencies are properly installed and that your WSL instance has been updated.

## install VS Code in wsl 

I'll help you install VS Code for WSL. There are two main approaches:

1. **Recommended Method** - Install VS Code on Windows and use the WSL extension:

```bash
# First, install VS Code on Windows from the official website
# Then, in your WSL terminal:
code .
```
This will automatically:
- Install VS Code Server in WSL
- Install the WSL extension
- Open VS Code with WSL integration

2. **Alternative Method** - Install VS Code directly in WSL:
```bash
# Add Microsoft's GPG key
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg
sudo sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
rm -f packages.microsoft.gpg

# Install VS Code
sudo apt install apt-transport-https
sudo apt update
sudo apt install code
```

I recommend the first method because:
- Better performance
- Seamless integration between Windows and WSL
- Shared extensions and settings
- Access to Windows clipboard
- Better system resource management

After installation, useful VS Code extensions for WSL development:
- Remote - WSL
- Remote Development
- WSL: Ubuntu (or your distro)

You can launch VS Code in your WSL project directory anytime by typing `code .` in the terminal.


## install poetry to manage multiple environments 
I'll help you install Poetry in WSL. Here's the recommended installation process:

1. Install using the official installer:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Add Poetry to your PATH by adding this line to your `~/.bashrc` (for bash) or `~/.zshrc` (for zsh):
a) First, let's find out which shell you're using
```bash
echo $SHELL
```
This will output something like /bin/bash or /bin/zsh
Based on your shell, you'll need to edit the correct configuration file:
For bash: ~/.bashrc
For zsh: ~/.zshrc
b) You can edit the file using any text editor like nano or vim. Let's use nano as it's simpler:
```bash
nano ~/.bashrc  # if using bash
# or
nano ~/.zshrc   # if using zsh
```
c) In the editor, scroll to the bottom and add the below line:
```bash
export PATH="/home/$USER/.local/bin:$PATH"
```
d) Save the file:
If using nano: Press Ctrl + X, then Y to confirm, then Enter to save
If using vim: Press Esc, type :wq, then press Enter

3. Reload your shell configuration:
```bash
source ~/.bashrc  # or source ~/.zshrc if using zsh
```

4. Verify the installation:
```bash
poetry --version
```

5. (Optional) Configure Poetry to create virtual environments in the project directory:
```bash
poetry config virtualenvs.in-project true
```

Common Poetry commands:
```bash
# Start a new project
poetry new my-project

# Initialize poetry in existing project
poetry init

# Add dependencies
poetry add requests

# Add dev dependencies
poetry add pytest --group dev

# Install dependencies
poetry install

# Activate the virtual environment (for Poetry 1.x versions)
poetry shell

# For Poetry 2.0.0+ (alternative method)
# Use this command to activate the environment in the current shell session
eval $(poetry env activate)
```

Let me know if you need help with any specific Poetry configurations or encounter any issues!

## run my first python program via Poetry in WSL
I'll help you run your first python program via Poetry in WSL. Here's the recommended steps:

1. **Create a directory for your projects:**
```bash
cd ~
mkdir -p ~/projects
cd ~/projects
```

2. **Create a new project within the projects directory:**
```bash
poetry new helloworld-project
```

3. **Move to the newly created project directory:**
```bash
cd helloworld-project
```

4. **Verify the project structure:**
Use the `ls` command to see the files and folders created by Poetry:
```bash
ls -R
```
Output:
```
.:
helloworld_project  pyproject.toml  tests
./helloworld_project:
__init__.py
./tests:
__init__.py  test_helloworld_project.py
```

5. **Install dependencies:**
Since `poetry new` already initialized the project with a `pyproject.toml`, just run:
```bash
poetry install
```

6. **Create an empty main.py file within helloworld-project:**
```bash
touch helloworld_project/main.py
```
7. **Open main.py file:**
   1. Open file either in bash
```bash
nano helloworld_project/main.py
```
   2. Or Open file in VS Code
```bash
code .
```

8. **Write your "Hello, World!" Python program in `main.py` either in bash or VS Code:**
```python
def main():
    print("Hello, World!")
if __name__ == "__main__":
    main()
```

9.  **Save either in bash or VS Code**

10.  **Run your program via Poetry:**
```bash
poetry run python helloworld_project/main.py
```
Output:
```
Hello, World!
```

---

### **Quick Note: `poetry new` vs `poetry init`**

| Feature               | `poetry new`                         | `poetry init`                    |
|-----------------------|--------------------------------------|----------------------------------|
| **Purpose**           | Creates a full project structure and initializes Poetry in one step. | Only initializes Poetry (creates pyproject.toml) in an existing directory. |
| **Creates `pyproject.toml`** | ✅ Yes                           | ✅ Yes                           |
| **Creates folders and files** | ✅ Includes `tests/` and `__init__.py`. | ❌ Only creates `pyproject.toml`. |
| **Interactive prompts** | ❌ No                            | ✅ Asks about dependencies, Python version, etc. |

---

### **What `poetry init` Does**
When you run `poetry init`, it interactively configures your `pyproject.toml` file. Here are the prompts you’ll typically encounter:

a) **Package name** (e.g., `projects`): Enter the name of your project.  
b) **Version** (default is `[0.1.0]`): Specify the version of your project.  
c) **Author** (e.g., `None, n to skip`): Add an author name or skip by typing `n`.  
d) **License** (default is `[]`): Enter a license for your project.  
e) **Compatible Python versions** (e.g., `[>=3.12]`): Specify the Python versions your project supports.  
f) **Define main dependencies interactively?** (yes/no): Choose whether to add main dependencies during setup.  
g) **Package to add or search for** (leave blank to skip): Add specific dependencies or skip.  
h) **Define development dependencies interactively?** (yes/no): Choose whether to add dev dependencies during setup.  
i) **Package to add or search for** (leave blank to skip): Add specific dev dependencies or skip.  
j) **Confirm generation?** (yes/no): Confirm and generate the `pyproject.toml` file.

This is useful when initializing Poetry in an **existing directory** or customizing project setup interactively. Use **`poetry init`** instead of `poetry new` when you don’t need Poetry to create the folder structure for you.
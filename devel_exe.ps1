# Create a bin\git.exe that runs bin\git.py

pyinstaller --onefile bin\shim.py --name git --distpath bin --hidden-import git

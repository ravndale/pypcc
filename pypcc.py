
import subprocess
from pathlib import Path
from datetime import datetime
from print_color import print
import git
import os

class PyPawnCC:
	def err(self, message: str):
		print(f'{message}', tag='fatal', tag_color='red', color='purple', format='bold')
		exit(1)
	
	def info(self, tag_string: str, tag_string_color: str, message: str):
		print(f'{message}', tag=tag_string, tag_color=tag_string_color, color='white', format='bold')

	def __init__(self, filename: str, rootDirectory: Path, extraDirectory: Path, includeDirectory: Path, arguments: list, flags: list):
		self.filename = filename
		self.rootDirectory = rootDirectory
		self.includeDirectory = includeDirectory
		self.extraDirectory = extraDirectory
		self.arguments = list(arguments)
		self.flags = list(flags)

		if Path(rootDirectory).is_dir() == False or Path(rootDirectory).exists() == False:
			self.err(f'{rootDirectory} does not exist or is not a directory!')

		if Path(includeDirectory).is_dir() == False or Path(rootDirectory).exists() == False:
			self.err(f'{includeDirectory} does not exist or is not a directory!')

		if Path(extraDirectory).is_dir() == False or Path(extraDirectory).exists() == False:
			self.err(f'{extraDirectory} does not exist or is not a directory!')

		fileDirectory = Path(f'{rootDirectory}/gamemodes/{filename}')
		if fileDirectory.is_file() == False or fileDirectory.exists() == False:
			self.err(f'{filename} does not exist or is not a file!')

		try: 
			subprocess.call(["pawncc"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
		except FileNotFoundError: 
			self.err(f'pawncc not found in PATH.')

	def prepare(self):
		self.info('builder', 'green', 'Prepping build environment..')

		if str(self.flags).find("RELTYPE") != -1:
			releaseType = self.flags[0].split('=', 1)[1]
			self.info('reltype', 'purple', f'Defined release type: {releaseType}.')

			if releaseType == "devel":
					self.info('reltype', 'purple', 'Developer mode enabled!')
					developerMode = True
			else:
					developerMode = False

		else:
			print('No release type specified!')
			self.info('warning', 'orange', 'No release type specified')

		if str(self.flags).find("VCS_ENABLE") != -1:
			try: 
				subprocess.call(["git"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
			except FileNotFoundError: 
				self.err(f'Git not found in PATH.')
			else:
				self.info('vcs', 'green', 'Git found in PATH.')

			repo = git.Repo(self.rootDirectory, search_parent_directories=True)
			if repo.git_dir == False:
				self.err(f'Version Control System enabled but {self.rootDirectory} is not a Git repo!')
			else:
				self.info('vcs', 'green', f'Git repo found: {self.rootDirectory}')
				commitCount = len(list(repo.iter_commits()))
				commitHash = str(repo.head.commit)[:6]
				commitBranch = str(repo.active_branch)

			self.info('vcs', 'green', 'Version Control System enabled.')

			try:
				with open(f'{self.extraDirectory}/vcs.inc', 'w') as temp:
					temp.write(f'#define BUILD_TYPE 		"{releaseType}"\n')
					temp.write(f'#define BUILD_DATE 		"{datetime.now().strftime("%d.%m.%Y, %H:%M:%S")}"\n')
					temp.write(f'#define BUILD_AUTHOR 	"rvndale"\n')
					temp.write(f'#define BUILD_VERSION 	"{releaseType}/{commitHash}"\n')
					temp.write(f'#define BUILD_COMMIT 	"r{commitCount}"\n')
					temp.write(f'#define BUILD_BRANCH 	"{commitBranch}"\n')

					if developerMode == True:
						temp.write(f'new const bool: developerMode = true;\n')

					temp.write("// --- done by pypcc")
			except Exception as e:
					self.err(f'File {self.extraDirectory}/vcs.inc was not found or is not a writeable file!')
					exit(1)

		else:
			self.info('vcs', 'green', 'Version Control System disabled.')
		
	def run(self):
		subprocess.run(['pawncc', f'{self.filename}'] + self.arguments, cwd=self.rootDirectory)
    
build = PyPawnCC("main.pwn", "Tests", "Tests", "Tests", ["-Dgamemodes"], ["RELTYPE=devel", "VCS_ENABLE"])
build.prepare()
build.run()
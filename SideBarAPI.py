# coding=utf8
import sublime
import os
import re
import shutil

class Object():
	pass

class SideBarSelection:

	def __init__(self, paths = []):

		if not paths or len(paths) < 1:
			try:
				path = sublime.active_window().active_view().file_name()
				if self.isNone(path):
					paths = []
				else:
					paths = [path]
			except:
				paths = []
		self._paths = paths
		self._paths.sort()
		self._obtained_selection_information_basic = False
		self._obtained_selection_information_extended = False

	def len(self):
		return len(self._paths)

	def hasDirectories(self):
		self._obtainSelectionInformationBasic()
		return self._has_directories

	def hasFiles(self):
		self._obtainSelectionInformationBasic()
		return self._has_files

	def hasOnlyDirectories(self):
		self._obtainSelectionInformationBasic()
		return self._only_directories

	def hasOnlyFiles(self):
		self._obtainSelectionInformationBasic()
		return self._only_files

	def hasProjectDirectories(self):
		if self.hasDirectories():
			project_directories = SideBarProject().getDirectories()
			for item in self.getSelectedDirectories():
				if item.path() in project_directories:
					return True
			return False
		else:
			return False

	def hasItemsUnderProject(self):
		for item in self.getSelectedItems():
			if item.isUnderCurrentProject():
				return True
		return False

	def hasImages(self):
		return self.hasFilesWithExtension('gif|jpg|jpeg|png')

	def hasFilesWithExtension(self, extensions):
		extensions = re.compile('('+extensions+')$', re.I);
		for item in self.getSelectedFiles():
			if extensions.search(item.path()):
				return True;
		return False

	def getSelectedItems(self):
		self._obtainSelectionInformationExtended()
		return self._files + self._directories;

	def getSelectedItemsWithoutChildItems(self):
		self._obtainSelectionInformationExtended()
		items = []
		for item in self._items_without_containing_child_items:
			items.append(SideBarItem(item, os.path.isdir(item)))
		return items

	def getSelectedDirectories(self):
		self._obtainSelectionInformationExtended()
		return self._directories;

	def getSelectedFiles(self):
		self._obtainSelectionInformationExtended()
		return self._files;

	def getSelectedDirectoriesOrDirnames(self):
		self._obtainSelectionInformationExtended()
		return self._directories_or_dirnames;

	def getSelectedImages(self):
		return self.getSelectedFilesWithExtension('gif|jpg|jpeg|png')

	def getSelectedFilesWithExtension(self, extensions):
		items = []
		extensions = re.compile('('+extensions+')$', re.I);
		for item in self.getSelectedFiles():
			if extensions.search(item.path()):
				items.append(item)
		return items

	def _obtainSelectionInformationBasic(self):
		if not self._obtained_selection_information_basic:
			self._obtained_selection_information_basic = True

			self._has_directories = False
			self._has_files = False
			self._only_directories = False
			self._only_files = False

			for path in self._paths:
				if self._has_directories == False and os.path.isdir(path):
					self._has_directories = True
				if self._has_files == False and os.path.isdir(path) == False:
					self._has_files = True
				if self._has_files and self._has_directories:
					break

			if self._has_files and self._has_directories:
				self._only_directories = False
				self._only_files 	= False
			elif self._has_files:
				self._only_files 	= True
			elif self._has_directories:
				self._only_directories = True

	def _obtainSelectionInformationExtended(self):
		if not self._obtained_selection_information_extended:
			self._obtained_selection_information_extended = True

			self._directories = []
			self._files = []
			self._directories_or_dirnames = []
			self._items_without_containing_child_items = []

			_directories = []
			_files = []
			_directories_or_dirnames = []
			_items_without_containing_child_items = []

			for path in self._paths:
				if os.path.isdir(path):
					item = SideBarItem(path, True)
					if item.path() not in _directories:
						_directories.append(item.path())
						self._directories.append(item)
					if item.path() not in _directories_or_dirnames:
						_directories_or_dirnames.append(item.path())
						self._directories_or_dirnames.append(item)
					_items_without_containing_child_items = self._itemsWithoutContainingChildItems(_items_without_containing_child_items, item.path())
				else:
					item = SideBarItem(path, False)
					if item.path() not in _files:
						_files.append(item.path())
						self._files.append(item)
					_items_without_containing_child_items = self._itemsWithoutContainingChildItems(_items_without_containing_child_items, item.path())
					item = SideBarItem(os.path.dirname(path), True)
					if item.path() not in _directories_or_dirnames:
						_directories_or_dirnames.append(item.path())
						self._directories_or_dirnames.append(item)

			self._items_without_containing_child_items = _items_without_containing_child_items

	def _itemsWithoutContainingChildItems(self, items, item):
		new_list = []
		add = True
		for i in items:
			if i.find(item+'\\') == 0 or i.find(item+'/') == 0:
				continue
			else:
				new_list.append(i)
			if (item+'\\').find(i+'\\') == 0 or (item+'/').find(i+'/') == 0:
				add = False
		if add:
			new_list.append(item)
		return new_list

	def isNone(self, path):
		if path == None or path == '' or path == '.' or path == '..' or path == './' or path == '../' or path == '/' or path == '//' or path == '\\' or path == '\\\\' or path == '\\\\\\\\' or path == '\\\\?\\' or path == '\\\\?' or path == '\\\\\\\\?\\\\':
			return True
		else:
			return False

class SideBarProject:

	def getDirectories(self):
		return sublime.active_window().folders()

	def hasDirectories(self):
		return len(self.getDirectories()) > 0

	def hasOpenedProject(self):
		return self.getProjectFile() != None

	def getDirectoryFromPath(self, path):
		for directory in self.getDirectories():
			maybe_path = path.replace(directory, '', 1)
			if maybe_path != path:
				return directory

	def getProjectFile(self):
		return sublime.active_window().project_file_name()

	def getProjectJson(self):
		return sublime.active_window().project_data()

	def setProjectJson(self, data):
		return sublime.active_window().set_project_data(data)

	def excludeDirectory(self, path, exclude):
		data = self.getProjectJson()
		for folder in data['folders']:
			project_folder = folder['path']
			if project_folder == '.':
				project_folder = SideBarItem(self.getProjectFile(), False).dirname();
			if path.find(project_folder) == 0:
				try:
					folder['folder_exclude_patterns'].append(exclude)
				except:
					folder['folder_exclude_patterns'] = [exclude]
		self.setProjectJson(data);

	def excludeFile(self, path, exclude):
		data = self.getProjectJson()
		for folder in data['folders']:
			project_folder = folder['path']
			if project_folder == '.':
				project_folder = SideBarItem(self.getProjectFile(), False).dirname();
			if path.find(project_folder) == 0:
				try:
					folder['file_exclude_patterns'].append(exclude)
				except:
					folder['file_exclude_patterns'] = [exclude]
		self.setProjectJson(data);

	def add(self, path):
		data = self.getProjectJson()
		if data:
			data['folders'].append({'follow_symlinks':True, 'path':path});
		else:
			data = {'folders': [{'follow_symlinks': True, 'path':path}]}
		self.setProjectJson(data);

	def refresh(self):
		sublime.active_window().run_command('refresh_folder_list')

class SideBarItem:

	def __init__(self, path, is_directory):
		self._path = path
		self._is_directory = is_directory

	def path(self, path = ''):
		if path == '':
			return self._path
		else:
			self._path = path
			self._is_directory = os.path.isdir(path)
			return path

	def pathWithoutProject(self):
		path = self.path()
		for directory in SideBarProject().getDirectories():
			path = path.replace(directory, '', 1)
		return path.replace('\\', '/')

	def pathProject(self):
		path = self.path()
		for directory in SideBarProject().getDirectories():
			path2 = path.replace(directory, '', 1)
			if path2 != path:
				return directory
		return False

	def isUnderCurrentProject(self):
		path = self.path()
		path2 = self.path()
		for directory in SideBarProject().getDirectories():
			path2 = path2.replace(directory, '', 1)
		return path != path2

	def pathRelativeFromProject(self):
		return re.sub('^/+', '', self.pathWithoutProject())

	def pathRelativeFromProjectEncoded(self):
		import urllib.request, urllib.parse, urllib.error
		return urllib.parse.quote(self.pathRelativeFromProject())

	def pathRelativeFromView(self):
		return os.path.relpath(self.path(), os.path.dirname(sublime.active_window().active_view().file_name())).replace('\\', '/')

	def pathRelativeFromViewEncoded(self):
		import urllib.request, urllib.parse, urllib.error
		return urllib.parse.quote(os.path.relpath(self.path(), os.path.dirname(sublime.active_window().active_view().file_name())).replace('\\', '/'))

	def pathAbsoluteFromProject(self):
		return self.pathWithoutProject()

	def pathAbsoluteFromProjectEncoded(self):
		import urllib.request, urllib.parse, urllib.error
		return urllib.parse.quote(self.pathAbsoluteFromProject())

	def uri(self):
		uri = 'file:'+(self.path().replace('\\', '/').replace('//', '/'));
		return uri

	def join(self, name):
		return os.path.join(self.path(), name)

	def dirname(self):
		branch, leaf = os.path.split(self.path())
		return branch;

	def forCwdSystemPath(self):
		if self.isDirectory():
			return self.path()
		else:
			return self.dirname()

	def forCwdSystemName(self):
		if self.isDirectory():
			return '.'
		else:
			path = self.path()
			branch = self.dirname()
			leaf = path.replace(branch, '', 1).replace('\\', '').replace('/', '')
			return leaf

	def forCwdSystemPathRelativeFrom(self, relativeFrom):
		relative = SideBarItem(relativeFrom, os.path.isdir(relativeFrom))
		path = self.path().replace(relative.path(), '', 1).replace('\\', '/')
		if path == '':
			return '.'
		else:
			return re.sub('^/+', '', path)

	def forCwdSystemPathRelativeFromRecursive(self, relativeFrom):
		relative = SideBarItem(relativeFrom, os.path.isdir(relativeFrom))
		path = self.path().replace(relative.path(), '', 1).replace('\\', '/')
		if path == '':
			return '.'
		else:
			if self.isDirectory():
				return re.sub('^/+', '', path)+'/'
			else:
				return re.sub('^/+', '', path)

	def dirnameCreate(self):
		try:
			self._makedirs(self.dirname())
		except:
			pass

	def name(self):
		branch, leaf = os.path.split(self.path())
		return leaf;

	def open(self):
		if sublime.platform() == 'osx':
			import subprocess
			subprocess.Popen(['open', self.name()], cwd=self.dirname())
		elif sublime.platform() == 'windows':
			import subprocess
			subprocess.Popen(['start',  '', escapeCMDWindows(self.path())], cwd=self.dirname(), shell=True)
		else:
			from . import desktop
			desktop.open(self.path())
			print('using desktop')

	def isDirectory(self):
		return self._is_directory

	def isFile(self):
		return self.isDirectory() == False

	def extension(self):
		try:
			return re.compile('(\.[^\.]+(\.[^\.]{2,4})?)$').findall('name'+self.name())[0][0].lower()
		except:
			return os.path.splitext('name'+self.name())[1].lower()

	def exists(self):
		return os.path.isdir(self.path()) or os.path.isfile(self.path())

	def overwrite(self):
		overwrite = sublime.message_dialog("Destination exists")
		return False

	def _makedirs(self, path):
		if 3000 <= int(sublime.version()) < 3088:
			# Fixes as best as possible a new directory permissions issue
			# See https://github.com/titoBouzout/SideBarEnhancements/issues/203
			# See https://github.com/SublimeTextIssues/Core/issues/239
			oldmask = os.umask(0o000)
			if oldmask == 0:
				os.makedirs(path, 0o755);
			else:
				os.makedirs(path);
			os.umask(oldmask)
		else:
			os.makedirs(path)

	def copy(self, location, replace = False):
		location = SideBarItem(location, os.path.isdir(location));
		if location.exists() and replace == False:
			return False
		elif location.exists() and location.isFile():
			os.remove(location.path())

		location.dirnameCreate();
		if self.isDirectory():
			if location.exists():
				self.copyRecursive(self.path(), location.path())
			else:
				shutil.copytree(self.path(), location.path())
		else:
			shutil.copy2(self.path(), location.path())
		return True

	def copyRecursive(self, _from, _to):

		if os.path.isfile(_from) or os.path.islink(_from):
			try:
				self._makedirs(os.path.dirname(_to));
			except:
				pass
			if os.path.exists(_to):
				os.remove(_to)
			shutil.copy2(_from, _to)
		else:
			try:
				self._makedirs(_to);
			except:
				pass
			for content in os.listdir(_from):
				__from = os.path.join(_from, content)
				__to = os.path.join(_to, content)
				self.copyRecursive(__from, __to)

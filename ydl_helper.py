#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import re
import glob
import json
import subprocess
import sys

class YdlPlaylistHelper(object):
	def __init__(self, setting_provider, file_system_provider,
	subprocess_caller, system_provider):
		self.setting_provider = setting_provider
		self.file_system_provider = file_system_provider
		self.subprocess_caller = subprocess_caller
		self.system_provider = system_provider
		
	def download_all_playlists(self):
		settings = self.setting_provider.get_download_settings()
		for setting in settings["download_playlists"]:
			try:
				self.__parse_setting(setting)
				before = self.__count_current_files()
				self.__download_one_playlist(setting)
				after = self.__count_current_files()
				self.__update_start_position(setting, after - before)
			except KeyError as e:
				print(e, 'is not set.')
		self.setting_provider.save_download_settings(settings)
		
	def __parse_setting(self, setting):
		self.__url = setting["url"]
		self.__start_from = setting["--playlist-start"]
		self.__name_pettern = setting["file_name_pettern"]

		self.__any_option_dict = {}
		for key in setting.keys():
			if(self.__is_optional_setting(key)):
				self.__any_option_dict[key] = setting[key]
				
	def __is_optional_setting(self, key):
		if(key=="url" or key=="--playlist-start" or key=="file_name_pettern" or key=="comment"):
			return False
		else:
			return True
				
	def __download_one_playlist(self, setting):
		args = self.__generate_subprocess_args(setting)
		self.subprocess_caller.call(args)
		
	def __generate_subprocess_args(self, setting):
		if self.system_provider.get_platform() == 'win32':
			args = ['youtube-dl.exe']
		else:
			args = ['youtube-dl']
		args.extend(['--playlist-start', str(self.__start_from)])
		for k,v in self.__any_option_dict.iteritems():
			if v != "":
				args.extend([k,v])
			else:
				args.append(k)
		args.append(self.__url)
		return args;
		
	def __count_current_files(self):
		count = 0
		file_paths = self.file_system_provider.get_filenames_pettern_matched(self.__name_pettern)
		for file_path in file_paths:
			match = re.search(r"\.part$", file_path)
			if match is None:
				count += 1
		return count
		
	def __update_start_position(self, setting, added):
		old = int(setting["--playlist-start"])
		setting["--playlist-start"] = old + added

class SettingProvider(object):
	def get_download_settings(self):
		with codecs.open('ydl_helper_list.json', 'r', 'utf-8') as f:
			setting_dict = json.load(f)
		return setting_dict
		
	def save_download_settings(self, settings):
		with codecs.open('ydl_helper_list.json', 'w', 'utf-8') as f:
			json.dump(settings, f, ensure_ascii=False, indent=4)
			
class FileSystemProvider(object):
	def get_filenames_pettern_matched(self, pettern):
		return glob.glob(pettern);
		
class SubProcessCaller(object):
	def call(self, args):
		subprocess.call(args, shell=True)

class SystemProvider(object):
	def get_platform(self):
		return sys.platform

if __name__ == '__main__':
	helper = YdlPlaylistHelper(SettingProvider(), FileSystemProvider(), SubProcessCaller(), SystemProvider())
	helper.download_all_playlists()
	

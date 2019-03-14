# -*- coding: utf-8 -*-

import sys
import os, os.path
import subprocess
import math
import requests
from multiprocessing.dummy import Pool as ThreadPool

def fetch(url):
	filename = "{}/{}".format(sys.argv[2], url.split('/').pop())
	if os.path.exists(filename):
		return filename

	print(url)
	r = requests.get(url)
	if r.status_code == requests.codes.OK:
		with open(filename, "wb") as f:
			f.write(r.content)
			f.close()
			# files.append(filename)
			print(filename)
			return filename
	else:
		print("failed!!!")
		return False

def marge(files):
	count = len(files)
	if count > 100:
		group = math.ceil(count / 100)
		b = 0
		ts = []
		while b < group:
			t = "{}/tmp-{}.mp4".format(sys.argv[2], b + 1)
			cmd = ['ffmpeg', '-i', "concat:{}".format("|".join(files[(b * 100):min((b + 1) * 100, count)])), '-c:a', 'copy', '-c:v', 'copy', t]
			print(' '.join(cmd))
			subprocess.call(cmd, shell=False)
			ts.append("file tmp-{}.mp4".format(b + 1))
			b = b + 1
		file = "{}/concat.txt".format(sys.argv[2])
		with open(file, "w") as f:
			f.write("\n".join(ts))
			f.close()
			cmd = ['ffmpeg', '-f', 'concat', '-i', file, '-c:a', 'copy', '-c:v', 'copy', "{}.mp4".format(sys.argv[2])]
			print(" ".join(cmd))
			subprocess.call(cmd, shell=False)
	else:
		cmd = ['ffmpeg', '-i', "concat:{}".format("|".join(files)), '-c:a', 'copy', '-c:v', 'copy', "{}.mp4".format(sys.argv[2])]
		print(" ".join(cmd))
		subprocess.call(cmd, shell=False)

if __name__ == '__main__':
	if len(sys.argv) < 3:
		print("usage: python3 m3u8.py <?.m3u8> <output-dir>")
		sys.exit(0)

	if not os.path.exists(sys.argv[2]):
		os.mkdir(sys.argv[2])

	with open(sys.argv[1], "r") as file:
		lines = list(filter(lambda line: line[0] != '#', [line.strip() for line in file.read().strip().split("\n")]))
		file.close()

		pool = ThreadPool(10)
		files = pool.map(fetch, lines)
		pool.close()
		pool.join()

		if 0 == len(list(filter(lambda r: r == False, files))):
			marge(files)
		else:
			print("same files download fail, please try again!")

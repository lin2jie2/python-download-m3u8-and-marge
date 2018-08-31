# -*- coding: utf-8 -*-

import sys
import os, os.path
import subprocess
import math
import requests

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print("usage: python3 m3u8.py <?.m3u8> <output-dir>")
		sys.exit(0)
	else:
		if not os.path.exists(sys.argv[2]):
			os.mkdir(sys.argv[2])

		files = []
		done = True
		with open(sys.argv[1], "r") as file:
			while True:
				line = file.readline().strip()
				if line == '':
					break
				elif line[0:1] != '#':
					filename = "{}/{}".format(sys.argv[2], line.split('/').pop())
					if os.path.exists(filename):
						files.append(filename)
					else:
						print(line)
						r = requests.get(line)
						if r.status_code == requests.codes.OK:
							with open("{}/{}".format(sys.argv[2], line.split('/').pop()), "wb") as f:
								f.write(r.content)
								f.close()
								files.append(filename)
								print(filename)
						else:
							print("fail!!!")
							done = False
			file.close()
			if done:
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
			else:
				print("same files download fail, please try again!")

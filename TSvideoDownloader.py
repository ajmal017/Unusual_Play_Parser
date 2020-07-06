import requests

# Downloaded a complete "live seminar" as it was going "live".
fileCount_MIN = 1
fileCount_MAX = 833
file_url_base = "https://cdn.joinnow.live/d152cd43-dbc0-4ca5-aee5-f278a3f06a3d/hls-1080p"

# Ts files were in format 00001.ts --> 00833.ts
for i in range(fileCount_MIN, fileCount_MAX + 1):
	file_url_file = "{:05d}.ts".format(i)

	r = requests.get(file_url_base + file_url_file, stream = True)

	with open(file_url_file,"wb") as ts:
		for chunk in r.iter_content(chunk_size=1024):

			# writing one chunk at a time to ts file
			if chunk:
				ts.write(chunk)

	print("Piece #", "{:03d}".format(i), "of", fileCount_MAX, "is complete.")

if i == 833:
	print("ALL PIECES COLLECTED!!!")
else:
	print("Error, pieces collected: ", i)
import requests

# Gets my github logo
image_url = "https://avatars2.githubusercontent.com/u/6798460?s=460&v=4"
r = requests.get(image_url)

# Saving received content as a png file in binary format
with open("../Misc/python_logo.png", 'wb') as f:
	# write the contents of the response (r.content) to a new file in binary mode.
	f.write(r.content)

print("Small Download Complete.")
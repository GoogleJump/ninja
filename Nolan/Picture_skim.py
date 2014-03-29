import urllib2

def download_image(website):
	website = str(website)
	opener1 = urllib2.build_opener()
	page1 = opener1.open(website)
	picture = page1.read()
	filename = "my_image2"
	print filename
	fout = open(filename, "wb")
	fout.write(picture)
	fout.close()

download_image("http://img1.wikia.nocookie.net/__cb20090819164333/sonic/images/d/df/Sonic_126.png")

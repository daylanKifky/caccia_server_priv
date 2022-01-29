import random
import string
import csv
import hashlib

import requests

from itertools import tee
import urllib.request
from urllib.parse import urlparse, urljoin
from os.path import basename, splitext, join, dirname, realpath, isfile
from os import remove
from math import floor
import re

from time import time, sleep
import imghdr 

from flask import current_app, flash


def random_string(length):
	posible_chars = string.ascii_letters + string.digits
	return ''.join(random.SystemRandom().choice(posible_chars) for _ in range(length))

def random_pass():
	length = 30
	posible_chars = string.ascii_letters + string.digits + '#$%^&*_!=+'
	return ''.join(random.SystemRandom().choice(posible_chars) for _ in range(length))

def get_error_id():
	return random_string(6).upper()


class Download_Image_Error(Exception):
	"""To be raised when an image could not being downladed"""

class Payload_Malformed(Exception):
	"""To be raised when receiving a bad CSV"""

# def download_image(url, path='static/content'):
# 	file_path = join(dirname(realpath(__file__)), path)

# 	# -----------  Image probably on disk  -----------
	
# 	url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
# 	if not re.match(url_pattern, url):
# 		current_app.logger.debug("Check image in disk: %s", url)
# 		save_image_as = join(file_path, url)
# 		if isfile(save_image_as):
# 			current_app.logger.debug("Image already present in disk, skipping: %s", url)
# 			return join(path, url)
# 		else:
# 			raise Download_Image_Error("The image {} was not found on the server, pass a complete URL to download it from a remote location".format(url))


# 	# -----------  Image comes from an external url  -----------

# 	u_parsed = urlparse(url)
# 	img_name = basename(u_parsed.path)
# 	ext = splitext(img_name)

# 	md5_hash = hashlib.md5()

# 	if ext[1] not in current_app.config['ALLOWED_IMGS_EXT']:
# 		raise Download_Image_Error("The image {} has an invalid extension, allowed: {}".format(img_name, current_app.config['ALLOWED_IMGS_EXT']))

# 	current_app.logger.debug("Requesting image %s", url)

# 	with requests.get(url, stream=True, timeout=1) as r:
# 		if not r:
# 			raise Download_Image_Error("Timeout while downloading image {}. Check the image exists at the location {}".format(img_name, url))

# 		if 'Content-length' not in r.headers:
# 			raise Download_Image_Error("The image image {} is missing a 'Content-length' header")

# 		if int(r.headers['Content-length']) > current_app.config['MAX_IMG_SIZE']:
# 			raise Download_Image_Error("The image image {} is too big, max allowed {}kb".format(img_name, current_app.config['MAX_IMG_SIZE']/1024))

# 		current_app.logger.debug("Downloaded image %s, response: %s", url, r)

# 		#duplicate iterator for later use
# 		hash_iter, file_iter = tee(r.iter_content(chunk_size=1024)) 

# 		for chunk in hash_iter:
# 			if chunk:
# 				md5_hash.update(chunk)
		
# 		# save_image_name = "{:.0f}_{}_{}".format(time(), random_string(8), img_name)
# 		save_image_name = "{}{}".format(md5_hash.hexdigest(), ext[1])
# 		save_image_as = join(file_path, save_image_name)
			
# 		if not isfile(save_image_as): #save the image only if it doesnt exists
# 			with open(save_image_as, "wb") as f:
# 				for chunk in file_iter:
# 					if chunk:
# 						f.write(chunk)

# 			img_type = imghdr.what(save_image_as)
# 			current_app.logger.debug("Saved image %s, type: %s", save_image_as, img_type)

# 			if img_type not in current_app.config['ALLOWED_IMGS_TYPES']:
# 				remove(save_image_as)
# 				current_app.logger.debug("Removed image %s, type: %s", save_image_as, img_type)
# 				raise Download_Image_Error("The image {} has an invalid type, allowed: {}".format(img_name, current_app.config['ALLOWED_IMGS_TYPES']))
# 		else:
# 			current_app.logger.debug("Image present in disk, skipping saving %s", save_image_as)

# 	return join(path, save_image_name)


def save_image(file, path='static/content'):
	ext = splitext(file.filename)

	if ext[1] not in current_app.config['ALLOWED_IMGS_EXT']:
		raise Download_Image_Error("The image {} has an invalid extension, allowed: {}".format(file.filename, current_app.config['ALLOWED_IMGS_EXT']))

	data = file.stream.read()
	md5_hash = hashlib.md5()
	md5_hash.update(data)
	save_image_name = "{}{}".format(md5_hash.hexdigest(), ext[1])
	save_image_path = join(path, save_image_name)

	file_path = join(dirname(realpath(__file__)), path)
	save_image_as = join(file_path, save_image_name)

	if not isfile(save_image_as): #save the image only if it doesnt exists
		with open(save_image_as, "wb") as f:
			f.write(data)

	img_type = imghdr.what(save_image_as)
	current_app.logger.debug("Saved image %s, type: %s", save_image_as, img_type)

	if img_type not in current_app.config['ALLOWED_IMGS_TYPES']:
		remove(save_image_as)
		current_app.logger.debug("Removed image %s, type: %s", save_image_as, img_type)
		raise Download_Image_Error("The image {} has an invalid type, allowed: {}".format(file.filename, current_app.config['ALLOWED_IMGS_TYPES']))

	return save_image_name, save_image_path



def parse_csv(content, required_keys):
		cvslines = content.split("\n")

		reader = csv.DictReader(cvslines, delimiter=',')

		if not required_keys.issubset(set(reader.fieldnames)):
			raise Payload_Malformed("The received CSV is not compatible with this endpoint, expecting keys:\n{}\nReceived keys:\n{}".format(list(required_keys), reader.fieldnames))

		if len(cvslines) > current_app.config["MAX_CSV_LINES"]:
			raise Payload_Malformed("The received CSV has too much entries ({}), max: {}".format(len(cvslines), current_app.config["MAX_CSV_LINES"]))

		return reader
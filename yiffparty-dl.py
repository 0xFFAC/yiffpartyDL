import requests
import os
import datetime
import shutil
import argparse
import sys
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser(description="Yiff.Party downloader.")
parser.add_argument("ids", help="yiff.party ID")
args = parser.parse_args(sys.argv[1:])
yiff_id = args.ids

def get_patreon_name(id=yiff_id):
	yiffparty_url = "https://yiff.party/patreon/" + id
	yiffparty_url_r = requests.get(yiffparty_url)
	yiffparty_soup = BeautifulSoup(yiffparty_url_r.text, 'html.parser')
	yiffparty_name = yiffparty_soup.find('span', {'class': 'yp-info-name'},'small').contents[1].text[1:-1]
	return yiffparty_name

def get_data(id=yiff_id):
	base_url = 'https://yiff.party/'
	url = base_url + id + '.json'
	all_data = requests.get(url)
	return all_data.json()

search = get_data()

def get_post_data():
	filelist = []
	for i in search["posts"]:
		date = str(i["created"])
		try:
			filelist.append({
				"id": i["id"],
				"file_name": os.path.basename(i["post_file"]["file_url"]),
				"epoch": int(date),
				"date": str(datetime.datetime.fromtimestamp(float(date)).strftime('%Y-%m-%d %H:%M:%S')),
				"url": i["post_file"]["file_url"]
				})
		except:
			pass
		for location in i["attachments"]:
			filelist.append({
				"id": location["id"],
				"file_name": os.path.basename(location["file_url"]),
				"epoch": int(date),
				"date": str(datetime.datetime.fromtimestamp(float(date)).strftime('%Y-%m-%d %H:%M:%S')),
				"url": location["file_url"]
				})
	for i in search["shared_files"]:
		date = str(i["uploaded"])
		try:
			filelist.append({
				"id": i["id"],
				"file_name": i["file_name"],
				"epoch": int(date),
				"date": str(datetime.datetime.fromtimestamp(float(date)).strftime('%Y-%m-%d %H:%M:%S')),
				"url": i["file_url"]
				})
		except:
			pass
	return filelist	

all_posts = get_post_data()
patreon_name = get_patreon_name() + '-' + yiff_id

def download_files():
	current_path = os.getcwd()
	for post in all_posts:
		try:
			file_r = requests.get(post["url"], stream=True)
			output_name = post["date"] + " " + post["file_name"]
			output_dir = os.path.join(current_path, patreon_name)
			output_location = os.path.join(output_dir, output_name)
			if os.path.exists(output_location) is False:
				try:
					os.mkdir(output_dir)
				except FileExistsError:
					pass
				print("Downloading {}".format(output_name))
				with open(output_location, "wb") as output_file:
					shutil.copyfileobj(file_r.raw, output_file)
				del file_r
				os.utime(output_location, (post["epoch"], post["epoch"]))
			else:
				print("{} already exits, skipped".format(output_name))
				pass
		except:
			print("Unable to download file.")
			pass
			
print("Downloading posts by {}.".format(patreon_name))
download_files()
print("Downloads finished!")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import urllib.request
from jinja2 import Template
import os
import shutil
from config import config
import sys
from datetime import datetime
import re


HOME_DIR = config.get('home_dir', 'path')
os.mkdir(HOME_DIR + 'temp_tables/')
TEMP_DIR = HOME_DIR + 'temp_tables/'

tournament_stats_url = "https://lfl.ru/?ajax=1&method=tournament_stats_table&tournament_id=0&club_id=2356&season_id=43"
tournament_calendar_url= "https://lfl.ru/?ajax=1&method=tournament_calendar_table&tournament_id=0&club_id=2356&season_id=43"
players_stats_url = "https://lfl.ru/?ajax=1&method=tournament_squads_table&tournament_id=13682&club_id=2356&season_id=43"
disqualifications_url= "https://lfl.ru/?ajax=1&mode=new_format&method=tournament_disqualifications_table&tournament_id=0&club_id=2356&season_id=43"
games_results_url = "https://lfl.ru/?ajax=1&method=tournament_resault_table&tournament_id=0&club_id=2356&season_id=43"
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'

up = ['pos_1', 'pos_2']
up2 = ['pos_3', 'pos_4']
down = ['pos_15', 'pos_16', 'pos_17', 'pos_18']
down2 = ['pos_19', 'pos_20']

payload  = {}
headers = {}


def catch_exception(func):
	def wrapper(*args):
		try:
			return func(*args)
		except:
			print('Something went wrong!' + '	' +  str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
			#shutil.rmtree(HOME_DIR + 'temp_tables')
			#sys.exit()
	return wrapper


@catch_exception
def get_table(file, url):
	with open(file, 'w') as f:
		stats_table = requests.request("GET", url, headers=headers, data = payload, timeout=60)
		f.write(stats_table.text)


get_table(TEMP_DIR + 'tournament_table', tournament_stats_url)
get_table(TEMP_DIR + 'calendar_table', tournament_calendar_url)
get_table(TEMP_DIR + 'players_table', players_stats_url)
get_table(TEMP_DIR + 'games_results_table', games_results_url)
get_table(TEMP_DIR + 'disqual_table', disqualifications_url)


#generate tournament table
@catch_exception
def tournament_table():
	with open(TEMP_DIR + 'tournament_table') as table:
		soup = BeautifulSoup(table, 'lxml')
		table = soup.find('tbody')
		team_list = ''


	def team_stat():
		return """<td class="col text-center">%s</td>
				<td class="col-3 team text-left">%s</td>
				<td class="col text-center">%s</td>
				<td class="col text-center">%s</td>
				<td class="col text-center">%s</td>
				<td class="col text-center">%s</td>
				<td class="col d-sm-none d-md-block d-none text-center">%s</td>
				<td class="col d-sm-none d-md-block d-none text-center">%s</td>
				<td class="col d-sm-none d-md-block d-none text-center">%s</td>
				<td class="col text-center">%s</td>
			""" %(place, team, games, wins, draws, losses, goals_for, goals_against, goal_diff, points)
	pos = 1
	tr = table.find_all('tr')
	for i in tr:
		place = i.find_all('td')[0].get_text()
		team = i.find_all('td')[2].get_text()
		games = i.find_all('td')[3].get_text()
		wins = i.find_all('td')[4].get_text()
		draws = i.find_all('td')[5].get_text()
		losses = i.find_all('td')[6].get_text()
		goals_for = i.find_all('td')[7].get_text()
		goals_against = i.find_all('td')[8].get_text()
		goal_diff = i.find_all('td')[9].get_text()
		points = i.find_all('td')[10].get_text()
		position = 'pos_' + str(pos)
		if position in up:
			position = position + ' table-success'
		elif position in up2:
			position = position + ' table-warning'
		elif position in down:
			position = position + ' table-danger'
		elif position in down2: 
			position = position + ' bg-danger'
		else:
			position = position + 'row table-light'
		pos += 1
		team_list += """<tr class="row %s">%s</tr>""" %(position, team_stat())
	return team_list


@catch_exception
def parse_schedule_for_bot():
	with open(TEMP_DIR + 'calendar_table') as table:
		with open(HOME_DIR + "schedule.txt", "w") as schedule:
			soup = BeautifulSoup(table, 'lxml')
			table = soup.find('tbody')
			tr = table.find_all('tr')
			for i in tr:
				if len(i.find_all('td')[1].get_text()) > 1:
					teams = i.find_all('td')[3].get_text().strip() + ' - ' + i.find_all('td')[5].get_text().strip()
					date = (i.find_all('td')[1].get_text().split(' ')[0] + ' ' + i.find_all('td')[2].get_text()).strip()
					place = "Стадион " + i.find_all('td')[7].get_text()
					game = teams + '\t' + date + '\t' + place + '\n'
					schedule.write(game)


parse_schedule_for_bot()

#generate calendar
@catch_exception
def calendar_table():
	with open(TEMP_DIR + 'calendar_table') as table:
		soup = BeautifulSoup(table, 'lxml')
		if soup.find('tbody'):
			table = soup.find('tbody')
			a = table.find_all('a')
			for i in a:
				i['class'] = 'text-body'
				i['target'] = '_blank'

			td = table.find_all('td')
			for i in td:
				i['class'] = 'align-middle'
				del i['style']
				del i['width']

			tr = table.find_all('tr')
			tour_list = ''


			def tour_list_desktop():
				return """<th class="col-2 d-sm-none d-md-block d-none">%s</th>
							<td class="col-3 d-sm-none d-md-block d-none text-right">%s<img class="club-logo" src="%s"></td>
							<td class="col-3 d-sm-none d-md-block d-none"><img class="club-logo" src="%s">%s</td>
							<td class="col-4 d-sm-none d-md-block d-none"><span class="place">%s</span></td>
						""" %(tour, host, path_to_host_img, path_to_guest_img, guest, date)


			def tour_list_tablet():
				return """<td class="col-2 d-none d-sm-block d-md-none text-center"><img class="club-logo-big" src="%s"></td>
							<td class="col-8 d-none d-sm-block d-md-none text-center">
							<span class="badge badge-success">Тур %s</span><br>
							<b>%s – %s</b><br>
							<span class="place">%s</span></td>
							<td class="col-2 d-none d-sm-block d-md-none text-center"><img class="club-logo-big" src="%s"><br></td>
						""" %(path_to_host_img, tour, host, guest, date, path_to_guest_img)


			def tour_list_mobile():
				return """<td class="col-12 d-block d-sm-none text-center">
							<span class="badge badge-success">Тур %s</span><br>
							<img class="club-logo-small" src="%s"><b>%s – %s</b><img class="club-logo-small" src="%s"><br>
							<span class="place">%s</span></td>
						"""%(tour, path_to_host_img, host, guest, path_to_guest_img, date)

			for i in tr:
				if i.find_all('td')[1].get_text() != '-':
					find_all_img = i.find_all('img')
					tour = i.find_all('td')[0].get_text()
					host = i.find_all('td')[3].get_text()
					host_img = i.find_all('img')[0]['src']
					guest = i.find_all('td')[5].get_text()
					guest_img = i.find_all('img')[1]['src']
					if len(i.find_all('td')[1].get_text()) > 1:
						date = (i.find_all('td')[1].get_text() + ' ' + i.find_all('td')[7].get_text() + ', ' + i.find_all('td')[2].get_text()) 
					else:
						date = '-'
					host_filename = host_img.split("/")[-1]
					guest_filename = guest_img.split("/")[-1]
					path_to_host_img = '/images/' + host_filename
					path_to_guest_img = '/images/' + guest_filename
					outpath = os.path.join(HOME_DIR + 'images/', host_filename)
					outpath2 = os.path.join(HOME_DIR + 'images/', guest_filename)
					tour_list += """<tr class="row">%s%s%s</tr>"""%(tour_list_desktop(), tour_list_tablet(), tour_list_mobile())
					if os.path.exists(outpath) and os.path.exists(outpath2):
						pass
					else:
						opener = urllib.request.build_opener()
						opener.addheaders = [('User-Agent', user_agent)]
						urllib.request.install_opener(opener)
						urllib.request.urlretrieve(host_img, outpath)
						urllib.request.urlretrieve(guest_img, outpath2)
				else:
					return tour_list
			return tour_list


#generate players table
@catch_exception
def players_table():
	with open(TEMP_DIR + 'players_table') as table:
		soup = BeautifulSoup(table, 'lxml')
		if soup.find('tbody'):
			table = soup.find('tbody')

			tr = table.find_all('tr')
			for i in tr:
				td = i.find_all('td')
				i['class'] = 'table-light'
				del i['data-division-id']
				del i['data-tournament-id']


			tour_header = table.find_all(attrs={"class":"tour-header"})
			for i in tour_header:
				i['class'] = 'amplua text-center font-weight-bold'

			players = table.find_all(attrs={"class":"player"})		
			for i in players:
				i['href'] = 'https://lfl.ru' + i['href']
				i['class'] = 'text-body'
				i['target'] = '_blank'

			images = table.find_all(attrs={"class":"usr-image_link"})
			for img in images:
				img['href'] = 'https://lfl.ru' + img['href']
				img['target'] = '_blank'
				style = img['style']
				image = re.search("http.*[)]", style)
				image_url = style[image.start():image.end()-1]
				image_name = image_url.split("/")[-1]
				img['style'] = 'background: url(images/%s) no-repeat center center' %image_name
				img['class'] = (img['class'] + ['pr-1'])
				outpath = os.path.join(HOME_DIR + 'images/', image_name)
				if os.path.exists(outpath):
					pass
				else:
					opener = urllib.request.build_opener()
					opener.addheaders = [('User-Agent', user_agent)]
					urllib.request.install_opener(opener)
					urllib.request.urlretrieve(image_url, outpath)

			td = table.find_all('td')
			for i in td:
				if not i.has_attr('class'):
					i['class'] = 'text-center align-middle'
				span = i.find_all('span')
				for s in span:
					s.extract()	
			return table
		else:
			table = soup.find_all('div')
			table[0]['class'] == ['empty-list']
			tour_list = """<tr class="row"> </tr>"""
			return tour_list


#generate disqual table
@catch_exception
def disqual_table():
	with open(TEMP_DIR + 'disqual_table') as table:
		soup = BeautifulSoup(table, 'lxml')
		if soup.find('tbody'):
			table = soup.find('tbody')
			tr = table.find_all('tr')
			tour_list = ''

			def players_list():
				return """<td class="col text-center">%s</td>
						<td class="col text-center">%s</td>
						<td class="col text-center">%s</td>
						<td class="col text-center">%s</td>
					"""%(player, skips_from, time, missed)

			for i in tr:
				player = i.find_all('td')[1].get_text()
				skips_from = i.find_all('td')[2].get_text()
				time = i.find_all('td')[3].get_text()
				missed = i.find_all('td')[4].get_text()
				tour_list = """<tr class="row">%s</tr>"""%(players_list())
			return tour_list
		else:
			table = soup.find_all('div')
			table[0]['class'] == ['empty-list']
			tour_list = """<tr class="row"> </tr>"""
			return tour_list


#generate games results table
@catch_exception
def games_results_table():
	with open(TEMP_DIR + 'games_results_table') as table:
		soup = BeautifulSoup(table, 'lxml')
		if soup.find('tbody'):
			table = soup.find('tbody')
			tr = table.find_all('tr')
			tour_list = ''


			def tour_list_desktop():
				return """<th class="col-1 d-sm-none d-md-block d-none">%s</th>
							<td class="col-3 d-sm-none d-md-block d-none text-right">%s<img class="club-logo" src="%s"></td>
							<td class="col-1 d-sm-none d-md-block d-none text-center"><span class="result">%s</span></td>
							<td class="col-3 d-sm-none d-md-block d-none"><img class="club-logo" src="%s">%s</td>
							<td class="col-4 d-sm-none d-md-block d-none"><span class="place">%s</span></td>
						""" %(tour, host, path_to_host_img, result, path_to_guest_img, guest, date)


			def tour_list_tablet():
				return """<td class="col-2 d-none d-sm-block d-md-none text-center"><img class="club-logo-big" src="%s"></td>
							<td class="col-8 d-none d-sm-block d-md-none text-center">
							<span class="badge badge-success">Тур %s</span><br>
							<b>%s %s %s</b><br>
							<span class="place">%s</span></td>
							<td class="col-2 d-none d-sm-block d-md-none text-center"><img class="club-logo-big" src="%s"><br></td>
						""" %(path_to_host_img, tour, host, result, guest, date, path_to_guest_img)


			def tour_list_mobile():
				return """<td class="col-12 d-block d-sm-none text-center">
							<span class="badge badge-success">Тур %s</span><br>
							<img class="club-logo-small" src="%s"><b>%s %s %s</b><img class="club-logo-small" src="%s"><br>
							<span class="place">%s</span></td>
						"""%(tour, path_to_host_img, host, result, guest, path_to_guest_img, date)


			for i in tr:
				find_all_img = i.find_all('img')
				tour = i.find_all('td')[0].get_text()
				date = (i.find_all('td')[1].get_text() + ' ' + i.find_all('td')[7].get_text() + ', ' + i.find_all('td')[2].get_text())
				host = i.find_all('td')[3].get_text()
				result = i.find_all('td')[4].get_text()
				guest = i.find_all('td')[5].get_text()
				host_img = i.find_all('img')[0]['src']
				guest_img = i.find_all('img')[1]['src']
				host_filename = host_img.split("/")[-1]
				guest_filename = guest_img.split("/")[-1]
				path_to_host_img = '/images/' + host_filename
				path_to_guest_img = '/images/' + guest_filename
				outpath = os.path.join(HOME_DIR + 'images/', host_filename)
				outpath2 = os.path.join(HOME_DIR + 'images/', guest_filename)
				tour_list += """<tr class="row">%s%s%s</tr>"""%(tour_list_desktop(), tour_list_tablet(), tour_list_mobile())
				if os.path.exists(outpath) and os.path.exists(outpath2):
					pass
				else:
					opener = urllib.request.build_opener()
					opener.addheaders = [('User-Agent', user_agent)]
					urllib.request.install_opener(opener)
					urllib.request.urlretrieve(host_img, outpath)
					urllib.request.urlretrieve(guest_img, outpath2)
			return tour_list


html = open(HOME_DIR + 'template.html').read()
template = Template(html)

tournament = tournament_table()
calendar = calendar_table()
players = players_table()
disqual = disqual_table()
results = games_results_table()


with open(HOME_DIR + "index.html", "w") as index:
	index.write(template.render(tournament_table=tournament, calendar_table=calendar,
		players_table=players, disqual_table=disqual, games_results_table=results))
	print('index.html updated successfully!' + '	' +  str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

shutil.rmtree(HOME_DIR + 'temp_tables')

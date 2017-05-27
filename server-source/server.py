#!/usr/bin/env python

#	Code from python docs

import SimpleHTTPServer, BaseHTTPServer
import SocketServer
import sys, csv, time

keep_running = True

#	Code adapted from http://blog.doughellmann.com/2007/12/pymotw-basehttpserver.html

def formatted_date_time():
	return time.strftime(("%d/%m/%Y %H:%M:%S"), time.gmtime())

from BaseHTTPServer import BaseHTTPRequestHandler
import cgi, urlparse

class PostHandler(BaseHTTPRequestHandler):
	
	def do_GET(self):
		self.parsed_path = urlparse.urlparse(self.path)
		
		validfiles = ["styles.css", "script.js", "help", "home", "stop_server"]
		OKfile = False
		
		self.filepath = self.parsed_path.path
		if (self.filepath == "/"):
			self.filepath = "/home"

		if (self.filepath == "/list"):
			self.send_response(200)
			self.end_headers()
			message = self.listRecords()
			self.wfile.write(message)
			return

		if (self.filepath == "/edit"):
			query_items = urlparse.parse_qsl(self.parsed_path.query)
			patientID  = False
			for items in query_items:
				if (items[0] == "patientID"):
					patientID = items[1]
			f = open("edit")
			page_data = "".join(f.readlines())
			f.close()
			OKfile = True
			page_data = self.do_edit_page(page_data, patientID)
			if (page_data == False):
				self.page404("record "+patientID)
				return
			self.send_response(200)
			self.end_headers()
			self.wfile.write(page_data)
			return
		#

		if (self.filepath == "/print"):
			query_items = urlparse.parse_qsl(self.parsed_path.query)
			patientID  = False
			for items in query_items:
				if (items[0] == "patientID"):
					patientID = items[1]
			if (patientID == False):	# No record speciality
				return self.page404("your unspecified record to print")
			page_data = self.print_letter(patientID)
			if (page_data == False):
				self.page404("record "+patientID)
				return
			self.send_response(200)
			self.send_header("Content-type", "text/rtf")
			self.end_headers()
			self.wfile.write(page_data)
			return
		#

		for filename in validfiles:
			if (self.filepath == ("/" + filename)):
				f = open(filename)
				message = "".join(f.readlines())
				if (filename == "stop_server"):
					css = "".join(open("styles.css").readlines())
					css = "<style>\n"+css+"</style>"
					message = message.replace("<!--@STYLE-->", css)
				f.close()
				OKfile = True
		
		if (OKfile == True):
			self.send_response(200)
			self.end_headers()
			self.wfile.write(message)
		else:
			self.page404(self.path)
		
		if (self.filepath == "/stop_server"):
			global keep_running
			keep_running = False
		return
	
	def page404(self, path = False):
		self.send_response(404)
		self.end_headers()
		f = open("404")
		message = "".join(f.readlines())
		if (path != False):
			new_string = "<i>" + path + "</i>"
			message = message.replace("that page", new_string)
		f.close()
		self.wfile.write(message)

	def page503(self, custom_message = False):
		self.send_response(503)
		self.end_headers()
		f = open("503")
		message = "".join(f.readlines())
		if (custom_message != False):
			message = message.replace("@useless_error_message", custom_message)
		f.close()
		self.wfile.write(message)
	
	def do_edit_page(self, page_data, patientID):
		if (patientID == False):	# New record
			record = self.empty_record()
		else:
			record = self.get_record(patientID)
		
		if (record == False):
			return False
		
		fields_list = self.get_fields_list()
		for item in fields_list:
			page_data = page_data.replace("@"+item, record[item])
		
		checkbox_list = self.get_checkbox_list()
		for box in checkbox_list:
			if (record[box] == "on"):
				#e.g.:	id="@radiological"	-->	id="radiological" checked
				page_data = page_data.replace("@"+box+"\"", box+"\" checked")
			else:	# Off, or a new record
				page_data = page_data.replace("@"+box, box)

		# First, select the selected radio options, then clear any remaining "@option"s
		radio_list = self.get_radio_list()
		for option in radio_list:
			selection = record[option]
			page_data = page_data.replace("@"+selection+"\"", selection+"\" checked")
		for item in self.get_radio_list_options():
			page_data = page_data.replace("@"+item, item)
		return page_data
	
	def get_record(self, patientID):
		settings_recordcsv = "../records.csv"
		fp = open(settings_recordcsv, mode = 'r')
		csv_reader = csv.reader(fp)
		row_count = 0
		# Yes, it's off by one - because the first row in the database is the header, to allow direct opening to make some sense!
		# It actually selects by row, not patientID, as there may be duplicates, as indicated below in the listRecords function
		for row in csv_reader:
			if (row_count == int(patientID)):
				fp.close()
				return self.row_to_record(row)
			row_count += 1
		fp.close()
		return False
		
	def row_to_record(self, row):
		this_record = self.empty_record()
		items = self.blank_items()
		column = 0
		for item in row:
			this_record[items[column]] = item
			column += 1
		return this_record
	
	def do_POST(self):
		# Parse the form data posted
		form = cgi.FieldStorage(
			fp=self.rfile, 
			headers=self.headers,
			environ={'REQUEST_METHOD':'POST', 'CONTENT_TYPE':self.headers['Content-Type'], })

		if (self.path == "/add"):
			patientID = self.saveRecord(form)
			if (patientID != False):
				self.redirect("/print?patientID="+str(patientID))
				return True
			else:
				self.page503("Error printing record "+patientID)
				return
		return self.page404()
	
	def redirect(self, URL):
		self.send_response(303)
		self.send_header("Location", URL)
		self.end_headers()
		return

	def writeOutCSV(self, items_dictionary):
		settings_recordcsv = "../records.csv"
		record = self.MakeRecord(items_dictionary)
		fp = open(settings_recordcsv, mode = 'a+')
		csv_writer = csv.writer(fp)
		csv_writer.writerow(record)
		fp.close()
	
	def MakeRecord(self, dictionary):
		record = []
		items = self.blank_items()
		for item in items:
			record.append(dictionary[item])
		return record

	def saveRecord(self, form):
		items_dictionary = self.empty_record()
		for field in form.keys():
			items_dictionary[field] = form[field].value
		if (items_dictionary['patientID'] == ""):
			items_dictionary['patientID'] = self.get_current_record_count() + 1
		
		try:
			self.writeOutCSV(items_dictionary)
			return items_dictionary['patientID']
		except:
			return False
	
	def print_letter(self, patientID):
		templateRecordFile = open("../templateprint.rtf")
		page_data = "".join(templateRecordFile.readlines())
		templateRecordFile.close()
		
		if (patientID == False):	# New record
			return False
		else:
			record = self.get_record(patientID)
		
		if (record == False):
			return False
		
		fields_list = self.get_fields_list()
		for item in fields_list:
			if (record[item] == ''):	page_data = page_data.replace("@"+item, "-")
			else:				page_data = page_data.replace("@"+item, record[item])
		
		checkbox_list = self.get_checkbox_list()
		
		left = right = False
		if (record['left'] == 'on'):	left = True
		if (record['right'] == 'on'):	right = True
		if (left and right):		side = "left and right"
		elif (left):			side = "left"
		elif (right):			side = "right"
		else:				side = "(side not recorded)"
		page_data = page_data.replace("@SIDED", side)
		
		clin = rad = False
		if (record['clinical'] == 'on'):	clin = True
		if (record['radiological'] == 'on'):	rad = True
		if (clin and rad):			conf = " (site confirmed clinically & radiologically)"
		elif (clin):				conf = " (site confirmed clinically)"
		elif (rad):				conf = " (site confirmed radiologically)"
		
		if (not (clin or rad)):			conf = " (pre-procedure site confirmation not recorded)"
		page_data = page_data.replace("@CONFIRM", conf)
		
		if (record['ultrasoundguided'] == 'on'):	page_data = page_data.replace("@USSUSE", "with")
		else:						page_data = page_data.replace("@USSUSE", "without")
		
		if (record['aseptictechnique'] == 'on'):	page_data = page_data.replace("@NOASEPSIS", "")
		else:						page_data = page_data.replace("@NOASEPSIS", "without ")
		
		if (record['localanaesthetic'] == 'on'):	page_data = page_data.replace("@LANOT", "")
		else:						page_data = page_data.replace("@LANOT", "not ")
		
		if (record['drainclamped'] == 'on'):	page_data = page_data.replace("@CLAMP", "Yes")
		else:					page_data = page_data.replace("@CLAMP", "No")
		
		if (record['suction'] == 'on'):		page_data = page_data.replace("@SUCTION", "Yes")
		else:					page_data = page_data.replace("@SUCTION", "No")
		
		if (record['fluttervalve'] == 'on'):	page_data = page_data.replace("@FLUTTERVALVE", "Yes")
		else:					page_data = page_data.replace("@FLUTTERVALVE", "No")
		
		if (record['underwaterseal'] == 'on'):	page_data = page_data.replace("@UNDERWATERSEAL", "Yes")
		else:					page_data = page_data.replace("@UNDERWATERSEAL", "No")
		
		if (record['cxrpost'] == 'on'):		page_data = page_data.replace("@CXRPOST", "Yes")
		else:					page_data = page_data.replace("@CXRPOST", "No")
		
		
		for box in checkbox_list:
			if (record[box] == "on"):
				#e.g.:	id="@radiological"	-->	id="radiological" checked
				page_data = page_data.replace("@"+box, box+"\" checked")
			else:	# Off, or a new record
				page_data = page_data.replace("@"+box, box)

		# First, select the selected radio options, then clear any remaining "@option"s
		radio_list = self.get_radio_list()
		for option in radio_list:
			selection = record[option]
			page_data = page_data.replace("@"+option, selection)
		for item in self.get_radio_list_options():
			page_data = page_data.replace("@"+item, item)
		
		page_data = page_data.replace("@PRINTDATETIME", formatted_date_time())
		
		return page_data
	
	def get_current_record_count(self):
		count = 0
		settings_recordcsv = "../records.csv"
		fp = open(settings_recordcsv, mode = 'r')
		csv_reader = csv.reader(fp)
		for row in csv_reader:
			count += 1;
		return count-1	# First row is comments
	
	def empty_record(self):
		return { 'right': '', 'speciality': '', 'grade': '', 'consent': '', 'underwaterseal': '', 'sutureclosuretechnique': '', 
			'aseptictechnique': '', 'fluttervalve': '', 'inserttime': '', 'drainsize': '', 'versiondate': '', 'insertdate': '', 
			'accesstechnique': '', 'radiological': '', 'drainsite': '', 'swversion': '', 'earlycomplications': '', 'clinical': '', 
			'premedicationantibiotics': '', 'cxrpost': '', 'Name': '', 'CHInumber': '', 'drainclamped': '', 'patientposition': '', 
			'suction': '', 'ultrasoundguided': '', 'inserteename': '', 'indication': '', 'localanaesthetic': '', 'additionalnotes': '', 
			'urgency': '', 'left': '', 'patientID': '' }

	def blank_items(self):
		return ["patientID", "Name", "CHInumber", "consent", "indication", "clinical", "radiological", "left", "right", "patientposition", "drainsite", 
			"accesstechnique", "urgency", "drainsize", "ultrasoundguided", "aseptictechnique", "sutureclosuretechnique", "localanaesthetic", 
			"premedicationantibiotics", "drainclamped", "suction", "fluttervalve", "underwaterseal", "cxrpost", "additionalnotes", 
			"earlycomplications", "inserteename", "speciality", "grade", "inserttime", "insertdate", "swversion", "versiondate"]

	def get_fields_list(self):
		return ["patientID", "Name", "CHInumber", "indication", "patientposition", "drainsite", "drainsize", "sutureclosuretechnique", 
			"premedicationantibiotics", "additionalnotes", "earlycomplications", "inserteename", "speciality", "grade", "inserttime", 
			"insertdate", "swversion", "versiondate"]
		
	def get_checkbox_list(self):
		return ["clinical", "radiological", "left", "right", "ultrasoundguided", "aseptictechnique", "localanaesthetic", 
		"drainclamped", "suction", "fluttervalve", "underwaterseal", "cxrpost" ]
		
	def get_radio_list_options(self):
		return ["verbal", "written", "na", "seldinger", "surgical", "elective", "emergency"]
		
	def get_radio_list(self):
		return ["consent", "accesstechnique", "urgency"]

	def row_template(self):
		row_file = open("row.html")
		row_template_data = "".join(row_file.readlines())
		row_file.close()
		return row_template_data

	def edit_print_links(self):
		edit_print_links_file = open("edit_print_links.html")
		edit_print_links_data = "".join(edit_print_links_file.readlines())
		edit_print_links_file.close()
		return edit_print_links_data

	def listRecords(self):
		all_results_file = open("allresults.html")
		all_results_page = "".join(all_results_file.readlines())
		all_results_file.close()

		settings_recordcsv = "../records.csv"
		fp = open(settings_recordcsv, mode = 'r')
		csv_reader = csv.reader(fp)
		
		all_rows = ""
		row_count = 0
		for row in csv_reader:
			items_list = self.blank_items()
			this_row = self.row_template()
			edit_print = self.edit_print_links()
			count = 0
			for item in row:
				this_row = this_row.replace(items_list[count], item)
				# Alternative, the above prints the "actual" ID; below prints the record ID
				# As the ID is a hidden column, this shouldn't really matter - it does below, for the edit link.
				#if (items_list[count] == "patientID"):
				#	this_row = this_row.replace(items_list[count], str(row_count))
				#else:
				#	this_row = this_row.replace(items_list[count], item)
				count += 1

			if (row_count == 0):	# Header
				this_row = this_row.replace("td", "th")
			else:		# Realised that the above 'for item in row:'... code replaces patientID in the links below => edited template
				this_row = this_row.replace("&#9998; &#9993;", edit_print)
				
				# was str(row[0]), now row_count, as instead of really *editing* a record, a new one is created
				# (this wasn't the original intention, but it does act as an audit trail!)
				# So, in summary, the edit & print links are now to the *current* row ID, 
				# but the actual patientID in the database acts as a link to the original.
				# Should be a fairly robust audit trail, as the originals can't really be edited
				# Editing and printing pages retrieve by row, not really by patientID, so this shouldn't be a problem!
				
				this_row = this_row.replace("@patientID", str(row_count))
			
			all_rows = all_rows + this_row
			row_count += 1
			
		all_results_page = all_results_page.replace("@TABLEDATA", all_rows)
		fp.close()
		return all_results_page

def launch_browser(url = 'http://localhost:8080/'):
	import webbrowser
	print "launching web browser..."
	webbrowser.open(url)

if __name__ == '__main__':
	sys.stdout = open("server.log", mode="a")
	sys.stderr = sys.stdout #open("server.log", mode="a")
	print formatted_date_time(), "Starting server... ",
	import threading
	from BaseHTTPServer import HTTPServer
	t = threading.Timer(1, launch_browser)
	t.start()
	try:
		server = HTTPServer(('localhost', 8080), PostHandler)
	except:
		t.cancel()
		print formatted_date_time(), "Error starting server. Browser start aborted."
		#base64 encoded:
		#<h1>The server couldn't start</h1>Maybe it's <a href="http://localhost:8080/">already running</a>?
		url = "data:text/html;base64,PGgxPlRoZSBzZXJ2ZXIgY291bGRuJ3Qgc3RhcnQ8L2gxPk1heWJlIGl0J3MgPGEgaHJlZj0iaHR0cDovL2xvY2FsaG9zdDo4MDgwLyI+YWxyZWFkeSBydW5uaW5nPC9hPj8K"
		launch_browser(url)
		sys.exit(1)
	
	while (keep_running == True):
		server.handle_request()
		t.cancel()
	
print formatted_date_time(), "Finished!"

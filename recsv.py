#!/usr/local/bin/python3
#
# @(!--#) @(#) recsv.py, version 003, 22-april-2016
#
# read in a CSV file and produce the same format but
# with everything inside double quotes
#

import csv
import os
import sys
import cgi
import cgitb
cgitb.enable()   # for troubleshooting

######################################################

def recsvbytestream(filename, bytes):
    httproot = "/home/andyc/www"
    uploaddir = "uploads"
    downloaddir = "downloads"
    basename = os.path.basename(filename)
    tempfilename = httproot + "/" + uploaddir + "/" + basename
    csvfilename = httproot + "/" + downloaddir + "/" + basename

    tempfile = open(tempfilename, "wb")
    tempfile.write(bytes)
    tempfile.close()

    tempfile = open(tempfilename, "r")

    csvobj = csv.reader(tempfile)

    csvfile = open(csvfilename, "w")

    writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

    for row in csvobj:
        writer.writerow(row)

    tempfile.close()

    csvfile.close()

    print("<a href=\"" + "/" + cgi.escape(downloaddir) + "/" + cgi.escape(basename) + "\">Download</a>", sep='')

    print("<hr>")

    print("<pre>")

    csvfile = open(csvfilename, "r")

    for line in csvfile:
        print(line.strip())

    csvfile.close()

    print("<pre>")

    print("<hr>")

    return

######################################################

#
# Main
#

title = "RE-CSV content of a comma separated values (CSV) file"

basescript = "recsv"

print("Content-type: text/html")
print("")

print("<head><title>", cgi.escape(title), "</title></head>", sep='')

print("<body>")

print("<h3>", cgi.escape(title), "</h3>", sep='')

form = cgi.FieldStorage()
upload = form.getfirst("upload", "")

print("<form action=\"", basescript, ".py\" enctype=\"multipart/form-data\" method=\"post\">", sep='')

print("<p>")
print("<input type=\"file\" name=\"userfile\">")
print("</p>")

print("<div>")
print("<input type=\"submit\" name=\"upload\" value=\"-- Upload --\">")
print("</div>")

print("</form>")

print("<hr>")

### print("<pre>")
### print(form)
### print("</pre>")

if upload != "":
    fileitem = form["userfile"]

    if fileitem.file:
        allbytes = fileitem.file.read()

        if len(allbytes) == 0:
            print("<pre>")
            print("Uploaded file appears to be empty")
            print("</pre>")
        else:
            recsvbytestream(fileitem.filename, allbytes)

print("</body>")

sys.exit()

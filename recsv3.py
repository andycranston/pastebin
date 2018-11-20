#!/usr/local/bin/python3
#
# @(!--#) @(#) recsv3.py, version 004, 19-april-2016
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

def outputfield(fieldcount, fielddata):
    """Output field data"""

    if fieldcount > 1:
        print(",", end='')

    print("\"", end='')

    for c in fielddata:
        if c == '"':
            print("\"\"", end='')

        print(c, end='')

    print("\"", end='')

    return

######################################################

def lookahead(line, linepos):
    if linepos >= (len(line) - 1):
        return ' '
    else:
        return line[linepos + 1]

######################################################

def csvoneline(line):
    """CSV one line of input"""

    lenline = len(line)

    if lenline == 0:
        print("")
        return

    fieldcount = 0
    currentfield = ""
    linepos = 0
    quoted = False

    while linepos < lenline:
        c = line[linepos]

        if c == '"' and quoted == False:
            quoted = True
        elif c == ',' and quoted == False:
            fieldcount = fieldcount + 1
            outputfield(fieldcount, currentfield)
            ### print(fieldcount, ">", currentfield, "<")
            currentfield = ""
        elif c == '"' and quoted == True:
            if lookahead(line, linepos) == '"':
                currentfield = currentfield + '"'
                linepos = linepos + 1
            else:
                fieldcount = fieldcount + 1
                outputfield(fieldcount, currentfield)
                ### print(fieldcount, ">", currentfield, "<")
                currentfield = ""
                quoted = False
                linepos = linepos + 1
        elif c == ',' and quoted == True:
            currentfield = currentfield + ','
        else:
            currentfield = currentfield + c

        linepos = linepos + 1

    if len(currentfield) > 0:
        fieldcount = fieldcount + 1
        outputfield(fieldcount, currentfield)
    elif line[-1] == ',':
        fieldcount = fieldcount + 1
        currentfield = ""
        outputfield(fieldcount, currentfield)
        ### print(fieldcount, ">", currentfield, "<")

    print("")

    return

######################################################

def recsvall(csvlines):
    csvlines = csvlines.split("\r\n")

    for line in csvlines:
        csvoneline(line)

    return

######################################################

#
# Main
#

title = "RE-CSV content of a comma separated values (CSV) file"

basescript = "recsv3"

print("Content-type: text/html")
print("")

print("<head><title>", cgi.escape(title), "</title></head>", sep='')

print("<body>")

print("<h3>", cgi.escape(title), "</h3>", sep='')

form = cgi.FieldStorage()
upload = form.getfirst("upload", "")

print("<form action=\"", basescript, ".py\" enctype=\"multipart/form-data\" method=\"post\">", sep='')

print("<p>")
print("<input type=\"file\" name=\"userfile\" size=\"1000000\">")
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
        bn = os.path.basename(fileitem.filename)
###        print(bn)
###        print(allbytes)
###        print(len(allbytes))
        tempfilename = "/tmp/" + bn
        tempfile = open(tempfilename, "wb")
        tempfile.write(allbytes)
        tempfile.close()

        tempfile = open(tempfilename, "r")
        tempdir = "/home/andyc/tmp"
        csvfilename = tempdir + "/" + bn
        csvfile = open(csvfilename, "w")

      
        csvobj = csv.reader(tempfile)

        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        for row in csvobj:
            writer.writerow(row)

        csvfile.close()
        tempfile.close()

        print("<a href=\"/tmp/" + cgi.escape(bn) + "\">Download</a>", sep='')

        print("<hr>")

        print("<pre>")

        csvfile = open(csvfilename, "r")

        for line in csvfile:
            print(line.strip())

        csvfile.close()

        print("<pre>")

        print("<hr>")

print("</body>")

sys.exit()

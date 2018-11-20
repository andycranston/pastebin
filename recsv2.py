#!/usr/local/bin/python3
#
# @(!--#) @(#) recsv2.py, version 001, 11-april-2016
#
# read in a CSV file and produce the same format but with everything
# inside double quotes
#

import csv
import sys
import cgi
import cgitb; cgitb.enable()  # for troubleshooting

############################################################################

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

############################################################################

def lookahead(line, linepos):
    if linepos >= (len(line) - 1):
        return ' '
    else:
        return line[linepos + 1]

############################################################################

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

############################################################################

def recsvall(csvlines):
    csvlines = csvlines.split("\r\n")

    for line in csvlines:
        csvoneline(line)

    return

############################################################################

#
# Main
#

title = "RE-CSV content of a comma separated values (CSV) file"

basescript = "recsv2"

print("Content-type: text/html")
print("")

print("<head><title>", cgi.escape(title), "</title></head>", sep='')

print("<body>")

print("<h3>", cgi.escape(title), "</h3>", sep='')

form = cgi.FieldStorage()
csvlines = form.getfirst("csvlines", "")
recsv = form.getfirst("recsv", "")

print("<form method=\"post\" action=\"", basescript, ".py\">", sep='')

print("<textarea name=\"csvlines\" rows=\"10\" cols=\"80\">", end='')
print(cgi.escape(csvlines), end='')
print("</textarea>")
print("<br>")

print("<input type=\"submit\" name=\"recsv\" value=\"Re-CSV\">")

print("</form>")

print("</p>")

if recsv != "":
    print("<pre>")
    print("Re-CSV'ing ...")
    recsvall(csvlines)
    print("</pre>")

print("</body>")

sys.exit()

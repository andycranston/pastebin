#!/usr/bin/python3
#
# @(!--#) @(#) sbxml.py, version 011, 11-february-2016
#

#
# imports
#

import sys
import cgi
import cgitb; cgitb.enable()  # for troubleshooting

##############################################################################

def keywordexists(keyword, line):
    keyword2 = " " + keyword + "=\""

    return(keyword2 in line)

##############################################################################

def keywordextract(keyword, line):
    keyword2 = " " + keyword + "=\""

    s = line.find(keyword2)

    s = s + len(keyword2)

    restofline = line[s:]

    e = restofline.find("\"")

    if e != -1:
        restofline = restofline[:e]

    return(restofline)

##############################################################################

def skipableline(productnumber, description, netprice):
    skip = False

    if netprice == "0":
        if productnumber.endswith(" 0D1"):
            if "Factory integrated" in description:
                skip = True
        elif productnumber.endswith(" B19"):
            if description == "Europe - Multilingual Localization":
                skip = True

    return skip
###    return False

##############################################################################

def rmmultspaces(s):
    s2 = ""
    lc = "@"

    for c in s:
        if lc == " " and c == " ":
            placeholder = "null"
        else:
            s2 = s2 + c

        lc = c

    return s2

##############################################################################

def csvout(s):
    print("\"", cgi.escape(s), "\"", sep='', end='')

##############################################################################

def analyserawxml(rawxml):
    grossprice = 0
    bundleprice = 0
    bundlelineitems = 0

    rawlines = rawxml.split("\r\n")

    for line in rawlines:
        if line == "":
            placeholder = "null"
        elif line == "<?xml version=\"1.0\" encoding=\"utf-8\"?>":
            versionline = line
        elif line == "<EclipseHeaders>":
            placeholder = "null"
        elif line == "    <EclipseLineItems>":
            placeholder = "null"
            bundleprice = 0
            bundlelineitems = 0
        elif line == "    </EclipseLineItems>":
            print("Bundle price:", bundleprice, "   Number line items:", bundlelineitems)
            print("")
            ### placeholder = "null"
        elif line == "  </EclipseHeader>":
            placeholder = "null"
        elif line == "</EclipseHeaders>":
            placeholder = "null"
        elif line.startswith("  <EclipseHeader "):
            if not keywordexists("ConfigName", line):
                print("!!! EclipseHeader line does not have a ConfigName")
            else:
                configname = keywordextract("ConfigName", line)
                print(cgi.escape(configname))
                ### print("\"0\",\"\",", end='')
                ### csvout(configname)
                ### print(",\"\",\"\"")
        elif line.startswith("      <EclipseLineItem "):
            if not keywordexists("ProductNumber", line):
                print("!!! EclipseLineItem line dose not have a ProductNumber")
            elif not keywordexists("Quantity", line):
                print("!!! EclipseLineItem line dose not have a Quantity")
            elif not keywordexists("Description", line):
                print("!!! EclipseLineItem line dose not have a Description")
            elif not keywordexists("NetPrice", line):
                print("!!! EclipseLineItem line dose not have a NetPrice")
            else:
                productnumber = rmmultspaces(keywordextract("ProductNumber", line))
                quantity = keywordextract("Quantity", line)
                description = keywordextract("Description", line)
                netprice = keywordextract("NetPrice", line)
                if skipableline(productnumber, description, netprice):
                    placeholder = "null"
                else:
                    print("  ", cgi.escape(quantity).rjust(4), cgi.escape(productnumber).ljust(20), cgi.escape(description).ljust(80), cgi.escape(netprice).rjust(8))
                    ### csvout(quantity)
                    ### print(",", end='')
                    ### csvout("HP")
                    ### print(",", end='')
                    ### csvout(description)
                    ### print(",", end='')
                    ### csvout(productnumber)
                    ### print(",", end='')
                    ### csvout(netprice)
                    ### print("")
                    grossprice = grossprice + (int(netprice) * int(quantity))
                    bundleprice = bundleprice + (int(netprice) * int(quantity))
                    bundlelineitems = bundlelineitems + 1
        else:
            print("!!! UNRECOGNISED INPUT !!! ", cgi.escape(line))

    print("")
    print("Gross price:", grossprice)

##############################################################################

#
# Main
#

print("Content-type: text/html")
print("")

print("<html>")

print("<head><title>Sales Builder XML Analyser (beta)</title></head>")

print("<body>")

print("<h3>Sales Builder XML Analyser (beta)</h3>")

form = cgi.FieldStorage()
rawxml = form.getfirst("rawxml", "")
analyse = form.getfirst("analyse", "")

print("<form method=\"post\" action=\"sbxml.py\">")

### print("<pre>")
### s = "Andy   xxx"
### print(s)
### print(rmmultspaces(s))
### print("</pre>")

print("<p>")

print("Raw XML:")
print("<br>")

print("<textarea name=\"rawxml\" rows=\"10\" cols=\"80\">", end='')
print(cgi.escape(rawxml), end='')
print("</textarea>")
print("<br>")

print("<input type=\"submit\" name=\"analyse\" value=\"Analyse\">")

print("</p>")

print("</form>")

if analyse != "":
    print("<pre>")
    print("Analysing ...")
    analyserawxml(rawxml)
    print("</pre>")

print("</body>")

print("</html>")

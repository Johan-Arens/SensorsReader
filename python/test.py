#!/usr/bin/env python
# -*- coding: UTF-8 -*-# enable debugging
import cgitb
import cgi
cgitb.enable()
print("Content-Type: text/html;charset=utf-8")
print("")

print "<html>"
print "<head>"
print "</head>"
print "<title>Sensor Config</title>"
print("Sensor Config")
form = cgi.FieldStorage() 

# Get data from fields
first_name = form.getvalue('first_name')
last_name  = form.getvalue('last_name')
print "<body>"
print "<form action = \"/test.py\" method = \"get\">"
print "First Name: <input type = \"text\" name = \"first_name\" value = \"" + form.getvalue('first_name') + "\"> <br />"
print "Last Name: <input type = \"text\" name = \"last_name\" />"
print "<input type = \"submit\" value = \"Save\" />"

print "</form>"
print "</body>"
print "</html>"

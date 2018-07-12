n = raw_input("Integer? ")#Pick an integer.  And remember, if raw_input is not supported by your OS, use input()
n = int(n)#Defines n as the integer you chose. (Alternatively, you can define n yourself)
if n < 10:
    print ("number ",n," is smaller than 10")
else:
    print ("number ",n," is greater than 10")

import sys
import string


# check argv
try:
    filename = sys.argv[1]

except:
    print("invalid arguments: python3 fw.py [ruleFile]")
    sys.exit()


# use to read the rulefile
def readRule():
    # open filename
    try:
        fd = open(filename, "r")
    except:
        print ("open %s failed" %filename)

    ruleTable = []
    # add new rule to table
    while True:
        rule = fd.readline()
        if not rule: break;
        rule = rule.strip()
        ruleset = rule.split()
        if len(ruleset) >0 :
            if ruleset[0] == "in" or ruleset[0] == "out":
                ruleTable.append(ruleset)
            else:
                sys.stderr.write("invalid rule: %s\n" %rule)
    return ruleTable;

def getInput():
    userin = sys.stdin.buffer.readline()
    if not userin: sys.exit()
    userin = userin.decode("utf-8").strip()
    traffic = userin.split()
    if len(traffic) > 0:
        if traffic[0] == "in" or traffic[0] == "out":
            return traffic
        else:
            sys.stderr.write("invalid input: %s\n" %userin)
            return 0

    return 0


def ruleSearch(t):
    ruleNum = 1
    for rule in RuleTable:
        if rule[0] == t[0]:
            # match ip and port and establish check
            if ipMatch(rule[2],t[1]) and portMatch(rule[3],t[2]) and establishedCheck(rule,t[3]):
                sys.stdout.write("%s(%i) %s %s %s %s\n" %(rule[1],ruleNum,t[0],t[1],t[2],t[3]))
                return;

        else: pass
        ruleNum += 1
    sys.stdout.write("drop() %s %s %s %s\n" %(t[0],t[1],t[2],t[3]))
    return

# use to convert ip to bit bytearray
def ipConverter(ip):
    ipBin =[]
    x = ip.split(".")
    for i in range(4):
        partip= int(x[i])
        partipBin = bin(partip)[2:].zfill(8)
        ipBin += partipBin


    return ipBin;

def ipMatch(ruleip, trafficip):
    if ruleip == "*":
        return True
    x = ruleip.split("/")
    mask = 32
    if len(x) > 1:
        mask = x[1]


    ruleipBin = ipConverter(x[0])
    trafficipBin = ipConverter(trafficip)

    if ruleipBin[:int(mask)] == trafficipBin[:int(mask)]:
        return True

    return False
def portMatch(ruleport, trafficport):
    if ruleport == "*":
        return True
    ruleport = ruleport.split(",")
    for port in ruleport:
        if trafficport == port:
            return True

    return False

def establishedCheck(rule, packetflag):
    if len(rule) > 4:
        if rule[4] == "established" and packetflag == "1":
            return True
    else:
        return True
    return False

# ================main=======================

RuleTable = readRule()
print (RuleTable)
print ()
while True:
    traffic = getInput()
    if traffic != 0:
        ruleSearch(traffic)

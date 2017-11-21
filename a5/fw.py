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
    userin = sys.stdin.buffer.read(256)
    userin = userin.strip()
    traffic = userin.split()
    if len(traffic) > 0:
        if traffic[0] == "in" or traffic[0] == "out":
            return traffic;
        else:
            sys.stderr.write("invalid input: %s\n" %userin)
            return 0;
    else:
        return 0;

# ================main=======================
try:
    RuleTable = readRule()

except Exception as err:
    print(err)

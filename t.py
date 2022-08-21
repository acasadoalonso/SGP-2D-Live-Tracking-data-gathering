def dao1(dd):  				# return the 3 digit of the decimal minutes
    print (dd)
    dd1 = round(abs(float(dd)), 5)
    print("DD1",dd1)
    cdeg = int(dd1)
    mmss = dd1 - float(cdeg)
    minsec = mmss *60.0
    print ("MMSS",minsec)

    decmin="%06.3f" % minsec
    print("DM",decmin, len(decmin))
    if len(decmin) < 5:
          return '0'
    return decmin[5]			# just return the last digita

def dao2(dd):  				# return the 3 digit of the decimal minutes
    print (dd)
    dd1 = round(abs(float(dd)), 4)
    cdeg = int(dd1)
    mmss = dd1 - float(cdeg)
    minsec = mmss *60.0
    decmin= "%03.3d%06.3f" % (cdeg, minsec)
    return decmin[8]

def deg2dmslat(dd):                     # convert degrees float in degrees and decimal minutes (to two decimal places)
    dd1 = round(abs(float(dd)), 4)
    cdeg = int(dd1)
    mmss = dd1 - float(cdeg)
    minsec = mmss *60.0
    if dd < 0:
        cdeg = cdeg * -1
    decmin= "%2.2d%05.3f" % (cdeg, minsec)
    print("Dm", decmin)
    return decmin[0:7]


def deg2dmslon(dd):                     # convert degrees float in degrees and decimal minutes (to two decimal places)
    dd1 = round(abs(float(dd)), 4)
    cdeg = int(dd1)
    mmss = dd1 - float(cdeg)
    minsec = mmss *60.0
    if dd < 0:
        cdeg = cdeg * -1
    decmin= "%3.3d%05.3f" % (cdeg, minsec)
    print("Dm", decmin)
    return decmin[0:8]

print ("DD.MMmm",deg2dmslat(52.98765), dao2(52.98765))
print ("DD.MMmm",deg2dmslon(123.345678), dao2(123.345678))
print ("DD.MMmm",deg2dmslat(abs(-1.12345678)), dao2(-1.12345678))
print ("DD.MMmm",deg2dmslon(abs(-123.456789)), dao2(-123.456789))

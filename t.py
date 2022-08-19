def dao(dd):  				# return the 3 digit of the decimal minutes
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


print (dao(52.98765))
print (dao(123.345678))
print (dao(-1.345678))
print (dao(-123.88776655))

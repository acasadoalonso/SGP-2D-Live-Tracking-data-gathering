def dao(dd):  				# return the 3 digit of the decimal minutes
    print (dd)
    dd1 = round(abs(float(dd)), 5)
    print(dd1)
    decmin="%08.5f" % dd1
    print(decmin)
    if dd > 99.99:
       return decmin[8]			# just return the last digita
    else:
       return decmin[7]			# just return the last digit


print (dao(12.345671))
print (dao(123.345671))

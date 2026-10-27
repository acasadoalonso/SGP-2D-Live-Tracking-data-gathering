import config

#-------------------------------------------------------------------------------------------------------------------#


global _adsbregcache_				# Global ADSB registration information	
_adsbregcache_ = {}
_adsbreg_ = {}


def getadsbreg(icao, mem=True, prt=False):    	# get the registration and model from the ICAO ID
    global _adsbregcache_
    global _adsbreg_
    if not config.ADSBreg:		    	# check if we want to import the huge file ADSBreg
        return(False)
    if not mem:				    	# if we don't want to use the cache, just return the value from the table
        return(False)				# if not enough memory lo load ADSBreg, we can just return False and not use the cache
    if len(_adsbreg_) == 0:	    	    	# only import the table if need it
        import ADSBreg			    	# this file is huge, so it will need a lot of memory, but it is only imported once
        _adsbreg_ = ADSBreg.ADSBreg	    	# update the global pointer
    if icao in _adsbregcache_:		    	# if ID on the table ???
        return (_adsbregcache_[icao])       	# return model and registration
    else:				    	# if not found, look into the whole registration DB
        if icao in _adsbreg_:
            _adsbregcache_[icao]=_adsbreg_[icao]  # and update the cache for next time
            return (_adsbregcache_[icao])     	# return model and registration
    return False			    	# return FALSE


def getsizeadsbcache():			    	# just return the size of the cache
    return (len(_adsbregcache_))

#-------------------------------------------------------------------------------------------------------------------#


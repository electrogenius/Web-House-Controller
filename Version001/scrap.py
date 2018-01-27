    # Check each zone.
    for zoneNumber in allZonesData :
        zoneMode = allZonesData [zoneNumber]["mode"]
        # Is boost active?
        if zoneMode [0:6] == "boost_" :
            # Boost is active. Get boost end time for this zone.
            boostEnd = allZonesData [zoneNumber]["boost_off_time"]
            # Have we reached boost end time?
            if (currentTime >= boostEnd):
                # Boost is finished so clear boost mode by removing "boost_"
                # from mode string.
                allZonesData [zoneNumber]["mode"] = zoneMode [6:]



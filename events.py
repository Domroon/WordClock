from asyncio import Event


# Network Events

wlan_connected = Event()
wlan_connected_timeout = Event()

# Update StateMachine Events

booted = Event()                # 0 - hier kann unterschieden werden ob das System schon an war oder neu gebootet ist
checkTimekeeperState = Event()  # 0.1 Hier wird geprüft ob der Timekeeper eine valide Uhrzeit liefert
connectToWlan = Event()         # 1 - Wird gesetzt wenn gerade versucht wird eine Internetverbindung aufzubauen
checkForUpdates = Event()       # 2 - Es wird gerade nach Updates gesucht
deliverWebServer = Event()      # 3 - Der Webserver zum eingeben von SSID und Password fürs Wlan ist gerade aktiv
updateFirmware = Event()        # 4 - Die Firmware wird gerade aktualisiert
waitToCheck = Event()           # 5 - Es wird gerade gewartet um später nach Updates zu suchen

# Time Validation Events

time_set_by_internet = Event()
timekeeper_time_is_valid = Event()

# Screen Events - es kann immer nur ein Screen Event aktiv sein, nicht mehrere gleichzeitig

showStartInfo = Event()         # Sollte einmal nach dem Start aktiv sein um zu zeigen ob der Timekeeper eine valide Zeit hat,
                                # ob Wlan verbunden ist und ob auf Updates geprüft werden konnte
                                # Erste LED zeigt grün oder rot (je nachdem ob Timekeeper valide ist)
                                # Zweite LED zeigt grün oder rot (je nachdem ob Internet verbunden)
                                # Dritte LED zeigt grün für Updates überprüft, es liegen keine neuen vor
                                # rot für es konnte nicht auf neue Updates geprüft werden und gelb für 
                                # es liegen neue Updates vor
showTime = Event()              # Sollte immer dann gesetzt werden wenn die Zeit angezeigt werden soll
showUpdateProgress = Event()    # Sollte angezeigt werden wenn gerade ein Update durchgeführt wird

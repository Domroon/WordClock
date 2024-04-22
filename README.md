# Word Clock

## 3D Printer Model
https://www.thingiverse.com/thing:6565727

## Pinout

| LED - Row | ESP32 GPIO Pin |
| --------  | -------        |
| 0         | 21             |
| 1         | 19             |
| 2         | 18             |
| 3         | 5              |
| 4         | 17             |
| 5         | 16             |
| 6         | 4              |
| 7         | 0              |
| 8         | 2              |
| 9         | 15             |

# Logic
- whole hour:                       ES IST 'HOUR-NUMBER'
- 5 min after whole hour:           ES IST FÜNF NACH 'HOUR-NUMBER'
- 10 min after whole hour:          ES IST ZEHN NACH 'HOUR-NUMBER'
- quarter after whole hour:         ES IST VIERTEL NACH 'HOUR-NUMBER'
- 20 min after whole hour:          ES IST ZWANZIG NACH 'HOUR-NUMBER'
- 5 min before half:                ES IST FÜNF VOR HALB 'NEXT-HOUR-NUMBER'
- half hour:                        ES IST HALB 'NEXT-HOUR-NUMBER'
- 5 min after half:                 ES IST FÜNF NACH HALB 'NEXT-HOUR-NUMBER'
- 20 min before whole hour:         ES IST ZWANZIG VOR 'NEXT-HOUR-NUMBER'
- quarter before whole hour:        ES IST VIERTEL VOR 'NEXT-HOUR-NUMBER'
- 10 min before whole hour:         ES IST ZEHN VOR 'NEXT-HOUR-NUMBER'
- 5 min before whole hour:          ES IST FÜNF VOR 'HOUR-NUMBER'


from machine import Pin
import time

# -------------------- HARDWARE --------------------
GroenLED = Pin(11, Pin.OUT)
GeelLED = Pin(12, Pin.OUT)
RoodLED = Pin(13, Pin.OUT)
AttractieLED = Pin(14, Pin.OUT)

Knop = Pin(1, Pin.IN, Pin.PULL_UP)
TiltSensor = Pin(2, Pin.IN, Pin.PULL_UP)

# -------------------- VARIABELEN --------------------
# status
StatusVeilig = "Veilig"
StatusRisico = "Risico"
StatusRisicoGrenswaarde = 3000
StatusGevaar = "Gevaar"
StatusGevaarGrenswaarde = 5000
HuidigeStatus = StatusVeilig

# setup status veilig voor initialisatie
GroenLED.value(1)

# trilling meting
Laatste_verandering = 0
DEBOUNCE_MS = 300
trilling_actief = False
start_tijd = 0
laatste_waarde = TiltSensor.value()

#attractie
Attractie_open = True

# periodiek update
laatste_update_5s = time.ticks_ms()
UPDATE_INTERVAL_MS = 2000
laatste_trilling_duur = 0

# -------------------- STATUS BEPALEN --------------------
def bepaalStatus(duur, HuidigeStatus):
    if duur >= StatusGevaarGrenswaarde:
        # status gevaar
        HuidigeStatus = StatusGevaar
        RoodLED.value(1)
        GeelLED.value(0)
        GroenLED.value(0)
        AttractieLED.value(1)
    elif duur >= StatusRisicoGrenswaarde:
        # status risico
        HuidigeStatus = StatusRisico
        GeelLED.value(1)
        GroenLED.value(0)
    elif duur < 3000 and not HuidigeStatus == StatusRisico:
        # status veilig
        HuidigeStatus = StatusVeilig
        GroenLED.value(1)
    return HuidigeStatus

# -------------------- LOOP --------------------
while True:
    if Attractie_open:
        # als de attractie open is
        nu = time.ticks_ms()
        waarde = TiltSensor.value()

        # bepaal of er trillingen zijn
        if waarde != laatste_waarde:
            laatste_waarde = waarde
            Laatste_verandering = nu

            # check of er al word gemeten voor de trillingen
            if not trilling_actief:
                trilling_actief = True
                start_tijd = nu

        # bereken de trilling duur en update de status
        if trilling_actief:
            if time.ticks_diff(nu, Laatste_verandering) > DEBOUNCE_MS:
                duur = time.ticks_diff(nu, start_tijd)
                HuidigeStatus = bepaalStatus(duur, HuidigeStatus)
                print(f"Trilling duur: {duur}ms")
                print(f"Status: {HuidigeStatus}")
                trilling_actief = False
                laatste_trilling_duur = duur
                if HuidigeStatus == StatusGevaar:
                    # als status gevaar is
                    Attractie_open = False
                    print("Attractie gesloten vanwege teveel trillingen")

        # elke update laten zien dat de status en laatste trilling was
        if time.ticks_diff(nu, laatste_update_5s) >= UPDATE_INTERVAL_MS:
            # Bereken duur van laatste trilling, of 0 als er geen actieve trilling is
            duur = time.ticks_diff(nu, start_tijd) if trilling_actief else laatste_trilling_duur
            HuidigeStatus = bepaalStatus(duur, HuidigeStatus)
            print(f"[5s Update] Status: {HuidigeStatus}")
            print(f"[5s Update] Laatste trilling: {Laatste_verandering}ms")
            print(f"[5s Update] Trilling duur: {duur}ms")
            laatste_update_5s = nu
            if HuidigeStatus == StatusGevaar:
                    # als status gevaar is
                    Attractie_open = False
                    print(f"Trilling duur: {duur}ms")
                    print(f"Status: {HuidigeStatus}")
                    print("Attractie gesloten vanwege teveel trillingen")

    # als er op de knop is gedrukt: reset de status en open de attractie
    if Knop.value() == 0:
        # -------- STATUS RESET --------
        HuidigeStatus = StatusVeilig
        Attractie_open = True

        # -------- LEDS RESET --------
        GroenLED.value(1)
        GeelLED.value(0)
        RoodLED.value(0)
        AttractieLED.value(0)

        # -------- TRILLING RESET --------
        trilling_actief = False
        start_tijd = 0
        Laatste_verandering = 0
        laatste_trilling_duur = 0
        laatste_waarde = TiltSensor.value()

        # -------- TIMERS RESET --------
        laatste_update_5s = time.ticks_ms()

        print("Systeem volledig gereset, attractie weer open")
        time.sleep(0.5)

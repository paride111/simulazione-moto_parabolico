import pygame
import math


LARGHEZZA, ALTEZZA = 1000, 700
ORIGINE_X = 80
ORIGINE_Y = ALTEZZA - 80

pygame.init()
schermo = pygame.display.set_mode((LARGHEZZA, ALTEZZA))
font = pygame.font.SysFont("Arial", 20)
font_piccolo = pygame.font.SysFont("Arial", 16)


dati = {
    "x0": "0",
    "y0": "0",
    "angolo": "45",
    "velocita": "50",
    "gravita": "9.81",
    "selezionato": 0
}

campi = ["x0", "y0", "angolo", "velocita", "gravita"]
tag = ["X iniziale", "Y iniziale", "Angolo", "Velocita'", "Gravita'"]

risultato = None
menu = True
buffer_input = dati[campi[dati["selezionato"]]]

# elaborazione dei dati e calcolo
def calcola():
    x0 = max(float(dati["x0"]), 0.0)
    y0 = max(float(dati["y0"]), 0.0)
    angolo = math.radians(float(dati["angolo"]))
    v = max(float(dati["velocita"]), 0.1)
    g = max(float(dati["gravita"]), 0.01)

    vx = v * math.cos(angolo)
    vy = v * math.sin(angolo)

    discriminante = vy**2 + 2 * g * y0
    if discriminante >= 0:
        radice = math.sqrt(discriminante)
        t_tot = (vy + radice) / g
    else:
        t_tot = 0.1

    gittata_reale = x0 + vx * t_tot
    if vy > 0:
        incremento_altezza = (vy ** 2) / (2 * g)
        altezza_max_reale = y0 + incremento_altezza
    else:
        altezza_max_reale = y0

    punti_metri = []
    t = 0
    dt = t_tot / 100

    while t <= t_tot:
        x = x0 + vx * t
        y = y0 + vy * t - 0.5 * g * t * t
        punti_metri.append((x, max(y, 0.0)))
        t += dt

    punti_metri.append((gittata_reale, 0.0))

    spazio_utile_x = LARGHEZZA - ORIGINE_X - 120
    spazio_utile_y = ORIGINE_Y - 120

    scala_x = spazio_utile_x / gittata_reale if gittata_reale > 0 else 1
    scala_y = spazio_utile_y / altezza_max_reale if altezza_max_reale > 0 else 1
    scala_auto = min(scala_x, scala_y)

    punti_pixel = []
    for (xm, ym) in punti_metri:
        px = ORIGINE_X + xm * scala_auto
        py = ORIGINE_Y - ym * scala_auto
        punti_pixel.append((px, py))

    t_picco = vy / g
    if t_picco > 0 and t_picco < t_tot:
        x_max, y_max = x0 + vx * t_picco, altezza_max_reale
    else:
        x_max, y_max = x0, y0

    px_max = ORIGINE_X + x_max * scala_auto
    py_max = ORIGINE_Y - y_max * scala_auto

    return {
        "punti": punti_pixel,
        "tempo": t_tot,
        "gittata": gittata_reale,
        "altezza_max": altezza_max_reale,
        "velocita_impatto": math.sqrt(vx**2 + (vy - g * t_tot)**2),
        "pixel_massimo": (int(px_max), int(py_max)),
        "x_max_reale": x_max,
        "scala_usata": scala_auto
    }


def griglia(scala):
    if scala > 20: 
        passo_metri = 1
    elif scala > 5: 
        passo_metri = 5
    elif scala > 1: 
        passo_metri = 20
    elif scala > 0.1: 
        passo_metri = 100
    else: 
        passo_metri = 500

    passo_pixel = passo_metri * scala

    x = ORIGINE_X
    while x < LARGHEZZA:
        pygame.draw.line(schermo, (30, 30, 35), (int(x), 0), (int(x), ALTEZZA))
        x += passo_pixel

    y = ORIGINE_Y
    while y > 0:
        pygame.draw.line(schermo, (30, 30, 35), (0, int(y)), (LARGHEZZA, int(y)))
        y -= passo_pixel

    pygame.draw.line(schermo, (150, 150, 150), (ORIGINE_X, 0), (ORIGINE_X, ALTEZZA), 2)
    pygame.draw.line(schermo, (150, 150, 150), (0, ORIGINE_Y), (LARGHEZZA, ORIGINE_Y), 2)


running = True
while running:
    schermo.fill((10, 10, 15))

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            running = False

        if menu:
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_TAB:
                    dati["selezionato"] = (dati["selezionato"] + 1) % 5
                    buffer_input = dati[campi[dati["selezionato"]]]

                elif evento.key == pygame.K_RETURN:
                    try:
                        risultato = calcola()
                        menu = False
                    except Exception:
                        pass

                elif evento.key == pygame.K_BACKSPACE:
                    buffer_input = buffer_input[:-1]
                    dati[campi[dati["selezionato"]]] = buffer_input if buffer_input != "" else "0"

                else:
                    c = evento.unicode
                    if c.isdigit() or c == '.':
                        if buffer_input == "0" and c != '.':
                            buffer_input = c
                        else:
                            buffer_input += c
                        dati[campi[dati["selezionato"]]] = buffer_input
        else:
            if evento.type == pygame.KEYDOWN:
                menu = True
                buffer_input = dati[campi[dati["selezionato"]]]


    # menu e grafico
    if menu:
        titolo = font.render("CONFIGURAZIONE LANCIO", True, (255, 255, 255))
        schermo.blit(titolo, (50, 50))

        for i, k in enumerate(campi):
            colore = (0, 255, 255) if i == dati["selezionato"] else (255, 255, 255)
            testo = f"{tag[i]}: {dati[k]}"
            schermo.blit(font.render(testo, True, colore), (60, 150 + i * 40))

        info = font.render("TAB cambia - INVIO avvia simulazione", True, (150, 150, 150))
        schermo.blit(info, (60, 600))

    else:
        griglia(risultato["scala_usata"])
        punti = risultato["punti"]

        if len(punti) > 1:
            pygame.draw.lines(schermo, (255, 255, 0), False, punti, 3)

        if punti:
            pt_impatto = (int(punti[-1][0]), int(punti[-1][1]))
            pygame.draw.circle(schermo, (0, 255, 0), pt_impatto, 6)
            
            testo_verde = font_piccolo.render(f"X: {risultato['gittata']:.2f}m, Y: 0.00m", True, (0, 255, 0))
            schermo.blit(testo_verde, (pt_impatto[0] - 60, pt_impatto[1] - 25))

        pt_massimo = risultato["pixel_massimo"]
        pygame.draw.circle(schermo, (255, 0, 0), pt_massimo, 6)
        
        testo_rosso = font_piccolo.render(f"X: {risultato['x_max_reale']:.2f}m, Y: {risultato['altezza_max']:.2f}m", True, (255, 100, 100))
        schermo.blit(testo_rosso, (pt_massimo[0] - 60, pt_massimo[1] - 25))

        box = pygame.Rect(20, 20, 340, 160)
        pygame.draw.rect(schermo, (30, 30, 35), box)
        pygame.draw.rect(schermo, (255, 255, 255), box, 1)

        righe_dati = [
            (f"Tempo Volo: {risultato['tempo']:.2f} s", (100, 200, 255)),   
            (f"Gittata Max: {risultato['gittata']:.2f} m", (100, 255, 100)),
            (f"Altezza Max: {risultato['altezza_max']:.2f} m", (255, 100, 100)),
            (f"Velocità impatto: {risultato['velocita_impatto']:.2f} m/s", (255, 200, 100))
        ]

        for i, (testo, colore) in enumerate(righe_dati):
            schermo.blit(font.render(testo, True, colore), (35, 30 + i * 32))

        info = font.render("Premi un tasto per tornare al menu", True, (200, 200, 200))
        schermo.blit(info, (20, ALTEZZA - 40))

    pygame.display.flip()

pygame.quit()
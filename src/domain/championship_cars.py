"""Catálogo histórico completo de monoplazas campeones de Fórmula 1 (1950–2025).

Soporta tanto temporadas de título unificado (1 coche) como temporadas de
título dividido (2 coches: Campeón de Pilotos y Campeón de Constructores).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

# Estructura por año:
# {
#   "coches": [
#       {
#           "rol": "Campeón de Pilotos y Constructores" | "Campeón de Pilotos" | "Campeón de Constructores",
#           "archivo": "1950" | "2021_piloto" | "2021_constructor",
#           "modelo": "...",
#           "piloto": "...",
#           "creditos": "...",
#           "resumen": "...",
#       },
#       ...
#   ]
# }

CHAMPIONSHIP_CARS: Dict[int, Dict[str, Any]] = {
    1950: {"coches": [{"rol": "Campeón de Pilotos (Era Pre-Constructores)", "archivo": "1950", "modelo": "Alfa Romeo 158", "piloto": "Giuseppe Farina", "creditos": "Gioacchino Colombo, Orazio Satta Puliga, Giuseppe Busso, Alberto Massimino", "resumen": "Carrocería tipo torpedo, motor delantero 1.5L sobrealimentado, parrilla ovalada clásica Alfa y rines de radios."}]},
    1951: {"coches": [{"rol": "Campeón de Pilotos (Era Pre-Constructores)", "archivo": "1951", "modelo": "Alfa Romeo 159", "piloto": "Juan Manuel Fangio", "creditos": "Gioacchino Colombo, Giuseppe Busso, Orazio Satta Puliga, Bruno Treviso", "resumen": "Evolución del 158 con silueta más baja, suspensión trasera De Dion y escape lateral modificado."}]},
    1952: {"coches": [{"rol": "Campeón de Pilotos (Normativa F2)", "archivo": "1952", "modelo": "Ferrari 500", "piloto": "Alberto Ascari", "creditos": "Aurelio Lampredi, Luigi Bazzi, Enzo Ferrari", "resumen": "Chasis compacto bajo reglamento Fórmula 2 (2.0L atmosférico) que dominó la temporada."}]},
    1953: {"coches": [{"rol": "Campeón de Pilotos (Normativa F2)", "archivo": "1953", "modelo": "Ferrari 500", "piloto": "Alberto Ascari", "creditos": "Aurelio Lampredi, Luigi Bazzi, Enzo Ferrari", "resumen": "Evolución del Ferrari 500 con toma de aire elevada para carburadores Weber y cola afinada."}]},
    1954: {"coches": [{"rol": "Campeón de Pilotos (Era Pre-Constructores)", "archivo": "1954", "modelo": "Mercedes-Benz W196 (y Maserati 250F)", "piloto": "Juan Manuel Fangio", "creditos": "Rudolf Uhlenhaut, Fritz Nallinger, Hans Scherenberg", "resumen": "Fangio ganó con Maserati 250F al inicio y Mercedes-Benz W196 (Streamliner y Open-Wheel) en la segunda mitad."}]},
    1955: {"coches": [{"rol": "Campeón de Pilotos (Era Pre-Constructores)", "archivo": "1955", "modelo": "Mercedes-Benz W196", "piloto": "Juan Manuel Fangio", "creditos": "Rudolf Uhlenhaut, Fritz Nallinger, Hans Scherenberg", "resumen": "Versión Open-Wheel perfeccionada con frenos de tambor internos y silueta ultralimpia sin alerones."}]},
    1956: {"coches": [{"rol": "Campeón de Pilotos (Era Pre-Constructores)", "archivo": "1956", "modelo": "Lancia-Ferrari D50", "piloto": "Juan Manuel Fangio", "creditos": "Vittorio Jano, Andrea Fraschetti, Ettore Zaccone Mina", "resumen": "Inconfundible por sus tanques laterales tipo pontón (pannier tanks) entre las ruedas."}]},
    1957: {"coches": [{"rol": "Campeón de Pilotos (Era Pre-Constructores)", "archivo": "1957", "modelo": "Maserati 250F", "piloto": "Juan Manuel Fangio", "creditos": "Gioacchino Colombo, Giulio Alfieri, Valerio Colotti, Vittorio Bellentani", "resumen": "Arquetipo clásico de los años 50: morro ovalado con tridente, branquias laterales y escape cromado."}]},
    1958: {
        "coches": [
            {"rol": "Campeón de Pilotos", "archivo": "1958_piloto", "modelo": "Ferrari Dino 246", "piloto": "Mike Hawthorn", "creditos": "Vittorio Jano, Carlo Chiti, Andrea Fraschetti", "resumen": "Último campeón de pilotos con motor delantero V6 de 2.4L antes de la revolución del motor trasero."},
            {"rol": "Campeón de Constructores (1.er Título FIA)", "archivo": "1958", "modelo": "Vanwall VW5", "piloto": "Stirling Moss / Tony Brooks", "creditos": "Tony Vandervell, Colin Chapman, Frank Costin, Leo Kuzmicki", "resumen": "Primer ganador oficial del Campeonato de Constructores con carrocería aerodinámica en lágrima."},
        ]
    },
    1959: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "1959", "modelo": "Cooper T51", "piloto": "Jack Brabham", "creditos": "Owen Maddock, John Cooper, Charles Cooper", "resumen": "Revolucionó la F1 al demostrar la superioridad definitiva del motor central-trasero Coventry Climax."}]},
    1960: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "1960", "modelo": "Cooper T53", "piloto": "Jack Brabham", "creditos": "Owen Maddock, John Cooper", "resumen": "Chasis más bajo y estilizado que consolidó el dominio del motor trasero."}]},
    1961: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "1961", "modelo": "Ferrari 156 'Sharknose'", "piloto": "Phil Hill", "creditos": "Carlo Chiti, Mauro Forghieri", "resumen": "Icónico morro de doble toma ('nariz de tiburón') y potente motor V6 a 120° de 1.5L."}]},
    1962: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "1962", "modelo": "BRM P57", "piloto": "Graham Hill", "creditos": "Tony Rudd, Peter Berthon", "resumen": "Motor V8 propio de BRM con escapes verticales tipo 'órgano' en su evolución inicial."}]},
    1963: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "1963", "modelo": "Lotus 25", "piloto": "Jim Clark", "creditos": "Colin Chapman, Len Terry", "resumen": "Primer monocasco de aluminio en F1, triplicando la rigidez torsional respecto a chasis tubulares."}]},
    1964: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "1964", "modelo": "Ferrari 158", "piloto": "John Surtees", "creditos": "Mauro Forghieri, Angelo Bellei", "resumen": "Monocasco Ferrari con motor V8 de 1.5L; Surtees se convirtió en el único campeón de motos y F1."}]},
    1965: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "1965", "modelo": "Lotus 33", "piloto": "Jim Clark", "creditos": "Colin Chapman, Len Terry", "resumen": "Evolución afinada del Lotus 25 adaptada a neumáticos más anchos, con 6 victorias de Clark."}]},
    1966: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "1966", "modelo": "Brabham BT19", "piloto": "Jack Brabham", "creditos": "Ron Tauranac, Jack Brabham", "resumen": "Motor V8 Repco 3.0L ligero y fiable en el inicio de la era de 3 litros; único campeón con su propio coche."}]},
    1967: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "1967", "modelo": "Brabham BT24", "piloto": "Denny Hulme", "creditos": "Ron Tauranac", "resumen": "Chasis tubular ligero y extremadamente fiable con motor Repco V8."}]},
    1968: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "1968", "modelo": "Lotus 49B", "piloto": "Graham Hill", "creditos": "Colin Chapman, Maurice Philippe", "resumen": "Introdujo el motor Cosworth DFV como elemento estructural y los primeros alerones aerodinámicos."}]},
    1969: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "1969", "modelo": "Matra MS80", "piloto": "Jackie Stewart", "creditos": "Gérard Ducarouge, Bernard Boyer", "resumen": "Aerodinámica muy equilibrada y motor Cosworth DFV; primer título de Jackie Stewart."}]},
    1970: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "1970", "modelo": "Lotus 72C", "piloto": "Jochen Rindt", "creditos": "Colin Chapman, Maurice Philippe", "resumen": "Revolucionario perfil en cuña con radiadores laterales y frenos inboard; único campeón póstumo."}]},
    1971: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "1971", "modelo": "Tyrrell 003", "piloto": "Jackie Stewart", "creditos": "Derek Gardner", "resumen": "Chasis ágil y fiable con motor Cosworth DFV y característico morro ancho."}]},
    1972: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "1972", "modelo": "Lotus 72D", "piloto": "Emerson Fittipaldi", "creditos": "Colin Chapman, Maurice Philippe", "resumen": "Icónica decoración negra y dorada; Fittipaldi fue el campeón más joven hasta entonces."}]},
    1973: {
        "coches": [
            {"rol": "Campeón de Pilotos", "archivo": "1973_piloto", "modelo": "Tyrrell 006", "piloto": "Jackie Stewart", "creditos": "Derek Gardner", "resumen": "Evolución ganadora con la que Jackie Stewart conquistó su tercer título mundial."},
            {"rol": "Campeón de Constructores", "archivo": "1973_constructor", "modelo": "Lotus 72E", "piloto": "Emerson Fittipaldi / Ronnie Peterson", "creditos": "Colin Chapman, Ralph Bellamy", "resumen": "La pareja Fittipaldi–Peterson sumó suficientes victorias para dar a Lotus el título de constructores."},
        ]
    },
    1974: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "1974", "modelo": "McLaren M23", "piloto": "Emerson Fittipaldi", "creditos": "Gordon Coppuck", "resumen": "Primer campeonato de McLaren, combinando diseño limpio en cuña con motor Cosworth DFV."}]},
    1975: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "1975", "modelo": "Ferrari 312T", "piloto": "Niki Lauda", "creditos": "Mauro Forghieri", "resumen": "Caja de cambios transversal ('T') y motor bóxer 12 cilindros de centro de gravedad ultrabajo."}]},
    1976: {
        "coches": [
            {"rol": "Campeón de Pilotos", "archivo": "1976_piloto", "modelo": "McLaren M23", "piloto": "James Hunt", "creditos": "Gordon Coppuck, Alistair Caldwell", "resumen": "Protagonista del legendario duelo de 1976 frente a Niki Lauda, decidido en Fuji."},
            {"rol": "Campeón de Constructores", "archivo": "1976_constructor", "modelo": "Ferrari 312T2", "piloto": "Niki Lauda / Clay Regazzoni", "creditos": "Mauro Forghieri", "resumen": "Evolución sin la gran toma de aire superior por cambio reglamentario; aseguró Constructores para Ferrari."},
        ]
    },
    1977: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "1977", "modelo": "Ferrari 312T2", "piloto": "Niki Lauda", "creditos": "Mauro Forghieri", "resumen": "Fiabilidad implacable y puesta a punto superior con el 12 cilindros plano."}]},
    1978: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "1978", "modelo": "Lotus 79", "piloto": "Mario Andretti", "creditos": "Colin Chapman, Geoff Aldridge, Martin Ogilvie, Peter Wright", "resumen": "El legendario 'Black Beauty': perfeccionó el efecto suelo con faldillas deslizantes."}]},
    1979: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "1979", "modelo": "Ferrari 312T4", "piloto": "Jody Scheckter", "creditos": "Mauro Forghieri", "resumen": "Adaptó el efecto suelo al ancho motor 12 cilindros plano con extraordinaria fiabilidad."}]},
    1980: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "1980", "modelo": "Williams FW07B", "piloto": "Alan Jones", "creditos": "Patrick Head, Frank Dernie, Neil Oatley", "resumen": "Referente aerodinámico de efecto suelo; primer título de Pilotos y Constructores para Williams."}]},
    1981: {
        "coches": [
            {"rol": "Campeón de Pilotos", "archivo": "1981_piloto", "modelo": "Brabham BT49C", "piloto": "Nelson Piquet", "creditos": "Gordon Murray", "resumen": "Famoso por su suspensión hidroneumática que bajaba el coche en pista para maximizar el efecto suelo."},
            {"rol": "Campeón de Constructores", "archivo": "1981_constructor", "modelo": "Williams FW07C", "piloto": "Alan Jones / Carlos Reutemann", "creditos": "Patrick Head, Frank Dernie", "resumen": "Consistencia sobresaliente de ambos pilotos para retener el campeonato de constructores."},
        ]
    },
    1982: {
        "coches": [
            {"rol": "Campeón de Pilotos", "archivo": "1982_piloto", "modelo": "Williams FW08", "piloto": "Keke Rosberg", "creditos": "Patrick Head, Frank Dernie", "resumen": "Chasis compacto y ágil con motor Cosworth DFV; Rosberg ganó el título con 1 victoria en un año caótico."},
            {"rol": "Campeón de Constructores", "archivo": "1982_constructor", "modelo": "Ferrari 126C2", "piloto": "Gilles Villeneuve / Didier Pironi / Patrick Tambay", "creditos": "Harvey Postlethwaite, Mauro Forghieri", "resumen": "Primer coche turbo en ganar un título (Constructores) con monocasco en panal de aluminio."},
        ]
    },
    1983: {
        "coches": [
            {"rol": "Campeón de Pilotos", "archivo": "1983_piloto", "modelo": "Brabham BT52", "piloto": "Nelson Piquet", "creditos": "Gordon Murray", "resumen": "Icónica silueta en flecha/dardo y motor BMW 4 cilindros turbo; primer campeón de pilotos turbo."},
            {"rol": "Campeón de Constructores", "archivo": "1983_constructor", "modelo": "Ferrari 126C2B / 126C3", "piloto": "René Arnoux / Patrick Tambay", "creditos": "Harvey Postlethwaite, Mauro Forghieri", "resumen": "Primer Ferrari con monocasco de fibra de carbono; dio a Maranello su segundo título consecutivo."},
        ]
    },
    1984: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "1984", "modelo": "McLaren MP4/2", "piloto": "Niki Lauda", "creditos": "John Barnard, Alan Jenkins, Steve Nichols", "resumen": "Chasis de fibra de carbono + motor TAG-Porsche V6 turbo; ganó 12 de 16 carreras."}]},
    1985: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "1985", "modelo": "McLaren MP4/2B", "piloto": "Alain Prost", "creditos": "John Barnard", "resumen": "Evolución aerodinámica con gestión superior de combustible; primer título de Prost."}]},
    1986: {
        "coches": [
            {"rol": "Campeón de Pilotos", "archivo": "1986_piloto", "modelo": "McLaren MP4/2C", "piloto": "Alain Prost", "creditos": "John Barnard", "resumen": "Prost superó a los Williams-Honda más potentes gracias a estrategia, fiabilidad y precisión."},
            {"rol": "Campeón de Constructores", "archivo": "1986_constructor", "modelo": "Williams FW11", "piloto": "Nigel Mansell / Nelson Piquet", "creditos": "Patrick Head, Frank Dernie", "resumen": "Dominador absoluto de la era turbo con el explosivo motor Honda RA166E V6."}
        ]
    },
    1987: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "1987", "modelo": "Williams FW11B", "piloto": "Nelson Piquet", "creditos": "Patrick Head, Frank Dernie", "resumen": "Incorporó suspensión activa en varias carreras y arrasó con 9 victorias."}]},
    1988: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "1988", "modelo": "McLaren MP4/4", "piloto": "Ayrton Senna", "creditos": "Gordon Murray, Steve Nichols", "resumen": "Leyenda absoluta: ganó 15 de 16 Grandes Premios con posición de conducción semireclinada y motor Honda V6 turbo."}]},
    1989: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "1989", "modelo": "McLaren MP4/5", "piloto": "Alain Prost", "creditos": "Neil Oatley, Gordon Murray", "resumen": "Inicio de la era atmosférica 3.5L con el potente motor Honda V10."}]},
    1990: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "1990", "modelo": "McLaren MP4/5B", "piloto": "Ayrton Senna", "creditos": "Neil Oatley, Henri Durand", "resumen": "Evolución aerodinámica con pontones revisados y gran equilibrio con el Honda V10."}]},
    1991: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "1991", "modelo": "McLaren MP4/6", "piloto": "Ayrton Senna", "creditos": "Neil Oatley, Henri Durand", "resumen": "Último campeón con motor V12 y cambio manual; tercer título de Ayrton Senna."}]},
    1992: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "1992", "modelo": "Williams FW14B", "piloto": "Nigel Mansell", "creditos": "Adrian Newey, Patrick Head", "resumen": "Obra maestra tecnológica: suspensión activa, control de tracción, cambio semiautomático y motor Renault V10."}]},
    1993: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "1993", "modelo": "Williams FW15C", "piloto": "Alain Prost", "creditos": "Adrian Newey, Patrick Head", "resumen": "El coche más sofisticado electrónicamente de la historia antes de prohibirse las ayudas en 1994."}]},
    1994: {
        "coches": [
            {"rol": "Campeón de Pilotos", "archivo": "1994_piloto", "modelo": "Benetton B194", "piloto": "Michael Schumacher", "creditos": "Rory Byrne, Ross Brawn, Pat Symonds", "resumen": "Morro elevado y excelente eficiencia aerodinámica con motor Ford Zetec-R V8; primer título de Schumacher."},
            {"rol": "Campeón de Constructores", "archivo": "1994_constructor", "modelo": "Williams FW16 / FW16B", "piloto": "Damon Hill / David Coulthard / Nigel Mansell", "creditos": "Adrian Newey, Patrick Head", "resumen": "Tras corregir su inestabilidad inicial, la versión FW16B aseguró Constructores para Williams."},
        ]
    },
    1995: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "1995", "modelo": "Benetton B195", "piloto": "Michael Schumacher", "creditos": "Rory Byrne, Ross Brawn", "resumen": "Equipado con el motor Renault V10, ganó 11 de 17 carreras y selló el doblete."}]},
    1996: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "1996", "modelo": "Williams FW18", "piloto": "Damon Hill", "creditos": "Adrian Newey, Patrick Head", "resumen": "12 victorias en 16 carreras; aerodinámica impecable y fiabilidad dominante."}]},
    1997: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "1997", "modelo": "Williams FW19", "piloto": "Jacques Villeneuve", "creditos": "Adrian Newey, Geoff Willis, Patrick Head", "resumen": "Último título de Williams, culminando la exitosa asociación con Renault V10."}]},
    1998: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "1998", "modelo": "McLaren MP4/13", "piloto": "Mika Häkkinen", "creditos": "Adrian Newey, Neil Oatley", "resumen": "Dominó el cambio a coches estrechos y neumáticos acanalados con el potente Mercedes V10."}]},
    1999: {
        "coches": [
            {"rol": "Campeón de Pilotos", "archivo": "1999_piloto", "modelo": "McLaren MP4/14", "piloto": "Mika Häkkinen", "creditos": "Adrian Newey, Neil Oatley", "resumen": "El coche más rápido a una vuelta de 1999, dando a Häkkinen su bicampeonato."},
            {"rol": "Campeón de Constructores", "archivo": "1999_constructor", "modelo": "Ferrari F399", "piloto": "Eddie Irvine / Michael Schumacher / Mika Salo", "creditos": "Ross Brawn, Rory Byrne", "resumen": "Puso fin a 16 años de sequía en Constructores para Ferrari e inició su era dorada."},
        ]
    },
    2000: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "2000", "modelo": "Ferrari F1-2000", "piloto": "Michael Schumacher", "creditos": "Ross Brawn, Rory Byrne, Paolo Martinelli", "resumen": "Motor V10 a 90° de centro de gravedad ultrabajo; primer título de pilotos Ferrari en 21 años."}]},
    2001: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "2001", "modelo": "Ferrari F2001", "piloto": "Michael Schumacher", "creditos": "Ross Brawn, Rory Byrne, Aldo Costa", "resumen": "Morro caído innovador y enorme fiabilidad para retener ambos títulos con holgura."}]},
    2002: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "2002", "modelo": "Ferrari F2002", "piloto": "Michael Schumacher", "creditos": "Ross Brawn, Rory Byrne, Ignazio Lunetta, Aldo Costa, Nikolas Tombazis, James Allison, Marco Fainello", "resumen": "Ganó 15 de 17 carreras con su caja de cambios de titanio ultracompacta y el motor V10 Tipo 051."}]},
    2003: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "2003", "modelo": "Ferrari F2003-GA", "piloto": "Michael Schumacher", "creditos": "Ross Brawn, Rory Byrne, Aldo Costa", "resumen": "Dedicado a Gianni Agnelli; batalla más larga y gran eficiencia aerodinámica."}]},
    2004: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "2004", "modelo": "Ferrari F2004", "piloto": "Michael Schumacher", "creditos": "Ross Brawn, Rory Byrne, Aldo Costa, John Iley", "resumen": "15 victorias en 18 carreras y récords de vuelta que resistieron más de una década."}]},
    2005: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "2005", "modelo": "Renault R25", "piloto": "Fernando Alonso", "creditos": "Bob Bell, Tim Densham, Dino Toso, Pat Symonds", "resumen": "Tracción extraordinaria y famosa amortiguación 'mass damper' que rompió la hegemonía de Ferrari."}]},
    2006: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "2006", "modelo": "Renault R26", "piloto": "Fernando Alonso", "creditos": "Bob Bell, Tim Densham, Dino Toso", "resumen": "Debut de los motores V8 de 2.4L; Alonso logró el bicampeonato frente a Schumacher."}]},
    2007: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "2007", "modelo": "Ferrari F2007", "piloto": "Kimi Räikkönen", "creditos": "Aldo Costa, Nikolas Tombazis, Giles Simon", "resumen": "Batalla larga, caja sin pérdida de par ('seamless') y victoria épica por 1 punto en Brasil."}]},
    2008: {
        "coches": [
            {"rol": "Campeón de Pilotos", "archivo": "2008_piloto", "modelo": "McLaren MP4-23", "piloto": "Lewis Hamilton", "creditos": "Paddy Lowe, Neil Oatley, Tim Goss, Doug McKiernan", "resumen": "Aerodinámica extrema de fin de era; Hamilton ganó su primer título en la última curva de Interlagos."},
            {"rol": "Campeón de Constructores", "archivo": "2008_constructor", "modelo": "Ferrari F2008", "piloto": "Felipe Massa / Kimi Räikkönen", "creditos": "Aldo Costa, Nikolas Tombazis", "resumen": "Introdujo el innovador morro con conducto perforado y aseguró Constructores para Ferrari."},
        ]
    },
    2009: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "2009", "modelo": "Brawn BGP 001", "piloto": "Jenson Button", "creditos": "Ross Brawn, Jörg Zander, Loïc Bigois", "resumen": "El milagro del doble difusor: un equipo debutante ganó ambos títulos en su única temporada."}]},
    2010: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "2010", "modelo": "Red Bull RB6", "piloto": "Sebastian Vettel", "creditos": "Adrian Newey, Rob Marshall, Peter Prodromou", "resumen": "Perfeccionó el difusor soplado por escapes y la suspensión trasera pull-rod."}]},
    2011: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "2011", "modelo": "Red Bull RB7", "piloto": "Sebastian Vettel", "creditos": "Adrian Newey, Rob Marshall, Peter Prodromou", "resumen": "Dominio de carga aerodinámica con 18 poles de 19 posibles y 12 victorias."}]},
    2012: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "2012", "modelo": "Red Bull RB8", "piloto": "Sebastian Vettel", "creditos": "Adrian Newey, Rob Marshall, Peter Prodromou", "resumen": "Escapes con efecto Coanda en una de las temporadas más igualadas de la historia."}]},
    2013: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "2013", "modelo": "Red Bull RB9", "piloto": "Sebastian Vettel", "creditos": "Adrian Newey, Rob Marshall, Peter Prodromou", "resumen": "Racha récord de 9 victorias consecutivas de Vettel para cerrar la era V8."}]},
    2014: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "2014", "modelo": "Mercedes F1 W05 Hybrid", "piloto": "Lewis Hamilton", "creditos": "Paddy Lowe, Aldo Costa, Geoff Willis, Andy Cowell", "resumen": "Revolucionó la era híbrida V6 turbo con el concepto de turbo partido ('split turbo')."}]},
    2015: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "2015", "modelo": "Mercedes F1 W06 Hybrid", "piloto": "Lewis Hamilton", "creditos": "Paddy Lowe, Aldo Costa, Geoff Willis", "resumen": "16 victorias en 19 carreras y 12 dobletes en una exhibición de eficiencia híbrida."}]},
    2016: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "2016", "modelo": "Mercedes F1 W07 Hybrid", "piloto": "Nico Rosberg", "creditos": "Paddy Lowe, Aldo Costa, Geoff Willis", "resumen": "Ganó 19 de 21 Grandes Premios; Rosberg superó a Hamilton en un intenso duelo interno."}]},
    2017: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "2017", "modelo": "Mercedes-AMG F1 W08 EQ Power+", "piloto": "Lewis Hamilton", "creditos": "James Allison, Aldo Costa, Geoff Willis", "resumen": "Adaptación a coches más anchos y rápidos con mayor distancia entre ejes."}]},
    2018: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "2018", "modelo": "Mercedes-AMG F1 W09 EQ Power+", "piloto": "Lewis Hamilton", "creditos": "James Allison, Aldo Costa, John Owen", "resumen": "Estrenó el Halo y mantuvo una evolución constante para conquistar el quinto doblete consecutivo."}]},
    2019: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "2019", "modelo": "Mercedes-AMG F1 W10 EQ Power+", "piloto": "Lewis Hamilton", "creditos": "James Allison, John Owen, Mike Elliott", "resumen": "Arrancó con 5 dobletes seguidos y sumó 15 victorias en 21 carreras."}]},
    2020: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "2020", "modelo": "Mercedes-AMG F1 W11 EQ Performance", "piloto": "Lewis Hamilton", "creditos": "James Allison, John Owen, Mike Elliott", "resumen": "Considerado el F1 más rápido de la historia a una vuelta; introdujo el innovador sistema DAS."}]},
    2021: {
        "coches": [
            {"rol": "Campeón de Pilotos", "archivo": "2021_piloto", "modelo": "Red Bull RB16B", "piloto": "Max Verstappen", "creditos": "Adrian Newey, Pierre Waché, Rob Marshall", "resumen": "Concepto de alto rake y motor Honda que llevó a Verstappen a su primer título mundial."},
            {"rol": "Campeón de Constructores", "archivo": "2021_constructor", "modelo": "Mercedes-AMG F1 W12 E Performance", "piloto": "Lewis Hamilton / Valtteri Bottas", "creditos": "James Allison, Mike Elliott, John Owen", "resumen": "Octavo título consecutivo de constructores para Mercedes en un final histórico."},
        ]
    },
    2022: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "2022", "modelo": "Red Bull RB18", "piloto": "Max Verstappen", "creditos": "Adrian Newey, Pierre Waché, Enrico Balbo", "resumen": "Referente del regreso del efecto suelo: máxima velocidad punta y control superior del porpoising."}]},
    2023: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "2023", "modelo": "Red Bull RB19", "piloto": "Max Verstappen", "creditos": "Adrian Newey, Pierre Waché, Enrico Balbo", "resumen": "El monoplaza más dominante estadísticamente de la F1: 21 victorias en 22 carreras (95.45%)."}]},
    2024: {
        "coches": [
            {"rol": "Campeón de Pilotos", "archivo": "2024_piloto", "modelo": "Red Bull RB20", "piloto": "Max Verstappen", "creditos": "Adrian Newey, Pierre Waché, Enrico Balbo", "resumen": "Arriesgado concepto de entradas verticales que permitió a Verstappen asegurar su cuarto título."},
            {"rol": "Campeón de Constructores", "archivo": "2024_constructor", "modelo": "McLaren MCL38", "piloto": "Lando Norris / Oscar Piastri", "creditos": "Rob Marshall, Peter Prodromou, Andrea Stella", "resumen": "Primer campeonato de constructores para McLaren desde 1998 tras su paquete evolutivo de Miami."},
        ]
    },
    2025: {"coches": [{"rol": "Campeón de Pilotos y Constructores", "archivo": "2025", "modelo": "McLaren MCL39", "piloto": "Lando Norris / Oscar Piastri", "creditos": "Rob Marshall, Peter Prodromou, Andrea Stella", "resumen": "Cierre de la normativa de efecto suelo 2022–2025 con excelente gestión térmica de neumáticos."}]},
    2026: {"coches": [{"rol": "Temporada en curso · Nueva Era FIA 2026", "archivo": "2026", "modelo": "Monoplaza FIA 2026 (Aerodinámica Activa)", "piloto": "Campeonato en disputa", "creditos": "Reglamento Técnico FIA 2026", "resumen": "Inicio de la nueva era técnica: monoplazas más ágiles y ligeros, unidad de potencia 50% eléctrica con combustible 100% sostenible y aerodinámica activa."}]},
}


def obtener_fichas_monoplazas(anio: int) -> List[Dict[str, str]]:
    """Devuelve la lista de monoplazas campeones (1 o 2 si hubo título dividido) para el año."""
    entrada = CHAMPIONSHIP_CARS.get(int(anio))
    if not entrada:
        return []
    return list(entrada.get("coches", []))


def obtener_ficha_monoplaza(anio: int) -> Optional[Dict[str, str]]:
    """Alias de compatibilidad: retorna la primera ficha disponible del año."""
    fichas = obtener_fichas_monoplazas(anio)
    return fichas[0] if fichas else None

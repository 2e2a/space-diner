################################################
# Space Diner (erste Testversion) installieren #
################################################

Zuerst python3 installieren, min. Version 3.7 (falls noch nicht vorhanden; ggf. prüfen mit "python3 --version").

###########
# Windows #
###########

(a) Datei space_diner-0.0.1.tar.gz speichern (nicht entpacken)
(b) Command prompt öffnen und in den Ordner gehen, in dem die Datei ist.
(c) Folgenden Befehl ausführen: pip3 install pyreadline
(d) Folgenden Befehl ausführen: pip3 install space_diner-0.0.1.tar.gz

--> Jetzt müsste es möglich sein, mit dem Befehl "space-diner" das Spiel im Command Prompt zu starten, egal wo man sich befindet.

##########
# MacOSX #
##########

(a) Datei space_diner-0.0.1.tar.gz speichern (nicht entpacken)
(b) Terminal öffnen und in den Ordner gehen, in dem die Datei ist.
(c) Folgenden Befehl ausführen: pip3 install space_diner-0.0.1.tar.gz

--> Jetzt müsste es möglich sein, mit dem Befehl "space-diner" das Spiel im Terminal zu starten, egal wo man sich befindet.

#########
# Linux #
#########

Installationsvariante 1 - um Space Diner im Home-Verzeichnis zu installieren:

(a) Datei space_diner-0.0.1.tar.gz speichern (nicht entpacken)
(b) Terminal öffnen und in den Ordner gehen, in dem die Datei ist.
(c) Folgenden Befehl ausführen: pip3 install space_diner-0.0.1.tar.gz
(d) Bei der Installation müsste eine Warnmeldung erscheinen, ungefähr sowas: "The scripts ... are installed in '/home/USER/.local/bin' which is not on PATH. Consider adding this directory to PATH"
(e) Um das zu tun, die Datei .bashrc im Home-Verzeichnis öffnen und am Ende folgende Zeile einfügen:
"export PATH="$PATH:/home/USER/.local/bin" (den Pfad aus der Warnmeldung)
(Falls eine andere Konsole als bash benutzt wird, entsprechende Datei suchen.)

--> Jetzt müsste es möglich sein, mit dem Befehl "space-diner" das Spiel im Terminal zu starten, egal wo man sich befindet.


Installationsvariante 2 - um Space Diner in einer virtuellen Python-Umgebung zu installieren:

(a) Ordner anlegen, in dem die virtuelle Umgebung angelegt werden soll, z.B. ~/space-diner
(b) Datei space_diner-0.0.1.tar.gz dort speichern (nicht entpacken)
(c) Terminal öffnen und in den Ordner gehen, in dem die Datei ist.
(d) Folgenden Befehl ausführen: python3 -m venv env
(e) Folgenden Befehl ausführen: source env/bin/activate
(f) Folgenden Befehl ausführen: pip3 install space_diner-0.0.1.tar.gz
(g) Jetzt zum Starten in diesem Ordner den Befehl "space-diner" eingeben.

--> Um das Spiel unter Installationsvariante 2 später nochmal zu starten, wieder in den Ordner begeben und folgende Befehle ausführen: "source env/bin/activate", dann "space-diner".
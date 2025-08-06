clear
#!/bin/bash
echo "Uruchamianie bota Discord \"Arsha\"..."

# Aktywacja środowiska wirtualnego
source ./arsha/Scripts/activate

# Aktualizacja pip
echo "Aktualizacja pip..."
python -m pip install --upgrade pip

# Sprawdzenie, czy wszystkie zależności są zainstalowane
echo "Sprawdzanie zaleznosci..."
pip install -r requirements.txt

# Uruchomienie bota z automatycznym restartem
echo "Uruchamianie bota..."
while true; do
    echo "Startowanie bota..."
    python bot.py
    echo "Bot się zatrzymał. Restart za 3 sekundy..."
    sleep 3
done
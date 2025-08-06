@echo off
echo Uruchamianie bota Discord "Arsha"...

:: Aktywacja środowiska wirtualnego
call .\arsha\Scripts\activate.bat

:: Aktualizacja pip
echo Aktualizacja pip...
python -m pip install --upgrade pip

:: Sprawdzenie, czy wszystkie zależności są zainstalowane
echo Sprawdzanie zaleznosci...
pip install -r requirements.txt

:: Uruchomienie bota z automatycznym restartem
echo Uruchamianie bota...
:restart
echo Startowanie bota...
python bot.py
echo Bot się zatrzymał. Restart za 3 sekundy...
timeout /t 3 /nobreak >nul
goto restart
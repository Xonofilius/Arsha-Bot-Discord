# Bot Discord "Arsha"

Prosty bot Discord stworzony przy użyciu biblioteki discord.py, który reaguje na komendę slash `/hello`.

## Wymagania

- Python 3.8 lub nowszy
- Biblioteki wymienione w pliku `requirements.txt`

## Instalacja

1. Sklonuj to repozytorium lub pobierz pliki
2. Zainstaluj wymagane biblioteki:

```bash
pip install -r requirements.txt
```

## Konfiguracja

Token bota jest już skonfigurowany w pliku `bot.py`. Jeśli chcesz użyć własnego bota, zastąp istniejący token swoim własnym.

## Uruchomienie

### Windows

Możesz uruchomić bota korzystając z dołączonego skryptu startowego:

```bash
start.bat
```

### Linux

Możesz uruchomić bota korzystając z dołączonego skryptu startowego (upewnij się, że ma uprawnienia do wykonania):

```bash
chmod +x start.sh
./start.sh
```

### Ręczne uruchomienie

Alternatywnie, możesz uruchomić bota ręcznie:

```bash
python bot.py
```

## Funkcje

- `/hello` - Bot odpowiada "Hello @użytkownik" (wspomina użytkownika)
- `/clear <ilość>` - Usuwa określoną liczbę wiadomości (maksymalnie 100) i wysyła embed z informacją o liczbie usuniętych wiadomości. Wymaga uprawnień do zarządzania wiadomościami.
- `/setup_verification` - Tworzy panel weryfikacji antybot z przyciskiem. Użytkownicy rozwiązują zadanie matematyczne przez DM i otrzymują rolę użytkownika (tylko właściciel bota)

## Dodawanie bota do serwera

Aby dodać bota do swojego serwera Discord, musisz:

1. Przejść do [Discord Developer Portal](https://discord.com/developers/applications)
2. Wybrać swoją aplikację lub stworzyć nową
3. Przejść do zakładki "OAuth2" > "URL Generator"
4. Zaznaczyć uprawnienia "bot" i "applications.commands"
5. Zaznaczyć odpowiednie uprawnienia dla bota:
   - "Send Messages" - do wysyłania wiadomości
   - "Manage Messages" - do używania komendy `/clear`
   - "Read Message History" - do czytania historii wiadomości (wymagane dla `/clear`)
   - "Manage Roles" - do używania komendy `/setup_verification` (tworzenie i edycja ról)
   - "Send Messages in DM" - do wysyłania wiadomości prywatnych (wymagane dla `/setup_verification`)
   - "Administrator" - do pełnej funkcjonalności wszystkich komend administracyjnych (opcjonalnie, jeśli chcesz mieć pełne uprawnienia)
6. Skopiować wygenerowany URL i otworzyć go w przeglądarce
7. Wybrać serwer, do którego chcesz dodać bota i potwierdzić
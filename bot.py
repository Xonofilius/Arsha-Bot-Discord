import os
import datetime
from typing import List, Dict, Any
import random
import asyncio
import sys

import discord
from discord import app_commands, Permissions
from discord.ext import commands

# Konfiguracja bota
TOKEN = os.getenv('DISCORD_TOKEN')  # Token z zmiennej środowiskowej
OWNER_ID = 1345378020437004319
RULES_CHANNEL_ID = 1402593142531948624

# Cache dla statusu bota
last_status_update = None
current_status = None

# Konfiguracja intencji bota
intents = discord.Intents.default()
intents.message_content = True

# Inicjalizacja bota
bot = commands.Bot(command_prefix='!', intents=intents)

# Funkcje pomocnicze
async def send_ephemeral_response(interaction, message):
    """Wysyła wiadomość ephemeral z obsługą wygaśnięcia interakcji."""
    try:
        await interaction.followup.send(message, ephemeral=True)
    except discord.NotFound:
        # Jeśli interakcja wygasła, nie rób nic
        pass

async def update_bot_status(status_text: str, force: bool = False):
    """Aktualizuje status bota w profilu."""
    global last_status_update, current_status
    
    # Sprawdź czy status się zmienił
    if current_status == status_text and not force:
        return
    
    # Sprawdź ograniczenie czasowe (minimum 10 minut między aktualizacjami)
    now = datetime.datetime.now()
    if last_status_update and not force:
        time_diff = (now - last_status_update).total_seconds()
        if time_diff < 600:  # 10 minut
            print(f"Status nie został zaktualizowany - zbyt częste zmiany (ostatnia: {time_diff:.0f}s temu)")
            return
    
    try:
        # Aktualizacja statusu w profilu bota
        if "💚" in status_text or "Aktywny" in status_text:
            activity = discord.CustomActivity(name=status_text)
            status = discord.Status.online
        elif "🔴" in status_text or "Nieaktywny" in status_text:
            activity = discord.CustomActivity(name=status_text)
            status = discord.Status.dnd
        elif "🔄" in status_text or "Restartowanie" in status_text:
            activity = discord.CustomActivity(name=status_text)
            status = discord.Status.idle
        else:
            activity = discord.CustomActivity(name=status_text)
            status = discord.Status.online
        
        await bot.change_presence(activity=activity, status=status)
        print(f"Status bota zaktualizowany: {status_text}")
        
        last_status_update = now
        current_status = status_text
        
    except discord.HTTPException as e:
        if e.status == 429:  # Rate limit
            print(f"Rate limit przy aktualizacji statusu - spróbuj ponownie za {e.retry_after} sekund")
        else:
            print(f"Błąd HTTP podczas aktualizacji statusu bota: {e}")
    except Exception as e:
        print(f"Błąd podczas aktualizacji statusu bota: {e}")

#######################
# Zdarzenia bota
#######################

@bot.event
async def on_ready():
    """Zdarzenie wywoływane, gdy bot jest gotowy."""
    print(f'Zalogowano jako {bot.user.name}')
    print(f'ID bota: {bot.user.id}')
    print('------')
    try:
        synced = await bot.tree.sync()
        print(f'Zsynchronizowano {len(synced)} komend')
        # Aktualizacja statusu bota na aktywny (wymuszona po restarcie)
        await update_bot_status("💚 Aktywny", force=True)
    except Exception as e:
        print(f'Błąd podczas synchronizacji komend: {e}')

@bot.event
async def on_disconnect():
    """Zdarzenie wywoływane, gdy bot się rozłącza."""
    print("Bot się rozłącza...")
    try:
        await update_bot_status("🔴 Nieaktywny", force=True)
    except Exception as e:
        print(f'Błąd podczas aktualizacji statusu przy rozłączeniu: {e}')

#######################
# Komendy slash
#######################

@bot.tree.command(name="hello", description="Przywitaj się z botem")
async def hello(interaction: discord.Interaction):
    """Komenda przywitania się z botem."""
    await interaction.response.send_message(f"Hello {interaction.user.mention}")

@bot.tree.command(name="clear", description="Usuń określoną liczbę wiadomości (wymaga uprawnień)")
@app_commands.describe(ilosc="Liczba wiadomości do usunięcia (maksymalnie 100)")
async def clear(interaction: discord.Interaction, ilosc: int):
    """Usuwa określoną liczbę wiadomości z kanału.
    
    Args:
        interaction: Interakcja Discord
        ilosc: Liczba wiadomości do usunięcia
    """
    # Sprawdzenie uprawnień użytkownika
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("Nie masz uprawnień do zarządzania wiadomościami!", ephemeral=True)
        return
    
    # Walidacja liczby wiadomości
    if ilosc < 1:
        await interaction.response.send_message("Liczba wiadomości do usunięcia musi być większa niż 0!", ephemeral=True)
        return
    
    # Ograniczenie liczby wiadomości (Discord API limit)
    if ilosc > 100:
        ilosc = 100
    
    # Odroczenie odpowiedzi jako ephemeral, aby uniknąć jej usunięcia podczas czyszczenia
    await interaction.response.defer(ephemeral=True)
    
    # Usuwanie wiadomości
    try:
        # Pobierz kanał i usuń wiadomości
        channel = interaction.channel
        deleted = await channel.purge(limit=ilosc)
        
        # Tworzenie embeda z informacją o usuniętych wiadomościach
        embed = discord.Embed(
            title="Wiadomości usunięte",
            description=f"Usunięto {len(deleted)} wiadomości.",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Komenda wywołana przez {interaction.user.display_name}")
        
        # Wysłanie potwierdzenia i publicznego embeda
        try:
            # Najpierw wyślij potwierdzenie jako ephemeral
            await interaction.followup.send("Wiadomości zostały usunięte.", ephemeral=True)
            # Następnie wyślij publiczny embed
            await channel.send(embed=embed)
        except discord.NotFound:
            # Jeśli interakcja wygasła, wyślij wiadomość bezpośrednio na kanał
            await channel.send(embed=embed)
    except discord.Forbidden:
        await send_ephemeral_response(interaction, "Bot nie ma uprawnień do usuwania wiadomości!")
    except discord.NotFound:
        await send_ephemeral_response(interaction, "Nie można znaleźć niektórych wiadomości do usunięcia.")
    except discord.HTTPException as e:
        await send_ephemeral_response(interaction, f"Wystąpił błąd podczas usuwania wiadomości: {e}")

@bot.tree.command(name="setup_verification", description="Tworzy panel weryfikacji antybot z przyciskiem")
async def setup_verification(interaction: discord.Interaction):
    """Tworzy panel weryfikacji antybot z przyciskiem."""
    # Sprawdzenie czy użytkownik to właściciel bota
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("Tylko właściciel bota może używać tej komendy!", ephemeral=True)
        return
    
    # Tworzenie embeda dla panelu weryfikacji
    embed = discord.Embed(
        title="🛡️ Weryfikacja Antybot",
        description="Aby uzyskać dostęp do serwera, musisz przejść weryfikację antybot.\n\nKliknij przycisk poniżej, aby rozpocząć proces weryfikacji.",
        color=discord.Color.blue(),
        timestamp=datetime.datetime.now()
    )
    
    embed.add_field(
        name="📋 Instrukcje",
        value="1. Kliknij przycisk 'Rozpocznij weryfikację'\n2. Sprawdź swoją skrzynkę DM\n3. Rozwiąż proste zadanie matematyczne\n4. Otrzymaj dostęp do serwera",
        inline=False
    )
    
    embed.set_footer(text="Madnes of Arsha • System weryfikacji")
    
    # Tworzenie przycisku weryfikacji
    view = VerificationView()
    
    # Wysłanie panelu weryfikacji
    await interaction.response.send_message(embed=embed, view=view)

class VerificationView(discord.ui.View):
    """Widok z przyciskiem weryfikacji."""
    
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="🛡️ Rozpocznij weryfikację", style=discord.ButtonStyle.primary, custom_id="verify_button")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Obsługuje kliknięcie przycisku weryfikacji."""
        # Sprawdzenie czy użytkownik już ma rolę użytkownika
        user_role = discord.utils.get(interaction.guild.roles, id=1402359877816291369)
        if user_role and user_role in interaction.user.roles:
            await interaction.response.send_message("✅ Jesteś już zweryfikowany!", ephemeral=True)
            return
        
        # Generowanie prostego zadania matematycznego
        num1 = random.randint(1, 20)
        num2 = random.randint(1, 20)
        operation = random.choice(["+", "-"])
        
        if operation == "+":
            correct_answer = num1 + num2
            question = f"{num1} + {num2}"
        else:
            # Upewniamy się, że wynik nie będzie ujemny
            if num1 < num2:
                num1, num2 = num2, num1
            correct_answer = num1 - num2
            question = f"{num1} - {num2}"
        
        # Tworzenie embeda dla DM
        dm_embed = discord.Embed(
            title="🔢 Zadanie weryfikacyjne",
            description=f"Aby ukończyć weryfikację, rozwiąż poniższe zadanie matematyczne:\n\n**{question} = ?**",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now()
        )
        
        dm_embed.add_field(
            name="📝 Instrukcje",
            value="Odpowiedz na tę wiadomość podając tylko liczbę będącą wynikiem działania.",
            inline=False
        )
        
        dm_embed.set_footer(text=f"Serwer: {interaction.guild.name}")
        
        try:
            # Wysłanie DM do użytkownika
            dm_message = await interaction.user.send(embed=dm_embed)
            
            # Potwierdzenie wysłania DM
            await interaction.response.send_message(
                "📨 Wysłano zadanie weryfikacyjne na DM! Sprawdź swoją skrzynkę prywatnych wiadomości.",
                ephemeral=True
            )
            
            # Oczekiwanie na odpowiedź użytkownika
            def check(message):
                return (
                    message.author == interaction.user and
                    isinstance(message.channel, discord.DMChannel) and
                    message.content.strip().isdigit()
                )
            
            try:
                response = await bot.wait_for('message', check=check, timeout=300.0)  # 5 minut timeout
                user_answer = int(response.content.strip())
                
                if user_answer == correct_answer:
                    # Poprawna odpowiedź - nadanie roli
                    if user_role:
                        await interaction.user.add_roles(user_role)
                        
                        success_embed = discord.Embed(
                            title="✅ Weryfikacja ukończona!",
                            description="Gratulacje! Pomyślnie przeszedłeś weryfikację antybot.\n\nMasz teraz dostęp do serwera.",
                            color=discord.Color.green(),
                            timestamp=datetime.datetime.now()
                        )
                        success_embed.set_footer(text=f"Serwer: {interaction.guild.name}")
                        
                        await response.reply(embed=success_embed)
                    else:
                        await response.reply("❌ Błąd: Nie można znaleźć roli użytkownika na serwerze.")
                else:
                    # Niepoprawna odpowiedź
                    fail_embed = discord.Embed(
                        title="❌ Niepoprawna odpowiedź",
                        description=f"Niestety, odpowiedź '{user_answer}' jest niepoprawna.\n\nPoprawna odpowiedź to: **{correct_answer}**\n\nSpróbuj ponownie klikając przycisk weryfikacji na serwerze.",
                        color=discord.Color.red(),
                        timestamp=datetime.datetime.now()
                    )
                    fail_embed.set_footer(text=f"Serwer: {interaction.guild.name}")
                    
                    await response.reply(embed=fail_embed)
                    
            except asyncio.TimeoutError:
                timeout_embed = discord.Embed(
                    title="⏰ Czas minął",
                    description="Czas na odpowiedź minął (5 minut).\n\nSpróbuj ponownie klikając przycisk weryfikacji na serwerze.",
                    color=discord.Color.orange(),
                    timestamp=datetime.datetime.now()
                )
                timeout_embed.set_footer(text=f"Serwer: {interaction.guild.name}")
                
                await interaction.user.send(embed=timeout_embed)
                
        except discord.Forbidden:
            # Nie można wysłać DM
            await interaction.response.send_message(
                "❌ Nie mogę wysłać Ci wiadomości prywatnej!\n\nUpewnij się, że masz włączone DM od członków serwera w ustawieniach prywatności.",
                ephemeral=True
            )
        except Exception as e:
            print(f"Błąd podczas weryfikacji: {e}")
            await interaction.response.send_message(
                "❌ Wystąpił błąd podczas procesu weryfikacji. Spróbuj ponownie później.",
                ephemeral=True
            )

async def delayed_restart():
    """Funkcja pomocnicza do opóźnionego restartu bota."""
    await asyncio.sleep(3)
    print("Bot zostaje zrestartowany przez właściciela...")
    await bot.close()

@bot.tree.command(name="restart_bot", description="Restartuje bota (tylko dla właściciela)")
async def restart_bot(interaction: discord.Interaction):
    """Restartuje bota - dostępne tylko dla właściciela."""
    # Sprawdzenie czy użytkownik to właściciel bota
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("❌ Tylko właściciel bota może używać tej komendy!", ephemeral=True)
        return
    
    # Aktualizacja statusu przed restartem (wymuś aktualizację)
    await update_bot_status("🔄 Restartowanie...", force=True)
    
    # Potwierdzenie restartu
    embed = discord.Embed(
        title="🔄 Restart bota",
        description="Bot zostanie zrestartowany za chwilę...",
        color=discord.Color.orange(),
        timestamp=datetime.datetime.now()
    )
    embed.set_footer(text="Madnes of Arsha • System zarządzania")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # Uruchomienie opóźnionego restartu w tle
    asyncio.create_task(delayed_restart())

@bot.tree.command(name="rules", description="Wysyła embed z zasadami serwera na kanał regulamin")
async def rules(interaction: discord.Interaction):
    """Wysyła embed z zasadami serwera na kanał regulamin."""
    # Sprawdzenie czy użytkownik ma uprawnienia administratora
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ Nie masz uprawnień do używania tej komendy. Wymagane uprawnienia administratora.",
            ephemeral=True
        )
        return
    
    try:
        # Pobranie kanału regulamin
        rules_channel = bot.get_channel(RULES_CHANNEL_ID)
        if not rules_channel:
            await interaction.response.send_message(
                "❌ Nie można znaleźć kanału regulamin.",
                ephemeral=True
            )
            return
        
        # Tworzenie embeda z zasadami
        embed = discord.Embed(
            title="📋 Regulamin Serwera",
            description="Zapoznaj się z zasadami obowiązującymi na naszym serwerze:",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(
            name="🤝 1. Szacunek",
            value="Traktuj wszystkich członków z szacunkiem. Nie tolerujemy obelg, dyskryminacji ani nękania.",
            inline=False
        )
        
        embed.add_field(
            name="💬 2. Język",
            value="Używaj odpowiedniego języka. Unikaj wulgaryzmów i treści nieodpowiednich.",
            inline=False
        )
        
        embed.add_field(
            name="📢 3. Spam",
            value="Nie spamuj wiadomościami, emoji ani pingami. Używaj odpowiednich kanałów.",
            inline=False
        )
        
        embed.add_field(
            name="🔗 4. Linki i reklamy",
            value="Nie publikuj linków ani reklam bez zgody administracji.",
            inline=False
        )
        
        embed.add_field(
            name="🎮 5. Kanały tematyczne",
            value="Używaj kanałów zgodnie z ich przeznaczeniem. Sprawdź opisy kanałów.",
            inline=False
        )
        
        embed.add_field(
            name="⚖️ 6. Konsekwencje",
            value="Łamanie regulaminu może skutkować ostrzeżeniem, wyciszeniem lub banem.",
            inline=False
        )
        
        embed.set_footer(text="Madnes of Arsha • Regulamin serwera")
        embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
        
        # Wysłanie embeda na kanał regulamin
        await rules_channel.send(embed=embed)
        
        # Potwierdzenie dla administratora
        await interaction.response.send_message(
            f"✅ Regulamin został wysłany na kanał {rules_channel.mention}",
            ephemeral=True
        )
        
    except Exception as e:
        await interaction.response.send_message(
            f"❌ Wystąpił błąd podczas wysyłania regulaminu: {str(e)}",
            ephemeral=True
        )

# Uruchomienie bota
if __name__ == "__main__":
    if not TOKEN:
        print("❌ Błąd: Nie znaleziono tokena Discord. Ustaw zmienną środowiskową DISCORD_TOKEN.")
        sys.exit(1)
    bot.run(TOKEN)
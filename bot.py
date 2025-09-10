import discord
import threading
from flask import Flask, render_template_string

TOKEN = "____TON_TOKEN_ICI____"
CHANNEL_ID = 123456789012345678  # ID du salon pour les remerciements
BOOST_ROLE_NAME = "🚀 Nitro Booster ❤️"  # rôle spécial pour les boosters

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
client = discord.Client(intents=intents)

app = Flask(__name__)

# Dernier boost affiché
last_boost = ""

@app.route("/overlay")
def overlay():
    return render_template_string(f"""
        <html>
        <body style='background: transparent; text-align: center; color: white; font-family: sans-serif;'>
            <div id="messages"></div>
            <button id="enableSound" style="font-size:16px; margin-top:20px;">Activer le son</button>
            <audio id="notif" src="/static/boost.mp3"></audio>
            <script>
                let audio = document.getElementById('notif');
                let soundEnabled = false;
                let msgDiv = document.getElementById('messages');

                document.getElementById('enableSound').addEventListener('click', () => {{
                    audio.play();
                    audio.pause();
                    soundEnabled = true;
                    document.getElementById('enableSound').style.display = 'none';
                }});

                let lastMessage = "";
                async function fetchMessage() {{
                    try {{
                        const response = await fetch('/messages');
                        const text = await response.text();

                        if(text && text !== lastMessage) {{
                            lastMessage = text;
                            msgDiv.innerHTML = text;

                            if(soundEnabled) audio.play();

                            // Supprime le message après 5s
                            setTimeout(() => {{
                                if(msgDiv.innerHTML === text) {{
                                    msgDiv.innerHTML = "";
                                    lastMessage = "";
                                }}
                            }}, 5000);
                        }}
                    }} catch(e) {{ console.log(e); }}
                }}
                setInterval(fetchMessage, 1000);
            </script>
        </body>
        </html>
    """)

@app.route("/messages")
def messages():
    global last_boost
    return last_boost

@client.event
async def on_ready():
    print(f"Bot connecté en tant que {client.user}")

    # Vérifie et crée le rôle s’il n’existe pas
    for guild in client.guilds:
        role = discord.utils.get(guild.roles, name=BOOST_ROLE_NAME)
        if role is None:
            role = await guild.create_role(
                name=BOOST_ROLE_NAME,
                color=discord.Color.magenta(),
                mentionable=True,
                reason="Rôle automatique pour les boosters"
            )
            print(f"Rôle créé : {role.name}")

@client.event
async def on_member_update(before, after):
    global last_boost
    if before.premium_since is None and after.premium_since is not None:
        last_boost = f"{after.name} a boosté le serveur ! 🚀"
        print(last_boost)

        # Vérifie ou crée le rôle
        role = discord.utils.get(after.guild.roles, name=BOOST_ROLE_NAME)
        if role is None:
            role = await after.guild.create_role(
                name=BOOST_ROLE_NAME,
                color=discord.Color.magenta(),
                mentionable=True,
                reason="Rôle automatique pour les boosters"
            )

        # Donne le rôle au booster
        await after.add_roles(role, reason="A boosté le serveur")

        # Message dans le salon
        channel = client.get_channel(CHANNEL_ID)
        if channel:
            await channel.send(f"🚀 Merci beaucoup {after.mention} d’avoir boosté le serveur ! ❤️\n"
                               f"Tu as reçu le rôle spécial **{BOOST_ROLE_NAME}** 🎉")

# Lancer Flask dans un thread
threading.Thread(target=lambda: app.run(port=5000, debug=False, use_reloader=False)).start()

# Lancer le bot
client.run(TOKEN)

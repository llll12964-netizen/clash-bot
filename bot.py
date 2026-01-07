import telebot
import requests
import urllib.parse
import os

# ====== التوكنات من Environment Variables ======
BOT_TOKEN = os.getenv("BOT_TOKEN")
CLASH_API_KEY = os.getenv("CLASH_API_KEY")
# =============================

bot = telebot.TeleBot(BOT_TOKEN)

# رسالة الترحيب
@bot.message_handler(commands=['start'])
def start(message):
    welcome = """
🎮 *أهلاً بك في بوت كلاش اوف كلانس السعودية!*

📊 أرسل كود اللاعب وبرد عليك بالإحصائيات الكاملة

✅ *طريقة الاستخدام:*
أرسل كود اللاعب بهذا الشكل:
`#ABC123XYZ`

أو اكتب الأمر:
`/player #ABC123XYZ`
"""
    bot.reply_to(message, welcome, parse_mode='Markdown')

# أمر المساعدة
@bot.message_handler(commands=['help'])
def help(message):
    help_text = """
📖 *أوامر البوت:*

/start - بدء البوت
/help - المساعدة
/player #كود - إحصائيات لاعب

✅ أو أرسل كود اللاعب مباشرة!
"""
    bot.reply_to(message, help_text, parse_mode='Markdown')

# جلب بيانات اللاعب
def get_player_stats(player_tag):
    tag = player_tag.strip().upper()
    if not tag.startswith('#'):
        tag = '#' + tag
    
    encoded_tag = urllib.parse.quote(tag)
    
    url = f"https://api.clashofclans.com/v1/players/{encoded_tag}"
    headers = {
        "Authorization": f"Bearer {CLASH_API_KEY}",
        "Accept": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        return None

# تنسيق بيانات اللاعب
def format_player_stats(data):
    clan_name = data.get('clan', {}).get('name', 'بدون كلان')
    clan_role = data.get('role', '')
    
    roles = {
        'leader': 'قائد 👑',
        'coLeader': 'نائب قائد ⭐',
        'admin': 'شيخ 🔰',
        'member': 'عضو 👤'
    }
    role_ar = roles.get(clan_role, '')
    
    heroes = data.get('heroes', [])
    heroes_text = ""
    for hero in heroes:
        heroes_text += f"   • {hero['name']}: {hero['level']}\n"
    
    if not heroes_text:
        heroes_text = "   لا يوجد أبطال"
    
    stats = f"""
🎮 *إحصائيات اللاعب*

👤 *الاسم:* {data.get('name', 'غير معروف')}
🏷 *الكود:* `{data.get('tag', '')}`
⭐ *المستوى:* {data.get('expLevel', 0)}
🏠 *تاون هول:* {data.get('townHallLevel', 0)}

🏆 *الكؤوس:* {data.get('trophies', 0)}
🏆 *أعلى كؤوس:* {data.get('bestTrophies', 0)}

⚔️ *نجوم الحرب:* {data.get('warStars', 0)}
🎯 *الهجمات الفائزة:* {data.get('attackWins', 0)}
🛡 *الدفاعات الفائزة:* {data.get('defenseWins', 0)}

🏰 *الكلان:* {clan_name}
📍 *الرتبة:* {role_ar}
🤝 *التبرعات:* {data.get('donations', 0)}
📥 *المستلمة:* {data.get('donationsReceived', 0)}

🦸 *الأبطال:*
{heroes_text}

🤖 @clashksa_bot
"""
    return stats

# معالجة أمر player
@bot.message_handler(commands=['player'])
def player_command(message):
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "❌ أرسل الكود بعد الأمر\nمثال: `/player #ABC123`", parse_mode='Markdown')
            return
        
        player_tag = parts[1]
        wait_msg = bot.reply_to(message, "⏳ جاري البحث...")
        data = get_player_stats(player_tag)
        
        if data:
            stats = format_player_stats(data)
            bot.edit_message_text(stats, message.chat.id, wait_msg.message_id, parse_mode='Markdown')
        else:
            bot.edit_message_text("❌ اللاعب غير موجود!\nتأكد من الكود", message.chat.id, wait_msg.message_id)
            
    except Exception as e:
        bot.reply_to(message, "❌ حدث خطأ، حاول مرة ثانية")

# معالجة الرسائل العادية
@bot.message_handler(func=lambda m: m.text and (m.text.startswith('#') or len(m.text) >= 6))
def handle_player_tag(message):
    text = message.text.strip()
    
    if text.startswith('#') or (len(text) >= 6 and text.isalnum()):
        wait_msg = bot.reply_to(message, "⏳ جاري البحث...")
        data = get_player_stats(text)
        
        if data:
            stats = format_player_stats(data)
            bot.edit_message_text(stats, message.chat.id, wait_msg.message_id, parse_mode='Markdown')
        else:
            bot.edit_message_text("❌ اللاعب غير موجود!\nتأكد من الكود وأرسله بهذا الشكل:\n`#ABC123XYZ`", message.chat.id, wait_msg.message_id, parse_mode='Markdown')

# تشغيل البوت
print("✅ البوت شغال...")
bot.infinity_polling()

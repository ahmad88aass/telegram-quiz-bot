import asyncio
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Poll
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, PollAnswerHandler, ContextTypes

BOT_TOKEN = "8509031195:AAGkmlK8AfOfzbDgvXWb-69E8VJV_1bPCfo"
ADMIN_CHAT_ID = 6729808723

# خادم ويب خفيف لإبقاء الخدمة المجانية حية
app_web = Flask(name)

@app_web.route('/')
def home():
    return "Bot is running 24/7!"

def run_web():
    app_web.run(host="0.0.0.0", port=10000)

QUIZ_DATA = {
    "cmd": {
        "title": "أوامر لينكس الأساسية (30 أمراً)",
        "questions": [
            {
                "question": "ما هو الأمر المستخدم لإنشاء مجلدات متداخلة دفعة واحدة؟",
                "options": ["mkdir -p", "mkdir -r", "touch -p", "cd -p"],
                "correct_id": 0,
                "explanation": "الخيار -p مع الأمر mkdir يتيح إنشاء المجلدات المتداخلة دفعة واحدة."
            },
            {
                "question": "أي خيار مع الأمر tar يُستخدم لضغط مجلد في أرشيف واحد؟",
                "options": ["-xzvf", "-czvf", "-rzvf", "-dzvf"],
                "correct_id": 1,
                "explanation": "الرمز c يرمز لـ Create في tar لضغط الملفات (-czvf)."
            },
            {
                "question": "ما الأمر الذي يتابع ملفات السجلات (Logs) مباشرة أثناء كتابتها؟",
                "options": ["head -f", "less -w", "tail -f", "cat -l"],
                "correct_id": 2,
                "explanation": "الأمر tail -f يُبقي الملف مفتوحاً لمتابعة الأسطر الجديدة فوراً."
            },
            {
                "question": "أي أمر يُظهر معرف العملية PID واستهلاك المعالج والذاكرة بشكل حي وتفاعلي؟",
                "options": ["top", "ps", "kill", "whoami"],
                "correct_id": 0,
                "explanation": "top يعرض العمليات واستهلاك الموارد بشكل حي، بينما ps يعرض لقطة لحظية."
            },
            {
                "question": "ما الفرق بين عامل التحويل > وعامل >> في لينكس؟",
                "options": ["> للقراءة و >> للكتابة", "> يحفظ ويستبدل، و >> يضيف إلى نهاية الملف", "> يحذف الملف و >> يفتحه", "كلاهما يؤدي نفس الغرض تماماً"],
                "correct_id": 1,
                "explanation": "> يقوم بالكتابة فوق الملف، بينما >> يُلحق النصوص في نهاية الملف."
            },
            {
                "question": "أي رقم يمثل صلاحية الإغلاق الإجباري لعملية معينة باستخدام kill؟",
                "options": ["kill -1", "kill -5", "kill -9", "kill -0"],
                "correct_id": 2,
                "explanation": "الخيار -9 يرسل إشارة SIGKILL لفرض إيقاف العملية فوراً."
            }
        ]
    },
    "osi": {
        "title": "الشبكات، OSI وTCP/IP وWireshark",
        "questions": [
            {
                "question": "في نموذج OSI، في أي طبقة يعمل بروتوكول IP والراوتر؟",
                "options": ["طبقة ربط البيانات (Data Link)", "طبقة النقل (Transport)", "طبقة الشبكة (Network)", "طبقة الجلسة (Session)"],
                "correct_id": 2,
                "explanation": "طبقة الشبكة (Layer 3) هي المسؤولة عن التوجيه وعناوين IP."
            },
            {
                "question": "ما هي وحدة البيانات (PDU) في طبقة النقل (Transport)؟",
                "options": ["Packet", "Segment", "Frame", "Bits"],
                "correct_id": 1,
                "explanation": "البيانات في طبقة النقل تسمى Segment، وفي الشبكة Packet، وفي ربط البيانات Frame."
            },
            {
                "question": "أي طبقة من نموذج TCP/IP تقابل طبقات (التطبيق والتمثيل والجلسة) في OSI؟",
                "options": ["الإنترنت (Internet)", "الوصول للشبكة (Network Access)", "التطبيق (Application)", "النقل (Transport)"],
                "correct_id": 2,
                "explanation": "في نموذج TCP/IP تم دمج الطبقات 7 و6 و5 تحت طبقة التطبيق (Application)."},
            {
                "question": "ما هو فلتر Wireshark المستخدم لعرض حزم بدء الاتصال (SYN) فقط؟",
                "options": ["tcp.port == 80", "tcp.flags.syn==1", "ip.addr == 192.168.1.1", "http.request"],
                "correct_id": 1,
                "explanation": "الفلتر tcp.flags.syn==1 يعزل حزم مصافحة TCP الأولية."
            },
            {
                "question": "ماذا يسمى المفهوم الذي يتم فيه إضافة ترويسة (Header) من كل طبقة للبيانات؟",
                "options": ["التغليف (Encapsulation)", "التجزئة (Segmentation)", "التشفير (Encryption)", "التوجيه (Routing)"],
                "correct_id": 0,
                "explanation": "عملية نزول البيانات وإضافة رؤوس كل طبقة تُعرف بـ Encapsulation."
            }
        ]
    },
    "adv": {
        "title": "المستوى المتقدم وأدوات eJPT",
        "questions": [
            {
                "question": "أي أمر يُستخدم للبحث عن الملفات التي تحمل إذن SUID على لينكس؟",
                "options": ["find / -perm -4000 -type f", "find / -perm -777", "find / -name suid", "getcap -r /"],
                "correct_id": 0,
                "explanation": "الخيار -perm -4000 مخصص للبحث عن البت الخاص بـ SUID."
            },
            {
                "question": "أي أداة تُستخدم لمراقبة العمليات التي تعمل بصلاحيات root دون الحاجة لامتلاك صلاحيات root؟",
                "options": ["linpeas.sh", "pspy", "LinEnum.sh", "enum4linux"],
                "correct_id": 1,
                "explanation": "أداة pspy تراقب استدعاءات العمليات والـ Cron jobs دون الحاجة لـ root."
            },
            {
                "question": "ما هو الإعداد الآمن لمنع تسجيل الدخول كمدير في /etc/ssh/sshd_config؟",
                "options": ["PermitRootLogin no", "PasswordAuthentication yes", "AllowUsers root", "Port 22"],
                "correct_id": 0,
                "explanation": "السطر PermitRootLogin no يمنع دخول حساب root عبر SSH نهائياً."
            },
            {
                "question": "ما هي وظيفة بروتوكول STP (Spanning Tree Protocol) في الشبكات؟",
                "options": ["توزيع عناوين IP", "تشفير الاتصال بين السويتشات", "منع الحلقات (Loops) الناتجة عن المسارات المتكررة", "تقسيم VLANs"],
                "correct_id": 2,
                "explanation": "بروتوكول STP يمنع حدوث العواصف البثية والحلقات عبر إيقاف المنافذ الزائدة مؤقتاً."
            },
            {
                "question": "ما هو الهجوم الذي يغرق خادم DHCP بالطلبات حتى تنفد العناوين؟",
                "options": ["ARP Spoofing", "DNS Spoofing", "DHCP Starvation", "Kerberoasting"],
                "correct_id": 2,
                "explanation": "هجوم DHCP Starvation يستنزف تجمع العناوين بالكامل لتمرير خادم مزيف."
            },
            {
                "question": "أي وحدة في Burp Suite تُستخدم لإعادة إرسال طلب HTTP وتعديل قيمه يدوياً لاختبار ثغرة؟",
                "options": ["Proxy", "Repeater", "Intruder", "Decoder"],
                "correct_id": 1,
                "explanation": "Repeater مخصص لإعادة إرسال وتكرار الطلبات وتعديل معاملاتها يدوياً."
            }
        ]
    }
}

user_sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🐧 أوامر لينكس الأساسية", callback_data="set_cmd")],
        [InlineKeyboardButton("🌐 الشبكات وOSI وWireshark", callback_data="set_osi")],
        [InlineKeyboardButton("⚔️ المستوى المتقدم وأدوات eJPT", callback_data="set_adv")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 أهلاً بك في بوت الاختبارات التفاعلي!\nاختر الدرس الذي ترغب في اختباره:",
        reply_markup=reply_markup
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data
if data.startswith("set_"):
        lesson_key = data.replace("set_", "")
        user_sessions[user_id] = {
            "lesson": lesson_key,
            "q_index": 0
        }
        title = QUIZ_DATA[lesson_key]["title"]
        keyboard = [
            [
                InlineKeyboardButton("نعم، ابدأ 🚀", callback_data="confirm_start"),
                InlineKeyboardButton("رجوع 🔙", callback_data="main_menu")
            ]
        ]
        await query.edit_message_text(
            f"اخترت درس: *{title}*\n\nهل أنت جاهز لبدء الاختبار الآن؟\n⏱️ لديك 30 ثانية لكل سؤال.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif data == "main_menu":
        keyboard = [
            [InlineKeyboardButton("🐧 أوامر لينكس الأساسية", callback_data="set_cmd")],
            [InlineKeyboardButton("🌐 الشبكات وOSI وWireshark", callback_data="set_osi")],
            [InlineKeyboardButton("⚔️ المستوى المتقدم وأدوات eJPT", callback_data="set_adv")]
        ]
        await query.edit_message_text(
            "اختر الدرس الذي ترغب في اختباره:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "confirm_start":
        await query.edit_message_text("⚡ سيبدأ الاختبار الآن، بالتوفيق!")
        await send_quiz_poll(query.message.chat_id, user_id, context)

async def send_quiz_poll(chat_id: int, user_id: int, context: ContextTypes.DEFAULT_TYPE):
    session = user_sessions.get(user_id)
    if not session:
        return

    lesson = session["lesson"]
    q_index = session["q_index"]
    questions = QUIZ_DATA[lesson]["questions"]

    if q_index < len(questions):
        q = questions[q_index]
        await context.bot.send_poll(
            chat_id=chat_id,
            question=f"[{q_index + 1}/{len(questions)}] {q['question']}",
            options=q['options'],
            type=Poll.QUIZ,
            correct_option_id=q['correct_id'],
            open_period=30,
            is_anonymous=False,
            explanation=q['explanation']
        )
    else:
        keyboard = [[InlineKeyboardButton("العودة للقائمة الرئيسية 🔄", callback_data="main_menu")]]
        await context.bot.send_message(
            chat_id=chat_id,
            text="🎉 أحسنت! أنهيت جميع أسئلة هذا القسم بنجاح.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def handle_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.poll_answer.user.id
    if user_id in user_sessions:
        user_sessions[user_id]["q_index"] += 1
        await asyncio.sleep(2)
        await send_quiz_poll(user_id, user_id, context)

def main():
    threading.Thread(target=run_web, daemon=True).start()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(PollAnswerHandler(handle_poll_answer))
    app.run_polling()

if name == "main":
    main()

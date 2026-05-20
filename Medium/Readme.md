# ---
Medium Room 1 – Multi-Stage Information Leak Chain

· خادم ويب على `http://localhost:7070`. لا توجد ثغرة مباشرة.
· robots.txt يفضح `/backup/`، الذي يحتوي على `config.old`.
· `config.old` يحوي تلميحاً إلى `/hidden/flag.txt` حيث العلم.
· المهارة: سلسلة التسريبات (Leak Chaining)، الصبر، نقل البيانات بين المراحل.
· العلم: `THM{multi_stage_ch4in}` – قيمة النقاط: +250

# ---
Medium Room 2 – Hidden Admin Panel via JS Analysis

· خادم ويب على `http://localhost:7071`. لا توجد روابط واضحة للوحة الإدارة.
· ملف JavaScript (`assets/app.js`) يحتوي على تعليق يفضح المسار المخفي: `/x7/admin-panel`.
· لوحة الإدارة محمية ببيانات اعتماد ضعيفة (`admin/admin123`).
· المهارة: مراجعة الكود المصدري، اكتشاف نقاط النهاية المخفية، استغلال بيانات الدخول الافتراضية.
· العلم: `THM{js_h1dd3n_p4n3l}` – قيمة النقاط: +250
# ---
Medium Room 3 – Weak JWT Authentication

· خدمة JWT على `http://localhost:6062`. تسجيل الدخول بـ guest/guest يعطي توكن بدور "user".
· المفتاح السري "admin" ضعيف، مما يسمح بتزوير التوكن وتغيير الدور إلى "admin".
· تقديم التوكن المزور إلى /flag يكشف العلم.
· المهارة: تحليل JWT، تزوير التوكن، تجاوز المصادقة.
· العلم: `THM{jwt_w34k_s3cr3t}` – قيمة النقاط: +250

# ---
Medium Room 4 – Combo Attack (Directory + Parameter Fuzzing)

· خادم على `http://localhost:6063`. يتطلب اكتشاف `/api/` و `/backup/` عبر gobuster.
· ملف `users.db` في `/backup/` يسرب قيم `id` مميزة.
· تلاعب بالبارامتر `id` في `/api/user` لا يكفي؛ يجب استنتاج وجود `/api/admin` وتجربة `id=flag`.
· المهارة: الدمج بين directory fuzzing و parameter tampering، ربط التسريبات.
· العلم: `THM{dir_and_param_combo}` – قيمة النقاط: +250

# ---
Medium Room 5 — Exposed .env File Misconfiguration

· خادم ويب على `http://localhost:6064` يبدو طبيعياً تماماً.
· ومع ذلك، ملف البيئة `.env` متاح للعامة في جذر الموقع.
· الطلب المباشر `/.env` يكشف متغيرات حساسة، من بينها العلم.
· المهارة: اكتشاف الملفات المنسية، عدم الاعتماد الكلي على الأدوات، فهم أخطاء المطورين الشائعة.
· العلم: `THM{dot_env_leaked}` – قيمة النقاط: +200

# ---
Medium Room 6 – API Mass Assignment Vulnerability

· خدمة API على `http://localhost:6065` تقبل JSON عبر `/register`.
· التسجيل العادي يعطي دور "user"، لكن يمكن إرسال حقل `"role":"admin"` غير المقيّد.
· الخادم يقبل الحقل الإضافي ويعيد العلم فوراً مع الاستجابة.
· المهارة: استغلال ثغرة Mass Assignment، إدراك أن الخادم قد يقبل حقولاً غير متوقعة، تغيير الصلاحيات عبر JSON.
· العلم: `THM{m4ss_ass1gn_4pi}` – قيمة النقاط: +250

# ---
Medium Room 7 – Blind Error-Based Enumeration (SQLi)

· خادم ويب على `http://localhost:6067` يوفر نقطة `/user` تستجيب للقيم المختلفة.
· إرسال `id=1'` ينتج خطأ 500 مع رسالة قاعدة بيانات، مما يكشف تركيب الاستعلام.
· الحقن بـ `id=1' OR '1'='1` يعرض جميع المستخدمين، ومن بينهم العلم المخفي.
· المهارة: Blind SQL injection بسيط، تحليل رموز الحالة (200, 404, 500)، الاستدلال من الأخطاء (Error-Based).
· العلم: `THM{blind_err0r_enum}` – قيمة النقاط: +250

# ---
Medium Room 8 – File Upload Misconfiguration (SQLi → RCE)

· خدمة ويب على `http://localhost:6068` تسمح برفع أي نوع ملفات بدون فلترة.
· الملفات تُخزّن بأسماء عشوائية، لكن وجود SQLi في `/files?user=...` يتيح استخراجها.
· تنفيذ ملف admin `.py` المُستخرج يؤدي إلى قراءة العلم مباشرة من مجلد محمي.
· المهارة: رفع ملفات ضارة، استغلال SQLi لاسترداد أسماء الملفات، تحقيق RCE محدود عبر بايثون.
· العلم: `THM{upload_rce_sqli}` – قيمة النقاط: +300

# ---
Medium Room 9 – Internal Endpoint Exposure (BOLA + Debug)

· خادم API على `http://localhost:6069` يكشف عن نقاط داخلية غير محمية.
· `/api/v1/internal/users` يتيح جلب أي مستخدم عبر `id` بدون تحقق من صلاحيات (BOLA).
· وجود `/api/v1/debug` يعرض معلومات حساسة تشمل العلم.
· المهارة: اكتشاف نقاط API الداخلية، استغلال ضعف تحكم الوصول (Broken Object Level Authorization)، استطلاع طريق التصحيح.
· العلم: `THM{internal_ep_exposed}` – قيمة النقاط: +250

# ---
Medium Room 10 – Password Reuse + JWT + Service Pivoting

· سيناريو مركّب: بوابة ويب (port 6070) تمنح JWT بمفتاح ضعيف `secret123`.
· تعديل JWT لدور admin يكشف تلميحاً عن خدمة TCP داخلية (port 6071) تستخدم نفس بيانات الدخول.
· الاتصال بالخدمة الثانية وتسجيل الدخول يسمح بتنفيذ أمر `READ flag.txt` واستخراج العلم.
· المهارة: إعادة استخدام كلمات المرور، تعديل JWT، الربط بين الخدمات (Pivoting)، التفكير التسلسلي.
· العلم: `THM{p4ssw0rd_r3us3_p1vot}` – قيمة النقاط: +300

# ---
Medium Room 11 – Realistic Pentest Chain: Web → SSH → Escape

· بوابة ويب على `http://localhost:6072` تخفي تعليقاً في المصدر يكشف بيانات SSH.
· يمكن تسجيل الدخول إلى البوابة (admin/admin123) للحصول على نفس المعلومات.
· خدمة SSH محاكية على `localhost:6073` تستخدم مستخدم `limited` وكلمة مرور `limited123`.
· بعد الولوج، نجد قشرة مقيدة (rbash) تسمح بـ `ls, pwd, less` وما شابه.
· الهروب من القشرة يتم عبر `less /opt/flag.txt` ثم استخدام `!cat /opt/flag.txt` لقراءة العلم.
· المهارات: سلسلة هجوم متكاملة (Web → Creds → SSH → Escape)، استغلال برامج عرض النصوص للخروج من القشرة المقيدة.
· العلم: `THM{r34l_ch4in_ssh_escape}` – قيمة النقاط: +350

# ---
Medium Room 12 – Chained Exploitation: SSRF + Credentials + Cyber Deception

· خدمة ويب رئيسية على `http://localhost:6080` تحتوي على تعليق HTML يكشف اعتماديات الدخول (admin/password123).
· بعد تسجيل الدخول، نجد “Internal URL Fetcher” الذي يسمح بجلب عناوين داخلية (SSRF).
· الخدمة الداخلية على `127.0.0.1:6081` تقدم العلم عبر `/flag`.
· يوجد عنصر خداع سيبراني: علم مزيف في `/fake-flag` و `/robots.txt` يحاول تضليل المهاجم.
· العلم الحقيقي يُستخرج عبر استغلال SSRF للوصول إلى `http://127.0.0.1:6081/flag`.
· المهارات: SSRF أساسي، استخراج بيانات الدخول من كود HTML، كشف الخداع السيبراني (Cyber Deception)، ربط الخطوات في هجوم متسلسل.
· العلم: `THM{ch4ined_ssrf_intern4l}` – قيمة النقاط: +350

# ---
Medium Room 13 – SSRF → Internal Admin Panel (Filter Bypass + Cyber Deception)

· موقع الشركة على `http://localhost:6082` يتضمن صفحة دخول بها تعليق يكشف بيانات الدخول.
· ملف `robots.txt` يسرب مسارين: `/backup/` و `/fake-admin` (خداع).
· الملف الاحتياطي `config.bak` يفضح منطق فلترة SSRF ويكشف وجود خدمة داخلية على المنفذ 6083.
· الفلتر يمنع الطلبات إلى مسارات تحتوي على كلمة `admin`، لكن يمكن تجاوزه باستخدام الصيغة العشرية لعنوان IP (`2130706433`).
· بإرسال `http://2130706433:6083/admin` عبر واجهة الجلب، يتم الوصول إلى لوحة الإدارة الداخلية والحصول على العلم الحقيقي.
· المهارات: SSRF متقدم مع تجاوز الفلاتر، قراءة النسخ الاحتياطية، Cyber Deception detection.
· العلم: `THM{ssrf_byp4ss_intern4l}` – قيمة النقاط: +350

# ---
Medium Room 14 – Path Traversal → System File Leak (with Cyber Deception)

· خادم ملفات على `http://localhost:6084` يعطي نقطة `/download?file=...` غير محمية.
· يمكن استغلال path traversal لقراءة ملفات نظام وهمي (`../../fake_root/etc/passwd`).
· يوجد خداع سيبراني: ملف `robots.txt` يكشف `/backup/` مع بيانات مزيفة، لكنها تحتوي تلميحًا حقيقيًا: العلم في `/root/flag.txt`.
· صفحة `/debug` تسرب معلومات تقنية مفيدة.
· المهارات: Path Traversal، Cyber Deception detection، ربط المعلومات من مصادر متعددة.
· العلم: `THM{path_tr4v3rs4l_l34k}` – قيمة النقاط: +350

# ---
Medium Room 15 – Race Condition Login Bypass (Timing + Cyber Deception)

· صفحة دخول على `http://localhost:6085` تستخدم خادمًا متعدد الخيوط مع تأخير 0.5s بعد التحقق.
· ملفات `dev-notes.txt` و `robots.txt` فضحت الآلية وبيانات الدخول.
· بإرسال طلبين متزامنين (صحيح + خاطئ) يمكن استغلال نافذة السباق لتجاوز المصادقة.
· يوجد علم مزيف في `/fake-admin` لاختبار انتباهك.
· المهارات: Race Condition، استغلال التوقيت، البرمجة المتزامنة، كشف الخداع.
· العلم: `THM{r4ce_c0nd1t10n_byp4ss}` – قيمة النقاط: +400

# ---
Medium Room 16 – Full Real Pentest Simulation (Medium++)

· محاكاة كاملة لاختبار اختراق: ويب (6086) و SSH (6087).
· تعداد الويب يكتشف `.env` (به بيانات SSH)، لوحة إدارة (admin/admin123)، وأمر اختياري.
· SSH بالقشرة المحدودة يكشف `sudo -l` يسمح بتشغيل `find` كجذر.
· استغلال `find` لقراءة `/root/flag.txt` يعطي العلم الحقيقي.
· يحتوي على خداع سيبراني: علم مزيف في `.env` و `/fake-flag`.
· المهارات: اختبار اختراق كامل، استغلال sudo، ربط الخدمات، Cyber Deception.
· العلم: `THM{full_pentest_sim}` – قيمة النقاط: +500

# ---
Medium Room 17 – Insecure APK Analysis (Medium++)

· محاكاة ADB على المنفذ 5556، يمكن سحب APK (base.apk) وتحليله.
· تحليل APK باستخدام `strings` أو `jadx` يكشف عن endpoint داخلي (http://localhost:9999/secret-admin) وبيانات دخول (admin:supersecret).
· خادم الويب الداخلي على 9999 يعرض العلم الحقيقي بعد المصادقة.
· يحتوي على خداع سيبراني: علم مزيف داخل APK.
· المهارات: ADB simulation، تحليل APK، استخراج النصوص، pivoting إلى خدمة داخلية.
· العلم: `THM{apk_revers3_eng}` – قيمة النقاط: +450


# ---
🟡 Medium Final Exam – NeoCorp Security Assessment

· بيئة كاملة: ويب (6088) وSSH (6089). متعددة المراحل.
· SQLi, XXE, تحليل JS, تسريب اعتماديات, API manipulation, تخطي headers, وصول SSH مع sudo privilege escalation.
· يمكن استخدام Metasploit لاستغلال Command Injection و SSH.
· خداع سيبراني: علم مزيف, مسارات مضللة.
· العلم النهائي: `THM{medium_level_chain_complete}` – قيمة النقاط: +600


# ---
🧠 Medium-Advanced Room 1 – Shadow Data Leak Graph

· لا توجد تلميحات حول المنافذ؛ الاستطلاع اليدوي (nmap, gobuster) هو المفتاح.
· الموقع على `http://...` يكشف عن `robots.txt` مما يؤدي إلى `/backup/` وملف `archive.zip`.
· تحليل الأرشيف يكشف عن مستودع `.git` مكشوف يحتوي على نقطة نهاية تصحيح مخفية في السجلات.
· نقطة التصحيح تسرب بيانات اعتماد، مما يتيح الدخول إلى لوحة الإدارة.
· تحتوي لوحة الإدارة على استعلام SQL قابل للحقن يكشف عن العلم النهائي.
· المهارات: استخراج الملفات، تحليل Git، تسريب API، حقن SQL.
· العلم: `THM{graph_sh4d0w_l34k}` – قيمة النقاط: +500

# ---
Medium-Advanced Room 2 – Frontend Attack Surface Mapping

· تطبيق React على المنفذ 7081. لا توجد روابط واضحة للوحة الإدارة.
· تحليل ملف `static/app.js` يكشف عن كائن `window.__CONFIG__` يحوي مسار `/super/secret/panel` وتعليقاً ببيانات الدخول.
· لوحة الإدارة تستخدم SQLite قابلة للحقن عبر البحث، مما يتيح استخراج العلم.
· يوجد علم مزيف في `/fake-secret` لاختبار اليقظة.
· المهارات: تحليل JS، اكتشاف أسرار الواجهة الأمامية، SQL injection.
· العلم: `THM{fr0nt3nd_s3cr3ts}` – قيمة النقاط: +500

# ---
Medium-Advanced Room 3 – JWT Trust Boundary Break

· لا توجد تلميحات حول المنفذ. الخدمة على 127.0.0.1:7082.
· ملف robots.txt يسرب معلومة حساسة: `JWT_SECRET=shadow123` ووجود مسار debug.
· يمكن الحصول على JWT بتسجيل الدخول كـ guest/guest.
· الخادم يقبل توقيع `alg=none` مما يسمح بتزوير رمز دخول بدور admin.
· بعد الوصول إلى لوحة الإدارة، يمكن استغلال SQLi للحصول على العلم الحقيقي.
· خداع: علم مزيف في `/debug/flag`.
· المهارات: JWT manipulation (alg=none)، تسريب الأسرار، SQLi.
· العلم: `THM{jwt_none_byp4ss}` – قيمة النقاط: +550

# ---
Medium-Advanced Room 4 – API Surface Expansion Attack

· منفذ الخدمة مخفي (7083). يجب اكتشافه.
· تعداد API عبر gobuster والتحليل اليدوي: `/api/`, `/debug/`, `/static/`.
· تسريب JWT secret في `/debug/config`، وتعليق في `/static/api-map.js` يكشف `/api/v2/internal/flag`.
· تسجيل الدخول يعطي JWT بدور `user`. يمكن تزويره لدور `admin`.
· نقطة `/api/v2/internal/flag` تعطي علماً مزيفاً افتراضياً، لكنها قابلة للحقن SQLi.
· استخراج العلم الحقيقي عبر `UNION SELECT`.
· خداع سيبراني متعدد الطبقات: علم مزيف في `/debug/flag` وآخر في استجابة SQL الأولية.
· المهارات: API fuzzing، تسريب الأسرار، تزوير JWT، SQL injection متقدم.
· العلم: `THM{api_exp4ns10n_sqli}` – قيمة النقاط: +600

# ---
Medium-Advanced Room 5 – Cloud Misconfiguration Leak

· خدمتان على 7084 (ويب) و7085 (تخزين S3-style). كلاهما مخفيان.
· ملف `.env` مكشوف على خادم الويب، يحتوي على مفاتيح AWS وهمية ورابط التخزين الداخلي وعلماً مزيفاً.
· خادم التخزين يتطلب توقيع HMAC-SHA256 للوصول إلى الكائنات.
· التوقيع مبني على الطريقة والتاريخ والمفتاح السري المسرب، مما يحاكي AWS Signature V4.
· استخراج الكائن `flag.txt` يعطي العلم الحقيقي.
· خداع سيبراني: علم مزيف في `.env` وكائن `fake-flag.txt`.
· المهارات: تسريب ملفات حساسة، فهم آليات التوقيع السحابي، التعامل مع خدمات داخلية.
· العلم: `THM{cl0ud_m1sc0nf1g_l34k}` – قيمة النقاط: +650


# ---
Medium-Advanced Room 6 – Business Logic Privilege Escalation

· الخدمتان مخفيتان على المنفذين 7101 (الويب) و7102 (لوحة الإدارة).
· يمكن تسجيل الدخول كـ guest/guest.
· صفحة الترقية تحتوي على ثغرة منطق أعمال: قبول أي خطة مع كوبون صالح.
· الترقية إلى enterprise تعطي مفتاح API للوصول إلى خدمة الإدارة الداخلية.
· تحتوي الخدمة الداخلية على IDOR: يمكن عرض بيانات أي مستخدم عبر معرّف (id=).
· العلم الحقيقي موجود في بيانات المستخدم صاحب id=7.
· خداع: علم مزيف في المسار /admin-panel/ وعند الترقية إلى premium.
· المهارات: استغلال منطق الأعمال (Business Logic Abuse)، IDOR، ربط الخدمات الداخلية.
· العلم: `THM{bus1n3ss_l0g1c_1d0r}` – قيمة النقاط: +700

# ---
Medium-Advanced Room 7 – Blind System Inference Attack

· الخدمة مخفية على منفذ غير تقليدي (7201).
· الموقع يبدو ثابتًا ويعيد نفس الصفحة دائمًا. لا توجد رسائل خطأ مرئية.
· لكن النظام يتسرب منه معلومات عبر قنوات جانبية: زمن الاستجابة، كوكيز `found`، ورأس `X-Response-Time`.
· باستخدام هذه المؤشرات يمكن التمييز بين `id` صحيح (`found=true`) وآخر خاطئ.
· بعد ذلك، يمكن استغلال ثغرة Blind SQL Injection (حقن منطقي) لاستخراج العلم حرفًا حرفًا.
· خداع سيبراني: صفحة `/debug/` تعرض علمًا مزيفًا، وملف `robots.txt` يشير إليها.
· المهارات: تحليل القنوات الجانبية (Side-Channel Analysis)، Blind SQLi، البرمجة لاستخراج البيانات.
· العلم: `THM{bl1nd_ch4nn3ls_m4st3r}` – قيمة النقاط: +700

# ---
Medium-Advanced Room 8 – File Upload → Execution Chain

· الخدمة مخفية على منفذ غير متوقع (7301).
· تطبيق رفع ملفات مع تحقق MIME ضعيف (يعتمد على Content-Type).
· الملفات تُحفظ بأسماء عشوائية، لكن يمكن استردادها عبر SQL Injection في معامل uploader.
· تجاوز MIME: إرسال ملف بامتداد `.py` مع `Content-Type: image/png`.
· تنفيذ الملف المرفوع عبر زيارة المسار `/uploads/<name>` يعطي RCE ويقرأ العلم من `/root/flag.txt`.
· خداع: صفحة admin-login (من robots.txt) تعطي علماً مزيفاً.
· المهارات: File Upload Bypass، SQL Injection، RCE عبر Python scripts، ربط الثغرات.
· العلم: `THM{upload_ch4in_rce}` – قيمة النقاط: +750

# ---
Medium-Advanced Room 9 – Internal Dev Endpoint Exposure

· الخدمة مخفية على منفذ 7401.
· ملف robots.txt يكشف مجلدات المطورين: /debug, /internal, /admin.
· /debug/env تعطي بيئة وهمية بعلم مزيف.
· /internal/metrics تسرب رمز وصول (devtoken123) وتلمح إلى ضرورة استخدام ترويسة X-Dev-Token.
· لوحة devtools على /admin/devtools تتطلب الرمز المسرب وتحتوي على بحث مستخدم ضعيف ضد SQL Injection.
· العلم الحقيقي يستخرج عبر UNION SELECT من قاعدة البيانات.
· المهارات: اكتشاف نقاط المطورين المخفية، تلاعب بالترويسات، SQLi.
· العلم: THM{d3v_endp01nt_l34k} – قيمة النقاط: +750

# ---
Medium-Advanced Room 10 – Cross-Service Credential Reuse Attack

· ثلاث خدمات مخفية على منافذ غير متسلسلة: ويب (7501)، SSH محاكي (7502)، MySQL محاكي (7503).
· كلمة المرور `MyS3cr3tP@ss` مُعاد استخدامها عبر جميع الخدمات.
· صفحة الويب تحتوي على تعليق HTML يسرب بيانات الدخول، ولوحة تحكم تسرب معلومات الخدمات الأخرى.
· قسم التعليقات مصاب بـ Stored XSS.
· العلم الحقيقي موجود على خادمي SSH وDB، بينما العلم الظاهر في الويب مزيف.
· المهارات: Cross-Service Pivoting، Credential Reuse، Stored XSS، Service Scanning.
· العلم: `THM{cr0ss_s3rv1ce_r3us3}` – قيمة النقاط: +800

# ---
Medium-Advanced Room 11 – True Pivot Attack Chain

· ثلاث خدمات على منافذ غير متسلسلة (8101, 8103). الطريق غير خطي.
· تسريب JWT secret عبر robots.txt و debug. تزوير JWT باستخدام alg=none لتصعيد إلى admin.
· لوحة Admin Metrics تحتوي على Time-Based Blind SQLi، مما يتطلب كتابة أداة استخراج.
· البيانات المستخرجة (token_data) تحتوي على SSH credentials (developer:dev123).
· على خادم SSH، تصعيد صلاحيات عبر `sudo find` لقراءة العلم من /root/flag.txt.
· خداع: العلم المعروض في الويب (dashboard) مزيف.
· المهارات: JWT alg=none، Time-Based Blind SQLi، SSH Privilege Escalation، Cyber Deception.
· العلم: `THM{true_p1v0t_ch4in}` – قيمة النقاط: +900

# ---
Medium-Advanced Room 12 – Full Web → System → PrivEsc Chain

· محاكاة اختراق لمؤسسة كاملة: استطلاع، اكتشاف نطاق فرعي، كسر تجزئة، SSH مع تصعيد صلاحيات.
· الخدمات على منفذين غير متسلسلين (8201, 8203). يجب إضافة إدخال /etc/hosts للوصول إلى بوابة المطورين.
· لوحة المطورين تحتوي على تجزئة MD5 Crypt لكلمة مرور مستخدم SSH، مما يتطلب كسر التجزئة.
· بعد استعادة كلمة المرور، الدخول SSH وتصعيد عبر `sudo tar` لقراءة العلم.
· خداع: علم مزيف في ملف `robots.txt` وهمي، بيانات دخول وهمية.
· المهارات: Virtual Host Enumeration, Hash Cracking, SSH PrivEsc (sudo tar), Stored XSS (optional).
· العلم: `THM{full_ch4in_pentest}` – قيمة النقاط: +1000

# ---
Medium-Advanced Room 13 – Logic-Based Exploitation (Pre‑Exam)

· الخدمة مخفية على منفذ 8301. لا توجد ثغرات تقليدية؛ بل أخطاء منطقية.
· تسريب مفتاح JWT ضعيف، يسمح بتزوير دور admin (Role Confusion).
· API الإدارة تتطلب ترويسة داخلية (X-Internal-Role) التي يمكن إضافتها بسهولة (Trust Issue).
· بعد الوصول، نكتشف SSTI حقيقية في صفحة الإدارة، مما يسمح بقراءة العلم.
· خداع سيبراني: علم مزيف في نقطة debug.
· المهارات: JWT forgery, Role Confusion, API trust abuse, SSTI.
· العلم: `THM{l0g1c_b4sed_tRust_br0ken}` – قيمة النقاط: +1000

# ---
Medium-Advanced Room 14 – SSRF → Internal Cloud Pivot

· ثلاث خدمات مخفية على منافذ غير متسلسلة (8401, 8402, 8403).
· SSRF في `/api/fetch` مع فلتر يمكن تجاوزه بالتمثيل العشري أو السداسي عشر لـ localhost.
· خدمة Metadata داخلية تسرب بيانات اعتماد لوحة إدارة داخلية.
· لوحة الإدارة تستخدم NoSQL Database قابلة للحقن (NoSQL Injection) لاستخراج العلم الحقيقي.
· خداع سيبراني: علم مزيف في Debug وMetadata.
· المهارات: SSRF Filter Bypass, Cloud Metadata Abuse, NoSQL Injection.
· العلم: `THM{ssrf_m3tadata_nosql}` – قيمة النقاط: +1000

# ---
Medium-Advanced Room 15 – Path Traversal → System Exposure Chain

· لا توجد أي إشارة إلى المنافذ؛ تُكتشف عبر nmap (8501 للويب، 8502 للـAPI الداخلية).
· ثغرة Path Traversal في `/download?file=` تسمح بقراءة ملفات نظام وهمي.
· ملف إعدادات `config.yml` يسرب بيانات اعتماد خدمة API داخلية تستخدم NoSQL.
· استغلال NoSQL Injection في `/api/query` لاستخراج العلم الحقيقي.
· خداع سيبراني متقدم: debug flag مزيف، مسار `/trap` مخفي، وملفات وهمية.
· المهارات: Path Traversal، Source Code/Config Review، NoSQL Injection، Service Pivoting.
· العلم: `THM{path_to_nosql_chain}` – قيمة النقاط: +1050

# ---
Medium-Advanced Room 16 – Race Condition Auth Bypass + IDOR

· الخدمة مخفية على منفذ 8601. لا توجد أي تلميحات مسبقة.
· يوجد تأخير 0.5 ثانية أثناء تسجيل الدخول، يتم خلاله إنشاء جلسة قبل التحقق من صحة كلمة المرور.
· يمكن استغلال ذلك عبر طلبات متوازية لتجاوز المصادقة دون بيانات اعتماد صحيحة.
· بعد تجاوز المصادقة، تعرض لوحة الملف الشخصي ثغرة IDOR عبر `user_id`، مما يسمح بقراءة بيانات مستخدمين آخرين يحتوي أحدهم على العلم الحقيقي.
· خداع سيبراني: علم مزيف في صفحة debug وملف المسؤول.
· المهارات: Race Condition Exploitation, Parallel Request Programming, IDOR.
· العلم: `THM{r4c3_4nd_id0r_ch4in}` – قيمة النقاط: +1100

# ---
Medium-Advanced Room 17 – ADB + Burp + Auth Bypass (Mobile Simulation)

· منفذان مخفيان (8701 للـ API، 8702 للـ ADB). يجب اكتشافهما عبر nmap.
· ADB يحاكي جهاز أندرويد ويمكن سحب APK مزيف منه، يحتوي على أسرار (JWT secret، API URL).
· بوابة API تستخدم JWT بمفتاح ضعيف (supersecretkey) يمكن تزويره (alg=none).
· بعد تصعيد الدور إلى admin، توجد NoSQL Injection في بحث المستخدمين، وIDOR في الملف الشخصي.
· خداع سيبراني: علم مزيف في Debug وفي ملف المسؤول.
· المهارات: ADB simulation، APK string analysis، Burp/ZAP interception، JWT manipulation، NoSQLi، IDOR.
· العلم: `THM{adb_burp_jwt_nosql_idor}` – قيمة النقاط: +1200

# ---
Medium-Advanced Room 18 – Full Enterprise Pentest Simulation (Capstone)

· ثلاث خدمات مخفية (8801, 8802, 8803). يجب اكتشافها عبر nmap.
· اكتشاف نطاق فرعي (staging.neocorp.local) يؤدي إلى بوابة تطوير.
· تسريب JWT secret واعتماديات API عبر نسخ احتياطية.
· تزوير JWT للوصول إلى API داخلي.
· استغلال NoSQL Injection و IDOR لاستخراج اعتماديات SSH.
· تسجيل الدخول SSH وتصعيد الصلاحيات عبر sudo find لقراءة العلم.
· خداع متعدد: أعلام مزيفة في debug و config.
· المهارات: Virtual Host Enumeration, JWT Forgery, NoSQL Injection, IDOR, SSH PrivEsc.
· العلم: `THM{c4pst0n3_ent3rpr1se_pwn3d}` – قيمة النقاط: +2000

# ---
🔶 Medium-Advanced Final Exam – NeoCorp Production Security Audit

· بيئة إنتاج كاملة (8901, 8902, 8903) تخفي خدماتها عن عمد.
· تحليل JS يكشف مفاتيح API ورؤوس.
· نظام API معقد مع NoSQL Injection, IDOR, تحكم عبر رؤوس.
· تسريب ملفات احتياطية وبيئة تكشف مسارات وكلمات سر.
· إمكانية تجاوز المصادقة عبر هيدر `X-Debug-User`.
· خدمة SSH مع تصعيد صلاحيات عبر sudo find.
· العلم الحقيقي: `THM{medium_plus_chain_complete}` – قيمة النقاط: +2500


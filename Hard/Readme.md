# ---
🔴 Hard Room 1 – Partial Exposure + Incomplete Context Leak

· ثلاث خدمات مخفية (9101, 9102, 9103) يجب اكتشافها.
· تسريب ملف إعدادات يكشف نصف الحقيقة فقط: مفتاح JWT وتلميح عن خدمة داخلية.
· تزوير JWT بدور admin يسمح بالوصول إلى API داخلي يُظهر اعتماديات SSH ورمز خدمة.
· الخدمة الداخلية (9102) تستخدم Pickle Deserialization غير آمنة، مما يسمح بتنفيذ أوامر عن بعد لقراءة العلم.
· مسار بديل: SSH مع تصعيد صلاحيات عبر sudo find.
· خداع سيبراني: علم مزيف في صفحات التصحيح.
· المهارات: الاستدلال بمعلومات ناقصة، JWT forgery، Insecure Deserialization (Pickle)، SSH Privilege Escalation.
· العلم: `THM{p4rt1al_l34k_deser}` – قيمة النقاط: +3000

# ---
🔴 Hard Room 2 – Multi‑Role Authorization Drift (OAuth + WebSocket)

· ثلاثة خدمات على منافذ غير متسلسلة: ويب (9201), OAuth (9202), WebSocket (9203).
· التطبيق الرئيسي يستخدم OAuth 2.0 مع ثغرة قبول أي redirect_uri، مما يسمح بتوجيه رمز التفويض إلى مخترق.
· مفتاح JWT ضعيف مُسرَّب في نسخة احتياطية. يمكن تزوير رمز بدور admin.
· بلوحة الإدارة، يظهر تلميح عن خدمة WebSocket داخلية.
· خدمة WebSocket لا تتحقق من الدور بشكل كافٍ، وتقبل رمز admin لتنفيذ أوامر مثل "flag".
· خداع: علم مزيف في debug.
· المهارات: OAuth Misconfiguration (open redirect), JWT manipulation, WebSocket hijacking, pivoting.
· العلم: `THM{dr1ft_0auth_ws}` – قيمة النقاط: +3000

# ---
🔴 Hard Room 3 – Token Replay with State Desync (GraphQL Abuse)

· خدمتان مخفيتان: ويب (9301) و GraphQL (9302).
· ملف إعدادات JSON على خادم الويب يكشف مفتاح JWT وعنوان GraphQL.
· يمكن الحصول على JWT بدور user عبر تسجيل الدخول.
· خدمة GraphQL تسمح بالـ introspection، مما يكشف عن وجود حقل "flag" في نوع User.
· على الرغم من أن الويب يطلب دور admin للوصول إلى العلم، فإن GraphQL يعيد حقل flag لأي مستخدم يملك رمزاً صالحاً (دون التحقق من الدور) – وهذا هو انزياح الصلاحيات (State Desync).
· استغلال ذلك عبر طلب GraphQL مباشر يسترجع العلم.
· خداع: لوحة الإدارة بالويب تظهر علماً مزيفاً.
· المهارات: GraphQL enumeration, Introspection abuse, JWT replay, Authorization drift detection.
· العلم: `THM{gr4phql_d3sync}` – قيمة النقاط: +3500

# ---
🔴 Hard Room 4 – Ghost Endpoint Behavior (Cache Poisoning + DOM XSS)

· ثلاث خدمات مخفية (9401، 9402، 9403) يجب اكتشافها.
· نقطة نهاية `/debug` لا تُرجع شيئًا حتى يتم "تهيئة" الجلسة عبر طلب خاص مع الرأس `X‑Init`.
· تحتوي صفحة البوابة على DOM‑based XSS (معامل `redirect`) كطُعم.
· إعدادات التطبيق تُسرّب مفتاح API لخدمة مخبأ داخلية.
· خدمة المخبأ (9402) تُنشئ مدخلاتها بناءً على رأس `Host` ويمكن تسميمها بحقن `evil` في الرأس.
· بعد التسميم، تُعيد خدمة المخبأ العلم الحقيقي بدلاً من العلم المزيف.
· مسار بديل: SSH (operator:gh0st_pass) + تصعيد صلاحيات عبر `sudo find`.
· خداع: نقطة التصحيح وبيانات المخبأ الأولية تُظهر أعلامًا مزيفة.
· المهارات: Ghost Endpoint Activation, Cache Poisoning (Web Cache Deception), DOM XSS Recognition, Header Manipulation.
· العلم: `THM{gh0st_c4che_xss}` – قيمة النقاط: +4000

# ---
🔴 Hard Room 5 – Business Logic Conflicts (XXE + Logic Abuse)

· ثلاث خدمات على منافذ غير متسلسلة (9501، 9502، 9503).
· تطبيق ويب يحتوي على ثغرة منطقية في آلية الاسترداد: يمكن إدخال مبلغ سالب لزيادة الرصيد.
· باستخدام الرصيد المُضخَّم، يمكن "شراء" مفتاح API للوحة الإدارة.
· مفتاح API يكشف عن خدمة داخلية تستخدم parser XML غير آمن.
· خدمة الـ XML (9502) تسمح بالـ XXE (الكيانات الخارجية) لقراءة ملفات النظام مثل `/root/flag.txt`.
· مسار بديل: SSH (operator:l0g1c_pass) + تصعيد صلاحيات عبر `sudo find`.
· خداع: ملف الإعدادات ولوحة التصحيح تحتويان على أعلام مزيفة.
· المهارات: Business Logic Abuse (negative amount), XXE (XML External Entity), Privilege Escalation.
· العلم: `THM{l0g1c_c0nfl1ct_xxe}` – قيمة النقاط: +4000

# ---
🔴 Hard Room 6 – Inconsistent File Access Control + Padding Oracle

· الخدمات مخفية على المنافذ 9601، 9602، 9603.
· خادم الملفات يطبق سياسات وصول متناقضة: `/download?file=flag.txt.enc` محظور، لكن `/api/file?file=flag.txt.enc` يسمح بتحميله.
· الملف المُنزَّل هو العلم مُشَفَّر بـ AES‑CBC.
· خدمة داخلية (9602) تعمل كـ Padding Oracle: تقبل IV+Ciphertext وتُبلغ عن صحة الحشوة.
· باستخدام هجوم Padding Oracle (مثل padbuster) يمكن فك تشفير العلم بايتًا بايتًا.
· مسار بديل: SSH (operator:oracle_pass) + تصعيد صلاحيات عبر `sudo find`.
· خداع: صفحة التصحيح تظهر علمًا مزيفًا.
· المهارات: Inconsistent Access Control, Padding Oracle Attack (AES‑CBC), Cryptographic Side‑Channel.
· العلم: `THM{p4dd1ng_0r4cl3_f1le}` – قيمة النقاط: +4500

# ---
🔴 Hard Room 7 – API Schema Mismatch + Race Condition File Upload (TOCTOU + CSRF)

· الخدمات مخفية على المنافذ 9701 (ويب)، 9702 (SSH).
· واجهة رفع ملفات تثق في التحقق الذي يجريه Frontend (JavaScript) بينما Backend يقبل أي ملف – ثغرة API Schema Mismatch.
· نافذة سباق (Race Condition) بين فحص الامتداد وحفظ الملف تسمح برفع سكربتات قابلة للتنفيذ.
· يمكن استغلال TOCTOU لرفع ملف Python وتنفيذه لقراءة العلم.
· ثغرة CSRF في ميزة "Share with Admin" تسمح بخداع الخادم لزيارة نقاط داخلية تعرض بيانات حساسة.
· مسار بديل: SSH مع تصعيد صلاحيات عبر sudo find.
· خداع: العلم الموجود في صفحة التصحيح واستجابات المسؤول مزيف.
· المهارات: API Schema Mismatch, Race Condition (TOCTOU), CSRF, File Upload Bypass, RCE.
· العلم: `THM{race_upload_csrf}` – قيمة النقاط: +4500

# ---
🔴 Hard Room 8 – Conditional Logic Injection (Parameter Pollution + YAML Deserialization)

· ثلاث خدمات على منافذ غير متسلسلة (9801, 9802, 9803).
· ميزة البحث عن المستخدمين تمنع الوصول المباشر إلى "admin" ولكن يمكن تجاوزها عبر HTTP Parameter Pollution (`?id=guest&id=admin`).
· تغيير User-Agent إلى "InternalBot/1.0" عند زيارة /debug يكشف عن مفتاح API لخدمة داخلية.
· خدمة داخلية (9802) تستخدم YAML parser غير آمن، مما يسمح بتنفيذ أوامر عبر YAML Deserialization.
· يمكن استخدام الحمولة `!!python/object/apply:subprocess.check_output` لقراءة `/root/flag.txt`.
· مسار بديل: SSH (operator:context_pass) + تصعيد صلاحيات عبر sudo find.
· خداع: العلم الموجود في debug وبيانات المستخدمين مزيف.
· المهارات: Parameter Pollution, Context-based Logic (User-Agent), YAML Deserialization, RCE.
· العلم: `THM{c0ntext_y4ml_pp}` – قيمة النقاط: +4500

# ---
🔴 Hard Room 9 – Upload → Async Processing Exploit (XPATH Injection + Container Escape)

· الخدمات مخفية على المنافذ 9901 (ويب)، 9902 (معالج Async/Container)، 9903 (SSH).
· تطبيق رفع ملفات XML تتم معالجتها بشكل غير متزامن بواسطة عامل خلفي.
· واجهة بحث XPath غير محمية تسمح باستخراج جميع البيانات من مستودع XML الداخلي (XPATH Injection).
· استخراج مفاتيح API للوصول إلى خدمة Container داخلية (9902).
· خدمة الـ Container تقبل file_id وتكشف العلم إذا احتوى الملف المُعالج على كلمات مفتاحية.
· محاكاة Container Escape: رفع ملف XML معد خصيصًا يؤدي إلى تسريب العلم بعد المعالجة.
· مسار بديل: SSH + sudo find.
· خداع: العلم الموجود داخل مستودع XML وسجلات التصحيح مزيف.
· المهارات: XPATH Injection, Async Exploitation, Container Escape (simulated), XML manipulation.
· العلم: `THM{xp4th_async_c0nt41n3r}` – قيمة النقاط: +5000

# ---
🔴 Hard Room 10 – Shadow Internal API Discovery (Prototype Pollution + WebSocket Hijacking)

· أربع خدمات مخفية على منافذ غير متسلسلة (10010 ويب، 10020 API داخلي، 10030 SSH، 10040 WebSocket).
· تحليل JavaScript يكشف عن تكوينات خفية: JWT secret، WebSocket URL، ومسارات API غير موثقة.
· تزوير JWT (secret ضعيف) يمنح دور admin ويفتح لوحة التحكم.
· API داخلي (10020) يعاني من Prototype Pollution: يمكن تعديل إعدادات السيرفر عبر `/api/updateConfig` لرفع الدور إلى admin.
· بعد التلويث، الوصول إلى `/api/flag` يعطي العلم الحقيقي.
· خدمة WebSocket (10040) تقبل توكن admin لتنفيذ أوامر مثل "flag".
· مسار بديل: SSH + sudo find.
· خداع: العلم الموجود في debug وبيانات المستخدمين مزيف.
· المهارات: Shadow API Discovery, JS Analysis, JWT Forgery, Prototype Pollution, WebSocket Hijacking.
· العلم: `THM{sh4d0w_4pi_pr0t0_poll}` – قيمة النقاط: +5000

# ---
🔴 Hard Room 11 – Pre-Exam: Ambiguous Exploitation Simulation (Hard++)

· خدمات مخفية على منافذ غير متسلسلة (10101 GraphQL، 10102 Async Worker، 10103 SSH).
· واجهة GraphQL مع Introspection تكشف عن طفرات غير محمية (updateUserRole) تسمح بتصعيد الدور إلى admin.
· بعد التصعيد، يمكن إنشاء مهام (createTask) تُعالج بشكل غير متزامن بواسطة خدمة داخلية (10102).
· الخدمة الداخلية تستخدم Pickle Deserialization غير آمنة لتنفيذ الأوامر.
· SSRF مع فلتر يمكن تجاوزه (127.1, 0x7f000001) يتيح الوصول إلى الخدمة الداخلية.
· يجب ربط SSRF مع Async Processing لتحقيق RCE واستخراج العلم.
· مسار بديل: SSH (operator:ambiguous_pass) + تصعيد صلاحيات عبر sudo find.
· خداع: GraphQL يعرض flag مزيف، صفحات debug تحتوي على أعلام خادعة.
· المهارات: GraphQL Abuse, SSRF Filter Bypass, Async Exploitation, Pickle Deserialization.
· العلم: `THM{4mb1gu0us_3xpl01t4t1on}` – قيمة النقاط: +5500

# ---
🔴 Hard Room 12 – Microservice Identity Confusion (JWT kid Injection + Smuggling)

· ثلاث خدمات على منافذ غير متسلسلة (10201, 10202, 10203).
· الخدمة الرئيسية تصدر JWT بتوقيع قوي، لكن الخدمة الداخلية تعاني من ثغرة `kid injection`: يمكن توجيهها لاستخدام `/dev/null` كمفتاح (فارغ).
· تزوير رمز `admin` بتوقيع فارغ يسمح بتجاوز الصلاحيات في الخدمة الداخلية.
· محاكاة HTTP Request Smuggling عبر وكيل يسمح بتمرير طلبات HTTP خام إلى الخدمة الداخلية، متجاوزًا جدار الحماية.
· الوصول إلى نقطة `/internal/admin/flag` يعيد العلم الحقيقي.
· مسار بديل: SSH (operator:micro_pass) + تصعيد صلاحيات عبر `sudo find`.
· خداع: صفحة التصحيح وملفات الإعدادات تحوي أعلامًا مزيفة.
· المهارات: JWT kid Injection, Microservice Identity Confusion, HTTP Request Smuggling (simulated), Privilege Escalation.
· العلم: `THM{m1cr0_id_c0nfus10n}` – قيمة النقاط: +5500

# ---
🔴 Hard Room 13 – SSRF → Internal Graph Pivoting (Hard++ | Enterprise Realism)

· أربع خدمات على منافذ غير متسلسلة (10801, 10820, 10833, 10847) تحاكي بنية تحتية مؤسسية.
· الخدمة الأمامية تعمل كـ Reverse Proxy، مع Rate Limiting، وتحتوي على SSRF وOpen Redirect.
· يتطلب تجاوز فلتر SSRF باستخدام Open Redirect للوصول إلى خدمة Metadata الداخلية.
· خدمة Metadata تصدر JWT مع kid ضعيف يمكن استغلاله (kid=/dev/null) لإنشاء رموز admin.
· باستخدام رمز admin، يتم الوصول إلى API الداخلية التي تمنح رمز قاعدة البيانات.
· قاعدة البيانات تقدم العلم النهائي بعد التحقق من الرمز.
· تم إضافة طبقات واقعية: rate limiting، سجلات وهمية، خداع بأعلام مزيفة في عدة أماكن.
· المهارات: SSRF Filter Bypass via Open Redirect, JWT kid Injection, Multi-step Internal Pivoting.
· العلم: `THM{ssrf_gr4ph_p1v0t}` – قيمة النقاط: +6000

# ---
🔴 Hard Room 15 – Permission Propagation Failure (Hard++ | Enterprise Realism)

· أربع خدمات مؤسسية على منافذ غير متسلسلة (11001 عكس، 11022 خدمة A، 11033 خدمة B، 11044 مراقبة).
· JWT مع kid ضعيف يسمح بتزوير دور admin في خدمة A.
· خدمة A تسمح بتحديث الدور في قاعدة البيانات المركزية.
· خدمة B لا تتحقق من الدور المحدث (فشل انتشار الصلاحيات)، وتسمح بـ IDOR لقراءة بيانات أي مستخدم.
· خدمة المراقبة تعرض سجلات وهمية تحاكي SIEM حقيقي.
· طبقات واقعية: Rate Limiting، Reverse Proxy، سجلات وهمية، خداع بأعلام مزيفة.
· المهارات: JWT kid Injection, Permission Propagation Failure, IDOR, Microservice Auth Drift.
· العلم: `THM{p3rm1ss10n_f4ilure}` – قيمة النقاط: +6500

# ---
🔴 Hard Room 16 – Full Real Enterprise Ambiguous Pentest Simulation (Hard++ | CRLF + JWT kid + bcrypt)

· خمس خدمات مؤسسية على منافذ غير متسلسلة (11101 عكس، 11122 بيانات وصفية، 11133 API داخلي، 11144 مراقبة، 11155 SSH).
· الوكيل الأمامي يحتوي على SSRF وثغرة حقن CRLF في عنوان URL، مما يسمح بإضافة رؤوس (مثل X-Internal-Role) للوصول المباشر إلى API الداخلية.
· خدمة البيانات الوصفية تسرب رمز JWT (مع kid=metadata_key) وتجزئة bcrypt لمستخدم SSH.
· يمكن تجاوز فلتر SSRF عبر التمثيل العشري لـ IP (2130706433) للوصول إلى الخدمات الداخلية.
· يمكن تزوير رمز JWT عبر kid=/dev/null (مفتاح فارغ) للحصول على صلاحيات admin.
· خدمة SSH تحتاج إلى كسر كلمة المرور (وضع bcrypt 3200) ثم تصعيد الصلاحيات عبر sudo find.
· سجلات مراقبة وهمية، خداع بأعلام مزيفة متعددة، وطبقات واقعية (Rate Limiting، Reverse Proxy).
· المسارات متعددة وغامضة: لا يوجد طريق وحيد للوصول إلى العلم الحقيقي.
· المهارات: CRLF Injection, SSRF Filter Bypass, JWT kid Injection, bcrypt Cracking, SSH PrivEsc.
· العلم: `THM{3nt3rpr1se_4mb1gu0us}` – قيمة النقاط: +7000

# ---
🔴 Hard Room 17 – ADB Escape & Privilege Escalation (Hard++ | JWT kid + bcrypt + SUID find)

· ثلاث خدمات مؤسسية على منافذ غير متسلسلة (11201 بوابة، 11222 ADB، 11233 مراقبة).
· البوابة تستخدم JWT مع kid ضعيف؛ يمكن تزوير رمز admin للحصول على تجزئة bcrypt لكلمة مرور ADB.
· كسر التجزئة (bcrypt) يكشف كلمة المرور لخدمة ADB المحاكية.
· خدمة ADB تقدم قشرة أندرويد محدودة. هناك `find` ذو صلاحيات SUID يمكن استغلاله لتنفيذ أوامر كـ root وقراءة العلم.
· طبقات واقعية: Rate Limiting، سجلات مراقبة وهمية، خداع بأعلام مزيفة.
· المهارات: JWT kid Injection، bcrypt Cracking، Android Shell Escape، SUID Exploitation.
· العلم: `THM{adb_escape_root_flag}` – قيمة النقاط: +7000

# ---
🔴 Hard Final Exam – EclipseCorp Full Infrastructure Assessment

· 5 خدمات متكاملة على منافذ غير متسلسلة (11381, 11423, 11507, 11642, 11739).
· نظام مؤسسي كامل: Reverse Proxy، Mobile API، Internal API، Async Worker، Monitoring.
· يجب بناء نموذج ذهني للبنية التحتية، حيث لا يوجد مسار مباشر للعلم.
· استغلال JWT kid injection لتصعيد الصلاحيات في الخدمة الأمامية.
· اكتشاف Mobile API عبر Virtual Host (m.eclipsecorp.internal).
· SSRF (تجاوز الفلتر بالتمثيل العشري) للوصول إلى Internal API.
· Inconsistent Authorization: بعض النقاط تعيد أدوار مختلفة.
· استغلال Worker عبر رفع ملف خاص واسترجاع جزئية العلم من ذاكرته.
· خداع سيبراني شامل: سجلات مراقبة وهمية، أعلام مزيفة في عدة أماكن.
· المهارات: System-wide Recon, JWT kid Injection, SSRF Filter Bypass, Virtual Host Discovery, Async Exploitation, Flag Fragmentation Reconstruction.
· العلم النهائي: `SHINIGAMI{enterprise_inference_mastered}` – قيمة النقاط: +9999


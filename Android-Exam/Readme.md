# ---
🔴 Android Final Exam – “Compromised Android Enterprise”

· بيئة مؤسسية معقدة تحاكي اختراق أجهزة أندرويد عبر ADB وAPIs داخلية.
· ستة خدمات على منافذ غير متسلسلة (12001 بوابة، 12022 ADB، 12033 API داخلي، 12044 Mobile API، 12055 Worker، 12066 مراقبة).
· تحليل APK يكشف أسرارًا (JWT secret، نقاط النهاية، تجزئة bcrypt لكلمة مرور ADB).
· كسر تجزئة bcrypt يمنح وصولاً إلى قشرة أندرويد محدودة.
· استغلال `find` ذي صلاحيات SUID لقراءة جزء العلم الأول من `/data/system`.
· تزوير JWT عبر kid injection لتصعيد الصلاحيات في البوابة والوصول إلى الجزء الثاني من العلم.
· اكتشاف Mobile API عبر Virtual Host لمعرفة Worker.
· استغلال Worker عبر رفع ملف خاص وتزوير JWT آخر لقراءة ذاكرته واستخراج العلم الكامل.
· طبقات واقعية: Rate Limiting، Reverse Proxy، سجلات مراقبة وهمية، خداع بأعلام مزيفة.
· المهارات: Mobile APK Reversing, ADB Shell, JWT kid Injection, SSRF Filter Bypass, Virtual Host Discovery, Async Exploitation, Flag Fragmentation.
· العلم النهائي: `SHINIGAMI{mobile_enterprise_compromised}` – قيمة النقاط: +10000


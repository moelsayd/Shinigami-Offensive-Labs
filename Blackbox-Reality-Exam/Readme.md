# ---
♾️ FINAL BLACKBOX REALITY SIMULATION v1.0

· سبع خدمات خلف عكس (13001) على منافذ غير متسلسلة.
· لا توجد صفحة هبوط حقيقية، ولا مسار مباشر، ولا ثغرة وحيدة.
· سلوك الخدمة يتغير حسب User‑Agent ورؤوس مخصصة.
· JWT kid injection يعطي صلاحيات admin.
· SSRF عبر ميزة "fetch" مع تجاوز فلتر يسمح بالوصول إلى الخدمات الداخلية.
· IDOR في خدمة المستخدمين يكشف جزءًا من العلم.
· ثغرة منطقية في الفوترة (refund سالب) ورأس خاص يعطي الجزء الأخير.
· خدمة Legacy يمكن تجاوزها عبر رأس `X‑Legacy‑Auth`.
· خدمة عامل غير متزامن تخزن العلم في الذاكرة بعد رفع مفتاح معين.
· سجلات مراقبة وهمية وأعلام مزيفة في كل مكان.
· المهارات: System‑wide Recon, JWT kid, SSRF, IDOR, Logic Abuse, Header Injection, Async Exploitation, Flag Assembly.
· العلم النهائي: `SHINIGAMI{blackbox_reality_mastered}` – قيمة النقاط: +15000

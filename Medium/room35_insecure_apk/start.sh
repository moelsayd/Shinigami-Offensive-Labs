#!/usr/bin/env bash
ROOM="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOM"
export PORT=9999   # ليفهمه اللودر عند اختبار t (لنفس المنفذ)

python3 << 'PY'
import zipfile, os
room = os.environ['ROOM'] if 'ROOM' in os.environ else os.path.dirname(os.path.abspath(__file__))
apk_path = os.path.join(room, "fake_app.apk")
with zipfile.ZipFile(apk_path, 'w') as z:
    z.writestr('AndroidManifest.xml', '<manifest package="com.fake.app"/>')
    z.writestr('resources.arsc', '')
    secrets = b"Injected string: http://localhost:9999/secret-admin\nDebug creds: admin:supersecret\nFake flag: THM{fake_apk_flag}\n"
    z.writestr('classes.dex', secrets)
PY

python3 adb_sim.py 5556 &
echo $! > .adb.pid
python3 secret_server.py 9999 &
echo $! > .web.pid
sleep 2
nc -z 127.0.0.1 5556 && echo "✅ ADB sim: localhost:5556"
nc -z 127.0.0.1 9999 && echo "✅ Secret server: http://localhost:9999"

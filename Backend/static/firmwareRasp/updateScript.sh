
rm ./unitTest.py
rm ./mongoCli.py
rm ./raspRefactored.py
rm ./updateScript.sh

wget "http://172.22.45.216:800/static/firmwareRasp/mongoCli.py"
wget "http://172.22.45.216:800/static/firmwareRasp/unitTest.py"
wget "http://172.22.45.216:800/static/firmwareRasp/raspRefactored.py"
wget "http://172.22.45.216:800/static/firmwareRasp/updateScript.sh" -O- | tr -d '\r' >updateScript.sh
chmod +x ./updateScript.sh

python ./raspRefactored.py

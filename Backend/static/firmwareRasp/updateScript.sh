cd /home/pi/henkaten_ols
rm ./unitTest.py
rm ./mongoCli.py
rm ./raspRefactored.py
rm ./iniciaRede.py
rm ./updateScript.sh
rm ./hostnameSet.sh


wget "http://172.22.45.216:800/static/firmwareRasp/mongoCli.py"
wget "http://172.22.45.216:800/static/firmwareRasp/unitTest.py"
wget "http://172.22.45.216:800/static/firmwareRasp/raspRefactored.py"
wget "http://172.22.45.216:800/static/firmwareRasp/iniciaRede.py"
wget "http://172.22.45.216:800/static/firmwareRasp/hostnameSet.sh" -O- | tr -d '\r' >hostnameSet.sh
wget "http://172.22.45.216:800/static/firmwareRasp/updateScript.sh" -O- | tr -d '\r' >updateScript.sh
chmod +x ./hostnameSet.sh
chmod +x ./updateScript.sh

source ~/.profile
workon cv 
python ./iniciaRede.py


python ./raspRefactored.py

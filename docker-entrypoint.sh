#!/bin/bash
set -e
# tail -f /dev/null
run_once(){
nginx -g 'daemon off;' &
cd /home/ash
echo "alias python=python3" >> ~/.bashrc
mkdir /home/ash/data
mongod --dbpath /home/ash/data --bind_ip 127.0.0.1 &
mongoimport --uri mongodb://localhost:27017/ash --collection=cis_benchmark --jsonArray --file=/home/ash/cis-benchmark-new.json
cat <<EOF > create_user_script.js
use admin
db.createUser(
  {
    user: "ash-db",
    pwd: "9LlEukAh85nPMH3vB1Wd",
    roles: [
       { role: "readWrite", db: "ash" }
    ]
  }
)
EOF
mongosh < create_user_script.js
export PATH="/home/ash/.local/bin:$PATH"
cd /ash/back/
cat <<EOF > env
MONGODB_URI=mongodb://ash-db:9LlEukAh85nPMH3vB1Wd@localhost
DB_NAME=ash
EOF
python3 main.py
}
DIRECTORY="/home/ash/data"
if [ -d "$DIRECTORY" ];then
  nginx -g 'daemon off;' &
  mongod --dbpath /home/ash/data --bind_ip 127.0.0.1 &
  cd /ash/back
  python3 main.py
else
  run_once
fi

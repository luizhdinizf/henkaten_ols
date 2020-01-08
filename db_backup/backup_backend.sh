#!/bin/bash
#RUN FROM OUTSIDE OF ANY CONTAINER
docker exec -it henkaten_ols_mongo_1 /db_backup/export.sh

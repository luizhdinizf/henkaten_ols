#!/bin/bash
mongodump --forceTableScan --host localhost:27017 -d henkaten_ols -o db_backup
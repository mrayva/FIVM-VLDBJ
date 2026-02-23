#!/bin/bash

TIMEOUT="130m"

WORK_DIR="/local/scratch/zhang/FIVM/examples"

queries=("Q5-sum-prod" "Q10-sum-prod" "Q15-sum-prod" "Q20-sum-prod")
dataset=$1
method="DBT"

DBTOASTER_EXE=/local/scratch/milos/experiments/dbtoaster_release/bin/dbtoaster
FIVM_FRONTEND=/local/scartch/zhang/FIVM/bin/run_frontend.sh
FIVM_BACKEND=/local/scartch/zhang/FIVM/bin/run_backend.sh

unamestr=`uname`
if [[ "$unamestr" == 'Linux' ]]; then
	TCMALLOC_LIB=/local/scratch/milos/local/lib	
else
	TCMALLOC_LIB=/opt/homebrew/lib
fi

CC=g++-8
CFLAGS="-O3 -DNDEBUG -Wall -Wno-unused-variable -std=c++17 -pedantic -ltcmalloc -L${TCMALLOC_LIB}"
export LD_LIBRARY_PATH=${TCMALLOC_LIB}

# ! switch to the specified dataset by creating soft links
./switch_data.sh $dataset

cd $WORK_DIR

rm -rf "generated/m3/path"
rm -rf "generated/cpp/path"
rm -rf "bin/path"

mkdir -p "generated/m3/path"
mkdir -p "generated/cpp/path"
mkdir -p "bin/path"
mkdir -p "path-experiments/output/path"

for query in "${queries[@]}"
do
    echo "---"
    echo \#\#\#\# "Compiling ${query}-${method}-${dataset}..."
    q_base=$(echo "$query" | cut -d '-' -f 1) # get the first part of the query name

    sql_file="path-experiments/queries/dbt/path-${query}.sql"
    m3_file="generated/m3/path/path-${query}-${method}.m3"
    backend_hpp="generated/cpp/path/path-${query}-${method}_BATCH.hpp"
    application_hpp="src/application/path/application_path-${q_base}.hpp"
    binary_name="bin/path/path-${query}-${method}_BATCH_1000"
    output_file="path-experiments/output/path/path-${query}-${method}-${dataset}_BATCH_1000.txt"


    echo ${DBTOASTER_EXE} --batch -l m3 -O3 -o "$m3_file" $sql_file
    eval ${DBTOASTER_EXE} --batch -l m3 -O3 -o "$m3_file" $sql_file

    echo ../bin/run_backend.sh --batch -o "$backend_hpp" "$m3_file"
    ../bin/run_backend.sh --batch -o "$backend_hpp" "$m3_file"

    echo g++-8 -O3 -DNDEBUG -Wall -Wno-unused-variable -std=c++17 -pedantic src/main.cpp -I ../backend/lib -I src -I src/lib -DBATCH_SIZE=1000 -include "$backend_hpp" -include "$application_hpp" -o "$binary_name"
    g++-8 -O3 -DNDEBUG -Wall -Wno-unused-variable -std=c++17 -pedantic src/main.cpp -I ../backend/lib -I src -I src/lib -DBATCH_SIZE=1000 -include "$backend_hpp" -include "$application_hpp" -o "$binary_name"

    echo $binary_name > $output_file
    timeout 250m  $binary_name > $output_file
done
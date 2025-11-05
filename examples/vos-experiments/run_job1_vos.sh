#!/bin/bash

WORK_DIR="/home/user/zhang/FIVM-static-dynamic/examples/"


# queries=("job1_vo0" "job1_vo1" "job1_vo2" "job1_vo3")
queries=("job1_static")

dataset=$1
if [ -z "$dataset" ]; then
    dataset="job"
fi

dataset=$1
method="F-IVM"

cd $WORK_DIR

rm -rf "generated/m3/vos"
rm -rf "generated/cpp/vos"
rm -rf "bin/vos"

mkdir -p "generated/m3/vos"
mkdir -p "generated/cpp/vos"
mkdir -p "bin/vos"
mkdir -p "vos-experiments/output/vos"

for query in "${queries[@]}"
do
    echo "---"
    echo \#\#\#\# "Compiling ${query}-${method}-${dataset}..."
    q_base=$(echo "$query" | cut -d '-' -f 1) # get the first part of the query name

    sql_file="vos-experiments/queries/${query}.sql"
    m3_file="generated/m3/vos/vos-${query}-${method}.m3"
    backend_hpp="generated/cpp/vos/vos-${query}-${method}_BATCH.hpp"
    application_hpp="src/application/jobs/application_jobs-Q1.hpp" 
    binary_name="bin/vos/vos-${query}-${method}_BATCH_1000"
    output_file="vos-experiments/output/vos/vos-${query}-${method}-${dataset}_BATCH_1000.txt"

    echo ../bin/run_frontend.sh --batch -o "$m3_file" $sql_file
    ../bin/run_frontend.sh --batch -o "$m3_file" $sql_file

    echo ../bin/run_backend.sh --batch -o "$backend_hpp" "$m3_file"
    ../bin/run_backend.sh --batch -o "$backend_hpp" "$m3_file"

    echo g++ -O3 -DNDEBUG -Wall -Wno-unused-variable -std=c++17 -pedantic src/main.cpp -I ../backend/lib -I src -I src/lib -DBATCH_SIZE=1000 -include "$backend_hpp" -include "$application_hpp" -o "$binary_name"
    g++ -O3 -DNDEBUG -Wall -Wno-unused-variable -std=c++17 -pedantic src/main.cpp -I ../backend/lib -I src -I src/lib -DBATCH_SIZE=1000 -include "$backend_hpp" -include "$application_hpp" -o "$binary_name"

    echo "${binary_name} > ${output_file}"
    timeout 250m $binary_name > $output_file
done




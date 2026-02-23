#!/bin/bash

WORK_DIR="/local/scratch/zhang/mflow/FIVM/examples"
queries=("0")
dataset=$1
method="F-IVM"

cd $WORK_DIR

# rm -rf "generated/m3/jobs"
rm -rf "generated/cpp/jobs"
rm -rf "bin/jobs"

# mkdir -p "generated/m3/jobs"
mkdir -p "generated/cpp/jobs"
mkdir -p "bin/jobs"
mkdir -p "jobs/output/jobs"

for query in "${queries[@]}"
do
    echo "---"
    echo \#\#\#\# "Compiling ${query}-${method}-${dataset}..."
    q_base=$(echo "$query" | cut -d '-' -f 1) # get the first part of the query name

    sql_file=$WORK_DIR/jobs/queries/${query}.sql
    m3_file="generated/m3/jobs/jobs-${query}-${method}.m3"
    backend_hpp="generated/cpp/jobs/jobs-${query}-${method}_BATCH.hpp"
    application_hpp="src/application/jobs/application_jobs-Q${q_base}.hpp"
    binary_name="bin/jobs/jobs-${query}-${method}_BATCH_1000"
    output_file="jobs/output/jobs-${query}-${method}-${dataset}_BATCH_1000.txt"

    # FIXME: do not compile sql to m3 for now
    echo ../bin/run_frontend.sh --batch -o "$m3_file" $sql_file
    ../bin/run_frontend.sh --batch -o "$m3_file" $sql_file

    echo ../bin/run_backend.sh --batch -o "$backend_hpp" "$m3_file"
    ../bin/run_backend.sh --batch -o "$backend_hpp" "$m3_file"

    echo g++ -O3 -DNDEBUG -Wall -Wno-unused-variable -std=c++17 -pedantic src/main.cpp -I ../backend/lib -I src -I src/lib -DBATCH_SIZE=1000 -include "$backend_hpp" -include "$application_hpp" -o "$binary_name"
    g++ -O3 -DNDEBUG -Wall -Wno-unused-variable -std=c++17 -pedantic src/main.cpp -I ../backend/lib -I src -I src/lib -DBATCH_SIZE=1000 -include "$backend_hpp" -include "$application_hpp" -o "$binary_name"

    echo "${binary_name} > ${output_file}"
    # timeout 250m $binary_name > $output_file
    # $binary_name > $output_file
done



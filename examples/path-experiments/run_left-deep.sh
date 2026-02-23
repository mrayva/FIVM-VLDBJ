#!/bin/bash

WORK_DIR="/local/scratch/zhang/FIVM/examples"
queries=("Q10-sum-prod" "Q15-sum-prod" "Q20-sum-prod" "Q5-sum-prod")
dataset=$1
method="LEFT-DEEP"

# switch to the specified dataset by creating soft links
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

    sql_file="path-experiments/queries/left-deep/path-${query}.sql"
    m3_file="generated/m3/path/path-${query}-${method}.m3"
    backend_hpp="generated/cpp/path/path-${query}-${method}_BATCH.hpp"
    application_hpp="src/application/path/application_path-${q_base}.hpp"
    binary_name="bin/path/path-${query}-${method}_BATCH_1000"
    output_file="path-experiments/output/path/path-${query}-${method}-${dataset}_BATCH_1000.txt"

    echo ../bin/run_frontend.sh --batch -o "$m3_file" $sql_file
    ../bin/run_frontend.sh --batch -o "$m3_file" $sql_file

    echo ../bin/run_backend.sh --batch -o "$backend_hpp" "$m3_file"
    ../bin/run_backend.sh --batch -o "$backend_hpp" "$m3_file"

    echo g++ -O3 -DNDEBUG -Wall -Wno-unused-variable -std=c++17 -pedantic src/main.cpp -I ../backend/lib -I src -I src/lib -DBATCH_SIZE=1000 -include "$backend_hpp" -include "$application_hpp" -o "$binary_name"
    g++ -O3 -DNDEBUG -Wall -Wno-unused-variable -std=c++17 -pedantic src/main.cpp -I ../backend/lib -I src -I src/lib -DBATCH_SIZE=1000 -include "$backend_hpp" -include "$application_hpp" -o "$binary_name"

    echo $binary_name > $output_file
    timeout 250m $binary_name > $output_file
done



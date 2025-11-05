#!/bin/bash

WORK_DIR="/home/user/zhang/FIVM-static-dynamic/examples/"

# queries=("retailer_sum" "retailer_sum_INVENTORY")
# queries=("retailer_sum_INVENTORY_flat" "retailer_sum" "retailer_sum_INVENTORY")
# queries=("retailer_sum_INVENTORY")
# queries=("retailer_sum_INVENTORY_WEATHER")


queries=("retailer_full_INVENTORY" "retailer_full")

dataset=$1
if [ -z "$dataset" ]; then
    dataset="retailer"
fi

method="FIVM"

cd $WORK_DIR

rm -rf "generated/m3/static-dynamic"
rm -rf "generated/cpp/static-dynamic"
rm -rf "bin/static-dynamic"

mkdir -p "generated/m3/static-dynamic"
mkdir -p "generated/cpp/static-dynamic"
mkdir -p "bin/static-dynamic"
mkdir -p "static-dynamic-experiments/output/static-dynamic"

for query in "${queries[@]}"
do
    echo "---"
    echo \#\#\#\# "Compiling ${query}-${method}-${dataset}..."

    sql_file="static-dynamic-experiments/queries/${query}.sql"
    m3_file="static-dynamic-experiments/queries/${query}.m3" # the m3 file is hand-written
    backend_hpp="generated/cpp/static-dynamic/static-dynamic-${query}-${method}_BATCH.hpp"
    application_hpp="src/application/retailer/application_retailer.hpp" 
    binary_name="bin/static-dynamic/static-dynamic-${query}-${method}_BATCH_1000"
    output_file="static-dynamic-experiments/output/static-dynamic/static-dynamic-${query}-${method}-${dataset}_BATCH_1000.txt"

    # echo ../bin/run_frontend.sh --batch -o "$m3_file" $sql_file
    # ../bin/run_frontend.sh --batch -o "$m3_file" $sql_file

    echo ../bin/run_backend.sh --batch -o "$backend_hpp" "$m3_file"
    ../bin/run_backend.sh --batch -o "$backend_hpp" "$m3_file"

    echo g++ -O3 -DNDEBUG -Wall -Wno-unused-variable -std=c++17 -pedantic src/main.cpp -I ../backend/lib -I src -I src/lib -DBATCH_SIZE=1000 -include "$backend_hpp" -include "$application_hpp" -o "$binary_name" 
    g++ -O3 -DNDEBUG -Wall -Wno-unused-variable -std=c++17 -pedantic src/main.cpp -I ../backend/lib -I src -I src/lib -DBATCH_SIZE=1000 -include "$backend_hpp" -include "$application_hpp" -o "$binary_name"

    echo $binary_name --no-output > $output_file
    timeout 250m $binary_name --no-output > $output_file
done

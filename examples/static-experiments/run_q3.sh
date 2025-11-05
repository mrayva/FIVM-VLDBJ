#!/bin/bash

WORK_DIR="/home/user/zhang/FIVM-static-dynamic/examples/"

# queries=("tpch_query03_vo1" "tpch_query03_vo2")
queries=("tpch_query03_vo1" "tpch_query03_vo2" "tpch_query03_nopred_vo1" "tpch_query03_nopred_vo2")

dataset=$1
if [ -z "$dataset" ]; then
    dataset="tpch"
fi


experiment_name="static"
method="FIVM"
dataset_versions=("tpch10" "tpch_unordered10" "jcch10" "jcch_unordered10")




cd $WORK_DIR

rm -rf "generated/m3/static"
rm -rf "generated/cpp/static"
rm -rf "bin/static"


mkdir -p "generated/m3/${experiment_name}"
mkdir -p "generated/cpp/${experiment_name}"
mkdir -p "bin/${experiment_name}"
mkdir -p "${experiment_name}-experiments/output/${experiment_name}"

for dataset_version in "${dataset_versions[@]}"
do
    echo "---"
    # create the softlink for the dataset
    rm -rf "$WORK_DIR/data/tpch"
    echo "Creating softlink data/tpch -> $HOME/data/${dataset_version}..."
    echo "ln -s $HOME/data/${dataset_version} $WORK_DIR/data/tpch"
    ln -s $HOME/data/${dataset_version} $WORK_DIR/data/tpch

    for query in "${queries[@]}"
    do
        echo "---"
        echo \#\#\#\# "Compiling ${query}-${method}-${dataset_version}..."

        sql_file="${experiment_name}-experiments/queries/${query}.sql"
        m3_file="generated/m3/${experiment_name}/${experiment_name}-${query}-${method}.m3"
        backend_hpp="generated/cpp/${experiment_name}/${experiment_name}-${query}-${method}_BATCH.hpp"
        application_hpp="src/application/tpch/application_tpch.hpp" 
        binary_name="bin/${experiment_name}/${experiment_name}-${query}-${method}_BATCH_1000"
        output_file="${experiment_name}-experiments/output/${experiment_name}/${experiment_name}-${query}-${method}-${dataset_version}_BATCH_1000.txt"


        # sql -> m3
        echo ../bin/run_frontend.sh --batch -o "$m3_file" $sql_file
        ../bin/run_frontend.sh --batch -o "$m3_file" $sql_file

        # m3 -> cpp
        echo ../bin/run_backend.sh --batch -o "$backend_hpp" "$m3_file"
        ../bin/run_backend.sh --batch -o "$backend_hpp" "$m3_file"

        # cpp -> binary
        echo g++ -O3 -DNDEBUG -Wall -Wno-unused-variable -std=c++17 -pedantic src/main.cpp -I ../backend/lib -I src -I src/lib -DBATCH_SIZE=1000 -include "$backend_hpp" -include "$application_hpp" -o "$binary_name"
        g++ -O3 -DNDEBUG -Wall -Wno-unused-variable -std=c++17 -pedantic src/main.cpp -I ../backend/lib -I src -I src/lib -DBATCH_SIZE=1000 -include "$backend_hpp" -include "$application_hpp" -o "$binary_name"

        # run binary
        echo "${binary_name} > ${output_file}"
        timeout 250m $binary_name --no-output > $output_file
    done
done

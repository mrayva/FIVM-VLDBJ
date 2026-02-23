#!/bin/bash

DATA_DIR="/local/scratch/zhang/data"
SNAP_DIR="/local/scratch/zhang/FIVM/examples/data/snap"

# if $1 is twitter, then switch to twitter dataset
if [[ "$1" == "twitter" ]]; then
    data_path=$DATA_DIR/ego-twitter/twitter_combined.txt
fi

# if $1 is tiktok
if [[ "$1" == "tiktok" ]]; then
    data_path=$DATA_DIR/tiktok/tiktok_edges_integers.tbl
fi

rm $SNAP_DIR/R*.tbl
for ((i=1; i<=20; i++))
do
    ln -s $data_path $SNAP_DIR/R$i.tbl
done
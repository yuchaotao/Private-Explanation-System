for month in $(seq -w 1 12) 
do
    wget https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2019-$month.csv
done
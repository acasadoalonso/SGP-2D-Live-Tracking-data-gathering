for f in $(ls -ctr /nfs/OGN/srv/*funcs.py ); do
                echo "Processing file:" $f
                ln $f .
done

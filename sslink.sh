rm *funcs.py kglid.py
ln /nfs/OGN/src/kglid.py .
for f in $(ls -ctr /nfs/OGN/src/funcs/*funcs.py ); do
                echo "Processing file:" $f
                ln -s $f .
done
ls -la *funcs.py 

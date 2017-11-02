rm *funcs.py
rm kglid.py libfap.py
for f in $(ls -ctr /nfs/OGN/src/*funcs.py ); do
                echo "Processing file:" $f
                ln -s $f .
done
ln -s /nfs/OGN/src/kglid.py .
ln -s /nfs/OGN/src/libfap.py .
ls -la *funcs.py

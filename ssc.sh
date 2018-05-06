rm *funcs.py kglid.py libfap.py
cp /nfs/OGN/src/*funcs.py .
cp /nfs/OGN/src/kglid.py .
cp /nfs/OGN/src/libfap.py .
git add .
git commit
git push origin master

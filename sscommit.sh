rm *funcs.py kglid.py 
cp /nfs/OGN/src/funcs/*funcs.py .
cp /nfs/OGN/src/kglid.py .
git add .
git commit
git push origin master

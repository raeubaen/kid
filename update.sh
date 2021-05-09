git add --all -- ':!data' ':!data/*'
dt=`date '+%d/%m/%Y_%H:%M:%S'`
git commit -m $dt
git push -u origin main

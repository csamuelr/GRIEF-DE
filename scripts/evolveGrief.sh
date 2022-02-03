date
f=0;
e=0;

#reset GRIEF comparison to BRIEF ones - for incremental training, comment out the following line
#cp tools/grief/test_pairs.brief tools/grief/test_pairs.txt;

#train a given number or generations
for i in $(seq 987 $2);
do
	f=$e;
	python3 ./pyscripts/de.py > /dev/null
	e=$(cat store.tmp|cut -f 3 -d ' ');
	r=$(cat store.tmp|cut -f 4 -d ' ');
	echo Population $i Fitness $e Error $r;
	j=$(printf %05i $i);
	cp tools/grief/pair_stats.txt grief_history/$j\_$e.txt;
done
date

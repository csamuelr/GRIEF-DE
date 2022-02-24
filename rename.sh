for i in $(seq 1 $1);
do
    j=$(printf %05i $i);
	mv ./history/$j* ./history/$j.txt;
done
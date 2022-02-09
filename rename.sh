for i in $(seq 1 $1);
do
    j=$(printf %05i $i);
	mv ./evaluations_DE_GRIEF/$j* ./evaluations_DE_GRIEF/$j.txt;
done
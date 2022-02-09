date
f=0;
e=0;

#reset GRIEF comparison to BRIEF ones - for incremental training, comment out this line
cp tools/grief/test_pairs.brief tools/grief/test_pairs.txt;
cd tools/;
./generate_eval.sh >/dev/null;
rm -r ../tools/grief/pair_stats.txt
cd ..;

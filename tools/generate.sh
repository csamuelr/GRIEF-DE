for i in 16 32 64;
do python3 grief/generate_code.py grief/test_pairs.txt $i >grief/generated_$i.i;
done
rm evolve_grief  &>/dev/null;
make evolve_grief # &>/dev/null;
rm match_all &>/dev/null;
make match_all  &>/dev/null;

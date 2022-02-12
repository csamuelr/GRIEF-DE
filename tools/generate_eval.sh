cd tools
for i in 16 32 64;
do python3 grief/generate_code.py grief/test_pairs.txt $i >grief/generated_$i.i;
done
rm evaluate
make evaluate #&>/dev/null;

cd ..

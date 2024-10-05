#!/bin/bash

timeoutInSeconds=600

if [[ ! -f ttp-checker ]]; then
    echo "Before running this script you need to unzip the ttp-checker (compiled for your OS) in this directory."
    exit 0
fi

chmod +x project1.py ttp-checker

for f in public-tests/*.ttp
do
    fbase="${f%.*}"
    fbase=$(basename $fbase)
    outfile=public-tests/"$fbase.myout"
    checkfile=public-tests/"$fbase.check"
    echo "Executing on instance $f"
    time timeout $timeoutInSeconds"s" ./project1.py < "$f" > "$outfile"
    ./ttp-checker "$f" "$outfile" > "$checkfile"
    cat "$checkfile"
    echo
    echo
    echo
done


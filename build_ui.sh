#!/usr/bin/env bash

UI_FILES="ui/*.ui"
OUT_FILES="src/"
for f in $UI_FILES
do
    echo "Processing ui file $f"
    xpath=${f%/*}
    xbase=${f##*/}
    xfext=${xbase##*.}
    xpref=${xbase%.*}
    pyuic5 -o "$OUT_FILES/$xpref.py" ${f}
done

#This shell script is adapted from https://github.com/pytorch/fairseq/blob/master/examples/translation/prepare-iwslt14.sh

echo 'Cloning Moses'
git clone https://github.com/moses-smt/mosesdecoder.git

echo 'Cloning Subword_NMT'
git clone https://github.com/rsennrich/subword-nmt.git

SCRIPTS=mosesdecoder/scripts
TOKENISER=$SCRIPTS/tokenizer/tokenizer.perl
LC=$SCRIPTS/tokenizer/lowercase.perl
CLEAN=$SCRIPTS/training/clean-corpus-n.perl
BPEROOT=subword-nmt/subword_nmt
BPE_TOKENS=10000

if [ ! -d "$SCRIPTS" ]; then
    echo "Please set SCRIPTS variable correctly to point to Moses scripts."
    exit
fi

src=en
tgt=ga
lang=en-ga
prep=opus.tokenised.en-ga
tmp=$prep/tmp
orig=orig

mkdir -p $orig $tmp $prep

echo "pre-processing train data..."
for l in $src $tgt; do
    f=EUbookshop.$lang.$l
    tok=EUbookshop.$lang.tok.$l
    
    perl $TOKENIZER -threads 8 -l $l > $tmp/$tok
    echo""
done

perl $CLEAN -ratio 1.5 $tmp/EUbookshop.$lang.tok $src $tgt $tmp/EUbookshop.$lang.clean 1 175

for l in $src $tgt; do
    perl $LC < $tmp/EUbookshop.$lang.clean.$l > $tmp/EUboookshop.$lang.$l
done

echo "pre-processing valid/test data..."
for l in $src $tgt; do
    for o in $orig/QED.en-ga.$l; do
    f=$tmp/QED.en-ga.$l
    echo $o $f
    perl $TOKENISER -threads 8 -l $l | \
    perl $LC > $f
    echo""
    done
done


echo "creating train, valid, test..."
for l in $src $tgt; do
    awk '{if (NR%23 == 0) print $0; }' $tmp/EUbookshop.$lang.$l > $tmp/valid/$l
    awk '{if (NR%23 != 0) print $0; }' $tmp/EUbookshop.$lang.$l > $tmp/train/$l
    
    cat $tmp/QED.en-ga.$l
        > $tmp/test.$l
done

TRAIN=$tmp/train.en-ga
BPE_CODE=$prep/code
rm -f $TRAIN

for l in $src $tgt; do
        cat $tmp/train.$l >> $TRAIN
done

echo "Applying learn_bpe.py on ${TRAIN}..."
python $BPEROOT/learn_bpe.py -s $BPE_TOKENS < TRAIN > $BPE_CODE

for L in $src $tgt; do
        for f in train.$L valid.$L test.$L; do
                echo "Applying apply_bpe.py to ${f}..."
                python $BPEROOT/apply_bpe.py -c $BPE_CODE < $tmp/$f > $prep/$f
        done
done

#This shell script is adapted from https://github.com/pytorch/fairseq/blob/master/examples/translation/prepare-iwslt14.sh

echo 'Cloning Moses'
git clone https://github.com/moses-smt/mosesdecoder.git

echo 'Cloning Subword_NMT'
git clone https://github.com/rsennrich/subword-nmt.git

SCRIPTS=mosesdecoder/scripts
TOKENISER=$SCRIPTS/tokenizer/tokenizer.perl
LC=$SCRIPTS/training/clean_corpus-n.perl
BPEROOT=subword-nmt/subword_nmt
BPE_TOKENS=10000

URL="http://opus.nlpl.eu/download.php?f=EUbookshop/v2/moses/en-ga.txt.zip"
GZ=en-ga.txt.zip

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

echo "Downloading Corpus (${URL})..."
cd $orig
wget "$URL"

if [ -f $GZ ]; then #prints whether the data has been successfully download
    echo "Data successfully downloaded."
else
    echo "Data not successfully downloaded."
    exit
fi

tar zxvf $GZ
cd ..

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
    for o in `ls $orig/
    fname=${o##*/}
    f=$tmp/${fname%.*}
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

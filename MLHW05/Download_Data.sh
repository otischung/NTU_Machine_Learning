git clone https://github.com/pytorch/fairseq.git
cd fairseq && git checkout 9a1c497 && cd ..
pip install --upgrade ./fairseq/

cd ..
mkdir -p ./DATA/
wget https://www.csie.ntu.edu.tw/~r09922057/ML2021-hw5/ted2020.tgz -O ./DATA/ted2020.tgz
wget https://www.csie.ntu.edu.tw/~r09922057/ML2021-hw5/test.tgz -O ./DATA/test.tgz
tar -xvf ./DATA/ted2020.tgz -C ./DATA
tar -xvf ./DATA/test.tgz -C ./DATA
rm -f ./DATA/ted2020.tgz ./DATA/test.tgz
mv ./DATA/raw.en ./DATA/train_dev.raw.en
mv ./DATA/raw.zh ./DATA/train_dev.raw.zh
mv ./DATA/test.en ./DATA/test.raw.en
mv ./DATA/test.zh ./DATA/test.raw.zh

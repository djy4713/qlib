date="2024-05-07"
root="/root/.qlib/qlib_data/cn_data"
file="qlib_bin.tar.gz"
wget https://github.com/chenditc/investment_data/releases/download/$date/$file .
mkdir -p $root; mv $file $root; cd $root; tar -xvf $file
cd $root; mv qlib_bin/* .; rm -r qlib_bin


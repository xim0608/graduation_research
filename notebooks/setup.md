# workerのセットアップ(idcfクラウド)

1. s1を建てた後、ファイアウォールとポートフォワードを設定して、sshできるようにする
2. 下記ライブラリをインストールしていく
```
yum -y groupinstall "Development Tools"
yum remove mariadb-libs
yum install -y https://centos7.iuscommunity.org/ius-release.rpm
yum install python36u python36u-libs python36u-devel python36u-pip
ln -s /usr/bin/python3.6 /usr/bin/python3
ln -s /usr/bin/pip3.6 /usr/bin/pip3
#yum localinstall http://dev.mysql.com/get/mysql57-community-release-el7-7.noarch.rpm
#yum install mysql-community-client
pip3 install pipenv
git clone https://github.com/xim0608/graduation_research.git
cd graduation_research


rpm -ivh http://packages.groonga.org/centos/groonga-release-1.1.0-1.noarch.rpm
yum -y install mecab mecab-devel mecab-ipadic git make curl xz

# ローカルで生成してscpでサーバに送信(メモリ不足でサーバ上ではコンパイルできない)
git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git
cd mecab-ipadic-neologd
./bin/install-mecab-ipadic-neologd -n
scp -r /usr/local/lib/mecab/dic/mecab-ipadic-neologd worker01.idcf:/usr/lib/mecab/dic/


yum -y install python-devel mysql-devel gcc
pipenv --python 3.6
pipenv install
yum -y install libX11 GConf2 fontconfig
wget https://chromedriver.storage.googleapis.com/2.41/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
mv chromedriver /usr/local/bin
yum -y install ipa-gothic-fonts ipa-mincho-fonts ipa-pgothic-fonts ipa-pmincho-fonts
fc-cache -fv

# vi /etc/yum.repos.d/google-chrome.repo

----- ここから -----
[google-chrome]
name=google-chrome
baseurl=http://dl.google.com/linux/chrome/rpm/stable/x86_64
enabled=1
gpgcheck=1
gpgkey=https://dl.google.com/linux/linux_signing_key.pub

yum update
yum install google-chrome-stable
```
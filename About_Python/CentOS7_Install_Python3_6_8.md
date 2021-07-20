## CentOS7 安装Python3.6.8

1. 安装依赖环境

```linux
yum -y install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel
```

2.下载Python3.6.8

```linux
mkdir /usr/local/python3
```

3.在python3文件夹下下载安装包（/usr/local/python3/Python-3.6.8 )，解压文件

```linux
wget https://www.python.org/ftp/python/3.6.8/Python-3.6.8.tar.xz
tar -xvf Python-3.6.8.tar.xz
```

4.编译（在解压的文件夹下 /usr/local/python3/Python-3.6.8)

```linux
./configure --prefix=/usr/local/python3
```

5.安装（在解压的文件夹下 /usr/local/python3/Python-3.6.8)

```linux
make
make install  # 先make再make install
```

6.创建新版本的软链接

修改旧版本

```linux
mv /usr/bin/python /usr/bin/python_bak
mv /usr/bin/pip /usr/bin/pip_bak  #这步可能会报错，没有没有这个目录，不用理会
```

创建新版本的软链接

```
ln -s /usr/local/python3/bin/python3 /usr/bin/python
ln -s /usr/local/python3/bin/pip3 /usr/bin/pip
```

7.检查python的版本

```
python -V
```

8.由于yum是py2写的，所以更换完python路径后，yum可能会出现错误 
所以要修改配置文件

```linux
vi /usr/bin/yum
第一行
#! /usr/bin/python
改为
#! /usr/bin/python2.7


vi /usr/libexec/urlgrabber-ext-down
第一行
#! /usr/bin/python
改为
#! /usr/bin/python2.7
```

如果没有gcc和make报错就用yum安装

```
yum installl gcc make -y
```

```
pip list 或者pip --version
```








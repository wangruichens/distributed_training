1.下载安装Openmpi

https://www.open-mpi.org/faq/?category=building#easy-build

gunzip -c openmpi-4.0.1.tar.gz | tar xf -
cd openmpi-4.0.1
./configure --prefix=/usr/local
make -j8  (8线程，速度快一些)
sudo make install

scp -r openmpi-4.0.1 wangrc@172.17.19.139:/home/wangrc


*(
完成后需要添加环境变量到.bashrc：
export PATH="$PATH:/usr/local/openmpi/bin"
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/openmpi/lib/"
完成后执行
sudo ldconfig
)

测试是否安装成功：
mpirun   或 which mpirun
或者编译运行测试脚本：
cd examples
make
mpirun -np 8 hello_c

也可以通过conda 安装，注意版本应该选择3.1.2 ：
Open MPI 3.1.3 has an issue that may cause hangs. It is recommended to downgrade to Open MPI 3.1.2 or upgrade to Open MPI 4.0.0.
conda install -c conda-forge openmpi=3.1.2

*这里我使用的tensorflow版本是1.12.0

2.pip安装 horovod
pip install -i  https://pypi.tuna.tsinghua.edu.cn/simple horovod

然而我遇到一个错误：
mpi_lib.cpython-36m-x86_64-linux-gnu.so: undefined symbol:_ZN10tensorflow12OpDefBuilder4AttrESs
解决办法：
https://github.com/horovod/horovod/issues/656

原因是因为conda和系统自带的gcc版本不同

$
$ conda install gcc_linux-64 gxx_linux-64

CC=/opt/anaconda3/bin/x86_64-conda_cos6-linux-gnu-gcc
需要手动指定gcc 位置，重新安装hvd：
HOROVOD_WITH_TENSORFLOW=1 CC=/opt/anaconda3/bin/x86_64-conda_cos6-linux-gnu-gcc ./pip3 install --no-cache-dir -i  https://pypi.tuna.tsinghua.edu.cn/simple horovod

$ [flags] pip install --no-cache-dir -i  https://pypi.tuna.tsinghua.edu.cn/simple horovod

测试代码：

import tensorflow as tf
import horovod.tensorflow as hvd

def fn(magic_number):
    import horovod.torch as hvd
    hvd.init()
    print('Hello, rank = %d, local_rank = %d, size = %d, local_size = %d, magic_number = %d' % (hvd.rank(), hvd.local_rank(), hvd.size(), hvd.local_size(), magic_number))
    return hvd.rank()
import horovod.spark
horovod.spark.run(fn, args=(42,))

3.pyspark支持

pyspark
petastorm >= 0.7.0
h5py >= 2.9.0
tensorflow-gpu >= 1.12.0 (or tensorflow >= 1.12.0)
horovod >= 0.15.3
def fn(magic_number):
    import horovod.torch as hvd
    hvd.init()
    print('Hello, rank = %d, local_rank = %d, size = %d, local_size = %d, magic_number = %d' % (hvd.rank(), hvd.local_rank(), hvd.size(), hvd.local_size(), magic_number))
    return hvd.rank()
import horovod.spark
horovod.spark.run(fn, args=(42,))
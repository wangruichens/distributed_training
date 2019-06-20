from __future__ import print_function
import tensorflow as tf
import argparse
import time
import os

FLAGS = None
log_dir = '/logdir'


def main():
    # Distributed Baggage
    cluster = tf.train.ClusterSpec({
        'ps': ['172.16.0.102:2822'],
        'worker': ['172.17.20.206:2823']
    })  # lets this node know about all other nodes
    if FLAGS.job_name == 'ps':  # checks if parameter server
        server = tf.train.Server(cluster,
                                 job_name="ps",
                                 task_index=FLAGS.task_index)
        server.join()
    else:
        is_chief = (FLAGS.task_index == 0)  # checks if this is the chief node
        server = tf.train.Server(cluster,
                                 job_name="worker",
                                 task_index=FLAGS.task_index)

        # Graph
        with tf.device('/cpu:0'):
            a = tf.Variable(tf.truncated_normal(shape=[1]), dtype=tf.float32)
            b = tf.Variable(tf.truncated_normal(shape=[1]), dtype=tf.float32)
            c = 2* a + b

            target = tf.constant(100., shape=[1], dtype=tf.float32)
            loss = tf.reduce_mean(tf.square(c - target))

            opt = tf.train.GradientDescentOptimizer(.01).minimize(loss)

        # Session
        # Monitored Training Session

        config = tf.ConfigProto()
        config.gpu_options.per_process_gpu_memory_fraction = 0.4

        sess = tf.train.MonitoredTrainingSession(
            master=server.target,
            is_chief=is_chief,
        config=config)
        for i in range(100):
            if sess.should_stop(): break
            sess.run(opt)
            if i % 10 == 0:
                ra = sess.run(a)
                rb = sess.run(b)
                print(ra, rb)
        sess.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # Flags for defining the tf.train.ClusterSpec
    parser.add_argument(
        "--job_name",
        type=str,
        default="",
        help="One of 'ps', 'worker'"
    )
    # Flags for defining the tf.train.Server
    parser.add_argument(
        "--task_index",
        type=int,
        default=0,
        help="Index of task within the job"
    )
    FLAGS, unparsed = parser.parse_known_args()
    main()
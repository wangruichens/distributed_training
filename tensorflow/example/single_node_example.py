from __future__ import print_function
import tensorflow as tf
import time


def main():
    # Graph
    with tf.device('/cpu:0'):
        a = tf.Variable(tf.truncated_normal(shape=[1]), dtype=tf.float32)
        b = tf.Variable(tf.truncated_normal(shape=[1]), dtype=tf.float32)
        c = 2*a + b

        target = tf.constant(100., shape=[1], dtype=tf.float32)
        loss = tf.reduce_mean(tf.square(c - target))

        opt = tf.train.GradientDescentOptimizer(.001).minimize(loss)

    # Session
    sv = tf.train.Supervisor()
    sess = sv.prepare_or_wait_for_session()
    for i in range(100):
        sess.run(opt)
        if i % 10 == 0:
            ra = sess.run(a)
            rb = sess.run(b)
            print(ra,rb)


if __name__ == '__main__':
    main()

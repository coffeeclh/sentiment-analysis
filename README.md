This repository contains all code necessary to perform sentiment analysis on a large dataset of Git commit messages
from GitHub (http://www.ghtorrent.org). The code is meant to be run on the Distributed ASCI Supercomputer 3 (DAS-3) at LIACS. It makes use of
Apache Hadoop's HDFS and MapReduce to perform the sentiment analysis. 

Prerequisites
=============

The version numbers mentioned below have been verified to work. Different versions might also work.

* Git 2.3
* Python 2.7.9

Cloning the repository
======================

The first step is to clone the repository to obtian a local copy of the code. Open a terminal window and run the following commands.

    $ git clone https://github.com/timvandermeij/SDDM.git
    $ cd SDDM

Running the code
================

All code is written in Python. To run the simple sentiment analaysis program, execute:

    $ python analyze.py "Yay, sentiment analysis is working perfectly!"

The output of the application is a score between -1 and 1, where -1 indicates that the message is negative, 1 indicates that the
message is positive and 0 indicates that the message is neutral.

Installation notes for the DAS-3
================================

Python 2.7.9
------------

Compile `python` from source:

    $ wget https://www.python.org/ftp/python/2.7.9/Python-2.7.9.tgz
    $ tar xzvf Python-2.7.9.tgz
    $ cd Python-2.7.9
    $ ./configure --prefix=$HOME/.local
    $ make
    $ make install

Virtualenv
----------

Install `virtualenv` using `pip`:

    $ pip install --user virtualenv
    $ cd /scratch/scratch/{username} (we assume this directory from now on)
    $ virtualenv -p $HOME/.local/bin/python2.7 python
    $ virtualenv --relocatable python

We have now created a virtual environment called `python`. The goal is to distribute this over all the nodes using HDFS.

Shared libaries
---------------

Note that this is optional. It's mostly about `wget`, `./configure --prefix=/scratch/scratch/{username}/opt`, `make` and `make install`.

* OpenBLAS: instead do the first part of http://stackoverflow.com/questions/11443302/compiling-numpy-with-openblas-integration/14391693#14391693
  with correct `PREFIX=...` and no `sudo` nor `ldconfig`.
* OpenMPI

Update ~/.bashrc
----------------

The final line for BLAS is optional.

    PATH="$PATH:$HOME/.local/bin:/mounts/CentOS/6.6/root/usr/bin:/scratch/scratch/{username}/python/bin:/scratch/scratch/{username}/opt/bin"
    export LIBRARY_PATH="$HOME/.local/lib:/scratch/scratch/{username}/opt/lib"
    export LD_LIBRARY_PATH="$HOME/.local/lib:/scratch/scratch/{username}/opt/lib"
    export CPATH="$HOME/.local/include:/scratch/scratch/{username}/opt/include"
    export BLAS="$HOME/.local/lib/libopenblas.a"

Then use `source ~/.bashrc` to reload the configuration.

Python libraries
----------------

    $ source python/bin/activate
    (python)$ pip install cython
    (python)$ pip install readline
    (python)$ pip install numpy
    (python)$ pip install scipy,pandas,scikit-learn,numexpr,matplotlib,mpi4py

For the last command you need to run it with every single comma-separated value. `mpi4py` is optional.

There is a chance that the `numpy` does not work because you might want OpenBLAS. Then we need to install from source according to the following link:
http://stackoverflow.com/questions/11443302/compiling-numpy-with-openblas-integration/14391693#14391693

Note that this might mess up the latter `pip` installations since they depend on `numpy` and consider `numpy` installed this way to be incompatible, but that
can be avoided by passing `--no-deps` to at least `scipy`, `pandas`, `scikit-learn` and `numexpr`.

HDFS
----

    $ tar xzvf python.tgz python/
    $ tar xzvf local.tgz $HOME/.local/*
    $ tar xzvf libs.tgz /usr/lib64/libg2c.so* /usr/lib/libgfortran.so*
    $ hdfs dfs -put python.tgz, local.tgz, libs.tgz

Update ~/.bashrc again
----------------------

    export HDFS_URL='hdfs://fs.das3.liacs.nl:8020/user/{username}'
    pyhadoop () {
        input=$1;shift;
        if [[ "x$input" = "x" ]]; then
            echo "Usage: pyhadoop <input> <output> <mapper> <reducer> [margs] [rargs] [...]"
            echo "Input and output are on HDFS, mapper and reducer are files in this directory."
            echo "Specify mapper and reducer arguments between quotes."
            echo "Rest of the parameters are used for the hadoop streaming command near start."
            return
        fi
        output=$1;shift;
        mapper=$1;shift;
        reducer=$1;shift;
        margs=$1;shift;
        rargs=$1;shift;
        echo "Arguments: input=$input output=$output mapper=\"$mapper $margs\" reducer=\"$reducer $rargs\" REST=\"$@\""
        hadoop jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar -archives "$HDFS_URL/python.tgz#python,$HDFS_URL/local.tgz#local,$HDFS_URL/libs.tgz#libs" $@ -input "$input" -output "$output" -cmdenv "LD_LIBRARY_PATH=./local/lib:./libs/usr/lib64" -cmdenv "PYTHONHOME=./python/python:./local" -cmdenv "PYTHONPATH=./python/python/lib/python2.7:./local/lib/python2.7" -mapper "./python/python/bin/python $mapper $margs" -reducer "./python/python/bin/python $reducer $rargs" -file "$mapper" -file "$reducer"
    }

After sourcing `~/.bashrc` again, the function gives help by running `pyhadoop`.

Finding application logs
------------------------
After completing a job, you can find the logs with:

    $ hdfs dfs -ls /app-logs/{username}/logs/

The latest one is the most recent application job. Copy the whole application ID behind the slash, e.g. `application_1421846212827_0079`. Then you can read the logs with:
    
    $ yarn logs -applicationId application_1421846212827_0079 | less

Authors
=======

* Tim van der Meij (Leiden University, @timvandermeij)
* Leon Helwerda (Leiden University, @lhelwerd)

References
==========

* https://github.com/jeffreybreen/twitter-sentiment-analysis-tutorial-201107/tree/master/data/opinion-lexicon-English (positive and negative word lists)

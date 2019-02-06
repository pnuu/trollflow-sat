FROM continuumio/miniconda3:latest
EXPOSE 9001
RUN conda config --add channels conda-forge && \
    conda update conda && \
    conda install satpy \
    pyresample \
    pykdtree \
    trollimage \
    pycoast \
    pyorbital \
    rasterio \
    gdal \
    h5py \
    ipython \
    pyinotify \
    pyzmq \
    h5netcdf \
    netifaces \
    meld3 \
    scp \
    paramiko \
    dpath && \
    conda clean -a -y && \
    pip install posttroll && \
    pip install pytroll-schedule && \
    pip install pytroll-collectors && \
    pip install trollmoves && \
    pip install trollflow && \
    pip install trollflow-sat && \
    cd /tmp/ && \
    git clone https://github.com/Supervisor/supervisor.git && \
    cd supervisor && python setup.py install && \
    cd /tmp/ && rm -rf /tmp/supervisor/ && \
    git clone https://github.com/Supervisor/superlance.git && \
    cd superlance && python setup.py install && \
    cd /tmp/ && rm -rf /tmp/superlance/
CMD ["supervisord", "-c", "/mnt/config/supervisord.conf"]

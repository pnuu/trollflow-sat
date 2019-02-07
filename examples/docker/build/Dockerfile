FROM continuumio/miniconda3:latest
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
    conda clean -a -y
ADD requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt && \
    rm -r /tmp/requirements.txt &&  \
    cd /tmp/ && \
    git clone https://github.com/Supervisor/supervisor.git && \
    cd supervisor && python setup.py install && \
    cd /tmp/ && rm -rf /tmp/supervisor/ && \
    git clone https://github.com/Supervisor/superlance.git && \
    cd superlance && python setup.py install && \
    cd /tmp/ && rm -rf /tmp/superlance/ && \
    python -c 'from pyspectral.utils import download_luts; \
      from pyspectral.utils import logging_on; import logging; \
      logging_on(logging.DEBUG); download_luts()' && \
    python -c 'from pyspectral.utils import download_rsr; \
      from pyspectral.utils import logging_on; import logging; \
      logging_on(logging.DEBUG); download_rsr()'

CMD ["supervisord", "-c", "/mnt/config/supervisord.conf"]


import Queue
from threading import Thread
import logging
import time
from urlparse import urlunsplit
import os.path

from posttroll.publisher import Publish
from posttroll.message import Message
from trollsift import compose
from trollflow_sat import utils


class DataWriterContainer(object):

    '''Container for DataWriter instance
    '''

    logger = logging.getLogger("DataWriterContainer")

    def __init__(self, topic=None, port=0, nameservers=[],
                 save_settings=None):
        self.topic = topic
        self._input_queue = None
        self.output_queue = Queue.Queue()
        self.thread = None

        # Create a Writer instance
        self.writer = DataWriter(queue=self.input_queue,
                                 save_settings=save_settings,
                                 topic=topic,
                                 port=port, nameservers=nameservers)
        # Start Writer instance into a new daemonized thread.
        self.thread = Thread(target=self.writer.run)
        self.thread.setDaemon(True)
        self.thread.start()

    @property
    def input_queue(self):
        """Property writer"""
        return self._input_queue

    @input_queue.setter
    def input_queue(self, queue):
        """Set writer queue"""
        self._input_queue = queue
        self.writer.queue = queue

    def __setstate__(self, state):
        self.__init__(**state)

    def restart(self):
        '''Restart writer after configuration update.
        '''
        if self.writer is not None:
            if self.writer.loop:
                self.stop()
        self.__init__()

    def stop(self):
        '''Stop writer.'''
        self.logger.debug("Stopping writer.")
        self.writer.stop()
        self.thread.join()
        self.logger.debug("Writer stopped.")
        self.thread = None


class DataWriter(Thread):

    """Writes data to disk.
    """

    logger = logging.getLogger("DataWriter")

    def __init__(self, queue=None, save_settings=None,
                 topic=None, port=0, nameservers=[]):
        Thread.__init__(self)
        self.queue = queue
        self._loop = False
        self._save_settings = save_settings
        self._port = port
        self._nameservers = nameservers
        self._topic = topic

    def run(self):
        """Run the thread."""
        self._loop = True
        # Parse settings for saving
        compression = self._save_settings.get('compression', 6)
        tags = self._save_settings.get('tags', None)
        fformat = self._save_settings.get('fformat', None)
        gdal_options = self._save_settings.get('gdal_options', None)
        blocksize = self._save_settings.get('blocksize', None)

        kwargs = {'compression': compression,
                  'tags': tags,
                  'fformat': fformat,
                  'gdal_options': gdal_options,
                  'blocksize': blocksize}

        # Initialize publisher context
        with Publish("l2producer", port=self._port,
                     nameservers=self._nameservers) as pub:

            while self._loop:
                if self.queue is not None:
                    try:
                        lcl = self.queue.get(True, 1)
                    except Queue.Empty:
                        continue
                    info = lcl.info
                    time_name = utils.find_time_name(info)
                    product_config = lcl.info["product_config"]
                    products = lcl.info["products"]
                    dataset_ids = lcl.info["dataset_ids"]

                    for i, prod in enumerate(products):
                        fnames, _ = utils.create_fnames(info,
                                                        product_config,
                                                        prod)
                        # Some of the files might have specific
                        # writers, use them if configured
                        writers = utils.get_writer_names(product_config, prod,
                                                         info["areaname"])
                        # product_config, prod_id, area_name
                        for fname in fnames:
                            self.logger.info("Saving %s", fname)
                            lcl.save_dataset(dataset_ids[i],
                                             filename=fname,
                                             writer=writers[i],
                                             **kwargs)
                            area = lcl[prod].info["area"]
                            to_send = {"nominal_time": info[time_name],
                                       "uid": os.path.basename(fname),
                                       "uri": os.path.abspath(fname),
                                       "area": {"name": area.name,
                                                "area_id": area.area_id,
                                                "proj_id": area.proj_id,
                                                "proj4": area.proj4_string,
                                                "shape": (area.x_size,
                                                          area.y_size)
                                                },
                                       "productname": info["productname"]
                                       }

                            if self._topic is not None:
                                msg = Message(self._topic, "file", to_send)
                                pub.send(str(msg))
                                self.logger.debug("Sent message: %s", str(msg))
                            self.logger.info("Saved %s", fname)

                    del lcl
                    lcl = None
                else:
                    time.sleep(1)

    def stop(self):
        """Stop writer."""
        self._loop = False

    @property
    def loop(self):
        """Property loop"""
        return self._loop
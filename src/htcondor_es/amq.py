import time
import logging
import multiprocessing
from htcondor_es.StompAMQ import StompAMQ

_amq_interface = None
def get_amq_interface():
    global _amq_interface
    if not _amq_interface:
        try:
            username = open('username', 'r').read().strip()
            password = open('password', 'r').read().strip()
        except IOError:
            print "ERROR: Provide username/password for CERN AMQ"
            return []
        _amq_interface = StompAMQ(username=username,
                                  password=password,
                                  producer='condor',
                                  topic='/topic/cms.jobmon.condor',
                                  host_and_ports=[('cms-mb.cern.ch', 61313)])

    return _amq_interface


def post_ads(ads, metadata=None):
    if not len(ads):
        logging.warning("No new documents found")
        return

    metadata = metadata or {}
    interface = get_amq_interface()
    list_data = []
    for id_, ad in ads:
        list_data.append(interface.make_notification(payload=ad,
                                                     docType='htcondor_job_info',
                                                     docId=id_,
                                                     ts=ad['RecordTime'],
                                                     metadata=metadata,
                                                     dataSubfield=None))

    starttime = time.time()
    failed_to_send = interface.send(list_data)
    elapsed = time.time() - starttime
    return (len(ads)-len(failed_to_send), len(ads), elapsed)

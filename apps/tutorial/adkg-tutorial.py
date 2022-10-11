"""
ADKG tutorial.

Instructions:
   run this with
```
sh scripts/launch-tmuxlocal.sh apps/tutorial/adkg-tutorial.py conf/adkg/local
```
"""
from adkg.config import HbmpcConfig
from adkg.adkg import ADKG
from adkg.poly_commit_hybrid import PolyCommitHybrid
import asyncio
import time
import logging
import uvloop

logger = logging.getLogger("benchmark_logger")
logger.setLevel(logging.ERROR)
# Uncomment this when you want logs from this file.
logger.setLevel(logging.NOTSET)

# from pypairing import ZR, G1, blsmultiexp as multiexp
from pypairing import Curve25519ZR as ZR, Curve25519G as G1, curve25519multiexp as multiexp

def get_avss_params(n, G1):
    g, h = G1.rand(b'g'), G1.rand(b'h')
    public_keys, private_keys = [None] * n, [None] * n
    for i in range(n):
        private_keys[i] = ZR.hash(str(i).encode())
        public_keys[i] = g**private_keys[i]
    return g, h, public_keys, private_keys


async def _run(peers, n, t, my_id, start_time):
    g, h, pks, sks = get_avss_params(n, G1)
    pc = PolyCommitHybrid(g, h, ZR, multiexp)

    from adkg.ipc import ProcessProgramRunner
    async with ProcessProgramRunner(peers, n, t, my_id) as runner:
        send, recv = runner.get_send_recv("ADKG")
        logging.info(f"Starting ADKG: {(my_id)}")
        logging.info(f"Start time: {(start_time)}, diff {(start_time-int(time.time()))}")

        benchmark_logger = logging.LoggerAdapter(
           logging.getLogger("benchmark_logger"), {"node_id": my_id}
        )
        deg = 2*t
        with ADKG(pks, sks[my_id], g, h, n, t, deg, my_id, send, recv, pc, multiexp, ZR, G1) as adkg:
            while True:
                if time.time() > start_time:
                    break
                time.sleep(0.1)
            
            begin_time = time.time()
            logging.info(f"ADKG start time: {(begin_time)}")
            adkg_task = asyncio.create_task(adkg.run_adkg(begin_time))
            # await adkg.output_queue.get()
            logging.info(f"Created ADKG task, now waiting...")
            await adkg_task
            end_time = time.time()
            adkg_time = end_time-begin_time
            logging.info(f"ADKG time: {(adkg_time)}")
            benchmark_logger.info("ADKG time: %f", adkg_time)
            try:
                adkg.kill()
                adkg_task.cancel()
            except:
                print("Processed killed!")
        bytes_sent = runner.node_communicator.bytes_sent
        for k,v in runner.node_communicator.bytes_count.items():
            print(f"[{my_id}] Bytes Sent: {k}:{v} which is {round((100*v)/bytes_sent,3)}%")
        print(f"[{my_id}] Total bytes sent out aa: {bytes_sent}")


if __name__ == "__main__":
    from adkg.config import HbmpcConfig
    logging.info("Running ADKG ...")
    HbmpcConfig.load_config()
    
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(
            _run(
                HbmpcConfig.peers,
                HbmpcConfig.N,
                HbmpcConfig.t,
                HbmpcConfig.my_id,
                HbmpcConfig.time,
            )
        )
    finally:
        loop.close()
from distributed import Client
from dask_lxplus import CernCluster
import socket

def hname():
    import socket
    return socket.gethostname()

def main():
    n_port = 8786
    with CernCluster(
            cores=1,
            memory='2000MB',
            disk='1000MB',
            death_timeout = '60',
            lcg = True,
            nanny = False,
            container_runtime = "none",
            log_directory = "/eos/user/b/bejones/condor/log",
            scheduler_options={
                'port': n_port,
                'host': socket.gethostname(),
                },
            job_extra={
                '+JobFlavour': '"tomorrow"',
                },
            extra = ['--worker-port 10000:10100']
            ) as cluster:
        print(cluster.job_script())
        with Client(cluster) as client:
            futures = []
            cluster.scale(4)
            for i in range(4):
              f = client.submit(hname)
              futures.append(f)
            print('Result is {}'.format(client.gather(futures)))

if __name__ == '__main__':
    main()

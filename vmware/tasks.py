from celery import shared_task

from vmware.workers.poolVmwareTask import poolVmwareTask

@shared_task(name="pollVmware_task")
def assetAsync_task(assetId, taskMoId, targetId):
    pass
    #return poolVmwareTask(assetId, taskMoId, targetId)

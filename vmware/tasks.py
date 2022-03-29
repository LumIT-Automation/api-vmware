from celery import shared_task

from vmware.workers.poolVmwareTask import poolVmwareTask

@shared_task(name="pollVmware_task")
def poolVmwareAsync_task(assetId, taskMoId, targetId):
    return poolVmwareTask(assetId, taskMoId, targetId)

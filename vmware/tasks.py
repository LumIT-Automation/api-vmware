from celery import shared_task

from vmware.workers.poolVmwareTask import poolVmwareTask

@shared_task(name="pollVmware_task")
def poolVmwareAsync_task(assetId, taskMoId, targetId):
    print("POLLO IL TASK")
    return poolVmwareTask(assetId, taskMoId, targetId)

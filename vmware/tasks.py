from celery import shared_task

from vmware.workers.pollVmwareTask import pollVmwareTask

@shared_task(name="pollVmware_task")
def poolVmwareAsync_task(assetId, taskMoId, targetId):
    return pollVmwareTask(assetId, taskMoId, targetId)
